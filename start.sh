#!/bin/bash -x

python manage.py migrate --no-input &&
gunicorn pdx_auth_gateway.wsgi:application --bind 0.0.0.0:$PORT