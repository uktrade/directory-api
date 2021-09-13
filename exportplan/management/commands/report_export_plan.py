from django.core.management.base import BaseCommand
from exportplan import models
from exportplan.management.commands.report_helper import is_ep_plan_empty, set_useable_fields

import csv


class Command(BaseCommand):
    def handle(self, *args, **options):

        empty_ep_counter = 0
        not_empty_ep_counter = 0

        no_product_country_no_data = 0
        no_product_country_with_data = 0

        product_country_no_data = 0
        product_country_with_data = 0

        export_plans = models.CompanyExportPlan.objects.all()
        with open("exportplan/management/commands/report_ep_each_csv.csv", "w", newline="") as each:
            fieldnames = ["Company", "Product", "Country", "Content"]
            thewriter = csv.DictWriter(each, fieldnames=fieldnames)
            fields_dict = {"Company": "", "Product": "", "Country": "", "Content": ""}

            thewriter.writeheader()

            for plan in export_plans.iterator():

                if plan.company:
                    self.stdout.write(self.style.SUCCESS(f'{plan.company}:'))
                    fields_dict["Company"] = plan.company
                else:
                    self.stdout.write(self.style.WARNING("No Company is associated with this EP."))

                # Terminal stdout for Picked Product or Country.
                if plan.export_commodity_codes or plan.export_countries:
                    if plan.export_commodity_codes and "commodity_name" in plan.export_commodity_codes[0]:
                        self.stdout.write(
                            self.style.SUCCESS(f'Picked Product: {plan.export_commodity_codes[0]["commodity_name"]}')
                        )
                        fields_dict["Product"] = plan.export_commodity_codes[0]["commodity_name"]
                    if plan.export_countries and "country_name" in plan.export_countries[0]:
                        self.stdout.write(
                            self.style.SUCCESS(f'Picked Country: {plan.export_countries[0]["country_name"]}')
                        )
                        fields_dict["Country"] = plan.export_countries[0]["country_name"]

                if is_ep_plan_empty(plan, set_useable_fields()):
                    empty_ep_counter += 1

                    if plan.export_commodity_codes or plan.export_countries:
                        product_country_no_data += 1
                    else:
                        no_product_country_no_data += 1

                    self.stdout.write(self.style.WARNING("EP is empty"))
                    fields_dict["Content"] = "EP is empty."
                    self.stdout.write("---")
                else:
                    not_empty_ep_counter += 1

                    if plan.export_commodity_codes or plan.export_countries:
                        product_country_with_data += 1
                    else:
                        no_product_country_with_data += 1
                    self.stdout.write(self.style.SUCCESS("This EP has content."))
                    fields_dict["Content"] = "This EP has content."

                thewriter.writerow(
                    {
                        "Company": fields_dict["Company"],
                        "Product": fields_dict["Product"],
                        "Country": fields_dict["Country"],
                        "Content": fields_dict["Content"],
                    }
                )
                self.stdout.write("---")

        self.stdout.write(self.style.SUCCESS(f"Empty plan: {empty_ep_counter}"))
        self.stdout.write(self.style.SUCCESS(f"Not Empty plan: {not_empty_ep_counter}"))
        self.stdout.write(
            self.style.SUCCESS(f"No product or country added, no data added by user: {no_product_country_no_data}")
        )
        self.stdout.write(
            self.style.SUCCESS(f"No product or country added, some data added by user: {no_product_country_with_data}")
        )
        self.stdout.write(
            self.style.SUCCESS(f"One of product/country added, no data added by user: {product_country_no_data}")
        )
        self.stdout.write(
            self.style.SUCCESS(f"One of product/country added, some data added by user: {product_country_with_data}")
        )

        with open("exportplan/management/commands/report_ep_sum_csv.csv", "w", newline="") as sum:
            fieldnames = ["Title", "Number"]
            thewriter = csv.DictWriter(sum, fieldnames=fieldnames)

            thewriter.writeheader()
            thewriter.writerow({"Title": "Empty plan", "Number": empty_ep_counter})
            thewriter.writerow({"Title": "Not Empty plan", "Number": not_empty_ep_counter})
            thewriter.writerow(
                {"Title": "No product or country added, no data added by user", "Number": no_product_country_no_data}
            )
            thewriter.writerow(
                {
                    "Title": "No product or country added, some data added by user",
                    "Number": no_product_country_with_data,
                }
            )
            thewriter.writerow(
                {"Title": "One of product/country added, no data added by user", "Number": product_country_no_data}
            )
            thewriter.writerow(
                {"Title": "One of product/country added, some data added by user", "Number": product_country_with_data}
            )
