import requests

import csv

from itertools import islice

from jsonschema import validate

from django.core.management.base import BaseCommand, CommandError
from base.models import MatkoWord


class Command(BaseCommand):
    help = "Imports matko words from file"

    # def add_arguments(self, parser):
    #    parser.add_argument('poll_ids', nargs='+', type=int)

    def transform_data(self, data):
        return {
            "id": data["id"],
            "type_name": "",
            "matkoword": {
                "fi": data["ontologyword_fi"],
                "sv": data["ontologyword_sv"],
                "en": data["ontologyword_en"],
            },
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
                "type_name": {"type": "string"},
                "matkoword": {
                    "type": "object",
                    "properties": {
                        "fi": {"type": "string"},
                        "sv": {"type": "string"},
                        "en": {"type": "string"},
                    },
                    "required": ["fi", "sv", "en"],
                },
            },
            "required": ["id", "typename" "matkoword"],
        }

        try:
            # json
            # # transformed_word =
            # validate(instance=transformed_word, schema=ontology_save_schema)
            save_array = []

            with open("/opt/tpr-ilmoituslomake-backend/ilmoituslomake/base/management/commands/matko_ids.csv") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=";")
                line_count = 0
                for row in csv_reader:
                    if line_count == 0:
                        pass
                        # print(f'Column names are {", ".join(row)}')
                    else:
                        # print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
                        # matko_type_id;type_name_matko;st;RUOTSIKSI;ENGLANNIKSI
                        save_array.append(
                            {
                                "id": int(row[0]),
                                "type_name": str(row[1]).strip(),
                                "matkoword": {
                                    "fi": str(row[2]).strip(),
                                    "sv": str(row[3]).strip(),
                                    "en": str(row[4]).strip(),
                                },
                            }
                        )
                    line_count += 1

            # Delete
            MatkoWord.objects.all().delete()
            # Save
            batch_size = 100
            objs = (MatkoWord(data=i) for i in save_array)
            while True:
                batch = list(islice(objs, batch_size))
                if not batch:
                    break
                MatkoWord.objects.bulk_create(batch, batch_size)

            # print(response)
            # print json content
        except Exception as e:
            # raise CommandError('Poll "%s" does not exist' % poll_id)
            self.stdout.write(self.style.ERROR(str(e)))

        # Success
        self.stdout.write(self.style.SUCCESS("Matko words loaded successfully."))
