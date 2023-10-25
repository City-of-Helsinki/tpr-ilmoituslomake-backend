from django.core.management.base import BaseCommand, CommandError
from base.models import IdMappingAll, IdMappingKaupunkialustaMaster
from datetime import datetime, timedelta
from ilmoituslomake.settings import (
    ACCESSIBILITY_API_URL,
    TPR_SYSTEM_ID,
    TPR_CHECKSUM_SECRET,
    KAUPUNKIALUSTA_SYSTEM_ID,
)
import hashlib
import requests


# Export the id mappings needed to integrate Kaupunkialusta with Esteettömyyssovellus
class Command(BaseCommand):
    def get_valid_until_next_day(self):
        # Return the current UTC datetime + 1 day in ISO format
        # Note that the string does not end with 'Z'
        now = datetime.utcnow().replace(microsecond=0)
        valid_until = (now + timedelta(days=1)).isoformat()
        return valid_until


    def add_accessibility_external_reference(self, kaupunkialusta_id, kaupunkialusta_user, tpr_internal_id):
        # Add the published notification id to Esteettömyyssovellus as an external reference
        tpr_servicepoint_id = str(tpr_internal_id)
        kaupunkialusta_servicepoint_id = str(kaupunkialusta_id)
        valid_until = self.get_valid_until_next_day()

        # Calculate the checksum using the values
        externalservicepoint_checksum_string = (
            str(TPR_CHECKSUM_SECRET)
            + str(TPR_SYSTEM_ID)
            + str(tpr_servicepoint_id)
            + str(kaupunkialusta_user)
            + str(valid_until)
            + str(KAUPUNKIALUSTA_SYSTEM_ID)
            + str(kaupunkialusta_servicepoint_id)
        )
        externalservicepoint_checksum = hashlib.sha256(externalservicepoint_checksum_string.encode("utf-8")).hexdigest()

        # Determine the data to post to the accessibility API
        externalservicepoint_data = {
            "ServicePointId": kaupunkialusta_servicepoint_id,
            "SystemId": KAUPUNKIALUSTA_SYSTEM_ID,
            "User": kaupunkialusta_user,
            "ValidUntil": valid_until,
            "Checksum": externalservicepoint_checksum,
        }
        externalservicepoint_url = ACCESSIBILITY_API_URL + "servicepoints/" + TPR_SYSTEM_ID + "/" + tpr_servicepoint_id + "/externalservicepoint/"

        # Create the external servicepoint reference in Esteettömyyssovellus
        try:
            create_response = requests.post(
                externalservicepoint_url,
                json=externalservicepoint_data,
                # headers=authorization_headers,
                timeout=5
            )

            self.stdout.write("Response for kaupunkialusta_id " + str(kaupunkialusta_id) + " tpr_internal_id " + str(tpr_internal_id) + ": " + str(create_response.status_code) + " - " + str(create_response.content))
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))


    def handle(self, *args, **options):
        self.stdout.write("Exporting data to esteettomyyssovellus")

        try:
            # Export the kaupunkialusta id mappings using the Esteettömyyssovellus API
            for id_mapping in IdMappingAll.objects.all().filter(kaupunkialusta_id__isnull = False):
                self.stdout.write("Adding external reference for kaupunkialusta_id " + str(id_mapping.kaupunkialusta_id) + " tpr_internal_id " + str(id_mapping.tpr_internal_id))

                self.add_accessibility_external_reference(id_mapping.kaupunkialusta_id, "kaupunkialusta@hel.fi", id_mapping.tpr_internal_id)

        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))

        # Success
        self.stdout.write(self.style.SUCCESS("Export to esteettomyyssovellus completed"))
