# PRD: Dashboard Rework - Separate Current Month Summary and Expense List

**Ticket:** [#0007](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/7)  
**Version:** 1.0  
**Date:** 2025-01-06

## Executive Summary

Rework the current dashboard to improve user experience by separating the current month summary from
the expense list and establishing a foundation for future widget-based enhancements.

## Problem Statement

The current dashboard combines monthly summary statistics with detailed expense items in a single
card, creating visual clutter and poor information hierarchy. This monolithic design makes it
difficult to:

- Quickly scan key financial metrics
- Focus on either summary or detailed information
- Add future dashboard widgets or features
- Customize the dashboard layout

## Goals

### Primary Goals

1. **Separate concerns**: Split monthly summary from expense list into distinct visual sections
2. **Improve readability**: Better visual hierarchy and information organization
3. **Establish widget foundation**: Create scalable architecture for future dashboard enhancements
4. **Maintain functionality**: Preserve all existing features and data

### Secondary Goals

1. **Enhanced UX**: More intuitive dashboard navigation and focus areas
2. **Responsive design**: Ensure layout works on all screen sizes
3. **Consistent styling**: Maintain current theme and design patterns

## Success Metrics

- [ ] Monthly summary displayed in dedicated widget/section
- [ ] Expense list shown in separate, dedicated section
- [ ] All existing functionality preserved (no regressions)
- [ ] Responsive design maintained across devices
- [ ] Code follows project coding standards
- [ ] User can easily distinguish between summary and detail information

## User Stories

### US1: Monthly Summary Widget

<<<<<<< HEAD
**As a user**, I want to see my current month's financial summary in a clear, dedicated section so
that I can quickly understand my overall financial status without being distracted by detailed line
items.
=======
**As a user**, I want to see my current month's financial summary in a clear, dedicated section so that I can quickly understand my overall financial status without being distracted by detailed line items.
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

**Acceptance Criteria:**

- Monthly summary is visually separated from expense details
- Shows total month amount, pending amount/count, paid amount/count
- Maintains current formatting and calculations
- Handles edge cases (no months, current month not processed)

<<<<<<< HEAD
### US2: Expense List Section

**As a user**, I want to see my current month's expense items in a dedicated section so that I can
focus on individual transactions when needed.
=======
### US2: Expense List Section  

**As a user**, I want to see my current month's expense items in a dedicated section so that I can focus on individual transactions when needed.
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

**Acceptance Criteria:**

- Expense list is in its own visual section/card
- Maintains current table format and functionality
- Preserves action buttons (pay/unpay, view details)
- Shows both pending and paid items with current styling

### US3: Improved Dashboard Layout

<<<<<<< HEAD
**As a user**, I want a well-organized dashboard layout so that I can efficiently navigate between
summary and detailed views.
=======
**As a user**, I want a well-organized dashboard layout so that I can efficiently navigate between summary and detailed views.
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

**Acceptance Criteria:**

- Clear visual separation between sections
- Logical information flow (summary first, then details)
- Consistent spacing and styling
- Mobile-responsive design

## Technical Requirements

### Architecture

- Maintain current Django view structure (`expenses/views.py:dashboard`)
- Preserve existing context data and calculations
- Update template only (`expenses/templates/expenses/dashboard.html`)
- No database schema changes required

### UI/UX Requirements

- Split current single card into two distinct sections:
  1. **Summary Widget**: Monthly totals and counts
  2. **Expense List Section**: Detailed expense items table
- Maintain current color scheme and styling patterns
- Preserve responsive grid layouts (`grid-3-cols`, etc.)
- Keep existing CSS classes and styling approach

### Data Requirements

- No changes to view logic or data fetching
- Preserve all current context variables:
  - `current_month`, `pending_items`, `paid_items`
  - `total_pending`, `total_paid`, `total_month`
  - `current_date`, `has_any_months`

## Implementation Approach

### Phase 1: Template Restructure

1. Split current single `.card` into two sections
2. Create summary widget with current totals display
3. Create separate expense list section with current table
4. Maintain all existing conditional logic and edge case handling

### Phase 2: Widget Architecture Foundation

1. Consider extracting summary widget into reusable component structure
2. Prepare template structure for future widget additions
3. Document widget patterns for future development

## Technical Constraints

- **No breaking changes**: All existing functionality must be preserved
- **Template-only changes**: No modifications to views, models, or business logic
- **CSS compatibility**: Must work with existing styling and responsive design
- **Edge case handling**: Must handle all current scenarios (no months, unprocessed months)

## Risk Assessment

**Low Risk:**

- Template-only changes minimize impact
- Existing styling and components can be reused
- No data or business logic changes required

**Mitigation:**

- Thorough testing of all existing functionality
- Verify responsive design across screen sizes
- Test all edge cases and conditional displays

## Future Considerations

This rework establishes foundation for future enhancements:

- Additional dashboard widgets (recent transactions, spending trends, etc.)
- User-customizable dashboard layouts
- Dashboard personalization features
- Enhanced financial analytics widgets

## Dependencies

- No external dependencies
- Uses existing Django template system
- Relies on current CSS grid and styling framework

## Success Criteria

✅ **Definition of Done:**

- Monthly summary appears in dedicated widget/section
- Expense list appears in separate section
- All existing functionality works identically
- Responsive design maintained
- Code follows project standards
- No visual regressions introduced
