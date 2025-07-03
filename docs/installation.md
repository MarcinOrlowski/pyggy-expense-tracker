# General information

## Technical Highlights

- Built with Django 5.2 LTS
- SQLite database (PostgreSQL-ready)
- Responsive HTML5/CSS3 interface with SASS styling
- Function-based views for simplicity
- Comprehensive model validation

## Requirements

- Docker (for containerized deployment (**recommended**))

or

- Python 3.12 or higher
- Django 5.2.1
- Virtual environment (built-in `venv` recommended)

## Installation

### Using Docker (Recommended)

1. **Clone the repository**

   ```bash
   git clone https://github.com/MarcinOrlowski/pyggy-expense-tracker.git
   cd pyggy-expense-tracker
   ```

2. **Start the application**

   ```bash
   docker compose up
   ```

3. **[Optional] Create superuser (in a new terminal)**

   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

See [docker.md](docker.md) for detailed Docker usage, including building and publishing images.

### Manual Installation

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

6. **(Optional) Create superuser for admin access**

   ```bash
   python manage.py createsuperuser
   ```

## Running the Application

Start the development server:

```bash
python manage.py runserver
```

Access the application:

- Main application: <http://127.0.0.1:8000/>
- Django Admin interface: <http://127.0.0.1:8000/admin/> (but you do not need it really)

## Quick Start Scripts

The project includes convenience scripts:

- **init.sh**: Run migrations and load initial data

  ```bash
  ./init.sh
  ```

- **run.sh**: Start the development server

  ```bash
  ./run.sh
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

- `./manage.py setup_initial_data`: Load all initial fixtures
- `./manage.py seed_initial_month`: Create the initial month (required once)

### Testing

Run Django tests:

```bash
./manage.py test
```
