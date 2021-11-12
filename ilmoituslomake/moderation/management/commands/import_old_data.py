import requests

import uuid
import csv

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


conversion_ids = {
    1: 914,
    165: 918,
    15: 214,
    56: 214,
    57: 214,
    3: 214,
    228: {"Bar": 869, "Pub": 869, "Nightclub": 919, "Club": 919},
    48: 239,
    # 149	ei muunneta
    # 243	ei muunneta
    # 116	ei muunneta
    # 111	ei muunneta
    22: 915,
    # 164	ei muunneta
    # 221	ei muunneta
    2: 326,
    # 248	ei muunneta
    40: 961,
    6: {"Museum": 961, "Gallery": 915},
    74: 916,
    5: {
        "Nature": 916,
        "RecreationalArea": 916,
        "Island": 916,
        "Viewpoint": 916,
        "Sport": 917,
        "SportCenter": 917,
        "SportOutdoor": 917,
        "Swimming": 917,
        "Athletics": 917,
        "Yoga": 917,
        "GymFitness": 917,
        "Football": 917,
        "Basketball": 917,
        "Tennis": 917,
        "IceSkating": 917,
        "Biking": 917,
        "SkateBoard": 917,
        "Karting": 917,
        "Golf": 917,
        "Bowling": 917,
        "Canoeing": 917,
        "Climbing": 917,
        "Dance": 917,
        "Frisbeegolf": 917,
        "HorseRiding": 917,
        "SkiingCrosscountry": 917,
        "SkiingDownhill": 917,
        "MiniGolf": 917,
        "RecreationalCentre": 917,
        "WaterPark": 917,
    },
    # 114	ei muunneta
    229: 577,
    10: {"Restaurant": 577, "Cafe": 239},
    18: 326,
    169: 864,
    # 158	ei muunneta
    9: 490,
    4: 473,
    # 113	ei muunneta
    225: 868,
    206: 864,
    # Exception:
    # 226: {
    #    "WorkSpace": 921
    # }
    # JOS ei ole Matko-tyyppiä "WorkSpace"
    # => #920 opiskelu
}


