import requests

import csv

from itertools import islice

from jsonschema import validate

from django.core.management.base import BaseCommand, CommandError
from moderation.models import ModeratedNotification


class Command(BaseCommand):
    help = "Imports conversions from file"

    def has_869(self, ont_list):
        if 869 in ont_list:
            return True

    def is_new_id(self, id):
        arr = [
            1036,
            4322,
            4323,
            4324,
            4325,
            4326,
            4327,
            4328,
            4330,
            4331,
            4332,
            4333,
            4336,
            4337,
            4338,
            4339,
            4342,
        ]
        return id in arr

    def handle(self, *args, **options):

        try:
            ns = ModeratedNotification.objects.all()
            data = {}
            with open(
                "/app/moderation/management/commands/ontology_conversion.csv"
            ) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=";")
                line_count = 0
                for row in csv_reader:
                    if line_count == 0:
                        pass
                        # print(f'Column names are {", ".join(row)}')
                    else:
                        pass
                        # print(row)
                        data[int(row[0])] = list(
                            map(lambda x: int(x), row[1].split("+"))
                        )
                    line_count += 1

            # print(data)
            for n in ns:
                if n.id in data:
                    ont_list = data[n.id]
                    if self.is_new_id(n.id) or self.has_869(ont_list):
                        n.data["ontology_ids"] = list(
                            set(n.data["ontology_ids"] + ont_list)
                        )
                        n.save()

            # print(response)
            # print json content
        except Exception as e:
            # raise CommandError('Poll "%s" does not exist' % poll_id)
            self.stdout.write(self.style.ERROR(str(e)))

        # Success
        self.stdout.write(self.style.SUCCESS("Ids updtead loaded successfully."))
