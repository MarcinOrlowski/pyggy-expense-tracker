# Visual Screen Distinctions Enhancement TRD

**Ticket**: [Add visual screen distinctions to improve user navigation](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/173)
**PRD Reference**: 0173_visual_screen_distinctions_PRD.md

## Technical Approach

We'll implement visual screen distinctions through SCSS enhancements to the existing dark terminal
theme, using CSS custom properties for section-specific color coding with 20% opacity and adding
subtle visual elements to the base template structure. The solution leverages Django's URL name
patterns and a custom context processor to apply section-specific CSS classes to the body element,
enabling targeted styling without affecting the existing component architecture or requiring
JavaScript modifications.

## Visual Design System

### Color Coding Scheme
Using existing terminal theme colors with 20% opacity for subtle distinction:

```scss
// Section-specific color variables (added to _variables.scss)
--section-budgets: rgba(189, 147, 249, 0.2);     // Purple - primary brand color
--section-dashboard: rgba(139, 233, 253, 0.2);   // Cyan - active/current state
--section-expenses: rgba(255, 184, 108, 0.2);    // Orange - transaction focus
--section-months: rgba(80, 250, 123, 0.2);       // Green - success/completion
--section-payees: rgba(241, 250, 140, 0.2);      // Yellow - contacts/people
--section-payments: rgba(255, 85, 85, 0.2);      // Red - payment/money flow
--section-payment-methods: rgba(255, 85, 85, 0.15); // Lighter red for payment methods
--section-help: rgba(189, 147, 249, 0.15);       // Lighter purple for help
```

### Implementation Strategy
1. **Body Class Assignment**: Use Django template context to add section-specific classes
2. **Header Border Accents**: 3px colored top border on navigation header using section colors
3. **Card Header Gradients**: Linear gradient (135deg) from base color to section color
4. **Navigation Active States**: Section-colored background and box-shadow glow on active nav items

## Template Structure Changes

### Base Template Modifications
```html
<!-- In expenses/templates/expenses/base.html -->
<body class="{% if section_class %}{{ section_class }}{% endif %}">
```

### Context Processor Implementation
```python
# In expenses/context_processors.py
def section_context(request):
    """Add section-specific CSS class based on URL name patterns."""
    if not request.resolver_match or not request.resolver_match.url_name:
        return {'section_class': ''}
    
    url_name = request.resolver_match.url_name
    
    # Simple mapping based on URL name prefixes
    # Order matters - more specific patterns first
    section_map = {
        'budget': 'section-budgets',
        'dashboard': 'section-dashboard',
        'expense_item': 'section-payments',  # Must come before 'expense'
        'expense': 'section-expenses',
        'month': 'section-months',
        'payee': 'section-payees',
        'payment_method': 'section-payment-methods',
        'help': 'section-help',
    }
    
    # Find matching section by checking URL name prefix
    for prefix, section_class in section_map.items():
        if url_name.startswith(prefix):
            return {'section_class': section_class}
    
    return {'section_class': ''}
```

## SCSS Implementation

### Section-Specific Styling
```scss
// In src/scss/_components.scss

// Section-Specific Visual Distinctions
// Header border accents for each section
.section-budgets header {
    border-top: 3px solid var(--section-budgets);
}
// ... (similar for all sections)

// Card header highlights with subtle section colors
.section-budgets .card-header {
    background: linear-gradient(135deg, var(--bg-secondary), var(--section-budgets));
}
// ... (similar for all sections)

// Navigation active state enhancements with section-specific glows
.section-budgets .nav-active {
    box-shadow: 0 0 8px var(--section-budgets);
    background-color: var(--section-budgets);
}
// ... (similar for all sections)
```

## Security & Performance

- **Performance**: CSS-only implementation with no JavaScript overhead, estimated <5ms impact on page load
- **Caching**: SCSS compilation maintains existing static file caching strategy
- **Accessibility**: Color distinctions supplemented with visual patterns to maintain WCAG compliance
- **Memory**: Context processor adds <1KB per request for section class determination

## Technical Risks & Mitigations

1. **Risk**: Color changes may conflict with existing theme → **Mitigation**: Use rgba transparency
   at 20% opacity and test against all existing components
2. **Risk**: URL name pattern changes could break section detection → **Mitigation**: Simple prefix
   matching with fallback to empty string for unknown patterns
3. **Risk**: Mobile responsiveness could be affected → **Mitigation**: Test all breakpoints and use
   existing responsive variables

## Implementation Plan

- **Phase 1** (S): Add context processor and update settings.py - 1 hour
- **Phase 2** (M): Update base template with section class integration - 30 minutes  
- **Phase 3** (L): Implement SCSS section styling and compile CSS - 2 hours
- **Phase 4** (S): Test across all sections and responsive breakpoints - 1 hour
- **Phase 5** (S): Update navigation active states with enhanced styling - 30 minutes

**Dependencies**: None - uses existing Django framework and SCSS build process

## Monitoring & Rollback

- **Feature flag**: CSS classes can be easily disabled by commenting out context processor
- **Key metrics**: Page load time monitoring, no degradation expected
- **Rollback**: Remove `section_context` from TEMPLATES context_processors in settings.py
- **Testing**: Visual regression testing on all main application screens before deployment
- **Unit tests**: Comprehensive test coverage in `test_section_context.py`
