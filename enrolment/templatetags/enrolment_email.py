from django import template
from enrolment import constants

register = template.Library()


@register.simple_tag
def header_image():
    return constants.EMAIL_HEADER_IMAGE
