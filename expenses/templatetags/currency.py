from django import template
from decimal import Decimal, InvalidOperation
from ..services import SettingsService

register = template.Library()


@register.filter
def currency(value):
    """Format value as currency using app settings."""
    if value is None or value == "":
        return ""

    try:
        amount = Decimal(str(value))
        return SettingsService.format_currency(amount)
    except (ValueError, TypeError, InvalidOperation):
        return value
