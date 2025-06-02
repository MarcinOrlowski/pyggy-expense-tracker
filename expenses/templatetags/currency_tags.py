from django import template
from decimal import Decimal, InvalidOperation
from babel.numbers import get_currency_symbol
from ..services import SettingsService

register = template.Library()


@register.filter
def currency(value):
    """Format value as currency using app settings."""
    if value is None or value == '':
        return ''
    
    try:
        amount = Decimal(str(value))
        return SettingsService.format_currency(amount)
    except (ValueError, TypeError, InvalidOperation):
        return value


@register.simple_tag
def currency_symbol():
    """Get current currency symbol."""
    settings = SettingsService.get_settings()
    
    try:
        return get_currency_symbol(settings.currency, settings.locale)
    except:
        return settings.currency


@register.simple_tag
def format_amount(amount, show_symbol=True):
    """Format amount with optional symbol control."""
    return SettingsService.format_currency(amount, include_symbol=show_symbol)