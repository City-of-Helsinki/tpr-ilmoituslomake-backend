from django.core.management.base import BaseCommand, CommandError
from base.models import IdMappingAll, IdMappingKaupunkialustaMaster
from itertools import islice
from urllib import request
import json


# Import the id mappings needed to integrate Kaupunkialusta with Esteettömyyssovellus
class Command(BaseCommand):
    def extract_data(self, item):
        # Extract the internal and kaupunkialusta sources, not any others such as lipas
        item_sources = item["sources"]

        kaupunkialusta_source = None
        tpr_source = None

        for source in item_sources:
            if source["source"] == "kaupunkialusta":
                kaupunkialusta_source = source
            elif source["source"] == "internal":
                tpr_source = source

        # Store the id mapping values in an object
        id_mapping = {}
        id_mapping["palvelukartta_id"] = item["id"]
        id_mapping["palvelukartta_name_fi"] = item["name_fi"]
        if tpr_source != None:
            id_mapping["tpr_internal_id"] = tpr_source["id"]
        if kaupunkialusta_source != None:
            id_mapping["kaupunkialusta_id"] = kaupunkialusta_source["id"]

        return id_mapping


    def insert_data_id_mapping_all(self, id_mapping_array):
        # Delete all existing id mappings
        IdMappingAll.objects.all().delete()

        # Insert the id mappings in batches
        batch_size = 100
        objs = (IdMappingAll(**mapping) for mapping in id_mapping_array)
        while True:
            batch = list(islice(objs, batch_size))
            if not batch:
                break
            IdMappingAll.objects.bulk_create(batch, batch_size)


    def insert_data_id_mapping_kaupunkialusta_master(self, id_mapping_array):
        # Delete all existing id mappings
        IdMappingKaupunkialustaMaster.objects.all().delete()

        # Insert the id mappings in batches
        batch_size = 100
        objs = (IdMappingKaupunkialustaMaster(**mapping) for mapping in id_mapping_array)
        while True:
            batch = list(islice(objs, batch_size))
            if not batch:
                break
            IdMappingKaupunkialustaMaster.objects.bulk_create(batch, batch_size)


    def handle(self, *args, **options):
        self.stdout.write("Importing data from servicemap")

        try:
            # Fetch all the id mappings into a json file
            remote_url = "https://www.hel.fi/palvelukarttaws/rest/v4/unit/?official=yes"
            local_file = "./base/management/commands/id_mapping_all.json"

            request.urlretrieve(remote_url, local_file)

            with open(local_file) as json_file:
                # Load the json data, extract the id mappings into an array, and insert them into the database
                json_data = json.load(json_file)

                id_mapping_array = list(map(lambda item: self.extract_data(item), json_data))

                self.insert_data_id_mapping_all(id_mapping_array)

        except Exception as e:
            # raise CommandError('Poll "%s" does not exist' % poll_id)
            self.stdout.write(self.style.ERROR(str(e)))

        self.stdout.write("Importing kaupunkialusta data from servicemap")

        try:
            # Fetch the kaupunkialusta id mappings into a json file
            remote_url = "https://www.hel.fi/palvelukarttaws/rest/v4/unit/?official=yes&suborganization=0c71aa86-f76c-466b-b6f3-81143bd9eecc"
            local_file = "./base/management/commands/id_mapping_kaupunkialusta_master.json"

            request.urlretrieve(remote_url, local_file)

            with open(local_file) as json_file:
                # Load the json data, extract the id mappings into an array, and insert them into the database
                json_data = json.load(json_file)

                id_mapping_array = list(map(lambda item: self.extract_data(item), json_data))

                self.insert_data_id_mapping_kaupunkialusta_master(id_mapping_array)

        except Exception as e:
            # raise CommandError('Poll "%s" does not exist' % poll_id)
            self.stdout.write(self.style.ERROR(str(e)))

        # Success
        self.stdout.write(self.style.SUCCESS("Import from servicemap completed"))
