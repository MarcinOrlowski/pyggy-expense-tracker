# Simplify List UI by Making Rows Clickable for View Action PRD

**Ticket**: [Simplify list UI by making rows clickable for view action](https://github.com/MarcinOrlowski/python-pyggy-expense-tracker/issues/140)

## Problem Statement

Currently all list views use dedicated view icons in action columns, creating visual clutter and
requiring precise clicking on small targets. Users must locate and click tiny eye icons to view
details, which is inefficient and inconsistent with modern UX patterns. This reduces usability and
creates unnecessary cognitive load when navigating the application.

## Solution Overview

Remove dedicated view icons from action columns and make entire table rows clickable to trigger view
actions. This creates larger, more intuitive click targets while maintaining other actions (edit,
delete) in dedicated columns. The solution follows common web application patterns where list rows
are naturally clickable for viewing details, resulting in a cleaner and more user-friendly
interface.

## User Stories

1. As a user browsing expenses, I want to click anywhere on a row to view details, so that I can
   quickly access information without precise targeting
1. As a user managing budgets, I want consistent row-clicking behavior across all lists, so that I
   can navigate intuitively throughout the application
1. As a user on mobile devices, I want larger click targets for viewing items, so that I can easily
   interact with lists on smaller screens

## Acceptance Criteria

- [ ] Entire table rows are clickable for view action across all list templates
- [ ] View icons are removed from action columns in expense_list.html and month_list.html
- [ ] Redundant view icon is removed from budget_list.html (keeping existing clickable name)
- [ ] Other actions (edit, delete, hide/unhide) remain in dedicated action columns
- [ ] Hover feedback is provided when users mouse over clickable rows
- [ ] Row clicking navigates to the same detail/view URLs as previous view icons
- [ ] Consistent behavior is applied across expenses, budgets, months, payees, and payment methods lists

## Out of Scope

- Changes to detail/view page layouts or functionality
- Modifications to create/edit forms
- Updates to action button styling beyond view icon removal
- Mobile-specific responsive design changes
- Keyboard navigation enhancements
- Screen reader accessibility improvements

## Success Metrics

1. All list views have consistent clickable row behavior within 1 development cycle
2. View icons are completely removed from action columns where applicable
3. User testing confirms improved click target usability (if conducted)
