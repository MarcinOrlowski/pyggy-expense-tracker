# Simplify List UI by Making Rows Clickable for View Action TRD

**Ticket**: [Simplify list UI by making rows clickable for view action](https://github.com/MarcinOrlowski/python-pyggy-expense-tracker/issues/140)
**PRD Reference**: 0140_simplify_list_ui_by_making_rows_clickable_for_view_action_PRD.md

## Technical Approach

This is a frontend-only change involving Django template modifications and CSS updates. We'll modify
existing list templates to remove redundant view icons and add JavaScript click handlers to table
rows. The implementation will use unobtrusive JavaScript that preserves existing URL patterns and
maintains accessibility. No backend changes are required since we're reusing existing detail view
URLs.

## Template Changes

### Files to Modify:
- `expenses/templates/expenses/expense_list.html` - Remove view icon, add row clickability
- `expenses/templates/expenses/budget_list.html` - Remove redundant view icon only  
- `expenses/templates/expenses/month_list.html` - Remove view icon, add row clickability

### HTML Structure:
```html
<!-- Before -->
<tr>
    <td>Data</td>
    <td class="actions-column">
        <a href="detail-url" class="btn btn-sm"><i class="fas fa-eye"></i></a>
        <a href="edit-url" class="btn btn-sm"><i class="fas fa-pen"></i></a>
    </td>
</tr>

<!-- After -->
<tr class="clickable-row" data-href="detail-url" style="cursor: pointer;">
    <td>Data</td>
    <td class="actions-column">
        <a href="edit-url" class="btn btn-sm"><i class="fas fa-pen"></i></a>
    </td>
</tr>
```

## JavaScript Implementation

### Click Handler:
```javascript
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.clickable-row').forEach(row => {
        row.addEventListener('click', function(e) {
            // Prevent row click when clicking action buttons
            if (!e.target.closest('.actions-column')) {
                window.location.href = this.dataset.href;
            }
        });
    });
});
```

## CSS Updates

### Row Hover Styles:
```css
.clickable-row {
    cursor: pointer;
    transition: background-color 0.2s ease;
}

.clickable-row:hover {
    background-color: var(--hover-color, #f5f5f5);
}

.clickable-row .actions-column {
    cursor: default;
}
```

## Security & Performance

- **XSS Protection**: Using existing Django URL template tags, no user input in data-href attributes
- **Performance**: Minimal JavaScript overhead, event delegation not needed due to small table sizes
- **Accessibility**: Maintained via existing URL structure and ARIA labels on remaining action buttons

## Technical Risks & Mitigations

1. **Risk**: JavaScript conflicts with existing click handlers → **Mitigation**: Event target checking to exclude action column clicks
2. **Risk**: Reduced accessibility for keyboard users → **Mitigation**: Preserve existing link structure and add proper ARIA attributes
3. **Risk**: Mobile touch target issues → **Mitigation**: CSS ensures proper hover states and touch feedback

## Implementation Plan

- Task 1 (S): Remove view icons from expense_list.html and month_list.html - 30 min
- Task 2 (S): Remove redundant view icon from budget_list.html - 10 min  
- Task 3 (M): Add JavaScript click handlers to base template - 45 min
- Task 4 (S): Add CSS hover styles for clickable rows - 15 min
- Task 5 (S): Test across all list views and browsers - 30 min

Dependencies: None

## Monitoring & Rollback

- **Feature flag**: Not required - simple template changes
- **Key metrics**: User feedback on usability, no errors in browser console
- **Rollback**: Git revert of template changes if issues arise
