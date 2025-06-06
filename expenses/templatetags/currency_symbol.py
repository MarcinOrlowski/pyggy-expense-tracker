from django import template
from babel.numbers import get_currency_symbol
from ..services import SettingsService

register = template.Library()


@register.simple_tag
def currency_symbol():
    """Get current currency symbol."""
    settings = SettingsService.get_settings()

    try:
        return get_currency_symbol(settings.currency, settings.locale)
    except (ValueError, LookupError, KeyError):
        return settings.currency