from django.core.management.base import BaseCommand

from exportplan import models
from exportplan.management.commands.report_helper import is_ep_plan_empty, set_useable_fields, write_ep_csv


class Command(BaseCommand):
    def handle(self, *args, **options):

        empty_ep_counter = 0
        not_empty_ep_counter = 0

        no_product_and_country_no_data = 0
        no_product_and_country_with_data = 0
        product_country_no_data = 0

        product_or_country_no_data = 0
        product_or_country_with_data = 0
        product_and_country_with_data = 0

        ssoid_no_product_and_country_data = []
        ssoid_product_or_country_data = []

        export_plans = models.CompanyExportPlan.objects.all()

        ep_list_to_csv = []

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
                    product_country_no_data += 1
                elif plan.export_commodity_codes or plan.export_countries:
                    product_or_country_no_data += 1
                else:
                    no_product_and_country_no_data += 1

                self.stdout.write(self.style.WARNING("EP is empty"))
            else:
                not_empty_ep_counter += 1
                if plan.export_commodity_codes and plan.export_countries:
                    product_and_country_with_data += 1
                elif plan.export_commodity_codes or plan.export_countries:
                    product_or_country_with_data += 1
                    ssoid_product_or_country_data.append(plan.sso_id)
                else:
                    no_product_and_country_with_data += 1
                    ssoid_no_product_and_country_data.append(plan.sso_id)
                self.stdout.write(self.style.SUCCESS("This EP has content."))

            self.stdout.write("---")

            # Appends to list to get converted to CSV file at the end.
            ep_list_to_csv.append(
                {
                    "sso_id": plan.sso_id,
                    "export_countries": plan.export_countries,
                    "export_commodity_codes": plan.export_commodity_codes,
                }
            )

        self.stdout.write(self.style.SUCCESS(f"Empty plan: {empty_ep_counter}"))
        self.stdout.write(self.style.SUCCESS(f"Not Empty plan: {not_empty_ep_counter}"))
        self.stdout.write(
            self.style.SUCCESS(
                f"NO product and NO country added, NO data added by user: {no_product_and_country_no_data}"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(f"Product and Country added, NO data added by use: {product_country_no_data}")
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"NO product and NO country added, some data added by user: {no_product_and_country_with_data}"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(f"Product or Country added, NO data added by user: {product_or_country_no_data}")
        )
        self.stdout.write(
            self.style.SUCCESS(f"Product and Country added, some data added by user: {product_and_country_with_data}")
        )
        self.stdout.write(
            self.style.SUCCESS(f"Product or Country added, some data added by user: {product_or_country_with_data}")
        )
        self.stdout.write(
            self.style.SUCCESS(f"No Product and No country with data SSOID: {ssoid_no_product_and_country_data}")
        )
        self.stdout.write(self.style.SUCCESS(f"Product or country with data SSOID: {ssoid_product_or_country_data}"))

        write_ep_csv(ep_list_to_csv, 'ep_plan.csv')
