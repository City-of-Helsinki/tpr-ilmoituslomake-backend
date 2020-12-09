import requests
from itertools import islice

from jsonschema import validate

from django.core.management.base import BaseCommand, CommandError
from base.models import Neighborhood


class Command(BaseCommand):
    help = "Imports neighborhoods from Helsinki API"

    # def add_arguments(self, parser):
    #    parser.add_argument('poll_ids', nargs='+', type=int)

    # {
    #     "id": 5258,
    #     "origin_id": "49-013",
    #     "ocd_id": "ocd-division/country:fi/kunta:espoo/kaupunginosa:013",
    #     "service_point_id": null,
    #     "start": null,
    #     "end": null,
    #     "modified_at": "2020-10-02T09:50:45.840055+03:00",
    #     "type": "neighborhood",
    #     "parent": 11,
    #     "municipality": "espoo",
    #     "name": {
    #         "fi": "Westend",
    #         "sv": "Westend"
    #     }
    # }

    def transform_data(self, data):
        return {"name": data["name"]}

    def handle(self, *args, **options):

        # Delete existing words
        # Import new ones!

        neighborhood_load_schema = {
            "$id": "<url>",
            "$schema": "http://json-schema.org/draft-07/schema#",
            "description": "<description>",
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": True,
                "properties": {
                    "name": {
                        "type": "object",
                        "properties": {
                            "fi": {"type": "string"},
                            "sv": {"type": "string"},
                        },
                        "required": ["fi", "sv"],
                    },
                },
                "required": ["name"],
            },
        }
        neighborhood_save_schema = {
            "$id": "<url>",
            "$schema": "http://json-schema.org/draft-07/schema#",
            "description": "<description>",
            "type": "object",
            "properties": {
                "name": {
                    "type": "object",
                    "properties": {
                        "fi": {"type": "string"},
                        "sv": {"type": "string"},
                    },
                    "required": ["fi", "sv"],
                },
            },
            "required": ["name"],
        }

        try:
            json_data = {
                "next": "https://api.hel.fi/servicemap/v2/administrative_division/?type=neighborhood"
            }
            # Iterate through words (should be a list)
            save_array = []
            while json_data["next"] != None:
                # Making a get request
                response = requests.get(json_data["next"])
                # print(json_data["next"])
                # Parse JSON
                json_data = response.json()
                # Validate against load schema
                validate(instance=json_data["results"], schema=neighborhood_load_schema)
                for neighborhood in json_data["results"]:
                    transformed_neighborhood = self.transform_data(neighborhood.copy())
                    validate(
                        instance=transformed_neighborhood,
                        schema=neighborhood_save_schema,
                    )
                    save_array.append(transformed_neighborhood)

            # Delete
            Neighborhood.objects.all().delete()
            # Save
            batch_size = 100
            objs = (Neighborhood(data=i) for i in save_array)
            while True:
                batch = list(islice(objs, batch_size))
                if not batch:
                    break
                Neighborhood.objects.bulk_create(batch, batch_size)

            # print(response)
            # print json content
        except Exception as e:
            # raise CommandError('Poll "%s" does not exist' % poll_id)
            self.stdout.write(self.style.ERROR(str(e)))

        # Success
        self.stdout.write(self.style.SUCCESS("Neighborhoods loaded successfully."))
