# Technical Requirements Document (TRD)

## Application Settings Infrastructure with Currency and Locale Support

**Feature ID:** #0014  
**Date:** January 6, 2025  
**Status:** Approved

### 1. Technical Overview

This document outlines the technical implementation of the application settings infrastructure with locale-aware currency formatting support. The solution uses Django's model system, babel for internationalization, and Django's caching framework for performance.

### 2. Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Templates     │────▶│ Template Tags   │────▶│ Settings Service│
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     Views       │────▶│ Settings Cache  │────▶│ Settings Model  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
                                                 ┌─────────────────┐
                                                 │  Babel Library  │
                                                 └─────────────────┘
```

### 3. Data Model

#### 3.1 Settings Model

```python
# expenses/models.py

class Settings(models.Model):
    """Application-wide settings singleton model."""
    
    currency = models.CharField(
        max_length=3,
        default='USD',
        help_text='ISO 4217 currency code'
    )
    
    locale = models.CharField(
        max_length=10,
        default='en_US',
        help_text='Locale identifier (e.g., en_US, fr_FR)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Settings"
        verbose_name_plural = "Settings"
    
    def save(self, *args, **kwargs):
        """Ensure only one Settings instance exists."""
        self.pk = 1
        super().save(*args, **kwargs)
        # Clear cache when settings are saved
        cache.delete('app_settings')
    
    def delete(self, *args, **kwargs):
        """Prevent deletion of settings."""
        pass
    
    @classmethod
    def load(cls):
        """Load or create settings instance."""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
```

### 4. Service Layer

#### 4.1 Settings Service

```python
# expenses/services.py

from django.core.cache import cache
from babel.numbers import format_currency as babel_format_currency
from babel.core import Locale
from decimal import Decimal
from .models import Settings

class SettingsService:
    """Service for managing application settings and currency formatting."""
    
    CACHE_KEY = 'app_settings'
    CACHE_TIMEOUT = 3600  # 1 hour
    
    @classmethod
    def get_settings(cls):
        """Get cached settings or load from database."""
        settings = cache.get(cls.CACHE_KEY)
        if settings is None:
            settings = Settings.load()
            cache.set(cls.CACHE_KEY, settings, cls.CACHE_TIMEOUT)
        return settings
    
    @classmethod
    def get_currency(cls):
        """Get current currency code."""
        return cls.get_settings().currency
    
    @classmethod
    def get_locale(cls):
        """Get current locale."""
        return cls.get_settings().locale
    
    @classmethod
    def format_currency(cls, amount, include_symbol=True):
        """
        Format amount as currency using current settings.
        
        Args:
            amount: Decimal or float amount to format
            include_symbol: Whether to include currency symbol
            
        Returns:
            Formatted currency string
        """
        if amount is None:
            return ''
        
        settings = cls.get_settings()
        
        # Ensure amount is Decimal
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        
        # Format using babel
        try:
            formatted = babel_format_currency(
                amount,
                settings.currency,
                locale=settings.locale,
                format_type='standard' if include_symbol else 'accounting'
            )
            return formatted
        except Exception as e:
            # Fallback to basic formatting if babel fails
            return f"{settings.currency} {amount:.2f}"
    
    @classmethod
    def clear_cache(cls):
        """Clear settings cache."""
        cache.delete(cls.CACHE_KEY)
```

### 5. Template Integration

#### 5.1 Template Tags

```python
# expenses/templatetags/currency_tags.py

from django import template
from decimal import Decimal
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
    except (ValueError, TypeError):
        return value

@register.simple_tag
def currency_symbol():
    """Get current currency symbol."""
    settings = SettingsService.get_settings()
    # Get symbol from locale
    from babel import Locale
    from babel.numbers import get_currency_symbol
    
    try:
        locale_obj = Locale.parse(settings.locale)
        return get_currency_symbol(settings.currency, locale_obj)
    except:
        return settings.currency

@register.simple_tag
def format_amount(amount, show_symbol=True):
    """Format amount with optional symbol control."""
    return SettingsService.format_currency(amount, include_symbol=show_symbol)
```

### 6. Dependencies

Add to `requirements.txt`:

```
babel==2.13.1
```

### 7. Database Migration

```python
# Migration file: 0007_add_settings_model.py

from django.db import migrations, models

def create_default_settings(apps, schema_editor):
    Settings = apps.get_model('expenses', 'Settings')
    Settings.objects.get_or_create(
        pk=1,
        defaults={
            'currency': 'USD',
            'locale': 'en_US'
        }
    )

class Migration(migrations.Migration):
    dependencies = [
        ('expenses', '0006_make_payee_optional'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(default='USD', help_text='ISO 4217 currency code', max_length=3)),
                ('locale', models.CharField(default='en_US', help_text='Locale identifier (e.g., en_US, fr_FR)', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Settings',
                'verbose_name_plural': 'Settings',
            },
        ),
        migrations.RunPython(create_default_settings),
    ]
```

### 8. Template Updates

Example template usage:

```django
{% load currency_tags %}

<!-- In expense list -->
<td>{{ expense.amount|currency }}</td>

<!-- In forms -->
<label>Amount ({% currency_symbol %})</label>

<!-- Custom formatting -->
{% format_amount expense.amount show_symbol=False %}
```

### 9. Admin Integration

```python
# expenses/admin.py

@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ['currency', 'locale', 'updated_at']
    fields = ['currency', 'locale']
    
    def has_add_permission(self, request):
        # Ensure only one instance
        return not Settings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion
        return False
```

### 10. Testing Strategy

```python
# expenses/tests/test_settings.py

class SettingsServiceTest(TestCase):
    def test_format_currency_usd_en_us(self):
        """Test USD formatting with US locale."""
        # Test implementation
        
    def test_format_currency_eur_fr_fr(self):
        """Test EUR formatting with French locale."""
        # Test implementation
        
    def test_cache_performance(self):
        """Test settings caching works correctly."""
        # Test implementation
```

### 11. Implementation Steps

1. **Install babel**: Add to requirements.txt and install
2. **Create Settings model**: Add to models.py
3. **Create migration**: Generate and apply migration
4. **Implement SettingsService**: Add to services.py
5. **Create template tags**: Add currency_tags.py
6. **Update templates**: Replace hardcoded currency displays
7. **Add admin interface**: Register Settings model
8. **Test implementation**: Verify formatting works correctly

### 12. Performance Considerations

- Settings cached for 1 hour to minimize database queries
- Cache invalidated on settings save
- Babel's locale data loaded once per locale
- Template tag results could be further cached if needed

### 13. Security Considerations

- Settings model restricted to single instance
- Admin permissions controlled
- Input validation on currency and locale fields
- No user input directly used in formatting

### 14. Currency Filter Usage Examples

#### Basic Usage

```django
{% load currency_tags %}

<!-- Replace hardcoded dollar signs -->
<!-- Before: -->
${{ item.amount|floatformat:2 }}

<!-- After: -->
{{ item.amount|currency }}
```

#### Template Examples

**expenses/includes/expense_items_table.html:**

```django
{% load currency_tags %}
...
<td class="text-right">{{ item.amount|currency }}</td>
```

**expenses/includes/month_summary.html:**

```django
{% load currency_tags %}
...
<dd>{{ summary.total|currency }}</dd>
<dd>{{ summary.paid|currency }}</dd>
<dd>{{ summary.pending|currency }}</dd>
```

**Forms with currency symbol:**

```django
{% load currency_tags %}
<div class="form-group">
    <label>Amount ({% currency_symbol %})</label>
    <input type="number" step="0.01" name="amount">
</div>
```

#### Formatting Examples by Locale

- **USD with en_US**: `{{ 1234.56|currency }}` → `$1,234.56`
- **EUR with de_DE**: `{{ 1234.56|currency }}` → `1.234,56 €`
- **GBP with en_GB**: `{{ 1234.56|currency }}` → `£1,234.56`
- **JPY with ja_JP**: `{{ 1234|currency }}` → `¥1,234`
