# Change Log

## @dev

- [#0007] Implemented reusable template components for dashboard and month views
- [#0001] Replaced text navigation links with icon-based action buttons
- Added sequential month creation (only next month after most recent)
- Added user-selectable initial month (no preset default)
- Added month deletion restrictions (only most recent, no paid expenses)
- Added dynamic button text showing specific next month
- Added management command for initial data setup
- Added start date validation (cannot be earlier than current month)
- Added immediate expense item creation for current month expenses
- Added future expense support (processed when month arrives)
- Added smart form defaults (current month's first day)
- Added optional `payment_id` field for transaction references
- Added payment reference ID to payment forms
- Removed payment method column from all table views
- Added paid item styling (dimmed + strikethrough)
- Added right alignment for amount and action columns
- Removed redundant status columns from all tables
- Removed Quick Actions section from dashboard
- Removed "Process Current Month" button from dashboard
- Changed payment date format to date-only (`YYYY-MM-DD`)
- Added `ExpenseItem.payment_id` field migration
- Fixed button styling with proper CSS classes (no inline styles)
- Enhanced model validation methods
- Made expense payee field optional
