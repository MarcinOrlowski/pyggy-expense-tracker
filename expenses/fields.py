import re
from decimal import Decimal, InvalidOperation
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class SanitizedDecimalField(forms.DecimalField):
    """
    Custom DecimalField that sanitizes input to handle international number formats.
    
    Supports:
    - Both comma (,) and dot (.) as decimal separators
    - Automatic removal of currency symbols (€, $, £, zł, etc.)
    - Removal of thousand separators and spaces
    - Copy-paste friendly input from various sources
    
    Examples:
    - "10,50" → "10.50"
    - "1 234,56" → "1234.56"  
    - "$1,234.56" → "1234.56"
    - "€ 50,25" → "50.25"
    - "12,34 zł" → "12.34"
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def to_python(self, value):
        """
        Sanitize the input value before converting to Decimal.
        """
        if value in self.empty_values:
            return None
            
        # Convert to string if not already
        if not isinstance(value, str):
            value = str(value)
            
        # Sanitize the input
        sanitized_value = self._sanitize_input(value)
        
        # Let parent class handle the actual Decimal conversion
        try:
            return super().to_python(sanitized_value)
        except ValidationError:
            # If sanitized value still fails, provide helpful error message
            raise ValidationError(
                _('Enter a valid number. Examples: 10.50, 10,50, $10.50'),
                code='invalid'
            )
    
    def _sanitize_input(self, value):
        """
        Sanitize input string to extract numeric value.
        
        Args:
            value (str): Raw input string
            
        Returns:
            str: Sanitized numeric string using dot notation
        """
        if not value:
            return value
            
        # Remove leading/trailing whitespace
        value = value.strip()
        
        # Remove supported currency symbols: $, €, zł, zl
        currency_pattern = r'[$€]|zł|zl'
        value = re.sub(currency_pattern, '', value, flags=re.IGNORECASE)
        
        # Remove extra spaces that might have been left by currency removal
        value = re.sub(r'\s+', ' ', value).strip()
        
        # Handle thousand separators and decimal separators
        # This regex handles various international formats:
        # - 1,234.56 (US format with thousand separators)
        # - 1.234,56 (European format with thousand separators)
        # - 1 234,56 (Space as thousand separator)
        # - 10,50 (Simple comma decimal)
        # - 10.50 (Simple dot decimal)
        
        # First, detect the decimal separator pattern
        # Look for the last occurrence of comma or dot with 1-2 digits after it
        decimal_match = re.search(r'[,.](\d{1,2})(?:\s|[^\d]|$)', value)
        
        if decimal_match:
            # Found a potential decimal separator
            decimal_pos = decimal_match.start()
            decimal_separator = value[decimal_pos]
            
            # Everything before the decimal separator
            integer_part = value[:decimal_pos]
            # The decimal part (digits after separator)
            decimal_part = decimal_match.group(1)
            
            # Clean the integer part: remove all separators and spaces
            integer_part = re.sub(r'[,.\s]', '', integer_part)
            
            # Combine with dot as decimal separator
            if decimal_part:
                sanitized = f"{integer_part}.{decimal_part}"
            else:
                sanitized = integer_part
        else:
            # No decimal separator found, treat as integer
            # Remove all non-digit characters except minus sign at the beginning
            sanitized = re.sub(r'[^\d-]', '', value)
            
        # Handle negative numbers (preserve minus sign at the beginning)
        if value.strip().startswith('-') and not sanitized.startswith('-'):
            sanitized = '-' + sanitized
            
        # Remove any remaining non-numeric characters except dot and minus
        sanitized = re.sub(r'[^\d.-]', '', sanitized)
        
        # Ensure only one decimal point
        parts = sanitized.split('.')
        if len(parts) > 2:
            # Multiple decimal points, keep only the last one
            integer_part = ''.join(parts[:-1])
            decimal_part = parts[-1]
            sanitized = f"{integer_part}.{decimal_part}"
            
        # Validate the result is a valid number format
        if sanitized and sanitized not in ['-', '.', '-.']:
            try:
                # Test if it can be converted to Decimal
                Decimal(sanitized)
                return sanitized
            except InvalidOperation:
                pass
                
        # If all sanitization fails, return original value
        # Let the parent validation handle the error
        return value