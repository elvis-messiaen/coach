from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Filtre pour accéder aux valeurs d'un dictionnaire dans les templates"""
    return dictionary.get(key) 