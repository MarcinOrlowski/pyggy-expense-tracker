"""Combined currency template tags for backward compatibility.

This module combines all currency-related template tags and filters
into a single library that can be loaded with {% load currency_tags %}.
"""

from django import template
from decimal import Decimal, InvalidOperation
from django.utils.safestring import mark_safe
from ..services import SettingsService

# Import all individual tag modules
from .currency import currency
from .currency_symbol import currency_symbol
from .format_amount import format_amount
from .amount_with_class import amount_with_class
from .create_date import create_date

# Create a new register for the combined library
register = template.Library()


# Dictionary lookup filter
@register.filter
def dict_lookup(dictionary, key):
    """Get value from dictionary by key"""
    if dictionary and isinstance(dictionary, dict) and key in dictionary:
        return dictionary[key]
    return None


@register.filter
def paid_amount_display(expense_item):
    """
    Display amount for expense item with special formatting for paid items.

    For pending items: shows remaining amount
    For paid items: shows full due amount with strikethrough
    """
    if not expense_item:
        return ""

    try:
        if expense_item.status == "paid":
            # For paid items, show the full due amount with strikethrough
            amount = expense_item.amount
            formatted_currency = SettingsService.format_currency(amount)
            # Use text-decoration-line: line-through for strikethrough
            return mark_safe(
                f'<span class="amount-paid-strikethrough">{formatted_currency}</span>'
            )
        else:
            # For pending items, show remaining amount (current behavior)
            remaining = expense_item.get_remaining_amount()
            formatted_currency = SettingsService.format_currency(remaining)

            # Determine the appropriate CSS class
            if remaining < 0:
                css_class = "amount-negative"
            elif remaining > 0:
                css_class = "amount-positive"
            else:
                css_class = "amount-zero"

            return mark_safe(f'<span class="{css_class}">{formatted_currency}</span>')

    except (ValueError, TypeError, InvalidOperation, AttributeError):
        return ""


# Register all imported tags and filters
register.filter("currency", currency)
register.simple_tag(currency_symbol)
register.simple_tag(format_amount)
register.filter("amount_with_class", amount_with_class)
register.simple_tag(create_date)
register.filter("dict_lookup", dict_lookup)
register.filter("paid_amount_display", paid_amount_display)
