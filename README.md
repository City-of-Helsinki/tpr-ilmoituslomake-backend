# tpr-ilmoituslomake-backend

## About

Notifification form app (Ilmoituslomakesovellus) for the city of Helsinki. People will be able to post notifications about places in Helsinki area (restaurants, travel, etc.) and after moderation process these places will be transfered to Toimipisterekisteri. This is the backend for the app.

## Tech stack

Backend is based on Django 2.2 LTS and Python 3.7.

# Development

## Getting started

* git clone <thisrepo>
* python3 -m venv venv
* source venv/bin/activate
* pip install -r requirements.txt
* python manage.py runserver 0.0.0.0:8008


## Getting started with Docker

* Docker & docker-compose is required
* Build: rebuild_dev.sh
* Run: run_dev.sh
* You need the UI: https://github.com/City-of-Helsinki/tpr-ilmoituslomake-ui/ and run it in development mode

# API Endpoints

## Admin

* /admin/, admin panel which will only available in dev

## Authentication

* /api/user/, GET current user info

# Moderation App
* /api/moderation/todos/find/?category=moderation_task&search=lol, GET category=moderation_task or change_request
* /api/moderation/todos/, GET show all moderation items (ones with moderator are shown last)
* /api/moderation/todos/<int:id>/, GET or PUT data
* /api/moderation/todos/my/, GET show all current user's moderation items
* /api/moderation/todos/recent/, GET show all recent unassigned moderation items
* /api/moderation/assign/<int:id>/, PUT assign moderation item to current user
* /api/moderation/unassign/<int:id>/, PUT unassign moderation
* /api/moderation/reject/<int:id>/, DELETE reject moderation task
* /api/moderation/approve/<int:id>/, POST approve moderation task
* /api/moderation/search/?q=encodeURIComponent(JSON.stringify(search_object))

search_object, all keys are optional and leave those out you dont want to use or defaults
```
{
    "search_name__contains": "",
    "search_address__contains": "",
    "data__ontology_ids__contains": [],
    "search_comments__contains": "",
    "published": True,
    "search_neighborhood": "",
    "lang": "fi"
}
```


# Notification Form App

The current API is unstable. It will go towards CRUD model once the functional requirements have been specified.

* /api/schema/get/<int:id>/, GET json schema
* /api/schema/create/, POST create json schema
* /api/notification/create/, POST create notification
* /api/notification/get/<int:id>/, GET notification
* /api/notification/list/, GET notifications
* /api/ontologywords/, GET ontology words