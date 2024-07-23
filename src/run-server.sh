#!/bin/bash

python3 manage.py migrate
python3 manage.py makemigrations
python manage.py migrate
#python3 manage.py collectstatic --no-input
#gunicorn library_project.wsgi:application --bind 0.0.0.0:8080
python3 manage.py runserver --insecure 0.0.0.0:8080