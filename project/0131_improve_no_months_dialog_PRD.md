# Improve No Months Dialog PRD

**Ticket**: [Improve no months dialog to include direct link to add month action](https://github.com/MarcinOrlowski/pyggy-expense-tracker/issues/131)

## Problem Statement

Users must manually navigate through menu paths ("Months → Add initial month") when no months exist
in their budget, creating unnecessary friction in the onboarding experience. New users see text
instructions instead of actionable buttons, leading to additional clicks and potential confusion.
This indirect approach delays users from completing the essential first step of expense tracking
setup.

## Solution Overview

Replace text-based navigation instructions with direct action buttons across all "no months" states
in the application. Users will see prominent "Add First Month" buttons that immediately take them to
the month creation process. This streamlined approach reduces cognitive load and click count while
maintaining clear messaging about the importance of creating an initial month.

## User Stories

1. As a new user setting up my budget, I want to click a direct "Add First Month" button, so that I
   can quickly start tracking expenses without navigating through menus
1. As a user viewing my empty dashboard, I want clear visual guidance with actionable buttons, so
   that I understand exactly what to do next
1. As a user in any "no months" state, I want consistent messaging and actions, so that the
   experience feels cohesive across the application

## Acceptance Criteria

- [ ] Dashboard "no months" section displays a prominent action button instead of navigation text
- [ ] Button text is clear and action-oriented (e.g., "Add First Month")
- [ ] Button styling is consistent with existing application design patterns
- [ ] All "no months" states across the application use consistent styling and messaging
- [ ] Clicking the button navigates directly to the month creation functionality
- [ ] Existing explanatory text about starting with first month is preserved for context

## Out of Scope

- Redesigning the month creation form itself
- Adding new month creation workflow steps
- Implementing JavaScript modals or popup dialogs
- Changing the underlying month creation logic
- Adding bulk month creation features

## Success Metrics

1. Reduce clicks from "no months" state to month creation by 50% (from 3+ clicks to 1 click)
2. Maintain clear user guidance with contextual messaging
3. Achieve consistent UX across all "no months" states within the application
