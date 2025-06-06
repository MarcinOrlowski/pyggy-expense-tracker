#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Compile SCSS files
echo "Compiling SCSS files..."
python compile_scss.py

# Collect static files (for other assets)
python manage.py collectstatic --noinput

# Run Django development server
echo "Starting Django development server..."
python manage.py runserver
