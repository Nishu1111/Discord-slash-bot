#!/usr/bin/env bash
# Run this script using cmd

python manage.py migrate

#for deployment
gunicorn config.wsgi:application