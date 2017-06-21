import csv

from django.http import HttpResponse


def generate_csv(model, queryset, filename, excluded_fields):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename="{filename}"'.format(
            filename=filename
        )
    )

    fieldnames = sorted(
        [field.name for field in model._meta.get_fields()
         if field.name not in excluded_fields]
    )

    objects = queryset.all().values(*fieldnames)
    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()

    for obj in objects:
        writer.writerow(obj)

    return response
