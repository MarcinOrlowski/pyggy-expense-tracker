# PRD: Explicit Due Date Functionality (#0087)

## Overview

Enhance the expense management system to expose explicit due date functionality, allowing users to better manage when expenses are due regardless of when they were created or scheduled to start.

## Problem Statement

Currently, the expense system ties due dates implicitly to start dates and month processing logic. Users need more flexibility to:

- Set due dates independent of expense creation dates
- Handle expenses where the due date occurs before the start date
- Better manage expense scheduling with explicit due date visibility

## Goals

1. **Expose Due Date Field**: Make due date functionality visible and manageable in the UI
2. **Flexible Scheduling**: Allow expenses to be due in different months than their start dates
3. **Improved UX**: Provide clear due date information in forms and displays
4. **Maintain Data Integrity**: Ensure existing expense data remains valid after changes

## Success Criteria

1. ✅ Users can see and edit due dates for expense items
2. ✅ Due date calculations work correctly for all expense types
3. ✅ One-time expenses can be scheduled flexibly based on due date
4. ✅ All existing functionality continues to work without regression
5. ✅ Database migrations preserve existing data

## User Stories

### Story 1: Explicit Due Date Management

**As a** user managing expenses  
**I want to** see and control when expenses are due  
**So that** I can better plan my payments regardless of when I created the expense

### Story 2: Flexible One-Time Expense Scheduling

**As a** user creating one-time expenses  
**I want to** set due dates that may differ from the expense start date  
**So that** I can handle scenarios like retroactive expense entry or future planning

### Story 3: Due Date Visibility

**As a** user viewing expenses  
**I want to** clearly see when each expense item is due  
**So that** I can prioritize my payments effectively

## Business Requirements

### Functional Requirements

1. **Due Date Calculation**: System calculates due dates using day_of_month for target months
2. **Flexible Processing**: One-time expenses can be created in any processed month if no item exists
3. **Form Integration**: Expense forms show due date information and controls
4. **Data Migration**: Existing expense data is preserved during model changes

### Non-Functional Requirements

1. **Performance**: Due date calculations must be efficient
2. **Data Integrity**: No data loss during field restructuring
3. **Backward Compatibility**: Existing API and form behavior maintained where possible
4. **Test Coverage**: All functionality covered by automated tests

## Technical Scope

### In Scope

- ExpenseItem due_date field exposure and management
- Expense model field restructuring (started_at → start_date, etc.)
- Due date calculation logic for different expense types
- Form and template updates for due date functionality
- Database migrations for model changes
- Test updates for new behavior

### Out of Scope

- Complete UI redesign
- New expense types
- Advanced scheduling features beyond due date
- Integration with external calendar systems

## Dependencies

- Django ORM for model changes
- Existing expense and month processing logic
- Database migration system
- Current form and template structure

## Risks and Mitigation

1. **Data Loss Risk**: Mitigated by comprehensive migration scripts
2. **Breaking Changes**: Mitigated by maintaining field compatibility where possible
3. **Test Failures**: Mitigated by updating all affected tests
4. **User Confusion**: Mitigated by maintaining familiar UI patterns

## Timeline

- **Analysis & Planning**: 1 day
- **Implementation**: 2-3 days  
- **Testing & Documentation**: 1 day
- **Total**: 4-5 days

## Acceptance Criteria

1. All tests pass (143+ tests)
2. Due date functionality works for all expense types
3. Database migrations complete successfully
4. Forms show appropriate due date information
5. No regression in existing functionality
6. Code follows project conventions and is well-documented

---
**Created**: 2025-01-04  
**Status**: Implemented  
**Ticket**: [#0087](https://github.com/project/issues/87)
