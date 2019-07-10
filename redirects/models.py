from django.db import models
from redirects.validators import self_redirect


class Redirect(models.Model):
    class Meta:
        ordering = ['id']

    id = models.AutoField(auto_created=True, primary_key=True)
    source_url = models.CharField(max_length=200, blank=True, null=True)
    target_url = models.URLField(blank=True, null=True, validators=[self_redirect])

    def __str__(self):
        return self.source_url + ' --> ' + self.target_url
