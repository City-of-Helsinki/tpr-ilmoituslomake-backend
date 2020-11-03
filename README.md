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

##

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
		"postal_address": {"type": "string"}
	},
	"required": ["name", "street_address", "postal_address"]
	{
  "organization": "object",
  "name": {
    "fi": "string",
    "sv": "string",
    "en": "string"
  },
  "description": {
    "short": {
      "fi": "string",
      "sv": "string",
      "en": "string"
    },
    "long": {
      "fi": "string",
      "sv": "string",
      "en": "string"
    }
  },
  "district": "object",
  "address": {
    "fi": {
      "street": "string",
      "postal_code": "string",
      "post_office": "string"
    },
    "sv": {
      "street": "string",
      "postal_code": "string",
      "post_office": "string"
    }
  },
  "phone": "string",
  "email": "string",
  "website": {
      "fi" : "string",
      "sv": "string",
      "en": "string"
  },
  "images": "object",
  "opening_times": "object",
  "price": {
    "fi": "object",
    "sv": "object",
    "en": "object"
  },
  "ontology_ids": "array"
}
}
```

### Example

Notification example

```
location: {"type":"Point","coordinates":[125.6,10.1]}
data: {"name":"Piippolan talo","street_address": "Tiekatu 123","postal_address":"Tiekatu 123"}
```