# tpr-ilmoituslomake-backend

## About

Notifification form app (Ilmoituslomakesovellus) for the city of Helsinki. People will be able to notifications about places in Helsinki area (restaurants, travel, etc.) and after moderation process these places will be transfered to Toimipisterekisteri. This is the backend for the app.

## Getting started

* git clone <thisrepo>
* python3 -m venv venv
* source venv/bin/activate
* pip install -r requirements.txt


## Gettings started with docker

* docker-compose is required
* Build: rebuild_dev.sh
* Run: run_dev.sh
* You need the UI: https://github.com/City-of-Helsinki/tpr-ilmoituslomake-ui/ and run it in development mode

##

# API Endpoints

## Admin

* /admin/, admin panel which will only available in dev

## Authentication

* /api/user/, GET current user info


# Notification Form App

The current API is unstable. It will go towards CRUD model once the functional requirements have been specified.

* /api/schema/get/<int:id>/, GET json schema
* /api/schema/create/, POST create json schema
* /api/notification/create/, POST create notification
* /api/notification/get/<int:id>/, GET notification
* /api/notification/list/, GET notifications
* /api/ontologywords/, GET ontology words