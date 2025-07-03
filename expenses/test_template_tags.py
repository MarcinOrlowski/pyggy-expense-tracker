from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.template import Context, Template
from django.test import TestCase

from expenses.models import Settings
from expenses.services import SettingsService
from expenses.templatetags.amount_with_class import amount_with_class
from expenses.templatetags.create_date import create_date
from expenses.templatetags.currency import currency
from expenses.templatetags.currency_symbol import currency_symbol
from expenses.templatetags.format_amount import format_amount


class CurrencyFilterTest(TestCase):
    """Test cases for the currency template filter."""

    def setUp(self):
        """Set up test data."""
        # Clear any existing settings
        Settings.objects.all().delete()
        # Create test settings
        self.test_settings = Settings.objects.create(locale="en_US", currency="USD")

    def test_currency_filter_with_valid_decimal(self):
        """Test currency filter with valid decimal value."""
        result = currency(Decimal("123.45"))
        self.assertEqual(result, "$123.45")

    def test_currency_filter_with_integer(self):
        """Test currency filter with integer value."""
        result = currency(100)
        self.assertEqual(result, "$100.00")

    def test_currency_filter_with_float(self):
        """Test currency filter with float value."""
        result = currency(99.99)
        self.assertEqual(result, "$99.99")

    def test_currency_filter_with_string_number(self):
        """Test currency filter with string number."""
        result = currency("456.78")
        self.assertEqual(result, "$456.78")

    def test_currency_filter_with_none(self):
        """Test currency filter with None value."""
        result = currency(None)
        self.assertEqual(result, "")

    def test_currency_filter_with_empty_string(self):
        """Test currency filter with empty string."""
        result = currency("")
        self.assertEqual(result, "")

    def test_currency_filter_with_invalid_string(self):
        """Test currency filter with non-numeric string."""
        result = currency("invalid")
        self.assertEqual(result, "invalid")

    def test_currency_filter_with_zero(self):
        """Test currency filter with zero value."""
        result = currency(0)
        self.assertEqual(result, "$0.00")

    def test_currency_filter_with_negative_value(self):
        """Test currency filter with negative value."""
        result = currency(Decimal("-50.25"))
        # Babel formats negative as -$50.25 or ($50.25) depending on locale
        self.assertIn("50.25", result)

    def test_currency_filter_in_template(self):
        """Test currency filter usage in Django template."""
        template = Template("{% load currency_tags %}{{ value|currency }}")
        context = Context({"value": Decimal("1234.56")})
        result = template.render(context)
        self.assertEqual(result, "$1,234.56")

    def test_currency_filter_with_different_locale(self):
        """Test currency filter with different locale settings."""
        # Change settings to Euro
        self.test_settings.locale = "de_DE"
        self.test_settings.currency = "EUR"
        self.test_settings.save()

        # Clear cache to ensure new settings are used
        SettingsService.clear_cache()

        result = currency(Decimal("1234.56"))
        # German locale uses different formatting
        self.assertIn("1.234,56", result)  # German number format
        self.assertIn("€", result)  # Euro symbol


class CurrencySymbolTagTest(TestCase):
    """Test cases for the currency_symbol template tag."""

    def setUp(self):
        """Set up test data."""
        Settings.objects.all().delete()
        self.test_settings = Settings.objects.create(locale="en_US", currency="USD")

    def test_currency_symbol_usd(self):
        """Test currency symbol for USD."""
        result = currency_symbol()
        self.assertEqual(result, "$")

    def test_currency_symbol_eur(self):
        """Test currency symbol for EUR."""
        self.test_settings.currency = "EUR"
        self.test_settings.save()
        SettingsService.clear_cache()

        result = currency_symbol()
        self.assertEqual(result, "€")

    def test_currency_symbol_gbp(self):
        """Test currency symbol for GBP."""
        self.test_settings.currency = "GBP"
        self.test_settings.locale = "en_GB"
        self.test_settings.save()
        SettingsService.clear_cache()

        result = currency_symbol()
        self.assertEqual(result, "£")

    def test_currency_symbol_jpy(self):
        """Test currency symbol for JPY."""
        self.test_settings.currency = "JPY"
        self.test_settings.locale = "ja_JP"
        self.test_settings.save()
        SettingsService.clear_cache()

        result = currency_symbol()
        # In Japanese locale, JPY symbol might be ¥ or ￥
        self.assertIn(result, ["¥", "￥", "JP¥"])

    @patch("expenses.templatetags.currency_symbol.get_currency_symbol")
    def test_currency_symbol_fallback_on_error(self, mock_get_symbol):
        """Test currency symbol falls back to currency code on error."""
        # Make get_currency_symbol raise a LookupError
        mock_get_symbol.side_effect = LookupError("Symbol lookup failed")

        result = currency_symbol()
        self.assertEqual(result, "USD")

    def test_currency_symbol_with_invalid_currency(self):
        """Test currency symbol with invalid currency code."""
        self.test_settings.currency = "XXX"  # Invalid currency code
        self.test_settings.save()
        SettingsService.clear_cache()

        result = currency_symbol()
        # Babel might return a symbol or fallback to code
        self.assertTrue(result in ["XXX", "¤"] or result == "XXX")

    def test_currency_symbol_in_template(self):
        """Test currency_symbol tag usage in Django template."""
        template = Template("{% load currency_tags %}{% currency_symbol %}")
        context = Context()
        result = template.render(context)
        self.assertEqual(result, "$")


