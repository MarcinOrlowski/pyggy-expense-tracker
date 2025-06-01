#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Run Django development server
echo "Starting Django development server..."
python manage.py runserver
