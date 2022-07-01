import logging
from datetime import datetime

from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from django.utils.crypto import constant_time_compare
from django.utils.decorators import decorator_from_middleware
from field_history.models import FieldHistory
from mohawk import Receiver
from mohawk.exc import HawkFail
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from activitystream.serializers import (
    ActivityStreamCompanySerializer,
    ActivityStreamExportPlanQuestionSerializer,
    ActivityStreamExportPlanSerializer,
)
from company.models import Company
from exportplan.models import CompanyExportPlan

logger = logging.getLogger(__name__)

NO_CREDENTIALS_MESSAGE = 'Authentication credentials were not provided.'
INCORRECT_CREDENTIALS_MESSAGE = 'Incorrect authentication credentials.'
MAX_PER_PAGE = 500


def lookup_credentials(access_key_id):
    """Raises a HawkFail if the passed ID is not equal to
    settings.ACTIVITY_STREAM_INCOMING_ACCESS_KEY
    """
    if not constant_time_compare(access_key_id, settings.ACTIVITY_STREAM_INCOMING_ACCESS_KEY):
        raise HawkFail(
            'No Hawk ID of {access_key_id}'.format(
                access_key_id=access_key_id,
            )
        )

    return {
        'id': settings.ACTIVITY_STREAM_INCOMING_ACCESS_KEY,
        'key': settings.ACTIVITY_STREAM_INCOMING_SECRET_KEY,
        'algorithm': 'sha256',
    }


def seen_nonce(access_key_id, nonce, _):
    """Returns if the passed access_key_id/nonce combination has been
    used within 60 seconds
    """
    cache_key = 'activity_stream:{access_key_id}:{nonce}'.format(
        access_key_id=access_key_id,
        nonce=nonce,
    )

    # cache.add only adds key if it isn't present
    seen_cache_key = not cache.add(
        cache_key,
        True,
        timeout=60,
    )

    if seen_cache_key:
        logger.warning('Already seen nonce {nonce}'.format(nonce=nonce))

    return seen_cache_key


def authorise(request):
    """Raises a HawkFail if the passed request cannot be authenticated"""
    return Receiver(
        lookup_credentials,
        request.META['HTTP_AUTHORIZATION'],
        request.build_absolute_uri(),
        request.method,
        content=request.body,
        content_type=request.content_type,
        seen_nonce=seen_nonce,
    )


class ActivityStreamAuthentication(BaseAuthentication):
    def authenticate_header(self, request):
        """This is returned as the WWW-Authenticate header when
        AuthenticationFailed is raised. DRF also requires this
        to send a 401 (as opposed to 403)
        """
        return 'Hawk'

    def authenticate(self, request):
        """Authenticates a request using Hawk signature

        If either of these suggest we cannot authenticate, AuthenticationFailed
        is raised, as required in the DRF authentication flow
        """

        return self.authenticate_by_hawk(request)

    def authenticate_by_hawk(self, request):
        if 'HTTP_AUTHORIZATION' not in request.META:
            raise AuthenticationFailed(NO_CREDENTIALS_MESSAGE)

        try:
            hawk_receiver = authorise(request)
        except HawkFail as e:
            logger.warning(
                'Failed authentication {e}'.format(
                    e=e,
                )
            )
            raise AuthenticationFailed(INCORRECT_CREDENTIALS_MESSAGE)

        return (None, hawk_receiver)


class ActivityStreamHawkResponseMiddleware:
    """Adds the Server-Authorization header to the response, so the originator
    of the request can authenticate the response
    """

    def process_response(self, viewset, response):
        """Adds the Server-Authorization header to the response, so the originator
        of the request can authenticate the response
        """
        response['Server-Authorization'] = viewset.request.auth.respond(
            content=response.content,
            content_type=response['Content-Type'],
        )
        return response


class BaseActivityStreamViewSet(ViewSet):
    authentication_classes = (ActivityStreamAuthentication,)
    permission_classes = ()

    @staticmethod
    def _parse_after(request):
        after = request.GET.get('after', '0.000000_0')
        after_ts_str, after_id_str = after.split('_')
        after_ts = datetime.fromtimestamp(float(after_ts_str))
        after_id = int(after_id_str)
        return after_ts, after_id

    @staticmethod
    def _build_after(request, after_ts, after_id):
        return f'{request.build_absolute_uri(request.path)}?after={after_ts.timestamp()}_{after_id}'

    @staticmethod
    def _generate_response(items, next_page_url):
        """Put together a response in the format required by activity stream"""
        next_page = {'next': next_page_url} if next_page_url else {}
        return Response(
            {
                '@context': [
                    'https://www.w3.org/ns/activitystreams',
                    {
                        'dit': 'https://www.trade.gov.uk/ns/activitystreams/v1',
                    },
                ],
                'type': 'Collection',
                'orderedItems': items,
                **next_page,
            }
        )


