from django.core.management.base import BaseCommand
from exportplan import models
from company.models import Company


class Command(BaseCommand):
    def handle(self, *args, **options):
        ep_sections = [
            "about_your_business",
            "objectives",
            "target_markets_research",
            "adaptation_target_market",
            "marketing_approach",
            "total_cost_and_price",
            "funding_and_credit",
            "getting_paid",
            "travel_business_policies",
            "business_risks",
        ]
        empty_ep_counter = 0
        not_empty_ep_counter = 0

        export_plans = models.CompanyExportPlan.objects.all()

        for plan in export_plans.iterator():
            self.stdout.write(self.style.SUCCESS(f'{plan.company}:')) if plan.company else self.stdout.write(
                self.style.WARNING("No Company is associated with this EP.")
            )

            if plan.export_commodity_codes or plan.export_countries:
                self.stdout.write(
                    self.style.SUCCESS(f'Picked Product: {plan.export_commodity_codes[0]["commodity_name"]}')
                )
                self.stdout.write(self.style.SUCCESS(f'Picked Country: {plan.export_countries[0]["country_name"]}'))

                if not plan.ui_progress:
                    empty_ep_counter += 1
                    self.stdout.write(self.style.WARNING("EP is empty"))
                    self.stdout.write("---")
                    return
                else:
                    for section in ep_sections:
                        content = getattr(plan, section)
                        if content:
                            not_empty_ep_counter += 1
                            self.stdout.write(self.style.SUCCESS("This EP has content."))
                            break
            else:
                if not plan.ui_progress:
                    empty_ep_counter += 1
                    self.stdout.write(self.style.WARNING("EP is empty"))
                    self.stdout.write("---")
                else:
                    for section in ep_sections:
                        content = getattr(plan, section)
                        if content:
                            not_empty_ep_counter += 1
                            self.stdout.write(self.style.SUCCESS("This EP has content."))
                            break

            self.stdout.write("---")

        self.stdout.write(self.style.SUCCESS(f"Empty plan: {empty_ep_counter}"))
        self.stdout.write(self.style.SUCCESS(f"Not Empty plan: {not_empty_ep_counter}"))
