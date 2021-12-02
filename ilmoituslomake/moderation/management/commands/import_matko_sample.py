import requests

import uuid
import csv

from itertools import islice

from jsonschema import validate

from base.image_utils import preprocess_images, process_images, unpublish_images

from django.core.management.base import BaseCommand, CommandError
from moderation.models import ModeratedNotification, ModeratedNotificationImage
from notification_form.models import Notification

# imports
from django.db import connection


class dotdict(dict):
    """dot.notation access to dictionary attributes"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class Command(BaseCommand):
    help = "Imports Matko sample from file"

    def create_fake_image_request(self, img_url, caption_fi, caption_sv, caption_en):

        if img_url == "":
            return dotdict({"data": {"data": {"images": []}, "images": []}})

        image_uuid = str(uuid.uuid4())
        return dotdict(
            {
                "data": {
                    "data": {
                        "images": [
                            {
                                "index": 0,
                                "uuid": image_uuid,
                                "url": img_url,
                                "permission": "Location only",
                                "source": "",
                                "source_type": "url",
                                "alt_text": {
                                    "fi": caption_fi,
                                    "sv": caption_sv,
                                    "en": caption_en,
                                },
                                "media_id": "",
                            }
                        ]
                    },
                    "images": [{"uuid": image_uuid, "url": img_url}],
                }
            }
        )

        return list(set(ontology_array)), list(set(matko_array))

    def handle(self, *args, **options):

        try:
            # json
            # # transformed_word =
            # validate(instance=transformed_word, schema=ontology_save_schema)
            save_array = []

            with open("/app/moderation/management/commands/tpr_data.csv") as csv_file:
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
                        lon = float(row[17])
                        lat = float(row[16])
                        nhood_ = requests.get(
                            "https://api.hel.fi/servicemap/v2/administrative_division/?type=neighborhood&lon="
                            + str(lon)
                            + "&lat="
                            + str(lat)
                            + "&format=json"
                        )

                        nhood = nhood_.json()

                        nhood_id = ""
                        nhood_name_fi = ""
                        nhood_name_sv = ""

                        if len(nhood["results"]) > 0:
                            nhood_id = str(nhood["results"][0]["origin_id"])
                            nhood_name_fi = str(nhood["results"][0]["name"]["fi"])
                            nhood_name_sv = str(nhood["results"][0]["name"]["sv"])

                        img_url = str(row[30])
                        caption_fi, caption_sv, caption_en = (
                            str(row[31]),
                            str(row[32]),
                            str(row[33]),
                        )
                        fake_image_request = self.create_fake_image_request(
                            img_url, caption_fi, caption_sv, caption_en
                        )
                        images = fake_image_request.data["data"]["images"]

                        data = {
                            "organization": {},
                            "name": {
                                "fi": str(row[6]),
                                "sv": str(row[7]),
                                "en": str(row[8]),
                            },
                            "location": [
                                lat,
                                lon,
                            ],
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
                                    "neighborhood_id": nhood_id,
                                    "neighborhood": nhood_name_fi,
                                },
                                "sv": {
                                    "street": str(row[19]),
                                    "postal_code": str(row[21]),
                                    "post_office": str(row[23]),
                                    "neighborhood_id": nhood_id,
                                    "neighborhood": nhood_name_sv,
                                },
                            },
                            "businessid": "",
                            "phone": str(row[25]),
                            "email": str(row[26]),
                            "website": {
                                "fi": str(row[27]),
                                "sv": str(row[28]),
                                "en": str(row[29]),
                            },
                            "images": images,
                            "opening_times": [],
                            "ontology_ids": list(
                                map(lambda x: int(x), str(row[15]).split("+"))
                            ),
                            "matko_ids": [],
                            "extra_keywords": {"fi": [], "sv": [], "en": []},
                            "comments": "tprid:%s" % str(row[5]),
                            "notifier": {
                                "notifier_type": "",
                                "full_name": "",
                                "email": "",
                                "phone": "",
                            },
                        }
                        new_notification = Notification(
                            data=data, moderated_notification_id=id, status="approved"
                        )
                        new_notification.save()
                        new_moderated_notification = ModeratedNotification(
                            id=id,
                            notification_id=new_notification.pk,
                            data=data,
                            published=True,
                        )
                        new_moderated_notification.save()

                        pimages = preprocess_images(fake_image_request)
                        process_images(
                            ModeratedNotificationImage,
                            new_moderated_notification,
                            pimages,
                        )
                        unpublish_images(
                            ModeratedNotificationImage, new_moderated_notification
                        )

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
