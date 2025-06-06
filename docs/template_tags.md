# Template Tags and Filters

This document describes the custom template tags and filters available in the Pyggy Expense Tracker application.

## Available Template Tags

### Currency Filter

**Location:** `expenses.templatetags.currency`

**Usage:** `{{ value|currency }}`

**Description:** Formats a numeric value as currency using the application's configured currency settings.

**Example:**

```django
{% load currency %}
{{ expense.amount|currency }}
```

**Output:** `$1,234.56` (format depends on locale settings)

---

### Currency Symbol Tag

**Location:** `expenses.templatetags.currency_symbol`

**Usage:** `{% currency_symbol %}`

**Description:** Returns the currency symbol for the currently configured currency and locale.

**Example:**

```django
{% load currency_symbol %}
{% currency_symbol %}
```

**Output:** `$` (symbol depends on currency settings)

---

### Format Amount Tag

**Location:** `expenses.templatetags.format_amount`

**Usage:** `{% format_amount amount [show_symbol] %}`

**Description:** Formats an amount with optional symbol control. The `show_symbol` parameter is optional and defaults to `True`.

**Examples:**

```django
{% load format_amount %}
{% format_amount expense.amount %}
{% format_amount expense.amount True %}
{% format_amount expense.amount False %}
```

**Output:** 
- With symbol: `$1,234.56`
- Without symbol: `1,234.56`

---

### Amount with Class Filter

**Location:** `expenses.templatetags.amount_with_class`

**Usage:** `{{ value|amount_with_class }}`

**Description:** Formats a value as currency and wraps it in a span with an appropriate CSS class based on whether the amount is positive, negative, or zero.

**CSS Classes:**

- `amount-positive` - for positive amounts
- `amount-negative` - for negative amounts  
- `amount-zero` - for zero amounts

**Example:**

```django
{% load amount_with_class %}
{{ balance|amount_with_class }}
```

**Output:** `<span class="amount-positive">$1,234.56</span>`

---

### Create Date Tag

**Location:** `expenses.templatetags.create_date`

**Usage:** `{% create_date year month day %}`

**Description:** Creates a date object from separate year, month, and day integers.

**Example:**

```django
{% load create_date %}
{% create_date 2024 12 25 as christmas %}
{{ christmas|date:"F j, Y" }}
```

**Output:** `December 25, 2024`

## Loading Template Tags

To use any of these template tags in your templates, you need to load the specific module:

```django
{% load currency %}
{% load currency_symbol %}
{% load format_amount %}
{% load amount_with_class %}
{% load create_date %}
```

Or load multiple tags at once:

```django
{% load currency currency_symbol format_amount amount_with_class create_date %}
```

## Implementation Notes

- All currency-related tags use the application's `SettingsService` to respect user-configured currency and locale settings
- Error handling is built into each tag to gracefully handle invalid input
- The `amount_with_class` filter returns safe HTML that won't be escaped by Django's auto-escaping
