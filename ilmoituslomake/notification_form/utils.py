from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from pyproj import Transformer
from urllib.parse import quote_plus
from base.models import (
    IdMappingAll,
    IdMappingKaupunkialustaMaster,
)
from ilmoituslomake.settings import (
    ACCESSIBILITY_API_URL,
    ACCESSIBILITY_APP_URL,
    TPR_SYSTEM_ID,
    TPR_CHECKSUM_SECRET,
    KAUPUNKIALUSTA_SYSTEM_ID,
    KAUPUNKIALUSTA_CHECKSUM_SECRET,
)
import hashlib
import requests


def get_valid_tpr_internal_id(kaupunkialusta_id):
    # Get the id mapping data to determine the esteettömyyssovellus servicepoint to link to
    id_mapping_all = None
    id_mapping_kaupunkialusta_master = None
    try:
        id_mapping_all = IdMappingAll.objects.get(kaupunkialusta_id = kaupunkialusta_id)
    except Exception as e:
        # return Response("Esteettömyyssovellus link creation failed, could not get mapping for id " + str(kaupunkialusta_id) + ".", status=status.HTTP_400_BAD_REQUEST)
        pass

    try:
        id_mapping_kaupunkialusta_master = IdMappingKaupunkialustaMaster.objects.get(kaupunkialusta_id = kaupunkialusta_id)
    except Exception as e:
        # return Response("Esteettömyyssovellus link creation failed, could not get master mapping for id " + str(kaupunkialusta_id) + ".", status=status.HTTP_400_BAD_REQUEST)
        pass

    # If the moderated notification id (kaupunkialusta id) exists in id_mapping_all, but not in id_mapping_kaupunkialusta_master, then the
    # accessibility info cannot be added via kaupunkialusta, since it is not the master of the place, for example 'Helsingin kaupunginmuseo'.
    # Otherwise return the tpr internal id found, or -1 if no ids are found to indicate this is a new place in kaupunkialusta
    valid_tpr_internal_id = None
    if id_mapping_all != None and id_mapping_kaupunkialusta_master == None:
        return Response("Esteettömyyssovellus link creation failed, not allowed to manage accessibility info for id " + str(kaupunkialusta_id) + ".", status=status.HTTP_400_BAD_REQUEST)
    elif id_mapping_kaupunkialusta_master != None:
        valid_tpr_internal_id = id_mapping_kaupunkialusta_master.tpr_internal_id
    elif id_mapping_kaupunkialusta_master == None or id_mapping_kaupunkialusta_master.tpr_internal_id == None:
        valid_tpr_internal_id = -1

    return Response(valid_tpr_internal_id, status=status.HTTP_200_OK)


def get_valid_until_next_day():
    # Return the current UTC datetime + 1 day in ISO format
    # Note that the string does not end with 'Z'
    now = datetime.utcnow().replace(microsecond=0)
    valid_until = (now + timedelta(days=1)).isoformat()
    return valid_until


def add_accessibility_external_reference(kaupunkialusta_id, kaupunkialusta_user, tpr_internal_id):
    # Add the published notification id to Esteettömyyssovellus as an external reference
    tpr_servicepoint_id = str(tpr_internal_id)
    kaupunkialusta_servicepoint_id = str(kaupunkialusta_id)
    valid_until = get_valid_until_next_day()

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
        return Response(create_response)
    except Exception as e:
        return Response("Esteettömyyssovellus link creation failed, external reference could not be created for id " + str(kaupunkialusta_id) + ".", status=status.HTTP_400_BAD_REQUEST)


def get_accessibility_url(kaupunkialusta_id, kaupunkialusta_user, moderated_data):
    # Get the url for opening Esteettömyyssovellus to show and edit accessibility info
    kaupunkialusta_servicepoint_id = str(kaupunkialusta_id)
    valid_until = get_valid_until_next_day()

    # Get the published notification values to use in the accessibility url
    name_obj = moderated_data["name"]
    name = name_obj["fi"] or name_obj["sv"] or name_obj["en"]
    address_obj = moderated_data["address"]
    address_obj_fi = address_obj["fi"]
    address_obj_sv = address_obj["sv"]
    street_address = address_obj_fi["street"] or address_obj_sv["street"]
    post_office = address_obj_fi["post_office"] or address_obj_sv["post_office"]

    # Convert the lat/lon location to EUREF-FIN coordinates
    location = moderated_data["location"]
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3067")
    coordinates = transformer.transform(location[0], location[1])
    easting = str(round(coordinates[0]))
    northing = str(round(coordinates[1]))

    # Calculate the checksum using the values
    accessibility_checksum_string = (
        str(KAUPUNKIALUSTA_CHECKSUM_SECRET)
        + str(KAUPUNKIALUSTA_SYSTEM_ID)
        + str(kaupunkialusta_servicepoint_id)
        + str(kaupunkialusta_user)
        + str(valid_until)
        + str(street_address)
        + str(post_office)
        + str(name)
        + str(northing)
        + str(easting)
    )
    accessibility_checksum = hashlib.sha256(accessibility_checksum_string.encode("utf-8")).hexdigest()

    # Construct the Esteettömyyssovellus url, using quote_plus to urlencode the values
    accessibility_url = (
        ACCESSIBILITY_APP_URL
        + "?systemId=" + KAUPUNKIALUSTA_SYSTEM_ID
        + "&servicePointId=" + kaupunkialusta_servicepoint_id
        + "&user=" + quote_plus(kaupunkialusta_user)
        + "&validUntil=" + quote_plus(valid_until)
        + "&name=" + quote_plus(name)
        + "&streetAddress=" + quote_plus(street_address)
        + "&postOffice=" + quote_plus(post_office)
        + "&northing=" + northing
        + "&easting=" + easting
        + "&checksum=" + accessibility_checksum
    )

    return accessibility_url
