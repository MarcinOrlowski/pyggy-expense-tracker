import os
import time
import hashlib
import tempfile
from pathlib import Path
from django.test import TestCase
from django.contrib.staticfiles import finders
from django.core.management import call_command
from django.conf import settings


class SCSSSassProcessorTest(TestCase):
    """Test SCSS auto-compilation functionality with django-sass-processor."""
    
    def setUp(self):
        """Set up test environment."""
        self.scss_source = Path(settings.BASE_DIR) / 'src' / 'scss' / 'main.scss'
        self.css_output = Path(settings.STATIC_ROOT) / 'scss' / 'main.css'
        
        # Ensure static root exists
        os.makedirs(settings.STATIC_ROOT, exist_ok=True)
        
        # Store original SCSS content if file exists
        self.original_content = None
        if self.scss_source.exists():
            with open(self.scss_source, 'r') as f:
                self.original_content = f.read()
    
    def tearDown(self):
        """Clean up after test."""
        # Restore original SCSS content if it was modified
        if self.original_content and self.scss_source.exists():
            with open(self.scss_source, 'w') as f:
                f.write(self.original_content)
    
    def get_file_hash(self, file_path):
        """Get MD5 hash of a file."""
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def test_scss_file_exists(self):
        """Test that the main SCSS source file exists."""
        self.assertTrue(
            self.scss_source.exists(),
            f"Main SCSS file should exist at {self.scss_source}"
        )
    
    def test_sass_processor_configuration(self):
        """Test that django-sass-processor is properly configured."""
        # Check that sass_processor is in INSTALLED_APPS
        self.assertIn('sass_processor', settings.INSTALLED_APPS)
        
        # Check that CssFinder is in STATICFILES_FINDERS
        self.assertIn('sass_processor.finders.CssFinder', settings.STATICFILES_FINDERS)
        
        # Check SASS processor settings exist
        self.assertTrue(hasattr(settings, 'SASS_PROCESSOR_ROOT'))
        self.assertTrue(hasattr(settings, 'SASS_PROCESSOR_INCLUDE_DIRS'))
    
    def test_scss_auto_compilation_on_collectstatic(self):
        """
        Test that SCSS files are automatically compiled when running collectstatic.
        
        This test verifies the issue described in ticket #18:
        SCSS files should be automatically recompiled when source files change.
        """
        # Skip if SCSS file doesn't exist
        if not self.scss_source.exists():
            self.skipTest("Main SCSS file not found")
        
        # Get initial CSS hash (if exists)
        initial_css_hash = self.get_file_hash(self.css_output)
        
        # Modify SCSS file to trigger recompilation
        test_comment = f"\n/* Test modification at {time.time()} */\n"
        modified_content = self.original_content + test_comment
        
        with open(self.scss_source, 'w') as f:
            f.write(modified_content)
        
        # Wait briefly for file system
        time.sleep(0.1)
        
        # Run collectstatic
        call_command('collectstatic', '--noinput', verbosity=0)
        
        # Check if CSS was recompiled
        post_collectstatic_hash = self.get_file_hash(self.css_output)
        
        # CSS should exist after collectstatic
        self.assertTrue(
            self.css_output.exists(),
            f"CSS file should be created at {self.css_output} after collectstatic"
        )
        
        # CSS should be different from initial (if it existed) or newly created
        self.assertNotEqual(
            initial_css_hash,
            post_collectstatic_hash,
            "CSS should be recompiled when SCSS source changes. "
            "This indicates the SCSS auto-compilation issue from ticket #18."
        )
    
    def test_static_file_finder_serves_compiled_css(self):
        """Test that Django's static file finder can locate the compiled CSS."""
        # Skip if SCSS file doesn't exist
        if not self.scss_source.exists():
            self.skipTest("Main SCSS file not found")
        
        # Ensure CSS is compiled
        call_command('collectstatic', '--noinput', verbosity=0)
        
        # Test that static file finder can locate the CSS
        found_css = finders.find('scss/main.css')
        
        self.assertIsNotNone(
            found_css,
            "Static file finder should be able to locate the compiled CSS file"
        )
        
        self.assertTrue(
            os.path.exists(found_css),
            f"Found CSS file should exist at {found_css}"
        )
    
    def test_scss_compilation_produces_valid_css(self):
        """Test that SCSS compilation produces valid CSS output."""
        # Skip if SCSS file doesn't exist
        if not self.scss_source.exists():
            self.skipTest("Main SCSS file not found")
        
        # Run collectstatic to compile SCSS
        call_command('collectstatic', '--noinput', verbosity=0)
        
        # Check that CSS file exists and has content
        self.assertTrue(self.css_output.exists(), "CSS file should exist after compilation")
        
        # Check that CSS file is not empty
        css_size = self.css_output.stat().st_size
        self.assertGreater(css_size, 0, "Compiled CSS file should not be empty")
        
        # Basic check that output looks like CSS
        with open(self.css_output, 'r') as f:
            css_content = f.read()
        
        # CSS should contain some basic CSS patterns
        self.assertTrue(
            any(char in css_content for char in ['{', '}', ':']),
            "Compiled output should contain CSS syntax"
        )
