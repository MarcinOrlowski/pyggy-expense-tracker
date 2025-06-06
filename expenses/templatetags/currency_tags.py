"""Combined currency template tags for backward compatibility.

This module combines all currency-related template tags and filters
into a single library that can be loaded with {% load currency_tags %}.
"""

from django import template

# Import all individual tag modules
from .currency import currency
from .currency_symbol import currency_symbol
from .format_amount import format_amount
from .amount_with_class import amount_with_class
from .create_date import create_date

# Create a new register for the combined library
register = template.Library()

# Register all imported tags and filters
register.filter('currency', currency)
register.simple_tag(currency_symbol)
register.simple_tag(format_amount)
register.filter('amount_with_class', amount_with_class)
register.simple_tag(create_date)
