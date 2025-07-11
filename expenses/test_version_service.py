from django.test import TestCase, RequestFactory
from django.template import Context, Template
from unittest.mock import patch
from expenses.services import VersionService
from expenses.context_processors import app_version_context


class VersionServiceTest(TestCase):
    """Test cases for VersionService functionality."""

    @patch('expenses.services.settings.APP_VERSION', '1.1.0')
    def test_get_version_returns_semantic_version(self):
        """Test that get_version returns a semantic version string."""
        service = VersionService()
        version = service.get_version()

        # Should return mocked test version
        self.assertEqual(version, "1.1.0")

        # Should be a string
        self.assertIsInstance(version, str)

        # Should follow semantic versioning pattern (basic check)
        parts = version.split(".")
        self.assertEqual(len(parts), 3)
        for part in parts:
            self.assertTrue(part.isdigit())

    @patch('expenses.services.settings.APP_VERSION', '1.1.0')
    def test_get_version_string_returns_formatted_version(self):
        """Test that get_version_string returns a formatted version with 'v' prefix."""
        service = VersionService()
        version_string = service.get_version_string()

        # Should return formatted version with 'v' prefix
        self.assertEqual(version_string, "v1.1.0")

        # Should start with 'v'
        self.assertTrue(version_string.startswith("v"))

        # Should be formatted version of get_version()
        expected = f"v{service.get_version()}"
        self.assertEqual(version_string, expected)

    @patch('expenses.services.settings.APP_VERSION', '1.1.0')
    def test_get_next_milestone_version(self):
        """Test that get_next_milestone_version increments minor version correctly and strips patch."""
        service = VersionService()
        next_version = service.get_next_milestone_version()

        # Should increment minor version from 1.1.0 to 1.2 (patch stripped)
        self.assertEqual(next_version, "1.2")

        # Should be a string
        self.assertIsInstance(next_version, str)

        # Should follow major.minor format (patch stripped)
        parts = next_version.split(".")
        self.assertEqual(len(parts), 2)
        self.assertEqual(parts[0], "1")  # major unchanged
        self.assertEqual(parts[1], "2")  # minor incremented

    @patch('expenses.services.settings.APP_VERSION', '1.1.0')
    def test_get_next_milestone_version_string(self):
        """Test that get_next_milestone_version_string returns formatted next version."""
        service = VersionService()
        next_version_string = service.get_next_milestone_version_string()

        # Should return formatted next version with 'v' prefix (patch stripped)
        self.assertEqual(next_version_string, "v1.2")

        # Should start with 'v'
        self.assertTrue(next_version_string.startswith("v"))

        # Should be formatted version of get_next_milestone_version()
        expected = f"v{service.get_next_milestone_version()}"
        self.assertEqual(next_version_string, expected)

    @patch('expenses.services.settings.APP_VERSION', '1.1.0')
    def test_get_github_issues_url(self):
        """Test that get_github_issues_url generates correct milestone filter URL."""
        service = VersionService()
        url = service.get_github_issues_url()

        # Should contain base GitHub issues URL
        self.assertIn(
            "https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues", url
        )

        # Should contain milestone filter for next version (1.2, patch stripped)
        self.assertIn("milestone%3A1.2", url)

        # Should contain issue query parameter
        self.assertIn("?q=", url)
        self.assertIn("is%3Aissue", url)

    @patch('expenses.services.settings.APP_VERSION', '1.1.0')
    def test_context_processor_adds_all_version_info(self):
        """Test that app_version_context processor adds all version info to template context."""
        factory = RequestFactory()
        request = factory.get("/")

        context = app_version_context(request)

        # Should return dict with all required keys
        self.assertIsInstance(context, dict)
        self.assertIn("app_version", context)
        self.assertIn("github_issues_url", context)

        # Should contain correct values
        self.assertEqual(context["app_version"], "v1.1.0")
        self.assertIn("milestone%3A1.2", context["github_issues_url"])

    @patch('expenses.services.settings.APP_VERSION', '1.1.0')
    def test_template_renders_version_correctly(self):
        """Test that version is accessible in templates via context processor."""
        # Create a simple template that uses app_version
        template = Template("{{ app_version }}")

        # Create context with app_version
        factory = RequestFactory()
        request = factory.get("/")
        context_data = app_version_context(request)
        context = Context(context_data)

        # Render template
        rendered = template.render(context)

        # Should render the version string
        self.assertEqual(rendered, "v1.1.0")

    def test_version_service_is_extensible(self):
        """Test that VersionService can be easily extended for future automation."""
        # Test that the service follows expected interface
        service = VersionService()

        # Should have required methods
        self.assertTrue(hasattr(service, "get_version"))
        self.assertTrue(hasattr(service, "get_version_string"))

        # Methods should be callable
        self.assertTrue(callable(service.get_version))
        self.assertTrue(callable(service.get_version_string))

        # Both methods should return strings
        self.assertIsInstance(service.get_version(), str)
        self.assertIsInstance(service.get_version_string(), str)

    def test_milestone_version_handles_edge_cases(self):
        """Test that milestone version calculation handles various version formats."""
        service = VersionService()

        # Test case 1: Version with patch (normal case)
        with patch.object(service, "get_version", return_value="2.3.5"):
            self.assertEqual(service.get_next_milestone_version(), "2.4")

        # Test case 2: Version at 9 minor (should increment to 10)
        with patch.object(service, "get_version", return_value="1.9.2"):
            self.assertEqual(service.get_next_milestone_version(), "1.10")

        # Test case 3: Version without patch (should still work)
        with patch.object(service, "get_version", return_value="3.1"):
            self.assertEqual(service.get_next_milestone_version(), "3.2")

        # Test case 4: Malformed version (fallback behavior)
        with patch.object(service, "get_version", return_value="invalid"):
            self.assertEqual(service.get_next_milestone_version(), "invalid")

        # Test case 5: Single number version (fallback behavior)
        with patch.object(service, "get_version", return_value="5"):
            self.assertEqual(service.get_next_milestone_version(), "5")

    @patch('expenses.services.settings.APP_VERSION', '1.1.0')
    def test_github_url_milestone_format_matches_expectations(self):
        """Test that GitHub URL uses correct milestone format (major.minor without patch)."""
        service = VersionService()
        url = service.get_github_issues_url()

        # Should NOT contain triple-digit version (with patch)
        self.assertNotIn("milestone%3A1.1.0", url)
        self.assertNotIn("1.1.0", url)

        # Should contain double-digit version (without patch)
        self.assertIn("milestone%3A1.2", url)

        # Verify the exact expected URL format
        expected_base = "https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues"
        expected_query = "?q=is%3Aissue+milestone%3A1.2"
        expected_url = f"{expected_base}{expected_query}"
        self.assertEqual(url, expected_url)
