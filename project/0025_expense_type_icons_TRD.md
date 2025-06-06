# Expense Type Icons TRD v1.0

**Last Updated**: 2025-06-02
**Ticket**: [Add icons for expense types](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/25)
**PRD Reference**: [0025_expense_type_icons_PRD.md](0025_expense_type_icons_PRD.md)

## Technical Approach

We'll implement expense type icons by adding a static icon mapping dictionary and helper method to the existing Expense model in Django.
The solution leverages the existing Font Awesome 6.5.1 integration and requires no database changes. Icons will be displayed in templates
using the helper method `get_expense_type_icon()` alongside existing `get_expense_type_display()` functionality.

## Data Model

No database schema changes required. Implementation uses existing Expense model structure:

```python
# expenses/models.py - New additions only
class Expense(models.Model):
    # Existing fields remain unchanged...
    
    EXPENSE_TYPE_ICONS = {
        'endless_recurring': 'fa-arrows-rotate',
        'split_payment': 'fa-money-bill-transfer', 
        'one_time': 'fa-circle-dot',
        'recurring_with_end': 'fa-calendar-check'
    }
    
    def get_expense_type_icon(self):
        return self.EXPENSE_TYPE_ICONS.get(self.expense_type, 'fa-question-circle')
```

## Template Integration

Template changes for icon display:

```html
<!-- expense_list.html -->
<i class="fas {{ expense.get_expense_type_icon }}" 
   aria-label="{{ expense.get_expense_type_display }}" 
   title="{{ expense.get_expense_type_display }}"></i>

<!-- expense_detail.html -->
<i class="fas {{ expense.get_expense_type_icon }}" 
   aria-label="{{ expense.get_expense_type_display }}"></i>
{{ expense.get_expense_type_display }}
```

## Security & Performance

- **XSS Protection**: Icon classes are hardcoded constants, no user input injection possible
- **Performance**: Static dictionary lookup, O(1) complexity with negligible overhead
- **Accessibility**: All icons include aria-label and title attributes for screen readers

## Technical Risks & Mitigations

1. **Risk**: Font Awesome class changes in future versions → **Mitigation**: Use Font Awesome 6.x stable classes with fallback icon
2. **Risk**: Inconsistent icon display across browsers → **Mitigation**: Leverage existing Font Awesome CSS already tested in project

## Implementation Plan

- **Phase 1** (S): Add icon mapping and helper method to Expense model - 30 minutes
- **Phase 2** (S): Update expense_list.html template with icons - 15 minutes
- **Phase 3** (S): Update expense_detail.html template with icons - 15 minutes
- **Phase 4** (XS): Test accessibility attributes and visual consistency - 15 minutes

Dependencies: None (uses existing Font Awesome integration)

## Monitoring & Rollback

- **Feature flag**: Not required (non-breaking change, icons display alongside existing text)
- **Key metrics**: Visual regression testing for icon display consistency
- **Rollback**: Simple template revert removes icons, no data loss risk since no schema changes

## Icon Mapping Rationale

- `endless_recurring`: `fa-arrows-rotate` - Circular arrows suggest continuous/endless cycle
- `split_payment`: `fa-money-bill-transfer` - Money transfer icon represents payment splitting
- `one_time`: `fa-circle-dot` - Single dot represents one-time occurrence
- `recurring_with_end`: `fa-calendar-check` - Calendar with check suggests scheduled/finite recurrence
