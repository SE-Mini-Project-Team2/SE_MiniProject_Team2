from django import template

register = template.Library()


@register.filter
def tone(pk):
    """Pick one of six cover colours so a book keeps the same cover."""
    try:
        return int(pk) % 6
    except (TypeError, ValueError):
        return 0
