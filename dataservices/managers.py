from django.db import models
from django.db.models import ExpressionWrapper, F, FloatField, Q, Sum
from django.db.models.expressions import Window
from django.db.models.functions import RowNumber


class UKTotalTradeDataManager(models.Manager):
    def current_period(self):
        return self.order_by('-year', '-quarter').distinct('year').values('year', 'quarter').first()

    def _last_four_quarters(self):
        year, quarter = self.current_period().values()

        if quarter != 4:
            quarters = [1, 2, 3, 4][quarter:]
            return self.filter(Q(year=year - 1, quarter__in=quarters) | Q(year=year))

        return self.filter(year__gte=year)

    def market_trends(self):
        qs = self
        year, quarter = self.current_period().values()

        if quarter != 4:
            qs = qs.exclude(year=year)

        return qs.values('country', 'year').annotate(imports=Sum('imports'), exports=Sum('exports')).order_by('year')

    def highlights(self):
        last_four_quarters = self._last_four_quarters()
        total = last_four_quarters.aggregate(total=Sum('exports'))

        return last_four_quarters.values('country__iso2').annotate(
            total_uk_exports=Sum('exports'),
            trading_position=Window(expression=RowNumber(), order_by=F('total_uk_exports').desc()),
            percentage_of_uk_trade=ExpressionWrapper(
                F('total_uk_exports') * 100.0 / total['total'], output_field=FloatField()
            ),
        )
