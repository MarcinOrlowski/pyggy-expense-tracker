# Change Log

## @dev

- [#0019] Added optional notes field to expense entity with unlimited database storage, form-level 1024 character validation, textarea input with character counter, and notes indicator in expense list
- [#0017] Enhanced dashboard with prominent month summary display using Tektur Google Font, redesigned as individual cards with consistent styling, and integrated calendar widget
- [#0014] Implemented application settings infrastructure with locale-aware currency formatting using babel library
- [#0013] Extracted CSS from templates to organized SASS files with django-sass-processor integration
- [#0004] Added calendar widget to dashboard with comprehensive payment due date visualization including color-coded indicators, weekend styling, and visual hierarchy for past/present/future days
- [#0008] Added Days column to dashboard expense items table showing days until due
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
