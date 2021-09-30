from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def email_image(image_name):
    return 'https://{0}.s3.amazonaws.com/{1}'.format(settings.AWS_STORAGE_BUCKET_NAME_EMAIL, image_name)
