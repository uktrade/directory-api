from django.core.management.base import BaseCommand
from exportplan import models
from exportplan.management.commands.report_helper import is_ep_plan_empty, set_useable_fields


class Command(BaseCommand):
    def handle(self, *args, **options):

        empty_ep_counter = 0
        not_empty_ep_counter = 0

        no_product_or_country_no_data = 0
        no_product_or_country_with_data = 0
        no_product_and_country_with_data = 0

        product_or_country_no_data = 0
        product_or_country_with_data = 0
        product_and_country_with_data = 0

        export_plans = models.CompanyExportPlan.objects.all()

        for plan in export_plans.iterator():
            # Terminal stdout for Picked Product or Country.
            if plan.export_commodity_codes or plan.export_countries:
                if plan.export_commodity_codes and "commodity_name" in plan.export_commodity_codes[0]:
                    self.stdout.write(
                        self.style.SUCCESS(f'Picked Product: {plan.export_commodity_codes[0]["commodity_name"]}')
                    )
                if plan.export_countries and "country_name" in plan.export_countries[0]:
                    self.stdout.write(self.style.SUCCESS(f'Picked Country: {plan.export_countries[0]["country_name"]}'))

            if is_ep_plan_empty(plan, set_useable_fields()):
                empty_ep_counter += 1

                if plan.export_commodity_codes and plan.export_countries:
                    no_product_and_country_with_data += 1
                elif plan.export_commodity_codes or plan.export_countries:
                    product_or_country_no_data += 1
                else:
                    no_product_or_country_no_data += 1

                self.stdout.write(self.style.WARNING("EP is empty"))
            else:
                not_empty_ep_counter += 1
                if plan.export_commodity_codes and plan.export_countries:
                    product_and_country_with_data += 1
                elif plan.export_commodity_codes or plan.export_countries:
                    product_or_country_with_data += 1
                else:
                    no_product_or_country_with_data += 1
                self.stdout.write(self.style.SUCCESS("This EP has content."))

            self.stdout.write("---")

        self.stdout.write(self.style.SUCCESS(f"Empty plan: {empty_ep_counter}"))
        self.stdout.write(self.style.SUCCESS(f"Not Empty plan: {not_empty_ep_counter}"))
        self.stdout.write(self.style.SUCCESS(f"No product or country added, no data: {no_product_or_country_no_data}"))
        self.stdout.write(
            self.style.SUCCESS(f"No product and country added, some data: {no_product_and_country_with_data}")
        )
        self.stdout.write(
            self.style.SUCCESS(f"No product or country added, some data: {no_product_or_country_with_data}")
        )
        self.stdout.write(self.style.SUCCESS(f"One of product/country added, no data: {product_or_country_no_data}"))
        self.stdout.write(
            self.style.SUCCESS(f"One of product and country added, some data:" f"{product_and_country_with_data}")
        )
        self.stdout.write(
            self.style.SUCCESS(f"One of product/country added, some data: {product_or_country_with_data}")
        )
