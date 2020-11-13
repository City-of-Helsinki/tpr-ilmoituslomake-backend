import requests
from itertools import islice

from jsonschema import validate

from django.core.management.base import BaseCommand, CommandError
from base.models import OntologyWord


class Command(BaseCommand):
    help = "Imports ontology words from Helsinki API"

    # def add_arguments(self, parser):
    #    parser.add_argument('poll_ids', nargs='+', type=int)

    def transform_data(self, data):
        return {
            "id": data["id"],
            "ontologyword": {
                "fi": data["ontologyword_fi"],
                "sv": data["ontologyword_sv"],
                "en": data["ontologyword_en"],
            },
            "can_add_schoolyear": data["can_add_schoolyear"],
            "can_add_clarification": data["can_add_clarification"],
        }

    def handle(self, *args, **options):

        # Delete existing words
        # Import new ones!

        ontology_load_schema = {
            "$id": "<url>",
            "$schema": "http://json-schema.org/draft-07/schema#",
            "description": "<description>",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "number"},
                    "ontologyword_fi": {"type": "string"},
                    "ontologyword_sv": {"type": "string"},
                    "ontologyword_en": {"type": "string"},
                    "can_add_schoolyear": {"type": "boolean"},
                    "can_add_clarification": {"type": "boolean"},
                },
                "required": [
                    "id",
                    "ontologyword_fi",
                    "ontologyword_sv",
                    "ontologyword_en",
                    "can_add_schoolyear",
                    "can_add_clarification",
                ],
            },
        }
        ontology_save_schema = {
            "$id": "<url>",
            "$schema": "http://json-schema.org/draft-07/schema#",
            "description": "<description>",
            "type": "object",
            "properties": {
                "id": {"type": "number"},
                "ontologyword": {
                    "type": "object",
                    "properties": {
                        "fi": {"type": "string"},
                        "sv": {"type": "string"},
                        "en": {"type": "string"},
                    },
                    "required": ["fi", "sv", "en"],
                },
                "can_add_schoolyear": {"type": "boolean"},
                "can_add_clarification": {"type": "boolean"},
            },
            "required": [
                "id",
                "ontologyword",
                "can_add_schoolyear",
                "can_add_clarification",
            ],
        }

        try:
            # Making a get request
            response = requests.get(
                "https://www.hel.fi/palvelukarttaws/rest/v4/ontologyword/"
            )

            # Parse JSON
            json_data = response.json()
            # Validate against load schema
            validate(instance=json_data, schema=ontology_load_schema)
            # Iterate through words (should be a list)
            save_array = []
            for word in json_data:
                transformed_word = self.transform_data(word.copy())
                validate(instance=transformed_word, schema=ontology_save_schema)
                save_array.append(transformed_word)

            # Delete
            OntologyWord.objects.all().delete()
            # Save
            batch_size = 100
            objs = (OntologyWord(data=i) for i in save_array)
            while True:
                batch = list(islice(objs, batch_size))
                if not batch:
                    break
                OntologyWord.objects.bulk_create(batch, batch_size)

            # print(response)
            # print json content
        except Exception as e:
            # raise CommandError('Poll "%s" does not exist' % poll_id)
            self.stdout.write(self.style.ERROR(str(e)))

        # Success
        self.stdout.write(self.style.SUCCESS("Ontologies loaded successfully."))