class ActivityStreamViewSet(BaseActivityStreamViewSet):
    """List-only view set for the activity stream"""

    @staticmethod
    def _company_in_db(companies_by_id, item):
        return int(item.object_id) in companies_by_id

    @staticmethod
    def _was_company_verified(item):
        return item.field_value and item.field_name in [
            'verified_with_code',
            'verified_with_companies_house_oauth2',
            'verified_with_preverified_enrolment',
        ]

    @decorator_from_middleware(ActivityStreamHawkResponseMiddleware)
    def list(self, request):
        """A single page of activities
        The last page is the page without a 'next' key. A page can be empty,
        but still have a 'next' key for the next page: The activity stream
        allows this.

        This is to allow post-db filtering of results, without blocking the
        request while a "full" page of results is found, which would take a
        non-constant number of queries. Ideally all filtering would be in the
        database, but it might be extremely awkward (.e.g. having to query on
        contents of a json field). Fields are only in FieldHistory because we
        then show them in the activity stream, so the amount of rows returned
        from the db that we then don't show in the activity _won't_ increase
        with unreleated development/fields added to models

        The db query is also kept as simple as possible to make it more likely
        that the db will use an index
        """
        after_ts, after_id = self._parse_after(request)
        history_qs_all = (
            FieldHistory.objects.all()
            .filter(Q(date_created=after_ts, id__gt=after_id) | Q(date_created__gt=after_ts))
            .order_by('date_created', 'id')
        )
        history_qs = history_qs_all[:MAX_PER_PAGE]
        history = list(history_qs)

        # prefetch_related / prefetch_related_objects fetches _all_ the fields
        # from the related table if using a GenericForeignKey, which Field
        # History uses. To only fetch the fields needed, we do our own join
        # in-code. This is what prefetch_related does anyway under the hood,
        # so is likely not worse.

        company_ids = [item.object_id for item in history]
        companies = Company.objects.all().filter(id__in=company_ids).values('id', 'number', 'name')
        companies_by_id = dict((company['id'], company) for company in companies)

        items = [
            {
                'id': ('dit:directory:CompanyVerification:' + str(item.id) + ':Create'),
                'type': 'Create',
                'published': item.date_created.isoformat('T'),
                'generator': {
                    'type': 'Application',
                    'name': 'dit:directory',
                },
                'object': {
                    'type': ['Document', 'dit:directory:CompanyVerification'],
                    'id': 'dit:directory:CompanyVerification:' + str(item.id),
                    'attributedTo': {
                        'type': ['Organization', 'dit:Company'],
                        'id': 'dit:directory:Company:' + item.object_id,
                        'dit:companiesHouseNumber': companies_by_id[int(item.object_id)]['number'],
                        'name': companies_by_id[int(item.object_id)]['name'],
                    },
                },
            }
            for item in history
            if (self._company_in_db(companies_by_id, item) and self._was_company_verified(item))
        ]

        return self._generate_response(
            items=items,
            next_page_url=(self._build_after(request, history[-1].date_created, history[-1].id) if history else None),
        )


class ActivityStreamCompanyViewSet(BaseActivityStreamViewSet):
    """View set to list companies for the activity stream"""

    @decorator_from_middleware(ActivityStreamHawkResponseMiddleware)
    def list(self, request):
        """A single page of companies to be consumed by activity stream."""
        after_ts, after_id = self._parse_after(request)
        companies = list(
            Company.objects.filter(
                Q(modified=after_ts, id__gt=after_id) | Q(modified__gt=after_ts), date_published__isnull=False
            ).order_by('modified', 'id')[:MAX_PER_PAGE]
        )
        return self._generate_response(
            ActivityStreamCompanySerializer(companies, many=True).data,
            self._build_after(request, companies[-1].modified, companies[-1].id) if companies else None,
        )


class ActivityStreamExportPlanViewSet(BaseActivityStreamViewSet):
    """View set to list export plan for the activity stream"""

    @decorator_from_middleware(ActivityStreamHawkResponseMiddleware)
    def list(self, request):
        """A single page of companies to be consumed by activity stream."""
        after_ts, after_id = self._parse_after(request)

        export_plans = list(
            CompanyExportPlan.objects.filter(
                Q(modified=after_ts, id__gt=after_id) | Q(modified__gt=after_ts),
            ).order_by('modified', 'id')[:MAX_PER_PAGE]
        )
        data = ActivityStreamExportPlanSerializer(export_plans, many=True).data
        return self._generate_response(
            data[0] if data else [],
            self._build_after(request, export_plans[-1].modified, export_plans[-1].id) if export_plans else None,
        )


class ActivityStreamExportPlanQuestionViewSet(BaseActivityStreamViewSet):
    """View set to list export plan questions for the activity stream"""

    @decorator_from_middleware(ActivityStreamHawkResponseMiddleware)
    def list(self, request):
        """A single page of export plan questions to be consumed by activity stream."""
        after_ts, after_id = self._parse_after(request)
        export_plan_questions = CompanyExportPlan.objects.get_questions(after_ts, after_id)[:MAX_PER_PAGE]

        return self._generate_response(
            ActivityStreamExportPlanQuestionSerializer(export_plan_questions, many=True).data,
            self._build_after(
                request, export_plan_questions[-1]['exportplan_modified'], export_plan_questions[-1]['exportplan_id']
            )
            if export_plan_questions
            else None,
        )
