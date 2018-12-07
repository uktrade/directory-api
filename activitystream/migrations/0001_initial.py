from django.db import (
    migrations,
    models,
)


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('field_history', '__latest__'),
    ]

    operations = [
        # There doesn't seem to be a better way to add an index to a table
        # added by a 3rd party application. However, this is only brittle
        # with respect to database table or field renames, which are unlikely
        migrations.RunSQL(
            'CREATE INDEX manual__fieldhistory__date_created_id ON ' +
            'field_history_fieldhistory(date_created, id)',
            'DROP INDEX manual__fieldhistory__date_created_id'
        ),
    ]
