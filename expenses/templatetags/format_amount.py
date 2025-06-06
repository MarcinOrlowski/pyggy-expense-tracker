from django import template
from ..services import SettingsService

register = template.Library()


@register.simple_tag
def format_amount(amount, show_symbol=True):
    """Format amount with optional symbol control."""
    return SettingsService.format_currency(amount, include_symbol=show_symbol)
