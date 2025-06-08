from django.test import TestCase, RequestFactory
from django.template import Context, Template
from django.template.context_processors import request as request_processor
from expenses.services import VersionService
from expenses.context_processors import app_version_context


class VersionServiceTest(TestCase):
    """Test cases for VersionService functionality."""

    def test_get_version_returns_semantic_version(self):
        """Test that get_version returns a semantic version string."""
        service = VersionService()
        version = service.get_version()
        
        # Should return current hardcoded version
        self.assertEqual(version, "1.1.0")
        
        # Should be a string
        self.assertIsInstance(version, str)
        
        # Should follow semantic versioning pattern (basic check)
        parts = version.split('.')
        self.assertEqual(len(parts), 3)
        for part in parts:
            self.assertTrue(part.isdigit())

    def test_get_version_string_returns_formatted_version(self):
        """Test that get_version_string returns a formatted version with 'v' prefix."""
        service = VersionService()
        version_string = service.get_version_string()
        
        # Should return formatted version with 'v' prefix
        self.assertEqual(version_string, "v1.1.0")
        
        # Should start with 'v'
        self.assertTrue(version_string.startswith('v'))
        
        # Should be formatted version of get_version()
        expected = f"v{service.get_version()}"
        self.assertEqual(version_string, expected)

    def test_context_processor_adds_app_version(self):
        """Test that app_version_context processor adds version to template context."""
        factory = RequestFactory()
        request = factory.get('/')
        
        context = app_version_context(request)
        
        # Should return dict with app_version key
        self.assertIsInstance(context, dict)
        self.assertIn('app_version', context)
        
        # Should contain formatted version string
        self.assertEqual(context['app_version'], 'v1.1.0')

    def test_template_renders_version_correctly(self):
        """Test that version is accessible in templates via context processor."""
        # Create a simple template that uses app_version
        template = Template('{{ app_version }}')
        
        # Create context with app_version
        factory = RequestFactory()
        request = factory.get('/')
        context_data = app_version_context(request)
        context = Context(context_data)
        
        # Render template
        rendered = template.render(context)
        
        # Should render the version string
        self.assertEqual(rendered, 'v1.1.0')

    def test_version_service_is_extensible(self):
        """Test that VersionService can be easily extended for future automation."""
        # Test that the service follows expected interface
        service = VersionService()
        
        # Should have required methods
        self.assertTrue(hasattr(service, 'get_version'))
        self.assertTrue(hasattr(service, 'get_version_string'))
        
        # Methods should be callable
        self.assertTrue(callable(service.get_version))
        self.assertTrue(callable(service.get_version_string))
        
        # Both methods should return strings
        self.assertIsInstance(service.get_version(), str)
        self.assertIsInstance(service.get_version_string(), str)