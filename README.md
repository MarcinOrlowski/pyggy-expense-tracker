# PyGGy - Python (Monthly) Expense Tracker

A Django-based expense tracking application designed to manage different types of expenses with monthly processing workflows. This proof-of-concept demonstrates core expense management functionality as a foundation for a comprehensive budget management system.

## Features

### Core Functionality
- **Three Expense Types**:
  - **Endless Recurring**: Monthly expenses without end date (utilities, subscriptions)
  - **Split Payments**: Fixed installments (loans, payment plans)
  - **One-time Payments**: Single payment expenses
- **Monthly Processing**: Sequential month creation with automatic expense generation
- **Payment Tracking**: Record actual payment dates and methods
- **Business Rules Enforcement**: Start date validation, automatic expense completion
- **Django Admin Interface**: Optimized for expense management

### Technical Highlights
- Built with Django 5.2 LTS
- SQLite database (PostgreSQL-ready)
- Responsive HTML5/CSS3 interface with SASS styling
- Function-based views for simplicity
- Comprehensive model validation

## Requirements

- Python 3.12 or higher
- Django 5.2.1
- Virtual environment (recommended `venv`)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/MarcinOrlowski/pyggy-expense-tracker.git
   cd pyggy-expense-tracker
   ```

2. **Create and activate virtual environment (see separate scripts in `bin/` folder for Fish, ZSh etc)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Load initial data**
   ```bash
   python manage.py loaddata fixtures/initial_data.json
   ```

6. **Create superuser for admin access**
   ```bash
   python manage.py createsuperuser
   ```

## Running the Application

Start the development server:
```bash
python manage.py runserver
```

Access the application:
- Main application: http://127.0.0.1:8000/
- Django Admin interface: http://127.0.0.1:8000/admin/

## Quick Start Scripts

The project includes convenience scripts:

- **init.sh**: Run migrations and load initial data
  ```bash
  chmod +x init.sh
  ./init.sh
  ```

- **run.sh**: Start the development server
  ```bash
  chmod +x run.sh
  ./run.sh
  ```

## Project Structure

```
expense_tracker/          # Django project configuration
├── expenses/            # Main Django app
│   ├── models.py       # Data models (Expense, ExpenseItem, Month, etc.)
│   ├── views.py        # View functions
│   ├── forms.py        # Django forms with validation
│   ├── services.py     # Business logic layer
│   └── templates/      # HTML templates
├── src/scss/           # SASS source files
│   ├── _variables.scss # Color palette and CSS variables
│   ├── _base.scss     # Base styles and typography
│   ├── _components.scss # UI components
│   └── main.scss      # Main SASS import file
├── fixtures/           # Initial data fixtures
└── project/           # Project documentation
    ├── PRD.md         # Product Requirements
    ├── TRD.md         # Technical Requirements
    └── *.md           # Additional documentation
```

## Usage Guide

### Creating Expenses

1. **Add Payment Methods**: Navigate to Payment Methods and add your preferred payment types
2. **Add Payees**: Create vendors/companies in the Payees section
3. **Create Expenses**: 
   - Choose expense type (Endless, Split, or One-time)
   - Set start date (must be current month or later)
   - For split payments, specify total installments
   - System automatically creates expense items for current month

### Monthly Processing

1. **View Current Month**: Dashboard shows all expenses for the current month
2. **Record Payments**: Mark expense items as paid with actual payment date
3. **Process Next Month**: Create next month to generate recurring expenses
4. **Month Constraints**:
   - Months must be created sequentially
   - Cannot delete months with paid expenses
   - Only the latest unpaid month can be deleted

### Business Rules

- Expenses cannot start before the current month
- Endless recurring expenses continue until manually closed
- Split payments automatically close after final installment
- One-time payments close after payment
- All dates default to current month for convenience

## Development

### SASS/CSS

The project uses SASS for styling with django-sass-processor for automatic compilation:
- Source files: `src/scss/` directory  
- Styles are automatically compiled when running the development server
- No manual compilation needed - Django handles it via `{% sass_src %}` template tag
- To modify styles, edit the `.scss` files and refresh your browser

### Management Commands

- `python manage.py setup_initial_data`: Load all initial fixtures
- `python manage.py seed_initial_month`: Create the initial month (required once)

### Testing

Run Django tests:
```bash
python manage.py test
```

### Database

The project uses SQLite by default but is designed to work with PostgreSQL. Database configuration is in `expense_tracker/settings.py`.

## Documentation

Comprehensive project documentation is available in the `project/` directory:
- **PRD.md**: Product Requirements Document
- **TRD.md**: Technical Requirements Document
- **architecture-spec.md**: System architecture details
- **frontend-guidelines.md**: Frontend development guidelines

## Future Enhancements

This PoC is designed to support future features:
- Multi-project support
- Budget management and tracking
- Advanced reporting and analytics
- Tags and categorization
- Receipt image storage
- Mobile application
- Bank statement import

## Contributing

This is a proof-of-concept project. For questions or contributions, please refer to the project documentation and follow Django best practices.

## License

[License information to be added]
