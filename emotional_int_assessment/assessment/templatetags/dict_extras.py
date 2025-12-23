from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return ""
    val = dictionary.get(key)
    if val is not None:
        return val
    return dictionary.get(str(key), "")
