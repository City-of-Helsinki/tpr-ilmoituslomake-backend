#!/bin/sh

# run Django development server

# wait for PSQL server to start
sleep 20

# prepare init migration
python manage.py makemigrations users base
# migrate db, so we have the latest db schema
python manage.py migrate
# start development server on public ip interface, on port 8008
python manage.py runserver 0.0.0.0:8008
