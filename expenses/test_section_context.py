from django.test import TestCase, RequestFactory
from django.urls import resolve
from expenses.context_processors import section_context


class SectionContextProcessorTest(TestCase):
    """Test suite for the section_context context processor."""
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def _get_section_class(self, url_path):
        """Helper method to get section class for a given URL path."""
        try:
            request = self.factory.get(url_path)
            request.resolver_match = resolve(url_path)
            result = section_context(request)
            return result.get('section_class', '')
        except Exception:
            # For URLs that don't resolve, return empty
            return ''
    
    def test_budget_section_detection(self):
        """Test that budget-related URLs are correctly identified."""
        self.assertEqual(self._get_section_class('/'), 'section-budgets')
        self.assertEqual(self._get_section_class('/budgets/'), 'section-budgets')
    
    def test_dashboard_section_detection(self):
        """Test that dashboard URLs are correctly identified."""
        self.assertEqual(self._get_section_class('/budgets/1/dashboard/'), 'section-dashboard')
    
    def test_expenses_section_detection(self):
        """Test that expense-related URLs are correctly identified."""
        self.assertEqual(self._get_section_class('/budgets/1/expenses/'), 'section-expenses')
        self.assertEqual(self._get_section_class('/budgets/1/expenses/create/'), 'section-expenses')
    
    def test_months_section_detection(self):
        """Test that month-related URLs are correctly identified."""
        self.assertEqual(self._get_section_class('/budgets/1/months/'), 'section-months')
        self.assertEqual(self._get_section_class('/budgets/1/months/2024/1/'), 'section-months')
    
    def test_payments_section_detection(self):
        """Test that payment-related URLs are correctly identified."""
        self.assertEqual(self._get_section_class('/budgets/1/expense-items/1/pay/'), 'section-payments')
        self.assertEqual(self._get_section_class('/budgets/1/expense-items/1/unpay/'), 'section-payments')
        self.assertEqual(self._get_section_class('/budgets/1/expense-items/1/payments/'), 'section-payments')
    
    def test_payees_section_detection(self):
        """Test that payee-related URLs are correctly identified."""
        self.assertEqual(self._get_section_class('/payees/'), 'section-payees')
        self.assertEqual(self._get_section_class('/payees/create/'), 'section-payees')
    
    def test_payment_methods_section_detection(self):
        """Test that payment method URLs are correctly identified."""
        self.assertEqual(self._get_section_class('/payment-methods/'), 'section-payment-methods')
        self.assertEqual(self._get_section_class('/payment-methods/create/'), 'section-payment-methods')
    
    def test_help_section_detection(self):
        """Test that help URLs are correctly identified."""
        self.assertEqual(self._get_section_class('/help/'), 'section-help')
        self.assertEqual(self._get_section_class('/help/getting_started/'), 'section-help')
    
    def test_no_resolver_match(self):
        """Test that missing resolver_match returns empty section class."""
        request = self.factory.get('/')
        request.resolver_match = None
        result = section_context(request)
        self.assertEqual(result['section_class'], '')
    
    def test_unknown_url_pattern(self):
        """Test that unknown URL patterns return empty section class."""
        # Test with a valid request but URL that doesn't match any patterns
        request = self.factory.get('/unknown/path/')
        # Simulate a resolver match that doesn't match our patterns
        class MockResolverMatch:
            def __init__(self):
                self.url_name = 'unknown_url_name'
        request.resolver_match = MockResolverMatch()  # type: ignore[assignment]
        result = section_context(request)
        self.assertEqual(result['section_class'], '')
    
    def test_section_class_in_template_context(self):
        """Test that section_class is properly available in template context."""
        from django.test import Client
        
        client = Client()
        response = client.get('/')
        
        # Check that the response contains the section class in the body tag
        self.assertContains(response, 'class="section-budgets"')
        
        # Verify the context processor is in the response context
        self.assertIn('section_class', response.context)
        self.assertEqual(response.context['section_class'], 'section-budgets')
    
    def test_section_metadata_approach(self):
        """Test that section metadata from URL patterns is correctly detected."""
        request = self.factory.get('/')
        request.resolver_match = resolve('/')
        
        result = section_context(request)
        self.assertEqual(result['section_class'], 'section-budgets')