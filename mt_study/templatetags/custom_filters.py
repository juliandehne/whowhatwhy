# templatetags/custom_filters.py

from django import template
from django.forms import BooleanField

register = template.Library()


@register.filter
def is_boolean_field(field):
    return isinstance(field.field, BooleanField)
