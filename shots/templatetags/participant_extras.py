from django import template

register = template.Library()

@register.filter()
def get_value_from_dict(dict, key):

    if str(key) in dict:
        return dict[str(key)]
    else:
        return " "
