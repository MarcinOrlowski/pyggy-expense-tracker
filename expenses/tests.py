import hashlib
import os
import sys
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.management import call_command
from django.test import TestCase, override_settings


@override_settings(
    SASS_PROCESSOR_ENABLED=True,
    SASS_PROCESSOR_AUTO_INCLUDE=True,
    STATICFILES_FINDERS=[
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        'sass_processor.finders.CssFinder',
    ]
)
class SCSSSassProcessorTest(TestCase):
    """Test SCSS auto-compilation functionality with django-sass-processor."""

    def setUp(self):
        """Set up test environment."""
        self.scss_source = Path(settings.BASE_DIR) / "src" / "scss" / "main.scss"
        self.css_output = Path(settings.STATIC_ROOT) / "scss" / "main.css"

        # Ensure static root exists
        os.makedirs(settings.STATIC_ROOT, exist_ok=True)

        # Store original SCSS content if file exists
        self.original_content = None
        if self.scss_source.exists():
            with open(self.scss_source, "r") as f:
                self.original_content = f.read()

    def tearDown(self):
        """Clean up after test."""
        # Restore original SCSS content if it was modified
        if self.original_content and self.scss_source.exists():
            with open(self.scss_source, "w") as f:
                f.write(self.original_content)

    def get_file_hash(self, file_path):
        """Get MD5 hash of a file."""
        if not os.path.exists(file_path):
            return None
        with open(file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def test_scss_file_exists(self):
        """Test that the main SCSS source file exists."""
        self.assertTrue(
            self.scss_source.exists(),
            f"Main SCSS file should exist at {self.scss_source}",
        )

    def test_sass_processor_configuration(self):
        """Test that django-sass-processor is properly configured."""
        # Check that sass_processor is in INSTALLED_APPS
        self.assertIn("sass_processor", settings.INSTALLED_APPS)

        # Check that CssFinder is in STATICFILES_FINDERS
        self.assertIn("sass_processor.finders.CssFinder", settings.STATICFILES_FINDERS)

        # Check SASS processor settings exist
        self.assertTrue(hasattr(settings, "SASS_PROCESSOR_ROOT"))
        self.assertTrue(hasattr(settings, "SASS_PROCESSOR_INCLUDE_DIRS"))

    def test_static_file_finder_serves_compiled_css(self):
        """Test that Django's static file finder can locate the compiled CSS."""
        # Skip if SCSS file doesn't exist
        if not self.scss_source.exists():
            self.skipTest("Main SCSS file not found")

        # Ensure CSS is compiled
        call_command("collectstatic", "--noinput", verbosity=0)

        # Test that static file finder can locate the CSS
        found_css = finders.find("scss/main.css")

        self.assertIsNotNone(
            found_css,
            "Static file finder should be able to locate the compiled CSS file",
        )

        if found_css is not None:
            self.assertTrue(
                os.path.exists(found_css), f"Found CSS file should exist at {found_css}"
            )

    def test_scss_compilation_produces_valid_css(self):
        """Test that SCSS compilation produces valid CSS output."""
        # Skip if SCSS file doesn't exist
        if not self.scss_source.exists():
            self.skipTest("Main SCSS file not found")

        # Run collectstatic to compile SCSS
        call_command("collectstatic", "--noinput", verbosity=0)

        # Check that CSS file exists and has content
        self.assertTrue(
            self.css_output.exists(), "CSS file should exist after compilation"
        )

        # Check that CSS file is not empty
        css_size = self.css_output.stat().st_size
        self.assertGreater(css_size, 0, "Compiled CSS file should not be empty")

        # Basic check that output looks like CSS
        with open(self.css_output, "r") as f:
            css_content = f.read()

        # CSS should contain some basic CSS patterns
        self.assertTrue(
            any(char in css_content for char in ["{", "}", ":"]),
            "Compiled output should contain CSS syntax",
        )
