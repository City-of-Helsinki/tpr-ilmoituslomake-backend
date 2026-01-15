import requests
from itertools import islice

from jsonschema import validate

from django.core.management.base import BaseCommand, CommandError
from base.models import OntologyWord


class Command(BaseCommand):
    help = "Imports ontology words from Helsinki API"

    # def add_arguments(self, parser):
    #    parser.add_argument('poll_ids', nargs='+', type=int)

    def transform_data(self, data, is_myhelsinki_keyword):
        return {
            "id": data["id"],
            "ontologyword": {
                "fi": data["ontologyword_fi"]
                + (" (MyHelsinki)" if is_myhelsinki_keyword else ""),
                "sv": data["ontologyword_sv"]
                + (" (MyHelsinki)" if is_myhelsinki_keyword else ""),
                "en": data["ontologyword_en"]
                + (" (MyHelsinki)" if is_myhelsinki_keyword else ""),
            },
            "can_add_schoolyear": data["can_add_schoolyear"],
            "can_add_clarification": data["can_add_clarification"],
            "is_myhelsinki_keyword": is_myhelsinki_keyword,
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
                "additionalProperties": True,
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
            marketing_response = requests.get(
                # 2025-04-03 JPLa muutos Janne Pyykön pyynnöstä
                "https://www.hel.fi/palvelukarttaws/rest/v4/ontologyword/?category=MyHelsinki"
                #"https://www.hel.fi/palvelukarttaws/rest/v4/ontologyword/?category=tree0718"
            )
            response = requests.get(
                "https://www.hel.fi/palvelukarttaws/rest/v4/ontologyword/"
            )

            # [A] Ensin lataa Marketing-asiasanat tästä (löytyy nyt 19 kpl):
            # https://www.hel.fi/palvelukarttaws/rest/v4/ontologyword/?category=tree0718

            # [B] Sitten lataa kaikki asiasanat tästä (löytyy nyt 990 kpl):
            # https://www.hel.fi/palvelukarttaws/rest/v4/ontologyword/

            # Jos [B]-alkio on [A]:ssa lisätään (MyHelsinki)

            # Parse JSON
            marketing_json_data = marketing_response.json()
            json_data = response.json()
            # Validate against load schema
            validate(instance=marketing_json_data, schema=ontology_load_schema)
            validate(instance=json_data, schema=ontology_load_schema)
            # Iterate through words (should be a list)
            marketing_data = {data["id"]: data["id"] for data in marketing_json_data}
            save_array = []
            for word in json_data:
                transformed_word = self.transform_data(
                    word.copy(), word["id"] in marketing_data
                )
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
