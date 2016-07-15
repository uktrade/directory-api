from django.contrib.postgres.fields import JSONField
from django.db import models


class Form(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    data = JSONField()

    def __str__(self):
        return "{} - {}: {}".format(self.id, self.created, self.data)
