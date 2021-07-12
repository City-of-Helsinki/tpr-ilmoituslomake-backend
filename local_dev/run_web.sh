#!/bin/sh

# run Django development server

# wait for PSQL server to start
sleep 20

# prepare init migration
python manage.py makemigrations users base moderation notification_form api
# migrate db, so we have the latest db schema
python manage.py migrate
# load ontologies
python manage.py import_ontology_words
# load matko words
python manage.py import_matko_words
# load mockdata
python manage.py import_mock_data
# start development server on public ip interface, on port 8008
python manage.py runserver 0.0.0.0:8008
