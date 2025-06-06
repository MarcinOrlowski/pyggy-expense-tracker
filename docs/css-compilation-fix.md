# CSS Compilation Issue - Fix Documentation

## Problem

After redirecting from certain actions (like deleting an expense), the CSS styles may not load
correctly, resulting in unstyled HTML elements.

## Root Cause

This issue occurs when django-sass-processor fails to compile SCSS files correctly during runtime.
The library sometimes has issues with its caching mechanism, especially after HTTP redirects.

## Solution

### Immediate Fix

1. Run the SCSS compilation script manually:

   ```bash
   python compile_scss.py
   ```

2. Restart the development server:

   ```bash
   ./run_dev.sh
   ```

### Long-term Solution

The base template has been updated to use the pre-compiled CSS file directly (`main.css`) instead of
relying on django-sass-processor's automatic compilation (`main.scss`).

### Development Workflow

Always use the `run_dev.sh` script to start the development server:

```bash
./run_dev.sh
```

This script ensures that:

- SCSS is compiled to CSS before server startup
- Static files are collected
- Migrations are applied
- The development server starts with all assets properly configured

### Manual SCSS Compilation

If you make changes to SCSS files during development:

```bash
python compile_scss.py
```

This will compile `src/scss/main.scss` to `staticfiles/scss/main.css`.

## Technical Details

- **Original issue**: `{% sass_src 'scss/main.scss' %}` tag in base.html
- **Fixed to**: `{% static 'scss/main.css' %}` tag
- **SCSS source**: `src/scss/main.scss`
- **Compiled CSS**: `staticfiles/scss/main.css`

## Prevention

- Always run `compile_scss.py` after modifying SCSS files
- Use `run_dev.sh` to start the development server
- Consider running `compile_scss.py` in a watch mode during active SCSS development
