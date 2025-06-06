from django import template
from datetime import date

register = template.Library()


@register.simple_tag
def create_date(year, month, day):
    """Create a date object from year, month, day integers."""
    try:
        return date(int(year), int(month), int(day))
    except (ValueError, TypeError):
        return None