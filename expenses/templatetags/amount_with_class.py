from django import template
from decimal import Decimal, InvalidOperation
from django.utils.safestring import mark_safe
from ..services import SettingsService

register = template.Library()


@register.filter
def amount_with_class(value):
    """Format value as currency with appropriate CSS class for positive/negative/zero amounts."""
    if value is None or value == "":
        return ""

    try:
        amount = Decimal(str(value))
        formatted_currency = SettingsService.format_currency(amount)

        # Determine the appropriate CSS class
        if amount < 0:
            css_class = "amount-negative"
        elif amount > 0:
            css_class = "amount-positive"
        else:
            css_class = "amount-zero"

        return mark_safe(f'<span class="{css_class}">{formatted_currency}</span>')
    except (ValueError, TypeError, InvalidOperation):
        return value
