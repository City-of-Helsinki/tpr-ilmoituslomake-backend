# tpr-ilmoituslomake-backend

## About

Notifification form app (Ilmoituslomakesovellus) for the city of Helsinki. People will be able to post notifications about places in Helsinki area (restaurants, travel, etc.) and after moderation process these places will be transfered to Toimipisterekisteri. This is the backend for the app.

## Tech stack

Backend is based on Django 5.2 LTS and Python 3.12.

The October 2026 dependency patch requires Python 3.12 and a database migration
for the nullable `users.User.last_api_use` field inherited from django-helusers.
See [deprecations.txt](deprecations.txt) for audit results, deferred social-auth
alerts, and deployment checks. The existing GET-based login flow is unchanged.

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

For a dependency-only rebuild that preserves the local database, use:

```sh
docker-compose build tpr-ilmoituslomake
```

Do not use `rebuild_dev.sh` just to update dependencies: that existing script
deletes `pgdata`. No database reset is needed for this patch.

With the development database running and `local_dev/.env` configured, review
the migration plan and run the checks before starting the updated backend:

```sh
docker-compose run --rm --no-deps tpr-ilmoituslomake python manage.py check
docker-compose run --rm --no-deps tpr-ilmoituslomake python manage.py test base users moderation
docker-compose run --rm --no-deps tpr-ilmoituslomake python manage.py migrate --plan
```

After reviewing the plan and backing up the database, apply the migrations:

```sh
docker-compose run --rm --no-deps tpr-ilmoituslomake python manage.py migrate
```

Non-Docker deployments need a new Python 3.12 virtual environment; installing
these requirements into the old Python 3.10 environment will not work. Switch
the application's launcher to the new environment only after checking it and
applying the required migrations.

# API Endpoints

## Admin

* /admin/, admin panel which will only available in dev

## Authentication

* /api/user/, GET current user info

# Moderation App
* /api/moderation/todos/find/?category=moderation_task&search=lol, GET category=moderation_task or change_request or moderator_edit
* /api/moderation/todos/, GET show all moderation items (ones with moderator are shown last)
* /api/moderation/todos/<int:id>/, GET or PUT data
* /api/moderation/todos/my/, GET show all current user's moderation items
* /api/moderation/todos/recent/, GET show all recent unassigned moderation items
* /api/moderation/assign/<int:id>/, PUT assign moderation item to current user
* /api/moderation/unassign/<int:id>/, PUT unassign moderation
* /api/moderation/reject/<int:id>/, DELETE reject moderation task
* /api/moderation/approve/<int:id>/, POST approve moderation task
* /api/moderation/search/?q=encodeURIComponent(JSON.stringify(search_object)) GET

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
