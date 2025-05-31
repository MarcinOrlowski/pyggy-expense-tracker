#!/bin/bash

python migrate
python manage.py loaddata fixtures/initial_data.json

# ./manage.py createsuperuser
