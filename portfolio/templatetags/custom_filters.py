from django import template
from django.utils.numberformat import format as number_format
import re

register = template.Library()

@register.filter
def custom_price(value):
    formatted_value = re.sub(r"(\d)(?=(\d{3})+(?!\d))", r"\1 ", str(value))
    return formatted_value