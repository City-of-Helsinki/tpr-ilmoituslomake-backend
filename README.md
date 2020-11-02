# tpr-ilmoituslomake-backend

## About


## Getting started

* git clone <thisrepo>
* python3 -m venv venv
* source venv/bin/activate
* pip install -r requirements.txt


## Gettings started with docker

* docker-compose is required
* sudo mkdir pgdata
* docker-compose up -d


# Navigate to

```
/api/schema/create/
```

data

```
{
	"$id": "<url>",
	"$schema": "http://json-schema.org/draft-07/schema#",
	"description": "<description>",
	"type": "object",
	"properties": {
		"name": {"type": "string"},
		"street_address": {"type": "string"},
		"postal_address": {"type": "string"},
	},
	"required": ["name", "street_address", "postal_address"],
}
```