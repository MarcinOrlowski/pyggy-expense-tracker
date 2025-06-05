from django.test import TestCase, Client
from django.urls import reverse
import os
import tempfile


class HelpViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_help_index_view(self):
        """Test that help index view loads correctly."""
        response = self.client.get(reverse("help_index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Help & Documentation")

    def test_help_page_view_existing_file(self):
        """Test that help page view loads for existing documentation."""
        # Test with docker.md which should exist
        response = self.client.get(reverse("help_page", kwargs={"page_name": "docker"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Docker Setup Guide")

    def test_help_page_view_nonexistent_file(self):
        """Test that help page view returns user-friendly error for non-existent files."""
        response = self.client.get(
            reverse("help_page", kwargs={"page_name": "nonexistent"})
        )
        self.assertEqual(response.status_code, 200)  # Returns 200 with error message
        self.assertContains(response, "Documentation page not found")
        self.assertContains(response, "does not exist")
        self.assertContains(response, "Go to Help Index")

    def test_help_page_security_path_traversal(self):
        """Test that path traversal attacks are prevented."""
        # Django URL patterns will reject '../' in page_name, but let's test a more subtle case
        # Test with double dots in filename (which would pass URL validation)
        response = self.client.get(
            reverse("help_page", kwargs={"page_name": "some..file"})
        )
        self.assertEqual(response.status_code, 200)  # Returns 200 with error message
        self.assertContains(response, "Documentation page not found")
        self.assertContains(response, "does not exist")

    def test_help_index_with_docs(self):
        """Test that help index lists available documentation files."""
        response = self.client.get(reverse("help_index") + "?list=1")
        self.assertEqual(response.status_code, 200)
        # Should contain at least the DOCKER.md file
        self.assertContains(response, "Docker")

    def test_help_index_shows_readme_by_default(self):
        """Test that help index shows README.md by default if it exists."""
        response = self.client.get(reverse("help_index"))
        self.assertEqual(response.status_code, 200)
        # Should show the README content, not the file listing
        self.assertContains(response, "PyGGy Usage Documentation")
        self.assertNotContains(response, "help-grid")

    def test_help_error_display(self):
        """Test that error pages display user-friendly messages."""
        response = self.client.get(
            reverse("help_page", kwargs={"page_name": "invalid_file_name"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "help-error")
        self.assertContains(response, "fas fa-exclamation-triangle")
        self.assertContains(response, "Go to Help Index")
        self.assertContains(response, "View All Documentation")
