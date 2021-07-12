from django.db import models
import django
from django.core.validators import BaseValidator
import jsonschema
from django.contrib.postgres.fields import JSONField

TRANSLATION_SCHEMA = {
    "$id": "<url>",
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Translation Schema",
    "description": "<description>",
    "type": "object",
    "properties": {
        "language": {
            "type": "string"
        },
        "organization": {
            "type": "object",
            "additionalProperties": True
        },
        "name": {
          "type": "object",
          "properties": {
            "lang": {
                "type": "string"
            }
          },
          "required": ["lang"]
        },
        "location": {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "items": {
                "type": "number"
            }
        },
        "description": {
            "type": "object",
            "properties": {
                "short": {
                    "type": "object",
                    "properties": {
                        "lang": {
                            "type": "string",
                            "maxLength": 150
                        }
                    },
                    "required": ["lang"]
                },
                "long": {
                    "type": "object",
                    "properties": {
                        "lang": {
                            "anyOf": [
                                {
                                    "type": "string",
                                    "minLength": 120,
                                    "maxLength": 4000
                                },
                                {
                                    "type": "string",
                                    "maxLength": 0
                                }
                            ]
                        }
                    },
                    "required": ["lang"]
                }
            },
            "required": ["short", "long"]
        },
        "address": {
            "type": "object",
            "properties": {
                "fi": {
                    "type": "object",
                    "properties": {
                        "street": {
                            "type": "string"
                        },
                        "postal_code": {
                            "anyOf": [
                                {
                                    "type": "string",
                                    "pattern": "^[0-9][0-9][0-9][0-9][0-9]$"
                                },
                                {
                                    "type": "string",
                                    "maxLength": 0
                                }
                            ]
                        },
                        "post_office": {
                            "type": "string"
                        },
                        "neighborhood_id": {
                            "type": "string"
                        },
                        "neighborhood": {
                            "type": "string"
                        }
                    },
                    "required": ["street", "postal_code", "post_office", "neighborhood_id", "neighborhood"]
                },
                "sv": {
                    "type": "object",
                    "properties": {
                        "street": {
                            "type": "string"
                        },
                        "postal_code": {
                            "anyOf": [
                                {
                                    "type": "string",
                                    "pattern": "^[0-9][0-9][0-9][0-9][0-9]$"
                                },
                                {
                                    "type": "string",
                                    "maxLength": 0
                                }
                            ]
                        },
                        "post_office": {
                            "type": "string"
                        },
                        "neighborhood_id": {
                            "type": "string"
                        },
                        "neighborhood": {
                            "type": "string"
                        }
                    },
                    "required": ["street", "postal_code", "post_office", "neighborhood_id", "neighborhood"]
                }
            },
            "required": ["fi", "sv"]
        },
        "phone": {
            "anyOf": [
                {
                    "type": "string",
                    "pattern": "^\\+?[0-9- ]+$"
                },
                {
                    "type": "string",
                    "maxLength": 0
                }
            ]
        },
        "email": {
            "anyOf": [
                {
                    "type": "string",
                    "format": "email"
                },
                {
                    "type": "string",
                    "maxLength": 0
                }
            ]
        },
        "website": {
            "type": "object",
            "properties": {
                "lang": {
                    "anyOf": [
                        {
                            "type": "string",
                            "format": "uri"
                        },
                        {
                            "type": "string",
                            "maxLength": 0
                        }
                    ]
                }
            },
            "required": ["lang"]
        },
        "images": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "index": {
                        "type": "number"
                    },
                    "uuid": {
                        "type": "string"
                    },
                    "source_type": {
                        "type": "string"
                    },
                    "url": {
                        "type": "string"
                    },
                    "permission": {
                        "type": "string"
                    },
                    "source": {
                        "type": "string"
                    },
                    "alt_text": {
                        "type": "object",
                        "properties": {
                            "lang": {
                                "type": "string",
                                "maxLength": 125
                            }
                        },
                        "required": ["lang"]
                    }
                },
                "required": ["index", "uuid", "source_type", "url", "permission", "source", "alt_text"]
            }
        },
        "opening_times": {
            "type": "object",
            "additionalProperties": True
        },
        "ontology_ids": {
            "type": "array",
            "items": {
                "type": "number"
            }
        },
        "matko_ids": {
            "type": "array",
            "items": {
                "type": "number"
            }
        },
        "extra_keywords": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "comments": {
            "type": "string"
        },
        "notifier": {
            "type": "object",
            "properties": {
                "notifier_type": {
                    "type": "string"
                },
                "full_name": {
                    "type": "string"
                },
                "email": {
                    "type": "string"
                },
                "phone": {
                    "type": "string"
                }
            },
            "required": ["notifier_type", "full_name", "email", "phone"]
        }
    },
    "required": [
        "language",
        "organization",
        "name",
        "location",
        "description",
        "address",
        "phone",
        "email",
        "website",
        "images",
        "opening_times",
        "ontology_ids",
        "matko_ids",
        "extra_keywords",
        "comments",
        "notifier"
    ]
}

class JSONSchemaValidator(BaseValidator):
    def compare(self, value, schema):
        try:
            jsonschema.validate(value, schema)
        except jsonschema.exceptions.ValidationError:
            raise django.core.exceptions.ValidationError(
                '%(value)s failed JSON schema check', params={'value': value}
            )



class TranslationTodo(models.Model):
    data = JSONField(
        default=dict,
        validators=[JSONSchemaValidator(limit_value=TRANSLATION_SCHEMA)]
    )
    