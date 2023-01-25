from django import template
from bson import Decimal128
from decimal import Decimal

register = template.Library()

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter(name='mul')
def mul(value, arg):
    decimal_arg = (100 - arg)
    decimal_value = Decimal(str(value))
    x = decimal_value * decimal_arg
    return x / 100

@register.filter(name='zip')
def zip_lists(a, b):
    return zip(a, b)