class FormatAmountTagTest(TestCase):
    """Test cases for the format_amount template tag."""

    def setUp(self):
        """Set up test data."""
        Settings.objects.all().delete()
        self.test_settings = Settings.objects.create(locale="en_US", currency="USD")

    def test_format_amount_with_symbol(self):
        """Test format_amount with symbol (default behavior)."""
        result = format_amount(Decimal("123.45"))
        self.assertEqual(result, "$123.45")

    def test_format_amount_without_symbol(self):
        """Test format_amount without symbol."""
        result = format_amount(Decimal("123.45"), show_symbol=False)
        # Note: The service doesn't actually remove symbols, it uses accounting format
        # which still includes the symbol
        self.assertIn("123.45", result)

    def test_format_amount_with_true_string(self):
        """Test format_amount with 'True' string for show_symbol."""
        result = format_amount(Decimal("123.45"), show_symbol=True)
        self.assertEqual(result, "$123.45")

    def test_format_amount_with_false_string(self):
        """Test format_amount with 'False' string for show_symbol."""
        result = format_amount(Decimal("123.45"), show_symbol=False)
        # The service uses accounting format which still includes symbol
        self.assertIn("123.45", result)

    def test_format_amount_with_large_number(self):
        """Test format_amount with large number (thousands separator)."""
        result = format_amount(Decimal("1234567.89"))
        self.assertEqual(result, "$1,234,567.89")

    def test_format_amount_with_zero(self):
        """Test format_amount with zero."""
        result = format_amount(0)
        self.assertEqual(result, "$0.00")

    def test_format_amount_in_template_with_symbol(self):
        """Test format_amount tag in template with symbol."""
        template = Template("{% load currency_tags %}{% format_amount value %}")
        context = Context({"value": Decimal("999.99")})
        result = template.render(context)
        self.assertEqual(result, "$999.99")

    def test_format_amount_in_template_without_symbol(self):
        """Test format_amount tag in template without symbol."""
        template = Template("{% load currency_tags %}{% format_amount value False %}")
        context = Context({"value": Decimal("999.99")})
        result = template.render(context)
        # The service uses accounting format which still includes symbol
        self.assertIn("999.99", result)

    def test_format_amount_with_different_locale(self):
        """Test format_amount with different locale."""
        # Change to French locale
        self.test_settings.locale = "fr_FR"
        self.test_settings.currency = "EUR"
        self.test_settings.save()
        SettingsService.clear_cache()

        result = format_amount(Decimal("1234.56"))
        # French format uses space as thousands separator and comma as decimal
        # Different versions of babel might use different space characters
        self.assertIn("234,56", result)  # Check for the decimal part
        self.assertIn("€", result)

    def test_format_amount_handles_none(self):
        """Test format_amount handles None value."""
        # This might raise an error or return empty, depending on implementation
        with patch("expenses.services.SettingsService.format_currency") as mock_format:
            mock_format.return_value = ""
            format_amount(None)
            mock_format.assert_called_once_with(None, include_symbol=True)


class TemplateTagIntegrationTest(TestCase):
    """Integration tests for template tags working together."""

    def setUp(self):
        """Set up test data."""
        Settings.objects.all().delete()
        self.test_settings = Settings.objects.create(locale="en_US", currency="USD")

    def test_multiple_tags_in_template(self):
        """Test multiple currency tags used together in a template."""
        template = Template(
            """
            {% load currency_tags %}
            Symbol: {% currency_symbol %}
            Filtered: {{ amount|currency }}
            With symbol: {% format_amount amount %}
            Without symbol: {% format_amount amount False %}
        """
        )
        context = Context({"amount": Decimal("42.50")})
        result = template.render(context)

        self.assertIn("Symbol: $", result)
        self.assertIn("Filtered: $42.50", result)
        self.assertIn("With symbol: $42.50", result)
        # Note: show_symbol=False still includes symbol in current implementation
        self.assertIn("42.50", result)

    def test_tags_with_changing_settings(self):
        """Test tags respond to settings changes."""
        template = Template(
            """
            {% load currency_tags %}
            {% currency_symbol %} - {{ amount|currency }}
        """
        )

        # Test with USD
        context = Context({"amount": Decimal("100")})
        result1 = template.render(context)
        self.assertIn("$ - $100.00", result1)

        # Change to GBP
        self.test_settings.currency = "GBP"
        self.test_settings.locale = "en_GB"
        self.test_settings.save()
        SettingsService.clear_cache()

        # Re-render with same context
        result2 = template.render(context)
        self.assertIn("£", result2)
        self.assertIn("100.00", result2)


