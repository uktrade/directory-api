from directory_constants.constants import choices, exred_sector_names
from directory_validators.company import no_html
from directory_validators import enrolment as shared_validators

from django.db import models
from django.utils.functional import cached_property

from api.model_utils import TimeStampedModel


class TriageResult(TimeStampedModel):
    sector = models.CharField(
        choices=exred_sector_names.SECTORS_CHOICES,
        max_length=255
    )
    exported_before = models.BooleanField()
    regular_exporter = models.BooleanField()
    used_online_marketplace = models.NullBooleanField()
    company_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        validators=[no_html],
    )
    company_number = models.CharField(
        max_length=8,
        validators=[
            shared_validators.company_number,
            no_html,
        ],
        unique=False,
        null=True,
        blank=True,
    )
    is_in_companies_house = models.BooleanField()
    sso_id = models.PositiveIntegerField(unique=True)

    @cached_property
    def sector_name(self):
        return exred_sector_names.CODES_SECTORS_DICT[self.sector]

    def __str__(self):  # pragma: no cover
        return self.company_name


class ArticleRead(TimeStampedModel):
    article_uuid = models.UUIDField(choices=choices.EXREAD_ARTICLES_CHOICES)
    sso_id = models.PositiveIntegerField()

    class Meta:
        unique_together = ('article_uuid', 'sso_id')


class TaskCompleted(TimeStampedModel):
    task_uuid = models.UUIDField()
    sso_id = models.PositiveIntegerField()
