# PRD: Separate CSS Styles from Templates (#0013)

## Overview

Extract embedded CSS from HTML templates into dedicated CSS files using SASS preprocessing to improve maintainability, unify styling, and eliminate code duplication.

## Goals

1. **Separate styles from markup** - Move all CSS from templates to external files
2. **Unify colors and styles** - Establish consistent design system
3. **Apply D.R.Y. principle** - Eliminate repeated CSS declarations

## Current State

- **base.html**: 825 lines of embedded CSS styles (lines 13-839)
- **payee_list.html**: 1 inline style attribute (`style="visibility: hidden;"`)
- All styling concentrated in template files
- CSS variables already established but could be better organized

## Implemented Solution

### File Structure

```text
src/scss/                    # Source SASS files
├── _variables.scss          # SASS variables, color palette
├── _base.scss              # Typography, layout, reset styles  
├── _components.scss        # Buttons, cards, tables, forms, messages
├── _calendar.scss          # Calendar grid and date-specific styles
├── _responsive.scss        # Media queries and mobile styles
└── main.scss              # Main import file
```

### Content Organization

- **_variables.scss**: All CSS custom properties (52 variables) using SASS format
- **_base.scss**: Reset, typography, body, container, layout utilities
- **_components.scss**: Reusable UI components (buttons, cards, tables, forms)
- **_calendar.scss**: Calendar grid, day states, indicators, legend
- **_responsive.scss**: All `@media` queries consolidated
- **main.scss**: Imports all partials in correct order

### SASS Processing

- **Development**: `django-sass-processor` compiles SASS on-the-fly
- **Template Tag**: `{% sass_src 'scss/main.scss' %}` handles compilation
- **Auto-compilation**: SASS files are automatically compiled when changed

## Benefits

- **Maintainability**: SASS partials with logical organization
- **Performance**: Single compressed CSS file served to browsers
- **Consistency**: Centralized design system with SASS variables
- **Developer Experience**: SASS features (nesting, imports, variables)
- **Separation of Concerns**: Source code separated from public assets

## Success Criteria

- [x] All CSS extracted from templates
- [x] Visual appearance unchanged
- [x] No duplicate CSS rules (DRY principle applied)
- [x] Consistent color usage through SASS variables
- [x] Proper Django static file integration
- [x] Source/public file separation
- [x] Automated build process

## Technical Implementation

- **Template Loading**: `{% sass_src 'scss/main.scss' %}` in base.html
- **SASS Compilation**: `django-sass-processor` handles compilation automatically
- **File Structure**: SASS sources in `src/scss/` directory
- **Configuration**: SASS processor configured in Django settings
- **Utility Classes**: Added `.btn-hidden` class to replace inline styles

## Dependencies Added

- `libsass==0.23.0` - SASS compilation library
- `django-sass-processor==1.4.1` - Django SASS integration for on-the-fly compilation

## Django Configuration

```python
INSTALLED_APPS = [
    # ...
    'sass_processor',
    'expenses',
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'sass_processor.finders.CssFinder',
]

SASS_PROCESSOR_ROOT = STATIC_ROOT
SASS_PROCESSOR_INCLUDE_DIRS = [
    BASE_DIR / 'src' / 'scss',
]
```

## Risk Mitigation

- [x] Created backup of original templates via git branch
- [x] Tested all pages for visual regression
- [x] Validated CSS syntax and organization
- [x] Verified static file serving works correctly
