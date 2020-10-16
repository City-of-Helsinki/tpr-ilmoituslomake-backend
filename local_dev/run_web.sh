#!/bin/sh

# run Django development server

# wait for PSQL server to start
sleep 10

# prepare init migration
su -m ilmoituslomake -c "python manage.py makemigrations ilmoituslomake"
# migrate db, so we have the latest db schema
su -m ilmoituslomake -c "python manage.py migrate"
# start development server on public ip interface, on port 8008
su -m ilmoituslomake -c "python manage.py runserver 0.0.0.0:8008"
