# Add Text Labels Next to Icons in Main Toolbar Action Buttons TRD

**Ticket**: [Add text labels next to icons in main toolbar action buttons](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/92)
**PRD Reference**: 0092_add_text_labels_next_to_icons_in_main_toolbar_action_buttons_PRD.md

## Technical Approach
We'll modify the existing Django template `expenses/templates/expenses/base.html` to add text spans alongside current FontAwesome icons in the main navigation toolbar. CSS updates in `src/scss/_components.scss` will handle layout adjustments for icon-text button styling. The implementation preserves all existing functionality, routing, and accessibility attributes while adding visible text labels using a flexbox layout within existing `.btn-icon` elements.

## Template Structure Changes
```html
<!-- Current structure -->
<a href="..." class="btn btn-icon" title="..." aria-label="...">
  <i class="fas fa-icon"></i>
</a>

<!-- New structure -->
<a href="..." class="btn btn-icon" title="..." aria-label="...">
  <i class="fas fa-icon"></i>
  <span>Label Text</span>
</a>
```

**Text Labels:**
- Dashboard: "Dashboard"
- Calendar: "Months" 
- Receipt: "Expenses"
- Plus: "Add Expense"
- Wallet: "Budgets"
- Users: "Payees"

## CSS Styling Approach
```scss
.nav-actions .btn-icon {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  i {
    flex-shrink: 0;
  }
  
  span {
    font-size: 0.875rem;
    white-space: nowrap;
  }
}
```

## Security & Performance
- No security implications: purely frontend template changes
- Performance impact: negligible (minimal HTML/CSS additions)
- Browser compatibility: Modern flexbox support (IE11+)

## Technical Risks & Mitigations
1. **Risk**: Text overflow on narrow viewports → **Mitigation**: Use `white-space: nowrap` and test responsive breakpoints
2. **Risk**: Breaking existing icon-only styling → **Mitigation**: Scope changes specifically to `.nav-actions .btn-icon`

## Implementation Plan
- Phase 1 (S): Update base.html template with text labels - 30 minutes
- Phase 2 (S): Update CSS styling for icon-text layout - 30 minutes  
- Phase 3 (S): Test responsive behavior and visual consistency - 30 minutes

Dependencies: None

## Monitoring & Rollback
- Feature flag: Not required (low-risk visual enhancement)
- Key metrics: Visual consistency verification through manual testing
- Rollback: Simple git revert of template and CSS changes if issues arise