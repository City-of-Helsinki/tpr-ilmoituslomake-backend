import requests

import csv

from itertools import islice

from jsonschema import validate

from django.core.management.base import BaseCommand, CommandError
from moderation.models import ModeratedNotification


class Command(BaseCommand):
    help = "Imports Matko sample from file"

    def handle(self, *args, **options):

        try:
            # json
            # # transformed_word =
            # validate(instance=transformed_word, schema=ontology_save_schema)
            save_array = []

            with open("/app/moderation/management/commands/tpr_data.csv") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=";")
                line_count = 0
                for row in csv_reader:
                    if line_count == 0:
                        pass
                        # print(f'Column names are {", ".join(row)}')
                    else:
                        # print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
                        # save_array.append()
                        pass
                        id = int(row[5])
                        data = {
                            "organization": {},
                            "name": {
                                "fi": str(row[6]),
                                "sv": str(row[7]),
                                "en": str(row[8]),
                            },
                            "location": [float(row[16]), float(row[17])],
                            "description": {
                                "short": {
                                    "fi": str(row[9]),
                                    "sv": str(row[10]),
                                    "en": str(row[11]),
                                },
                                "long": {
                                    "fi": str(row[12]),
                                    "sv": str(row[13]),
                                    "en": str(row[14]),
                                },
                            },
                            "address": {
                                "fi": {
                                    "street": str(row[18]),
                                    "postal_code": str(row[21]),
                                    "post_office": str(row[22]),
                                    "neighborhood_id": "",
                                    "neighborhood": "",
                                },
                                "sv": {
                                    "street": str(row[19]),
                                    "postal_code": str(row[21]),
                                    "post_office": str(row[23]),
                                    "neighborhood_id": "",
                                    "neighborhood": "",
                                },
                            },
                            "phone": str(row[25]),
                            "email": str(row[26]),
                            "website": {
                                "fi": str(row[27]),
                                "sv": str(row[28]),
                                "en": str(row[29]),
                            },
                            "images": [],
                            "opening_times": {},
                            "ontology_ids": list(
                                map(lambda x: int(x), str(row[15]).split(","))
                            ),
                            "matko_ids": [],
                            "extra_keywords": [],
                            "comments": "",
                            "notifier": {
                                "notifier_type": "",
                                "full_name": "",
                                "email": "",
                                "phone": "",
                            },
                        }
                        new = ModeratedNotification(id=id, data=data)
                        new.save()
                    line_count += 1

            # Create instances and load data

            # print(response)
            # print json content
        except Exception as e:
            # raise CommandError('Poll "%s" does not exist' % poll_id)
            self.stdout.write(self.style.ERROR(str(e)))

        # Success
        self.stdout.write(self.style.SUCCESS("Matko sample loaded successfully."))
