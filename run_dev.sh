#!/bin/bash
# Development server startup script

# Activate virtual environment
source venv/bin/activate

# Compile SCSS
echo "Compiling SCSS..."
python compile_scss.py

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Start development server
echo "Starting development server..."
python manage.py runserver 0.0.0.0:8000
