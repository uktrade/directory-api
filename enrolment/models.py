from django.contrib.postgres.fields import JSONField

from api.model_utils import TimeStampedModel


class Enrolment(TimeStampedModel):
    data = JSONField()

    def __str__(self):
        return "{} - {}: {}".format(
            self.id, self.created, self.data
        )