class AmountWithClassFilterTest(TestCase):
    """Test cases for the amount_with_class template filter."""

    def setUp(self):
        """Set up test data."""
        Settings.objects.all().delete()
        self.test_settings = Settings.objects.create(locale="en_US", currency="USD")

    def test_amount_with_class_positive(self):
        """Test amount_with_class filter with positive amount."""
        result = amount_with_class(Decimal("123.45"))
        self.assertIn("amount-positive", result)
        self.assertIn("$123.45", result)
        self.assertIn("<span", result)
        self.assertIn("</span>", result)

    def test_amount_with_class_negative(self):
        """Test amount_with_class filter with negative amount."""
        result = amount_with_class(Decimal("-50.25"))
        self.assertIn("amount-negative", result)
        self.assertIn("50.25", result)  # Currency formatting might vary
        self.assertIn("<span", result)
        self.assertIn("</span>", result)

    def test_amount_with_class_zero(self):
        """Test amount_with_class filter with zero amount."""
        result = amount_with_class(Decimal("0.00"))
        self.assertIn("amount-zero", result)
        self.assertIn("$0.00", result)
        self.assertIn("<span", result)
        self.assertIn("</span>", result)

    def test_amount_with_class_with_none(self):
        """Test amount_with_class filter with None value."""
        result = amount_with_class(None)
        self.assertEqual(result, "")

    def test_amount_with_class_with_empty_string(self):
        """Test amount_with_class filter with empty string."""
        result = amount_with_class("")
        self.assertEqual(result, "")

    def test_amount_with_class_with_invalid_string(self):
        """Test amount_with_class filter with non-numeric string."""
        result = amount_with_class("invalid")
        self.assertEqual(result, "invalid")

    def test_amount_with_class_in_template(self):
        """Test amount_with_class filter usage in Django template."""
        template = Template("{% load currency_tags %}{{ value|amount_with_class }}")
        context = Context({"value": Decimal("1234.56")})
        result = template.render(context)

        self.assertIn("amount-positive", result)
        self.assertIn("$1,234.56", result)
        self.assertIn("<span", result)

    def test_amount_with_class_with_different_locale(self):
        """Test amount_with_class filter with different locale settings."""
        # Change settings to Euro
        self.test_settings.locale = "de_DE"
        self.test_settings.currency = "EUR"
        self.test_settings.save()

        # Clear cache to ensure new settings are used
        SettingsService.clear_cache()

        result = amount_with_class(Decimal("-1234.56"))
        # Should have negative class regardless of locale
        self.assertIn("amount-negative", result)
        # German locale formatting
        self.assertIn("1.234,56", result)
        self.assertIn("€", result)

    def test_amount_with_class_is_safe_html(self):
        """Test that amount_with_class returns safe HTML."""
        from django.utils.safestring import SafeString

        result = amount_with_class(Decimal("100.00"))
        # Check that it's marked as safe HTML
        self.assertIsInstance(result, SafeString)

    def test_amount_with_class_all_scenarios_in_template(self):
        """Test all amount scenarios in a template."""
        template = Template(
            """
            {% load currency_tags %}
            Positive: {{ positive|amount_with_class }}
            Negative: {{ negative|amount_with_class }}
            Zero: {{ zero|amount_with_class }}
        """
        )
        context = Context(
            {
                "positive": Decimal("100.50"),
                "negative": Decimal("-25.75"),
                "zero": Decimal("0.00"),
            }
        )
        result = template.render(context)

        self.assertIn("amount-positive", result)
        self.assertIn("amount-negative", result)
        self.assertIn("amount-zero", result)
        self.assertIn("$100.50", result)
        self.assertIn("25.75", result)  # Negative formatting varies
        self.assertIn("$0.00", result)


class CreateDateTagTest(TestCase):
    """Test cases for the create_date template tag."""

    def test_create_date_valid_parameters(self):
        """Test create_date with valid year, month, day."""
        result = create_date(2023, 12, 25)
        expected = date(2023, 12, 25)
        self.assertEqual(result, expected)

    def test_create_date_string_parameters(self):
        """Test create_date with string parameters."""
        result = create_date("2023", "6", "15")
        expected = date(2023, 6, 15)
        self.assertEqual(result, expected)

    def test_create_date_invalid_parameters(self):
        """Test create_date with invalid parameters."""
        result = create_date("invalid", "month", "day")
        self.assertIsNone(result)

    def test_create_date_invalid_date(self):
        """Test create_date with invalid date (February 30th)."""
        result = create_date(2023, 2, 30)
        self.assertIsNone(result)

    def test_create_date_in_template(self):
        """Test create_date tag usage in Django template."""
        template = Template(
            '{% load currency_tags %}{% create_date 2023 12 25 as test_date %}{{ test_date|date:"Y-m-d" }}'
        )
        context = Context({})
        result = template.render(context)
        self.assertEqual(result, "2023-12-25")
