from django.core.management.base import BaseCommand
from exportplan import models
from company.models import Company
from exportplan.helpers import is_ep_plan_empty


class Command(BaseCommand):
    def handle(self, *args, **options):

        empty_ep_counter = 0
        not_empty_ep_counter = 0

        export_plans = models.CompanyExportPlan.objects.all()

        for plan in export_plans.iterator():
            self.stdout.write(self.style.SUCCESS(f'{plan.company}:')) if plan.company else self.stdout.write(
                self.style.WARNING("No Company is associated with this EP.")
            )

            # With country or commodity checks.
            if plan.export_commodity_codes or plan.export_countries:
                self.stdout.write(
                    self.style.SUCCESS(f'Picked Product: {plan.export_commodity_codes[0]["commodity_name"]}')
                ) if plan.export_commodity_codes else None
                self.stdout.write(
                    self.style.SUCCESS(f'Picked Country: {plan.export_countries[0]["country_name"]}')
                ) if plan.export_countries else None

                if is_ep_plan_empty(plan):
                    empty_ep_counter += 1
                    self.stdout.write(self.style.WARNING("EP is empty"))
                    self.stdout.write("---")
                else:
                    not_empty_ep_counter += 1
                    self.stdout.write(self.style.SUCCESS("This EP has content."))

            # No country or product selected then checks everything elses.
            else:
                if is_ep_plan_empty(plan):
                    empty_ep_counter += 1
                    self.stdout.write(self.style.WARNING("EP is empty"))
                    self.stdout.write("---")
                else:
                    not_empty_ep_counter += 1
                    self.stdout.write(self.style.SUCCESS("This EP has content."))

            self.stdout.write("---")

        self.stdout.write(self.style.SUCCESS(f"Empty plan: {empty_ep_counter}"))
        self.stdout.write(self.style.SUCCESS(f"Not Empty plan: {not_empty_ep_counter}"))
