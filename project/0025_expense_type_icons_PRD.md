# Expense Type Icons PRD v1.0

**Last Updated**: 2025-06-02
**Ticket**: [Add icons for expense types](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/25)

## Problem Statement

Users currently see only text labels for expense types in the active expenses display, making it harder to quickly identify and categorize different expense types at a glance. The lack of visual differentiation reduces the user experience and scanning efficiency when managing multiple expenses across different categories.

## Solution Overview

Add hardcoded Font Awesome icons to each expense type that display alongside or instead of text labels in expense listings. Each of the four expense types (Endless Recurring, Split Payment, One Time, Recurring with End Date) will have a distinct, intuitive icon with fixed mapping in the code. Success means users can identify expense types instantly through visual cues rather than reading text labels.

## User Stories

1. As a user viewing my expense list, I want to see distinct icons for each expense type, so that I can quickly identify different categories of expenses without reading text labels
2. As a user managing multiple expenses, I want visual differentiation between recurring and one-time payments, so that I can better organize my financial planning
3. As a user with accessibility needs, I want icon tooltips with expense type names, so that I understand the meaning of each visual indicator

## Acceptance Criteria

- [ ] Each of the 4 expense types displays a unique Font Awesome icon in expense listings with hardcoded mapping
- [ ] Icons appear in the main expense list view replacing or alongside text labels
- [ ] Icons appear in the expense detail view
- [ ] Icons have proper accessibility attributes (aria-labels or tooltips) with expense type names
- [ ] Icons are visually consistent with existing UI styling and Font Awesome integration
- [ ] Icons are intuitive and clearly represent their respective expense types

## Out of Scope

- Dynamic icon configuration or admin interface for changing icons
- Custom icon uploads or non-Font Awesome icons
- Animation or interactive icon effects
- Icons in expense creation/edit forms (form functionality unchanged)
- Database schema changes (icons stored as hardcoded mapping in code)

## Success Metrics

1. Icons display correctly for all expense types in expense listings
2. Visual consistency maintained with existing UI components
3. Accessibility standards met with proper aria-labels for screen readers
