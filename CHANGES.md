![PyGGy Logo](docs/img/logo.png)

# PyGGy Changelog

---

## v1.2 (2025-07-03)

- [#0187] Replaced hardcoded application version with centralized configuration file approach, enabling easy version updates without code changes
- [#0185] Fixed Python code formatting issues identified by flake8 linter, adding missing docstrings, removing unused imports and variables, correcting whitespace, and improving code quality
- [#0179] Fixed incorrect calculations in month details page summary panel showing proper total, paid, and pending amounts
- [#0181] Created universal development helper script (dev.sh) unifying all development tasks with auto-detection of containerized vs local workflows
- [#0169] Enhanced amount display for paid expense items in dashboard to show full due amount with strikethrough formatting for better historical context
- [#0175] Improved budget currency editing with preselected currency dropdown (PLN, EUR, USD) replacing case-sensitive text input to prevent validation errors
- [#0176] Fixed budget date validation preventing form submission when start date unchanged during editing
- [#0173] Add visual screen distinctions to improve user navigation with section-specific color coding, header accents, card gradients, and subtle background icon patterns
- [#0171] Simplified footer version display by removing debug progress text and showing only current version
- [#0167] Fixed version-to-milestone mapping to strip patch version and use GitHub-standard format (1.2.3 → 1.2 for milestone filtering)
- [#0159] Implemented expense item deletion functionality allowing removal of unpaid one-time expense items from current month with automatic parent expense cleanup
- [#0161] Implemented dynamic GitHub issues filtering by milestone with version progress display
- [#0163] Fixed mypy warning about undefined lgz74f240 variable by escaping dollar signs in Docker Compose SECRET_KEY
- [#0160] Implemented centralized version management system with VersionService class, enabling consistent version display and future automation options

## v1.1 (2025-06-08)

- [#0113] Enforced minimum 2 total installments validation for split payments to ensure split payment concept integrity
- [#0149] Added quick expense form to dashboard for streamlined one-time expense creation with optional immediate payment marking
- [#0151] Refactored Month entity to BudgetMonth for better semantic clarity and improved code self-documentation
- [#0100] Reworked payment system to support multiple payments per expense item, enabling partial payment tracking and preventing overpayments
- [#0005] Enhanced dashboard to display past months with pending expenses in main expense list with month separators for better visibility
- [#0147] Group expense list entries by year-month for better date validation visibility and improved chronological organization
- [#0142] Enhanced dashboard title with relative time indicator for past months (e.g., "Dashboard (3 months ago)")
- [#0140] Made table rows clickable for view actions, removed view icons for cleaner UI
- [#0051] Added close buttons to flash messages with Font Awesome icons and smooth animation effects
- [#0134] Unified edit icons across the application to use fa-pencil consistently
- [#0124] Improved payment confirmation redirect behavior to navigate to budget dashboard after payment operations
- [#0131] Replace text navigation instructions with direct "Add First Month" buttons
- Fixed CSS loading issue after HTTP redirects by switching from django-sass-processor runtime compilation to pre-compiled CSS files

## v1.0 (2025-06-06)

- [#0112] Set default values for new expense creation (expense type defaults to "one-time", start date defaults to current date)
- [#0120] Added comprehensive type hints to Python codebase for improved code quality and developer experience
- [#0118] Changed expense item edit behavior to redirect to budget dashboard after save or cancel
- [#0114] Added in-app help system that renders markdown documentation files with README.md priority, user-friendly error handling, and responsive design
- [#0062] Added separate colors for expense type icons to improve visual differentiation between expense types
- [#0102] Split application files into one-file-one-class model for improved code organization and maintainability
- [#0105] Allow negative initial values for budget creation and editing to support deficit tracking
- [#0104] Added balance column to month list view showing total amount for each month
- [#0096] Fixed calendar weekday highlighting to only appear when viewing current month
- [#0099] Added payment methods management UI with full CRUD operations
- [#0095] Fixed budget dashboard edit action to redirect to expense item editing instead of expense editing
- [#0095] Enhanced expense item editing to allow modification of both amount and due date (restricted to same month)
- [#0092] Added text labels next to icons in main toolbar action buttons for improved user experience and accessibility
- [#0087] Exposed explicit due date functionality with comprehensive expense model restructuring, flexible one-time expense scheduling, and enhanced due date calculation logic
- [#0084] Added date editing restrictions for expenses to prevent historical date modifications and maintain financial data integrity
- [#0072] Refactored payees list layout by removing created column and right-aligning expenses column for better readability
- [#0073] Enhanced amount input sanitization with international format support (comma/dot decimal separators, currency symbols)
- [#0075] Bind expenses directly to budgets to fix invisible expenses bug
- [#0063] Added partial split payment tracking with configurable start installment number
- [#0069] Added linters and Github Actions to guard the code.
- [#0067] Added edit expense button next to each expense in dashboard (when editable)
- [#0050] Added conditional expense editing with restrictions based on payment status and expense type
- [#0064] Refactored split payments to use monthly installment amount instead of total amount calculation
- [#0058] Disabled budget start date field in edit form when months exist
- [#0016] Renamed Django configuration directory from expense_tracker to pyggy to match project name
- [#0056] Fixed failing unit tests by updating method names and function signatures to match current codebase
- [#0056] Added comprehensive model method tests covering string representations, properties, and validation methods
- [#0056] Added comprehensive template tag tests for currency formatting filters and tags
- [#0012] Standardized action button styling and icons in table rows with consistent default styling and clear action icons
- [#0052] Reworked footer layout with split design for better information organization
- [#0046] Hide delete icons for items that cannot be deleted based on business rules
- [#0026] Added Docker configuration with compose.yml for development environment and Dockerfile for production builds
- [#0025] Added Font Awesome icons for expense types with hardcoded mapping and accessibility support
- [#0041] Added Budget management UI (CRUD operations)
- [#0029] Introduced Budget entity with Month relationship and expense tracking
- [#0036] Improved worktree.sh script to check if worktree already exists and prevent creating worktrees from within worktrees
- [#0021] Added recurring with end date expense type allowing automatic expense item generation through specified end date month
- [#0024] Reworked expense filter controls into single-line layout with stretching dropdowns and icon-only clear button
- [#0022] Fixed Django static files configuration copying excessive files to static files
- [#0019] Added optional notes field to expense entity and notes indicator in expense list
- [#0017] Enhanced dashboard with prominent month summary display, redesigned as individual cards, and integrated calendar widget
- [#0014] Implemented application settings infrastructure with locale-aware currency formatting using babel library
- [#0013] Extracted CSS from templates to organized SASS files with django-sass-processor integration
- [#0004] Added calendar widget to dashboard with comprehensive payment due date visualization
- [#0008] Added Days column to dashboard expense items table showing days until due
- [#0007] Implemented reusable template components for dashboard and month views
- [#0001] Replaced text navigation links with icon-based action buttons
- Fixed test failures in ExpenseItemEditForm validation and view context to ensure consistent form behavior
- Added sequential month creation (only next month after most recent)
- Added user-selectable initial month (no preset default)
- Added month deletion restrictions (only most recent, no paid expenses)
- Added dynamic button text showing specific next month
- Added management command for initial data setup
- Added start date validation (cannot be earlier than current month)
- Added immediate expense item creation for current month expenses
- Added future expense support (processed when month arrives)
- Added smart form defaults (current month's first day)
- Added payment reference ID to payment forms
- Added paid item styling (dimmed + strikethrough)
- Added right alignment for amount and action columns
