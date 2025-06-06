#!/usr/bin/env python3
"""
Manual SCSS compilation script for development.

This script directly compiles SCSS files to CSS, bypassing django-sass-processor
caching issues. Run this when you make SCSS changes during development.
"""

import os
import sys
import sass
from pathlib import Path

def compile_scss():
    """Compile main.scss to CSS."""
    project_root = Path(__file__).parent
    scss_source = project_root / 'src' / 'scss' / 'main.scss'
    css_output = project_root / 'staticfiles' / 'scss' / 'main.css'
    
    # Ensure output directory exists
    css_output.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Compiling {scss_source} -> {css_output}")
    
    try:
        # Compile SCSS with source maps for development
        result = sass.compile(
            filename=str(scss_source),
            output_style='expanded',
            source_map_filename=str(css_output) + '.map',
            source_map_root='../../src/scss/'
        )
        
        # Write CSS file
        with open(css_output, 'w') as f:
            f.write(result[0])  # CSS content
        
        # Write source map if generated
        if result[1]:
            with open(str(css_output) + '.map', 'w') as f:
                f.write(result[1])
        
        print(f"✓ SCSS compiled successfully")
        print(f"  Output: {css_output}")
        print(f"  Size: {css_output.stat().st_size} bytes")
        
        return True
        
    except Exception as e:
        print(f"✗ SCSS compilation failed: {e}")
        return False

if __name__ == '__main__':
    success = compile_scss()
    sys.exit(0 if success else 1)