class Command(BaseCommand):
    help = "Imports data from OPEN API"

    def handle_tags(self, id, place, xml_data, conversion_ids, ontology_words_for_id):
        matkos = self.extract_property_list(xml_data, "fi", "matko:type2s")
        arr = list(
            map(
                lambda t: int(t["id"].split(":")[-1]),
                filter(
                    lambda t: t["id"].split(":")[-1].isnumeric(),
                    list(place.get("tags", [])),
                ),
            )
        )
        ontology_array = ontology_words_for_id.get(id, [])
        matko_array = []
        for a in arr:
            if a in conversion_ids:
                d = conversion_ids[a]
                if type(d) == int:
                    ontology_array = ontology_array + [d]
                else:
                    if a == 226:
                        if "WorkSpace" in matkos:
                            ontology_array = ontology_array + [921]
                        else:
                            ontology_array = ontology_array + [920]
                    else:
                        fw = list(set(matkos).intersection(set(list(d.keys()))))
                        for f in fw:
                            ontology_array.append(d[f])

            else:
                matko_array.append(a)

        return list(set(ontology_array)), list(set(matko_array))

    def find_xml_element(self, id, elems, elems_sv, elems_en):
        return {
            "fi": elems.get(str(id), None),
            "sv": elems_sv.get(str(id), None),
            "en": elems_en.get(str(id), None)
        }

    def extract_property_list(self, elems, lang, prop):
        if elems[lang] == None:
            return []
        f = elems[lang].find(prop)
        if f:
            return list(map(lambda x: str(x.string), f))
        return []

    def extract_property(self, elems, lang, prop):
        if elems[lang] == None:
            return ""
        f = elems[lang].find(prop)
        if f:
            return str(f.string or "")
        return ""

    def create_fake_image_request(self, place):
        data_images = []
        data = []
        images = place.get("description", {}).get("images", [])
        i = 0
        if images != None and len(images) > 0:
            for image in images:
                if image["license_type"]["id"] != 1:
                    image_uuid = str(image["media_id"])  # str(uuid.uuid4())
                    data.append({"uuid": image_uuid, "url": image["url"]})
                    data_images.append(
                        {
                            "index": i,
                            "uuid": image_uuid,
                            "url": image["url"],
                            "permission": "Creative Commons BY 4.0"
                            if image["license_type"]["id"] == 3
                            else "Location only",
                            "source": image["copyright_holder"],
                            "source_type": "url",
                            "alt_text": {"fi": "", "sv": "", "en": ""},
                            "media_id": image["media_id"],
                        }
                    )
                    i += 1
        # print(ret)
        return dotdict({"data": {"data": {"images": data_images}, "images": data}})

    def handle(self, *args, **options):
        max_id = 0
        try:
            ontology_words_for_id = {}
            with open(
                "/opt/tpr-ilmoituslomake-backend/ilmoituslomake/moderation/management/commands/ontology_conversion.csv"
            ) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=";")
                line_count = 0
                for row in csv_reader:
                    if line_count == 0:
                        pass
                    else:
                        from_id = int(row[0])
                        to_ids = list(map(lambda x: int(x), row[1].split("+")))
                        ontology_words_for_id[from_id] = to_ids
                    line_count += 1

            response = requests.get("http://open-api.myhelsinki.fi/v1/places/")
            xml_fi_ = BeautifulSoup(
                requests.get(
                    "http://feeds.myhelsinki.fi/places/helsinki_matkailu_poi.xml"
                ).content,
                "xml",
            ).find_all("item")
            xml_sv_ = BeautifulSoup(
                requests.get(
                    "http://feeds.myhelsinki.fi/places/helsingfors_turism_poi.xml"
                ).content,
                "xml",
            ).find_all("item")
            xml_en_ = BeautifulSoup(
                requests.get(
                    "http://feeds.myhelsinki.fi/places/helsinki_tourism_poi.xml"
                ).content,
                "xml",
            ).find_all("item")

            xml_fi = {i.find("matko:id").string: i for i in xml_fi_}
            xml_sv = {i.find("matko:id").string: i for i in xml_sv_}
            xml_en = {i.find("matko:id").string: i for i in xml_en_}

            data = response.json()["data"]

            ids = list(map(lambda x: x.id, list(ModeratedNotification.objects.all())))

            ii = 0
            for loc in data:
                # ii += 1
                # if ii > 15:
                #    break
                id = int(loc["id"])

                if id in ids:
                    continue

                # print(id)
                xml = self.find_xml_element(id, xml_fi, xml_sv, xml_en)

                place = requests.get(
                    "http://open-api.myhelsinki.fi/v1/place/"
                    + str(id)
                    + "?language_filter=fi"
                ).json()

                place_sv = {}
                place_sv_ = requests.get(
                    "http://open-api.myhelsinki.fi/v1/place/"
                    + str(id)
                    + "?language_filter=sv"
                )
                if place_sv_.status_code == 200:
                    place_sv = place_sv_.json()

                place_en = {}
                place_en_ = requests.get(
                    "http://open-api.myhelsinki.fi/v1/place/"
                    + str(id)
                    + "?language_filter=en"
                )

                if place_en_.status_code == 200:
                    place_en = place_en_.json()

                place_zh = {}
                place_zh_ = requests.get(
                    "http://open-api.myhelsinki.fi/v1/place/"
                    + str(id)
                    + "?language_filter=zh"
                )

                if place_zh_.status_code == 200:
                    place_zh = place_zh_.json()

                lon = float(place.get("location", {}).get("lon", 0))
                lat = float(place.get("location", {}).get("lat", 0))

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

                max_id = max(id, max_id)

                fake_image_request = self.create_fake_image_request(place)
                images = fake_image_request.data["data"]["images"]

                ontology_array, matko_array = self.handle_tags(
                    id, place, xml, conversion_ids, ontology_words_for_id
                )

                fi_name = str(place.get("name", {}).get("fi", "") or "").strip()
                sv_name = str(place.get("name", {}).get("sv", "") or "").strip()
                en_name = str(place.get("name", {}).get("en", "") or "").strip()

                _pc_fi = str(
                    place.get("location", {}).get("address", {}).get("postal_code", "")
                    or ""
                )
                pc_fi = _pc_fi
                _pc_sv = str(
                    place_sv.get("location", {})
                    .get("address", {})
                    .get("postal_code", "")
                    or ""
                )
                pc_sv = _pc_sv
                _po_fi = str(
                    place.get("location", {}).get("address", {}).get("locality", "")
                    or ""
                )
                po_fi = _po_fi
                _po_sv = str(
                    place_sv.get("location", {}).get("address", {}).get("locality", "")
                    or ""
                )
                po_sv = _po_sv

                #
                if _pc_fi.isdigit():
                    pass
                elif _po_fi.isdigit():
                    pc_fi = _po_fi
                    po_fi = _pc_fi
                else:
                    po_fi = _pc_fi
                    pc_fi = ""

                if _pc_sv.isdigit():
                    pass
                elif _po_sv.isdigit():
                    pc_sv = _po_sv
                    po_sv = _pc_sv
                else:
                    po_sv = _pc_sv
                    pc_sv = ""

                data = {
                    "organization": {},
                    "name": {
                        "fi": fi_name,
                        "sv": sv_name,
                        "en": en_name,
                    },
                    "location": [
                        lat,
                        lon,
                    ],
                    "description": {
                        "short": {
                            "fi": str(
                                place.get("description", {}).get("body", "") or ""
                            ).strip(),
                            "sv": str(
                                place_sv.get("description", {}).get("body", "") or ""
                            ).strip(),
                            "en": str(
                                place_en.get("description", {}).get("body", "") or ""
                            ).strip(),
                        },
                        "long": {
                            "fi": str(
                                place.get("description", {}).get("body", "") or ""
                            ).strip(),
                            "sv": str(
                                place_sv.get("description", {}).get("body", "") or ""
                            ).strip(),
                            "en": str(
                                place_en.get("description", {}).get("body", "") or ""
                            ).strip(),
                        },
                    },
                    "address": {
                        "fi": {
                            "street": str(
                                place.get("location", {})
                                .get("address", {})
                                .get("street_address", "")
                                or ""
                            ),
                            "postal_code": pc_fi,
                            "post_office": po_fi,
                            "neighborhood_id": nhood_id,
                            "neighborhood": nhood_name_fi,
                        },
                        "sv": {
                            "street": self.extract_property(xml, "sv", "matko:address")
                            or (
                                str(
                                    place.get("location", {})
                                    .get("address", {})
                                    .get("street_address", "")
                                    or ""
                                )
                            ),
                            "postal_code": pc_sv,
                            "post_office": muni_translations.get(
                                po_sv.upper(),
                                po_sv,
                            ),
                            "neighborhood_id": nhood_id,
                            "neighborhood": nhood_name_sv,
                        },
                    },
                    "businessid": "",
                    "phone": self.extract_property(xml, "fi", "matko:phone") or "",
                    "email": self.extract_property(xml, "fi", "matko:email") or "",
                    "website": {
                        "fi": self.extract_property(xml, "fi", "link")
                        or "",  # str(place.get("info_url", "") or ""),
                        "sv": self.extract_property(xml, "sv", "link") or "",  # ,
                        "en": self.extract_property(xml, "en", "link") or "",  # ,
                    },
                    "images": images,
                    "opening_times": [],
                    "ontology_ids": ontology_array,
                    "matko_ids": matko_array,
                    "extra_keywords": {"fi": [], "sv": [], "en": []},
                    "comments": "Tuotu ohjelmallisesti vanhoista järjestelmistä.",
                    "notifier": {
                        "notifier_type": "",
                        "full_name": "",
                        "email": "",
                        "phone": "",
                    },
                }

                # print(data)

                has_zh = False
                zh_val = place.get("name", {}).get("zh", "")
                zh_name = str(zh_val) if zh_val != None else ""
                tdata = {}
                if zh_name != "":
                    has_zh = True
                    # tdata["task_id"] = translation_task
                    # tdata["images"] = translation_task_data["images"]
                    tdata["name"] = zh_name.strip()
                    tdata["language"] = "zh"
                    tdata["description_short"] = str(
                        place_zh.get("description", {}).get("body", "") or ""
                    ).strip()
                    tdata["description_long"] = str(
                        place_zh.get("description", {}).get("body", "") or ""
                    ).strip()
                    tdata["website"] = str(place_zh.get("info_url", "") or "")
                    # tdata["target_revision"] = target_revision
                    tdata["images"] = []
                    # images_dict = { i["uuid"]: i for i in images }
                    t_images = []
                    for i in range(len(images)):
                        image = images[i]
                        t_images.append(
                            {
                                "index": i,
                                "uuid": image["uuid"],
                                "source": image["source"],
                                "alt_text": {"lang": ""},
                            }
                        )
                    tdata["images"] = t_images

                    # print(tdata)

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

                if has_zh:

                    ttask = {
                        "published": True,
                        "request_id": TranslationTask.objects.count() + 1,
                        "target": new_moderated_notification,
                        "target_revision": new_moderated_notification.revision,
                        "language_from": "en",
                        "language_to": "zh",
                        "category": "translation_task",
                        "item_type": "created",
                        "status": "closed",
                        "data": tdata,
                        "message": "Imported from old systems.",
                    }

                    translation_task = TranslationTask(**ttask)
                    translation_task.save()

                    tdata["task_id"] = translation_task
                    tdata["target_revision"] = new_moderated_notification.revision

                    translation_data = TranslationData(**tdata)
                    translation_data.save()

        except Exception as e:
            # raise CommandError('Poll "%s" does not exist' % poll_id)
            self.stdout.write(self.style.ERROR(str(e)))
        # return

        # Alter sequence so that it wont break
        # with connection.cursor() as cursor:
        #    query = (
        #        "ALTER SEQUENCE moderation_moderatednotification_id_seq RESTART WITH "
        #        + str(max_id + 100)
        #        + ";"
        #    )
        #    cursor.execute(query)

        # Success
        self.stdout.write(self.style.SUCCESS("Data loaded successfully."))
