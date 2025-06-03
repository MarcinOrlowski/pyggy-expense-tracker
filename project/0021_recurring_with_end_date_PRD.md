# Recurring with End Date Expense Type PRD v1.0

**Last Updated**: January 6, 2025  
**Author**: Claude  
**Status**: Approved

## Problem Statement

<<<<<<< HEAD
Users need to track recurring expenses that have a known end date (like fixed-term subscriptions or
rental agreements). Currently, they must either use endless recurring (and remember to close
manually) or calculate installments for split payments, which is error-prone and inconvenient.

## Solution Overview

Add a new expense type "Recurring with End Date" that automatically creates monthly expense items
from a start date through the month of the end date. Since PyGGy operates on monthly granularity,
the expense will generate items for all months up to and including the month containing the end
date. This provides the convenience of recurring expenses with the certainty of split payments.

## User Stories

1. As a user, I want to create recurring expenses with an end date, so that I can track fixed-term
   commitments without manual calculations
2. As a user, I want the system to automatically stop creating expense items after the end date
   month, so that I don't have to remember to close expenses manually
3. As a user, I want to see how many payments will be made, so that I can verify the expense setup
   is correct
=======
Users need to track recurring expenses that have a known end date (like fixed-term subscriptions or rental agreements). Currently, they must either use endless recurring (and remember to close manually) or calculate installments for split payments, which is error-prone and inconvenient.

## Solution Overview

Add a new expense type "Recurring with End Date" that automatically creates monthly expense items from a start date through the month of the end date. Since PyGGy operates on monthly granularity, the expense will generate items for all months up to and including the month containing the end date. This provides the convenience of recurring expenses with the certainty of split payments.

## User Stories

1. As a user, I want to create recurring expenses with an end date, so that I can track fixed-term commitments without manual calculations
2. As a user, I want the system to automatically stop creating expense items after the end date month, so that I don't have to remember to close expenses manually
3. As a user, I want to see how many payments will be made, so that I can verify the expense setup is correct
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629

## Acceptance Criteria

- [ ] User can select "Recurring with End Date" as an expense type
- [ ] End date field appears when this type is selected
- [ ] System calculates and displays total number of payments before saving (inclusive of end date month)
- [ ] Expense items are created monthly through the month containing the end date
- [ ] The month containing the end date receives a full payment (no proration)
- [ ] No expense items are created for months after the end date month
- [ ] Expense automatically closes after the end date month
- [ ] End date must be in same month as start date or later validation

## Out of Scope

- Modifying payment frequency (only monthly supported)
- Changing end date after expense creation
- Converting existing expenses to this new type
- Prorating partial months
- Custom payment schedules
- Day-specific end date behavior (end date day is only for record keeping)

## Success Metrics

1. Zero reported issues with incorrect payment calculations

---

<<<<<<< HEAD
**Key behavior clarification**: If end date is May 20th, 2025, the May 2025 payment will be
generated as the final payment. The specific day (20th) is stored for reference but doesn't affect
payment generation.
=======
**Key behavior clarification**: If end date is May 20th, 2025, the May 2025 payment will be generated as the final payment. The specific day (20th) is stored for reference but doesn't affect payment generation.
>>>>>>> 5e8c4ef357def9f66782b45b0ad8d57943146629
