from django.db import models
from django.db.models import ExpressionWrapper, F, FloatField, Q, Sum
from django.db.models.expressions import Window
from django.db.models.functions import RowNumber


class BaseDataManager(models.manager.Manager):
    def _last_four_quarters(self):
        year, quarter = self.get_current_period().values()

        if quarter and year and quarter != 4:
            quarters = [1, 2, 3, 4][quarter:]
            return self.filter(Q(year=year - 1, quarter__in=quarters) | Q(year=year))

        return self.filter(year__gte=int(year or 0))

    def get_current_period(self):
        return self.order_by('-year', '-quarter').distinct('year').values('year', 'quarter').first() or {
            'year': None,
            'quarter': None,
        }


class UKTotalTradeDataManager(BaseDataManager):
    def market_trends(self):
        qs = self
        year, quarter = self.get_current_period().values()

        if quarter and quarter != 4:
            qs = qs.exclude(year=year)

        return qs.values('country', 'year').annotate(imports=Sum('imports'), exports=Sum('exports')).order_by('year')

    def highlights(self):
        last_four_quarters = self._last_four_quarters()
        total = last_four_quarters.aggregate(total=Sum('exports'))['total']

        if total and total != 0:
            return last_four_quarters.values('country__iso2').annotate(
                total_uk_exports=Sum('exports'),
                trading_position=Window(expression=RowNumber(), order_by=F('total_uk_exports').desc()),
                percentage_of_uk_trade=ExpressionWrapper(
                    F('total_uk_exports') * 100.0 / total, output_field=FloatField()
                ),
            )

        return self.none()


class UKTtradeInServicesDataManager(BaseDataManager):
    def top_services_exports(self):
        last_four_quarters = self._last_four_quarters()

        return (
            last_four_quarters.values('country__iso2', 'service_code')
            .annotate(label=F('service_name'), value=Sum('exports'))
            .order_by('-value')
        )
