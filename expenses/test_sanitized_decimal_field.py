from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.forms import Form
from expenses.fields import SanitizedDecimalField


class SanitizedDecimalFieldTest(TestCase):
    """Test cases for SanitizedDecimalField functionality."""
    
    def setUp(self):
        """Set up test field instance."""
        self.field = SanitizedDecimalField(max_digits=10, decimal_places=2, min_value=0)
    
    def test_basic_decimal_formats(self):
        """Test basic decimal number formats."""
        test_cases = [
            ('10.50', Decimal('10.50')),
            ('10,50', Decimal('10.50')),
            ('0.01', Decimal('0.01')),
            ('0,01', Decimal('0.01')),
            ('100', Decimal('100')),
            ('100.00', Decimal('100.00')),
            ('100,00', Decimal('100.00')),
        ]
        
        for input_value, expected in test_cases:
            with self.subTest(input_value=input_value):
                result = self.field.to_python(input_value)
                self.assertEqual(result, expected)
    
    def test_currency_symbol_removal(self):
        """Test removal of supported currency symbols."""
        test_cases = [
            ('$10.50', Decimal('10.50')),
            ('€10,50', Decimal('10.50')),
            ('10,50 zł', Decimal('10.50')),
            ('12,34 zł', Decimal('12.34')),
            ('12,34 zl', Decimal('12.34')),  # Also support zl
            ('100 zl', Decimal('100')),
        ]
        
        for input_value, expected in test_cases:
            with self.subTest(input_value=input_value):
                result = self.field.to_python(input_value)
                self.assertEqual(result, expected)
    
    def test_thousand_separators(self):
        """Test handling of thousand separators."""
        test_cases = [
            ('1,234.56', Decimal('1234.56')),  # US format
            ('1.234,56', Decimal('1234.56')),  # European format
            ('1 234,56', Decimal('1234.56')),  # Space separator
            ('1 234.56', Decimal('1234.56')),  # Space separator with dot
            ('12,345.67', Decimal('12345.67')),
            ('123,456.78', Decimal('123456.78')),
            ('1,000', Decimal('1000')),
            ('10,000.00', Decimal('10000.00')),
        ]
        
        for input_value, expected in test_cases:
            with self.subTest(input_value=input_value):
                result = self.field.to_python(input_value)
                self.assertEqual(result, expected)
    
    def test_complex_formatted_amounts(self):
        """Test complex formatted amounts with multiple formatting elements."""
        test_cases = [
            ('$ 1,234.56', Decimal('1234.56')),
            ('€ 1 234,56', Decimal('1234.56')),
            ('1 234,56 €', Decimal('1234.56')),
            ('12 345,67 zł', Decimal('12345.67')),
            ('12 345,67 zl', Decimal('12345.67')),
            ('  $  100.50  ', Decimal('100.50')),  # Extra spaces
        ]
        
        for input_value, expected in test_cases:
            with self.subTest(input_value=input_value):
                result = self.field.to_python(input_value)
                self.assertEqual(result, expected)
    
    def test_negative_numbers(self):
        """Test handling of negative numbers."""
        # Create field that allows negative values
        field = SanitizedDecimalField(max_digits=10, decimal_places=2)
        
        test_cases = [
            ('-10.50', Decimal('-10.50')),
            ('-10,50', Decimal('-10.50')),
            ('- $10.50', Decimal('-10.50')),
            ('-€ 100,25', Decimal('-100.25')),
            ('- 1,234.56', Decimal('-1234.56')),
        ]
        
        for input_value, expected in test_cases:
            with self.subTest(input_value=input_value):
                result = field.to_python(input_value)
                self.assertEqual(result, expected)
    
    def test_empty_and_none_values(self):
        """Test handling of empty and None values."""
        test_cases = [
            (None, None),
            ('', None),
            ('   ', None),
        ]
        
        for input_value, expected in test_cases:
            with self.subTest(input_value=input_value):
                result = self.field.to_python(input_value)
                self.assertEqual(result, expected)
    
    def test_invalid_inputs(self):
        """Test that truly invalid inputs raise ValidationError."""
        invalid_inputs = [
            'abc',          # No numbers at all
            '...',          # Just dots
            'currency only €',  # Currency symbol without numbers
            '',             # Empty string (should return None, not raise error)
        ]
        
        for invalid_input in invalid_inputs:
            with self.subTest(input_value=invalid_input):
                if invalid_input == '':
                    # Empty string should return None, not raise error
                    result = self.field.to_python(invalid_input)
                    self.assertIsNone(result)
                else:
                    with self.assertRaises(ValidationError):
                        self.field.to_python(invalid_input)
    
    def test_permissive_extraction(self):
        """Test that the field can extract numbers from complex inputs (permissive behavior)."""
        test_cases = [
            ('10.50.25', Decimal('10.50')),  # Takes last decimal point
            ('text with numbers 123', Decimal('123')),  # Extracts the number
            ('10,50,25', Decimal('10.50')),  # Converts last comma to decimal
            ('Price is $25.99 total', Decimal('25.99')),  # Extracts from sentence
        ]
        
        for input_value, expected in test_cases:
            with self.subTest(input_value=input_value):
                result = self.field.to_python(input_value)
                self.assertEqual(result, expected)
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        test_cases = [
            ('0', Decimal('0')),
            ('0.00', Decimal('0.00')),
            ('0,00', Decimal('0.00')),
            ('00.50', Decimal('0.50')),
            ('000,50', Decimal('0.50')),
            ('.50', Decimal('0.50')),
            (',50', Decimal('0.50')),
        ]
        
        for input_value, expected in test_cases:
            with self.subTest(input_value=input_value):
                result = self.field.to_python(input_value)
                self.assertEqual(result, expected)
    
    def test_precision_and_validation(self):
        """Test that field respects max_digits and decimal_places constraints."""
        # Field with specific constraints
        field = SanitizedDecimalField(max_digits=5, decimal_places=2, min_value=0, max_value=999.99)
        
        # Valid inputs within constraints
        valid_cases = [
            ('999.99', Decimal('999.99')),
            ('100,50', Decimal('100.50')),
            ('0.01', Decimal('0.01')),
        ]
        
        for input_value, expected in valid_cases:
            with self.subTest(input_value=input_value, test_type='valid'):
                result = field.to_python(input_value)
                self.assertEqual(result, expected)
        
        # Invalid inputs that exceed constraints
        invalid_cases = [
            '1000.00',  # Exceeds max_value
            '999.999',  # Too many decimal places
            '-1.00',    # Below min_value
        ]
        
        for invalid_input in invalid_cases:
            with self.subTest(input_value=invalid_input, test_type='invalid'):
                with self.assertRaises(ValidationError):
                    field.clean(invalid_input)  # Use clean() to test full validation
    
    def test_form_integration(self):
        """Test that the field works correctly when used in a Django form."""
        
        class TestForm(Form):
            amount = SanitizedDecimalField(max_digits=10, decimal_places=2, min_value=0)
        
        # Test valid form submission
        valid_data = {
            'amount': '€ 1,234.56'
        }
        form = TestForm(valid_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['amount'], Decimal('1234.56'))
        
        # Test invalid form submission
        invalid_data = {
            'amount': 'invalid amount'
        }
        form = TestForm(invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)
    
    def test_real_world_examples(self):
        """Test with real-world copy-paste examples."""
        test_cases = [
            # Bank statement formats
            ('Balance: $1,523.45', Decimal('1523.45')),
            ('Amount: € 2 456,78', Decimal('2456.78')),
            
            # Invoice formats
            ('Subtotal: 1.234,56 €', Decimal('1234.56')),
            ('Tax: 123,45 zł', Decimal('123.45')),
            ('Tax: 123,45 zl', Decimal('123.45')),
            
            # E-commerce formats
            ('Price: $19.99', Decimal('19.99')),
            ('Cost: 50,00 € (incl. VAT)', Decimal('50.00')),
        ]
        
        for input_value, expected in test_cases:
            with self.subTest(input_value=input_value):
                result = self.field.to_python(input_value)
                self.assertEqual(result, expected)
    
    def test_whitespace_handling(self):
        """Test various whitespace scenarios."""
        test_cases = [
            ('  10.50  ', Decimal('10.50')),
            ('\t100,25\t', Decimal('100.25')),
            ('\n50.00\n', Decimal('50.00')),
            ('1 000,50', Decimal('1000.50')),  # Space as thousand separator
            ('€  10,50  ', Decimal('10.50')),  # Multiple spaces around currency
        ]
        
        for input_value, expected in test_cases:
            with self.subTest(input_value=input_value):
                result = self.field.to_python(input_value)
                self.assertEqual(result, expected)