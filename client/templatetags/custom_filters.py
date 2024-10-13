from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def to_int(value):
    try:
        return int(value)
    except ValueError:
        return 0
    
    
@register.filter
def to(value, arg):
    return range(int(value), int(arg) + 1)


@register.filter
def range_filter(value):
    return range(value)

@register.filter
def to(value, current_year):
    return range(value, current_year + 1)