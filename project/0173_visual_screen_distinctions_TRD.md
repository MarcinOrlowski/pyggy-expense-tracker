# Visual Screen Distinctions Enhancement TRD

**Ticket**: [Add visual screen distinctions to improve user navigation](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/173)
**PRD Reference**: 0173_visual_screen_distinctions_PRD.md

## Technical Approach

We'll implement visual screen distinctions through SCSS enhancements to the existing dark terminal
theme, using CSS custom properties for section-specific color coding and adding subtle visual
elements to the base template structure. The solution leverages Django's URL namespacing and
template context to apply section-specific CSS classes to the body element, enabling targeted
styling without affecting the existing component architecture or requiring JavaScript modifications.

## Visual Design System

### Color Coding Scheme
Using existing terminal theme colors with 20% opacity for subtle distinction:

```scss
// Section-specific color variables
$section-budgets: rgba(189, 147, 249, 0.2);    // Purple - primary brand color
$section-dashboard: rgba(139, 233, 253, 0.2);  // Cyan - active/current state
$section-expenses: rgba(255, 184, 108, 0.2);   // Orange - transaction focus
$section-months: rgba(80, 250, 123, 0.2);      // Green - success/completion
$section-payees: rgba(241, 250, 140, 0.2);     // Yellow - contacts/people
$section-payments: rgba(255, 85, 85, 0.2);     // Red - payment/money flow
```

### Implementation Strategy
1. **Body Class Assignment**: Use Django template context to add section-specific classes
2. **Header Border Accents**: 3px colored border on navigation header
3. **Card Header Highlights**: Subtle background tint on card headers within sections
4. **Navigation Icon Glow**: CSS box-shadow on active section navigation items

## Template Structure Changes

### Base Template Modifications
```html
<!-- In expenses/templates/expenses/base.html -->
<body class="{% if section_class %}{{ section_class }}{% endif %}">
```

### Context Processor Addition
```python
# In expenses/context_processors.py
def section_context(request):
    """Add section-specific CSS class based on URL namespace"""
    section_map = {
        'expenses:budget_list': 'section-budgets',
        'expenses:dashboard': 'section-dashboard', 
        'expenses:expense_list': 'section-expenses',
        'expenses:month_list': 'section-months',
        'expenses:payee_list': 'section-payees',
        'expenses:payment_method_list': 'section-payments',
    }
    
    resolver_match = request.resolver_match
    if resolver_match:
        url_name = f"{resolver_match.namespace}:{resolver_match.url_name}"
        return {'section_class': section_map.get(url_name, '')}
    
    return {'section_class': ''}
```

## SCSS Implementation

### Section-Specific Styling
```scss
// In src/scss/_components.scss

// Header border accents
.section-budgets .header-nav { border-top: 3px solid $section-budgets; }
.section-dashboard .header-nav { border-top: 3px solid $section-dashboard; }
.section-expenses .header-nav { border-top: 3px solid $section-expenses; }
.section-months .header-nav { border-top: 3px solid $section-months; }
.section-payees .header-nav { border-top: 3px solid $section-payees; }
.section-payments .header-nav { border-top: 3px solid $section-payments; }

// Card header highlights  
.section-budgets .card-header { background: linear-gradient(135deg, $card-header-bg, $section-budgets); }
.section-dashboard .card-header { background: linear-gradient(135deg, $card-header-bg, $section-dashboard); }
// ... (similar for other sections)

// Navigation active state enhancement
.section-budgets .nav-link.active { box-shadow: 0 0 8px $section-budgets; }
.section-dashboard .nav-link.active { box-shadow: 0 0 8px $section-dashboard; }
// ... (similar for other sections)
```

## Security & Performance

- **Performance**: CSS-only implementation with no JavaScript overhead, estimated <5ms impact on page load
- **Caching**: SCSS compilation maintains existing static file caching strategy
- **Accessibility**: Color distinctions supplemented with visual patterns to maintain WCAG compliance
- **Memory**: Context processor adds <1KB per request for section class determination

## Technical Risks & Mitigations

1. **Risk**: Color changes may conflict with existing theme → **Mitigation**: Use rgba transparency
   and test against all existing components
1. **Risk**: URL namespace changes could break section detection → **Mitigation**: Fallback to empty
   string for unknown URLs, no visual impact
1. **Risk**: Mobile responsiveness could be affected → **Mitigation**: Test all breakpoints and use
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
- **Rollback**: Remove context processor from settings.py and recompile SCSS without section styles
- **Testing**: Visual regression testing on all main application screens before deployment
