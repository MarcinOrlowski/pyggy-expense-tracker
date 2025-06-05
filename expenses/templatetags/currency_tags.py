from django import template
from decimal import Decimal, InvalidOperation
from babel.numbers import get_currency_symbol
from datetime import date
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
    except (ValueError, LookupError, KeyError):
        return settings.currency


@register.simple_tag
def format_amount(amount, show_symbol=True):
    """Format amount with optional symbol control."""
    return SettingsService.format_currency(amount, include_symbol=show_symbol)


@register.filter
def amount_with_class(value):
    """Format value as currency with appropriate CSS class for positive/negative/zero amounts."""
    from django.utils.safestring import mark_safe
    
    if value is None or value == '':
        return ''
    
    try:
        from decimal import Decimal
        amount = Decimal(str(value))
        formatted_currency = SettingsService.format_currency(amount)
        
        # Determine the appropriate CSS class
        if amount < 0:
            css_class = 'amount-negative'
        elif amount > 0:
            css_class = 'amount-positive'
        else:
            css_class = 'amount-zero'
        
        return mark_safe(f'<span class="{css_class}">{formatted_currency}</span>')
    except (ValueError, TypeError, InvalidOperation):
        return value


@register.simple_tag
def create_date(year, month, day):
    """Create a date object from year, month, day integers."""
    try:
        return date(int(year), int(month), int(day))
    except (ValueError, TypeError):
        return None