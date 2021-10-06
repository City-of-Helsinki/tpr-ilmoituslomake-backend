import requests

import uuid

from itertools import islice

# from jsonschema import validate

from django.core.management.base import BaseCommand, CommandError

from moderation.models import ModeratedNotification, ModeratedNotificationImage
from notification_form.models import Notification

from base.image_utils import preprocess_images, process_images, unpublish_images

#

# This is needed so we can fake request object out of a dictionary
class dotdict(dict):
    """dot.notation access to dictionary attributes"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


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

    def create_fake_image_request(self, place):
        data_images = []
        data = []
        images = place.get("description", {}).get("images", [])
        if images != None and len(images) > 0:
            for image in images:
                if image["license_type"]["id"] != 1:
                    image_uuid = str(uuid.uuid4())
                    data.append({"uuid": image_uuid, "url": image["url"]})
                    data_images.append(
                        {
                            "uuid": image_uuid,
                            "url": image["url"],
                            "permission": "Creative Commons BY 4.0"
                            if image["license_type"]["id"] == 3
                            else "Location only",
                            "source": image["copyright_holder"],
                            "source_type": "url",
                            "alt_text": {"fi": "", "sv": "", "en": ""},
                        }
                    )
        # print(ret)
        return dotdict({"data": {"data": {"images": data_images}, "images": data}})

    def handle(self, *args, **options):

        try:
            max_id = 0
            response = requests.get("http://open-api.myhelsinki.fi/v1/places/")

            data = response.json()["data"]

            for place in data:
                id = int(place["id"])

                max_id = max(id, max_id)

                fake_image_request = self.create_fake_image_request(place)
                images = fake_image_request.data["data"]["images"]

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
                    "images": images,
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

                # TODO: LANG
                # zh_val = place.get("name", {}).get("zh", "")
                # zh = str(zh_val) if zh_val != None else ""
                # if zh != "":
                #    print(zh)

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
                    ModeratedNotificationImage, new_moderated_notification, pimages
                )
                unpublish_images(ModeratedNotificationImage, new_moderated_notification)
                break

        except Exception as e:
            # raise CommandError('Poll "%s" does not exist' % poll_id)
            self.stdout.write(self.style.ERROR(str(e)))

        # Success
        self.stdout.write(self.style.SUCCESS("Data loaded successfully."))
