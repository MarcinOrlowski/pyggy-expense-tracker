# Standardize Action Button Styling and Icons TRD

**Last Updated**: January 6, 2025
**Ticket
**: [Standardize action button styling and icons in table rows](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/12)
**PRD Reference**: 0012_standardize_action_button_styling_and_icons_PRD.md

## Technical Approach

<<<<<<< HEAD
This is a pure frontend styling update that requires modifications to Django HTML templates only.
We'll remove custom color classes from action buttons (keeping only default `btn` and `btn-danger`
for delete actions) and update specific icons to be more action-oriented. The existing CSS framework
already supports default button styling, so no CSS changes are required. All modifications will be
made to template files in the `expenses/templates/expenses/` directory.
=======
This is a pure frontend styling update that requires modifications to Django HTML templates only. We'll remove
custom color classes from action buttons (keeping only default `btn` and `btn-danger` for delete actions) and
update specific icons to be more action-oriented. The existing CSS framework already supports default button
styling, so no CSS changes are required. All modifications will be made to template files in the
`expenses/templates/expenses/` directory.
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

## Template Modifications

**Files to Update:**

- `expense_list.html` - Lines 76-79 (view, edit, delete buttons)
- `payee_list.html` - Lines 42-55 (edit, hide/show, delete buttons)
- `month_list.html` - Lines 31-38 (view, delete buttons)
- `budget_list.html` - Lines 29-42 (open, edit, delete buttons)
- `includes/expense_items_table.html` - Lines 42-46 (pay/unpay, view buttons)
- `expense_detail.html` - Lines 74-84 (pay/unpay buttons)

**Button Class Changes:**

```html
<!-- Before -->
<a class="btn btn-secondary btn-sm" ...>  <!-- Remove btn-secondary -->
   <a class="btn btn-success btn-sm" ...>    <!-- Remove btn-success -->
      <a class="btn btn-warning btn-sm" ...>    <!-- Remove btn-warning -->
         <a class="btn btn-danger btn-sm" ...>     <!-- Keep btn-danger for delete -->

            <!-- After -->
            <a class="btn btn-sm" ...>               <!-- Default styling -->
               <a class="btn btn-sm" ...>               <!-- Default styling -->
                  <a class="btn btn-sm" ...>               <!-- Default styling -->
                     <a class="btn btn-danger btn-sm" ...>    <!-- Warning color for delete -->
```

**Icon Updates:**

- `fa-circle-check` → `fa-check` (Mark as Paid action)
- `fa-rotate-left` → `fa-undo` (Mark as Unpaid action)
- `fa-folder-open` → `fa-eye` (View/Open action in budget_list.html)

## Security & Performance

- **No security impact**: Changes are cosmetic CSS class modifications only
- **Performance**: Negligible impact, potentially slight improvement due to fewer CSS classes
- **Accessibility**: All existing `aria-label` and `title` attributes preserved

## Technical Risks & Mitigations

1. **Risk**: Visual regression in button appearance → **Mitigation**: Default button styling already
   exists in `_components.scss` lines 170-182
2. **Risk**: Broken functionality due to modified templates → **Mitigation**: Only class names and
   icon classes being changed, no structural modifications
3. **Risk**: Inconsistent styling across browsers → **Mitigation**: Default button styling uses CSS
   variables that are already tested across browsers

## Implementation Plan

- **Phase 1** (XS): Update expense_list.html and payee_list.html - 15 minutes
- **Phase 2** (XS): Update month_list.html and budget_list.html - 10 minutes
- **Phase 3** (XS): Update expense_items_table.html and expense_detail.html - 15 minutes
- **Phase 4** (XS): Visual testing across all table views - 10 minutes

**Dependencies**: None - standalone template modifications

## Monitoring & Rollback

- **Feature flag**: Not applicable (pure styling change)
- **Key metrics**: Visual consistency verification across 6 template files
- **Rollback**: Simple git revert of template changes if visual issues arise
- **Testing**: Manual verification of all table views to ensure consistent button appearance
