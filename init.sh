#!/bin/bash

python manage.py migrate
python manage.py loaddata fixtures/initial_data.json

# ./manage.py createsuperuser
