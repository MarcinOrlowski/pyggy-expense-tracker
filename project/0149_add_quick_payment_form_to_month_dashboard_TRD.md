# Add Quick Payment Form to Month Dashboard TRD

**Ticket**: [Add quick payment form to month dashboard](https://github.com/MarcinOrlowski/python-pyggy-expense-tracker/issues/149)
**PRD Reference**: 0149_add_quick_payment_form_to_month_dashboard_PRD.md

## Technical Approach

We'll implement a simplified form on the dashboard.html template that creates one-time expenses with
optional immediate payment. The form will use existing Django forms and models (Expense,
ExpenseItem, Payment) with a new QuickPaymentForm class. The form will post to a new dashboard view
method that handles expense creation and optional payment recording in a single transaction.
Integration will reuse existing expense creation logic from services.py and redirect back to
dashboard with flash messages.

## Data Model

No new database tables required. We'll use existing models:

```text
Expense (existing)
- budget: FK to current budget
- title: from form input  
- expense_type: hardcoded to 'one_time'
- amount: from form input
- payee: from form dropdown (optional)
- start_date: current date
- day_of_month: current day

ExpenseItem (auto-created)
- expense: FK to created expense
- month: current BudgetMonth
- due_date: current date
- amount: same as expense amount

Payment (conditionally created)
- expense_item: FK to created ExpenseItem  
- amount: same as expense amount
- payment_date: current datetime
- payment_method: null (user can edit later)
```

## API Design

```text
POST /dashboard/{budget_id}/quick-pay/
Request: {
    'title': 'Coffee',
    'payee': '5',  # optional payee ID
    'amount': '4.50',
    'mark_as_paid': 'on'  # checkbox value
}
Response: Redirect to dashboard with success message

Form validation:
- title: required, max 255 chars
- amount: required, decimal > 0.01
- payee: optional, must exist if provided
- mark_as_paid: boolean checkbox

Error handling: Form validation errors displayed on dashboard
```

## Security & Performance

- Authentication: Existing budget access control (user must own budget)
- Input validation: Use existing SanitizedDecimalField for amounts
- CSRF protection: Standard Django CSRF token in form
- Performance: Single page load with form embed, <200ms form processing
- Data integrity: Database transaction for expense + payment creation

## Technical Risks & Mitigations

1. **Risk**: Form submission errors could lose user input → **Mitigation**: Form errors redisplay with preserved values on dashboard
2. **Risk**: Concurrent month creation could cause ExpenseItem failures → **Mitigation**: Use get_or_create for BudgetMonth validation
3. **Risk**: Dashboard page complexity increases → **Mitigation**: Extract form to include template, minimal logic in view

## Implementation Plan

- Phase 1 (S): Create QuickPaymentForm in expenses/forms/ - 1 day
- Phase 2 (M): Add dashboard POST handler and expense creation logic - 2 days  
- Phase 3 (S): Update dashboard.html template with form integration - 1 day
- Phase 4 (S): Add URL routing and update dashboard context - 1 day

Dependencies: None (uses existing expense creation infrastructure)

## Monitoring & Rollback

- Feature flag: None needed (simple form addition)
- Key metrics: Quick payment form usage, error rates, time to completion
- Rollback: Remove form from template, disable POST route (template-only change)
