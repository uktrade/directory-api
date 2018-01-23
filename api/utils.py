import csv

from django.http import HttpResponse


def generate_csv_response(queryset, filename, excluded_fields):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename="{filename}"'.format(
            filename=filename
        )
    )
    generate_csv(
        file_object=response,
        queryset=queryset,
        excluded_fields=excluded_fields
    )
    return response


def generate_csv(file_object, queryset, excluded_fields):
    model = queryset.model
    fieldnames = sorted(
        [field.name for field in model._meta.get_fields()
         if field.name not in excluded_fields]
    )

    objects = queryset.all().values(*fieldnames)
    writer = csv.DictWriter(file_object, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(objects)

    return writer
