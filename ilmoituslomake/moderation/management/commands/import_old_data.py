import requests

import csv

from itertools import islice

# from jsonschema import validate

from django.core.management.base import BaseCommand, CommandError

from moderation.models import ModeratedNotification
from notification_form.models import Notification

#


class Command(BaseCommand):
    help = "Imports data from OPEN API"

    def handle_matko_tags(self, place):
        return list(
            map(
                lambda t: int(t["id"].split(":")[-1]),
                filter(
                    lambda t: t["id"].split(":")[-1].isnumeric(),
                    list(place.get("tags", [])),
                ),
            )
        )

    def handle_images(self, place):
        ret = []
        images = place.get("description", {}).get("images", [])
        if images != None and len(images) > 0:
            for image in images:
                if image["license_type"]["id"] != 1:
                    ret.append(
                        {
                            "url": "",
                            "permission": "Creative Commons BY 4.0"
                            if image["license_type"]["id"] == 3
                            else "Location only",
                            "source": image["copyright_holder"],
                            "alt_text": {"fi": "", "sv": "", "en": ""},
                        }
                    )
        return ret

    def handle(self, *args, **options):

        try:
            max_id = 0
            response = requests.get("http://open-api.myhelsinki.fi/v1/places/")

            data = response.json()["data"]

            for place in data:
                id = int(place["id"])

                max_id = max(id, max_id)

                data = {
                    "organization": {},
                    "name": {
                        "fi": str(place.get("name", {}).get("fi", "")),
                        "sv": str(place.get("name", {}).get("sv", "")),
                        "en": str(place.get("name", {}).get("en", "")),
                    },
                    "location": [
                        float(place.get("location", {}).get("lat", 0)),
                        float(place.get("location", {}).get("lon", 0)),
                    ],
                    "description": {
                        "short": {
                            "fi": str(place.get("description", {}).get("body", "")),
                            "sv": "",
                            "en": "",
                        },
                        "long": {
                            "fi": str(place.get("description", {}).get("body", "")),
                            "sv": "",
                            "en": "",
                        },
                    },
                    "address": {
                        "fi": {
                            "street": str(
                                place.get("location", {})
                                .get("address", {})
                                .get("street_address", "")
                            ),
                            "postal_code": str(
                                place.get("location", {})
                                .get("address", {})
                                .get("postal_code", "")
                            ),
                            "post_office": str(
                                place.get("location", {})
                                .get("address", {})
                                .get("locality", "")
                            ),
                            "neighborhood_id": "",
                            "neighborhood": "",
                        },
                        "sv": {
                            "street": str(
                                place.get("location", {})
                                .get("address", {})
                                .get("street_address", "")
                            ),
                            "postal_code": str(
                                place.get("location", {})
                                .get("address", {})
                                .get("postal_code", "")
                            ),
                            "post_office": str(
                                place.get("location", {})
                                .get("address", {})
                                .get("locality", "")
                            ),
                            "neighborhood_id": "",
                            "neighborhood": "",
                        },
                    },
                    "businessid": "",
                    "phone": "",
                    "email": "",
                    "website": {
                        "fi": str(place.get("info_url", "")),
                        "sv": str(place.get("info_url", "")),
                        "en": str(place.get("info_url", "")),
                    },
                    "images": self.handle_images(place),
                    "opening_times": [],
                    "ontology_ids": [],
                    "matko_ids": self.handle_matko_tags(place),
                    "extra_keywords": [],
                    "comments": "",
                    "notifier": {
                        "notifier_type": "",
                        "full_name": "",
                        "email": "",
                        "phone": "",
                    },
                }

                # zh_val = place.get("name", {}).get("zh", "")
                # zh = str(zh_val) if zh_val != None else ""
                # if zh != "":
                #    print(zh)

                # new_notification = Notification(data=data, moderated_notification_id=id, status="approved")
                # new_notification.save()
                # new_moderated_notification = ModeratedNotification(id=id, notification_id=new_notification.pk, data=data, published=True)
                # new_moderated_notification.save()

        except Exception as e:
            # raise CommandError('Poll "%s" does not exist' % poll_id)
            self.stdout.write(self.style.ERROR(str(e)))

        # Success
        self.stdout.write(self.style.SUCCESS("Data loaded successfully."))
