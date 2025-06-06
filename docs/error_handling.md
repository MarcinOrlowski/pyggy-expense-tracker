# Error Handling Documentation

This document explains how the application handles errors and how to test user-friendly error pages.

## Overview

The application provides user-friendly error handling for:

1. **General 404 errors** - When pages don't exist
2. **Help system errors** - When documentation pages are missing or broken
3. **Permission errors** - When users don't have access to resources

## Testing Error Handling

### During Development (DEBUG = True)

By default, Django shows detailed debug pages when `DEBUG = True`. To test user-friendly error
pages:

1. **Temporarily set DEBUG = False** in `pyggy/settings.py`
2. **Run `python manage.py collectstatic --noinput`** to collect static files
3. **Test error pages** in your browser or with curl
4. **Set DEBUG = True** when done testing

**Note**: The application is configured to serve static files correctly even when `DEBUG = False`,
so styling will work properly on error pages.

### Error Page Types

#### 1. General 404 Error Page

- **Template**: `expenses/templates/404.html`
- **Handler**: `expenses.views.custom_404`
- **Test URLs**:
  - `/budgets/999/dashboard/` (non-existent budget)
  - `/invalid-url/`
  - `/budgets/1/expenses/999/` (non-existent expense)

#### 2. Help System Error Pages

- **Template**: `expenses/templates/expenses/help_page.html` (with error styling)
- **Handler**: `expenses.views._render_help_error`
- **Test URLs**:
  - `/help/nonexistent/` (missing documentation file)
  - `/help/broken-file/` (file that can't be read)

## Error Page Features

### General 404 Page

- Clean, branded design matching the application
- Helpful explanations of why the error occurred
- Navigation buttons to return to safety (Budget List, Help)
- Mobile-responsive design

### Help System Error Pages

- Context-aware error messages
- Navigation back to Help Index or documentation listing
- Maintains help system styling and layout
- Icons and visual cues for better UX

## Testing Commands

```bash
# Test general 404 with DEBUG = False
curl -s http://localhost:8000/budgets/999/dashboard/ | grep "Page Not Found"

# Test help system error handling
curl -s http://localhost:8000/help/nonexistent/ | grep "Documentation page not found"

# Check HTTP status codes
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/invalid-url/
```

## Security Considerations

- Path traversal protection in help system
- Proper file validation before rendering
- No sensitive information exposed in error messages
- Graceful handling of permission errors

## Customization

To customize error pages:

1. **Edit templates** in `expenses/templates/`
2. **Modify error handlers** in `expenses/views/error_handlers.py`
3. **Update styling** using existing CSS variables for consistency

The error handling system is designed to be user-friendly while maintaining security and providing
helpful navigation options.
