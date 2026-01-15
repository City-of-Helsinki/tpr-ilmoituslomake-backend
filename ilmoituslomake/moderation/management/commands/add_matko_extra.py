import requests

import uuid
import csv

from itertools import islice

from jsonschema import validate

from django.core.management.base import BaseCommand, CommandError
from moderation.models import ModeratedNotification


class Command(BaseCommand):
    help = "Imports Matko extra from file"

    def handle(self, *args, **options):

        try:
            # json
            # # transformed_word =
            # validate(instance=transformed_word, schema=ontology_save_schema)
            # save_array = []

            with open("/opt/tpr-ilmoituslomake-backend/ilmoituslomake/moderation/management/commands/tpr_data2.csv") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=";")
                line_count = 0
                id = 4999
                for row in csv_reader:
                    if line_count == 0:
                        pass
                        # print(f'Column names are {", ".join(row)}')
                    else:
                        # print(f'\t{row[0]} works in the {row[1]} department, and was born in {row[2]}.')
                        # save_array.append()
                        pass
                        id += 1
                        #
                        try:
                            _fi = str(row[34]).strip()
                            _sv = str(row[35]).strip()
                            _en = str(row[36]).strip()
                            fi = (
                                []
                                if len(_fi) == 0
                                else list(map(lambda x: x.strip(), _fi.split(",")))
                            )
                            sv = (
                                []
                                if len(_sv) == 0
                                else list(map(lambda x: x.strip(), _sv.split(",")))
                            )
                            en = (
                                []
                                if len(_en) == 0
                                else list(map(lambda x: x.strip(), _en.split(",")))
                            )
                            if len(fi) > 0 or len(sv) > 0 or len(en) > 0:
                                moderated_notification = (
                                    ModeratedNotification.objects.get(id=id)
                                )
                                moderated_notification.data["extra_keywords"][
                                    "fi"
                                ] = list(
                                    set(
                                        moderated_notification.data["extra_keywords"][
                                            "fi"
                                        ]
                                        + fi
                                    )
                                )
                                moderated_notification.data["extra_keywords"][
                                    "sv"
                                ] = list(
                                    set(
                                        moderated_notification.data["extra_keywords"][
                                            "sv"
                                        ]
                                        + sv
                                    )
                                )
                                moderated_notification.data["extra_keywords"][
                                    "en"
                                ] = list(
                                    set(
                                        moderated_notification.data["extra_keywords"][
                                            "en"
                                        ]
                                        + en
                                    )
                                )
                                moderated_notification.save()
                        except Exception as e:
                            print("Not found %s" % id)

                    line_count += 1

            # Alter sequence so that it wont break
            # with connection.cursor() as cursor:
            #    query = "ALTER SEQUENCE moderation_moderatednotification_id_seq RESTART WITH 5100;"
            #    cursor.execute(query)

        except Exception as e:
            # raise CommandError('Poll "%s" does not exist' % poll_id)
            self.stdout.write(self.style.ERROR(str(e)))

        # Success
        self.stdout.write(self.style.SUCCESS("Matko sample loaded successfully."))
