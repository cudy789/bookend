#!/bin/bash

python3 manage.py migrate
python3 manage.py makemigrations
#python3 manage.py runserver 0.0.0.0:8080
python manage.py collectstatic --no-input
gunicorn library_project.wsgi:application --bind 0.0.0.0:8080
#python3 manage.py runserver_plus 0.0.0.0:443 --cert-file cert.pem --key-file privkey.pem
