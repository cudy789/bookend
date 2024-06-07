#!/bin/bash

source ../.env

python3 manage.py migrate
python3 manage.py makemigrations
python manage.py collectstatic --no-input
gunicorn library_project.wsgi:application --bind "$ALLOWED_HOST":8080
