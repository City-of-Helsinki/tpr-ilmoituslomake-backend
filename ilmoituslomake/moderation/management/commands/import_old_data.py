import requests

import uuid

from itertools import islice

import lxml
from bs4 import BeautifulSoup

# from jsonschema import validate

from django.core.management.base import BaseCommand, CommandError

from moderation.models import ModeratedNotification, ModeratedNotificationImage
from notification_form.models import Notification
from translation.models import TranslationData, TranslationTask

from base.image_utils import preprocess_images, process_images, unpublish_images

from django.db import connection

#
muni_translations = {"HELSINKI": "Helsingfors", "ESPOO": "Esbo"}

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

    def find_xml_element(self, id, elems, elems_sv, elems_en):
        return {
            "fi": list(
                filter(lambda item: item.find("matko:id", string=str(id)), elems)
            )[0],
            "sv": "",
            "en": "",
        }

    def extract_property(self, elems, lang, prop):
        return str(elems[lang].find(prop).string)

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
        max_id = 0
        try:

            response = requests.get("http://open-api.myhelsinki.fi/v1/places/")
            xml_fi = BeautifulSoup(
                requests.get(
                    "http://feeds.myhelsinki.fi/places/helsinki_matkailu_poi.xml"
                ).content,
                "xml",
            ).find_all("item")
            xml_sv = BeautifulSoup(
                requests.get(
                    "http://feeds.myhelsinki.fi/places/helsinki_turism_poi.xml"
                ).content,
                "xml",
            ).find_all("item")
            xml_en = BeautifulSoup(
                requests.get(
                    "http://feeds.myhelsinki.fi/places/helsinki_tourism_poi.xml"
                ).content,
                "xml",
            ).find_all("item")

            data = response.json()["data"]

            for loc in data:
                id = int(loc["id"])

                xml = self.find_xml_element(id, xml_fi, xml_sv, xml_en)

                place = requests.get(
                    "http://open-api.myhelsinki.fi/v1/place/"
                    + str(id)
                    + "?language_filter=fi"
                ).json()
                place_sv = requests.get(
                    "http://open-api.myhelsinki.fi/v1/place/"
                    + str(id)
                    + "?language_filter=sv"
                ).json()
                place_en = requests.get(
                    "http://open-api.myhelsinki.fi/v1/place/"
                    + str(id)
                    + "?language_filter=en"
                ).json()

                address = (
                    place.get("location", {})
                    .get("address", {})
                    .get("street_address", "")
                )

                lon = float(place.get("location", {}).get("lon", 0))
                lat = float(place.get("location", {}).get("lat", 0))

                nhood = requests.get(
                    "https://api.hel.fi/servicemap/v2/administrative_division/?type=neighborhood&lon="
                    + str(lon)
                    + "&lat="
                    + str(lat)
                    + "&format=json"
                ).json()

                nhood_id = ""
                nhood_name_fi = ""
                nhood_name_sv = ""

                if len(nhood["results"]) > 0:
                    nhood_id = str(nhood["results"][0]["origin_id"])
                    nhood_name_fi = str(nhood["results"][0]["name"]["fi"])
                    nhood_name_sv = str(nhood["results"][0]["name"]["sv"])

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
                        lat,
                        lon,
                    ],
                    "description": {
                        "short": {
                            "fi": str(place.get("description", {}).get("body", "")),
                            "sv": str(place_sv.get("description", {}).get("body", "")),
                            "en": str(place_en.get("description", {}).get("body", "")),
                        },
                        "long": {
                            "fi": str(place.get("description", {}).get("body", "")),
                            "sv": str(place_sv.get("description", {}).get("body", "")),
                            "en": str(place_en.get("description", {}).get("body", "")),
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
                            "neighborhood_id": nhood_id,
                            "neighborhood": nhood_name_fi,
                        },
                        "sv": {
                            "street": self.extract_property(xml, "sv", "matko:address"),
                            "postal_code": str(
                                place_sv.get("location", {})
                                .get("address", {})
                                .get("postal_code", "")
                            ),
                            "post_office": muni_translations.get(
                                str(
                                    place_sv.get("location", {})
                                    .get("address", {})
                                    .get("locality", "")
                                ).to_upper(),
                                str(
                                    place_sv.get("location", {})
                                    .get("address", {})
                                    .get("locality", "")
                                ),
                            ),
                            "neighborhood_id": nhood_id,
                            "neighborhood": nhood_name_sv,
                        },
                    },
                    "businessid": "",
                    "phone": self.extract_property(xml, "fi", "matko:phone"),
                    "email": self.extract_property(xml, "fi", "matko:email"),
                    "website": {
                        "fi": str(place.get("info_url", "")),
                        "sv": str(place_sv.get("info_url", "")),
                        "en": str(place_en.get("info_url", "")),
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

                print(data)

                continue

                has_zh = False
                zh_val = place.get("name", {}).get("zh", "")
                zh = str(zh_val) if zh_val != None else ""
                if zh != "":
                    has_zh = True

                new_moderated_notification = None
                try:
                    new_moderated_notification = ModeratedNotification.objects.get(
                        id=id
                    )
                    new_moderated_notification.data = data
                    new_moderated_notification.save()
                except Exception as e:  # Model.DoesNotExist:
                    new_notification = Notification(
                        data=data, moderated_notification_id=id, status="approved"
                    )
                    new_notification.save()
                    new_moderated_notification = (
                        new_moderated_notification
                    ) = ModeratedNotification(
                        id=id,
                        notification_id=new_notification.pk,
                        data=data,
                        published=True,
                    )
                    new_moderated_notification.save()

                if new_moderated_notification == None:
                    print("error")
                    continue

                pimages = preprocess_images(fake_image_request)
                process_images(
                    ModeratedNotificationImage, new_moderated_notification, pimages
                )
                unpublish_images(ModeratedNotificationImage, new_moderated_notification)

                # TODO: Implement translation
                if has_zh:
                    pass
                    # Create TranslationTask and TranslationData manually for 'new_moderated_notification'
                    # It is from 'en' to 'zh'
                    # The variable 'zh' contains the translation. It is a string for the name field.
                    # All other fields are untranslated = empty.

        except Exception as e:
            # raise CommandError('Poll "%s" does not exist' % poll_id)
            self.stdout.write(self.style.ERROR(str(e)))
        return

        # Alter sequence so that it wont break
        with connection.cursor() as cursor:
            query = (
                "ALTER SEQUENCE moderation_moderatednotification_id_seq RESTART WITH "
                + str(max_id + 10)
                + ";"
            )
            cursor.execute(query)

        # Success
        self.stdout.write(self.style.SUCCESS("Data loaded successfully."))
