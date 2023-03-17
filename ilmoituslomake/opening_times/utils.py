from rest_framework.response import Response
from rest_framework import status
from ilmoituslomake.settings import (
    API_TOKEN,
    HAUKI_API_URL,
    HAUKI_SECRET_KEY,
    HAUKI_UI_URL,
)
import hashlib
import hmac
import requests
import json

REQUIRED_AUTH_PARAM_NAMES = [
    "hsa_source",
    "hsa_username",
    "hsa_created_at",
    "hsa_valid_until",
    "hsa_signature",
]

OPTIONAL_AUTH_PARAM_NAMES = [
    "hsa_organization",
    "hsa_resource",
    "hsa_has_organization_rights",
]


def calculate_signature(source_string):
    """
    Calculates the hmac signature
    """
    return hmac.new(
        key=HAUKI_SECRET_KEY.encode("utf-8"),
        msg=source_string.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()


def create_url(url_data):
    """
    Creates the Hauki UI url
    """
    # Create data string from required and optional params
    data_fields = [
        i
        for i in (REQUIRED_AUTH_PARAM_NAMES + OPTIONAL_AUTH_PARAM_NAMES)
        if i != "hsa_signature"
    ]
    data_string = "".join([url_data.get(field_name, "") for field_name in data_fields])

    # Calculate the signature from the data string
    calculated_signature = calculate_signature(data_string)

    # Add different parameters to the url string
    param_string = (
        "hsa_source="
        + url_data.get("hsa_source")
        + "&hsa_username="
        + url_data.get("hsa_username")
    )
    param_string = (
        param_string
        + "&hsa_created_at="
        + url_data.get("hsa_created_at")
        + "&hsa_valid_until="
        + url_data.get("hsa_valid_until")
    )

    # Optional params
    if url_data.get("hsa_resource") != "":
        param_string = param_string + "&hsa_resource=" + url_data.get("hsa_resource")
    if url_data.get("hsa_organization") != "":
        param_string = (
            param_string + "&hsa_organization=" + url_data.get("hsa_organization")
        )

    param_string = (
        param_string
        + "&hsa_has_organization_rights="
        + url_data.get("hsa_has_organization_rights")
        + "&hsa_signature="
        + calculated_signature
    )

    # Return url string
    return HAUKI_UI_URL + url_data.get("hsa_resource") + "/?" + param_string


def create_or_update_draft_hauki_data(published_id, draft_id, notification_data, stop_on_error):
    published_resource = "kaupunkialusta:" + published_id
    draft_resource = "kaupunkialusta:" + draft_id

    # Get the data values from the notification
    data_response = get_hauki_data_from_notification(draft_id, notification_data)

    name = data_response["name"]
    description = data_response["description"]
    address = data_response["address"]
    resource_type = data_response["resource_type"]
    origins = data_response["origins"]
    is_public = data_response["is_public"]
    timezone = data_response["timezone"]

    published_id_response = None
    try:
        # Search for published id from Hauki
        published_id_response = requests.get(
            HAUKI_API_URL + "resource/" + published_resource + "/", timeout=10
        )
    except Exception as e:
        pass

    draft_id_response = None
    try:
        # Search for draft id from Hauki
        draft_id_response = requests.get(
            HAUKI_API_URL + "resource/" + draft_resource + "/", timeout=10
        )
    except Exception as e:
        pass

    if draft_id_response != None and draft_id_response.status_code == 200:
        # Draft kaupunkialusta id already exists in Hauki, so just update the name and address
        update_response = update_name_and_address(
            name, address, draft_resource
        )

        if stop_on_error == True and update_response.status_code != 200:
            return Response(update_response)
    elif draft_id_response != None:
        # Draft kaupunkialusta id does not exist in Hauki, so create it
        create_response = create_hauki_resource(
            name,
            description,
            address,
            resource_type,
            origins,
            is_public,
            timezone,
        )

        if stop_on_error == True and create_response.status_code != 201:
            return Response(create_response)

        if published_id_response.status_code == 200:
            # Kaupunkialusta id already exists in Hauki, so copy the published date periods to the draft resource
            copy_response = copy_hauki_date_periods(published_resource, draft_resource)

            if stop_on_error == True and copy_response.status_code != 200:
                return Response(copy_response)


def update_origin(
    origin_id,
    resource,
    is_draft=False,
    id="kaupunkialusta",
    name_fi=None,
    name_sv=None,
    name_en=None,
):
    """
    Update the origin of the given target.
    Returns the response json
    """
    # Get the existing data
    try:
        response = requests.get(HAUKI_API_URL + "resource/" + str(resource) + "/", timeout=5)
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)

    # Check if response is successful
    if response.status_code != 200:
        return response

    # If the notification is a draft add "ilmoitus-" -prefix.
    if is_draft:
        origin_id = "ilmoitus-" + str(origin_id)
    # Add the new origin to existing origins.
    origin = {
        "data_source": {
            "id": id,
        },
        "origin_id": origin_id,
    }

    # Add the new origin to existing ones.
    origins = []
    for item in response.json()["origins"]:
        if item["data_source"]["id"] != "kaupunkialusta":
            origins.append(item)

    origins.append(origin)

    update_params = {
        "origins": origins,
    }

    # Partially update the resource
    return partially_update_hauki_resource(HAUKI_API_URL + "resource/" + str(resource) + "/", update_params)


def update_name_and_address(name, address, resource):
    update_params = {
        "name": name,
        "address": address,
    }
    return partially_update_hauki_resource(HAUKI_API_URL + "resource/" + resource + "/", update_params)


def get_hauki_data_from_notification(origin_id, notification_data):
    # Get the name and description from the notification
    name = {
        "fi": notification_data["name"]["fi"],
        "sv": notification_data["name"]["sv"],
        "en": notification_data["name"]["en"]
    }
    description = {
        "fi": notification_data["description"]["short"]["fi"],
        "sv": notification_data["description"]["short"]["sv"],
        "en": notification_data["description"]["short"]["en"]
    }

    # Get the address from the notification
    addressFi = notification_data["address"]["fi"]
    addressSv = notification_data["address"]["sv"]
    if len(addressFi["street"]) > 0:
        addressStrFi = addressFi["street"] + ", " + addressFi["postal_code"] + " " + addressFi["post_office"]
    else:
        addressStrFi = ""
    if len(addressSv["street"]) > 0:
        addressStrSv = addressSv["street"] + ", " + addressSv["postal_code"] + " " + addressSv["post_office"]
    else:
        addressStrSv = ""
    address = {
        "fi": addressStrFi,
        "sv": addressStrSv,
        "en": addressStrFi,
    }

    # Get the other data
    resource_type = "unit"
    origins = [{
        "data_source": {
            "id": "kaupunkialusta",
        },
        "origin_id": origin_id,
    }]
    is_public = True
    timezone = "Europe/Helsinki"

    return {
        "name": name,
        "description": description,
        "address": address,
        "resource_type": resource_type,
        "origins": origins,
        "is_public": is_public,
        "timezone": timezone
    }


def create_hauki_resource(
    name, description, address, resource_type, origins, is_public, timezone
):
    # Authorization header.
    authorization_headers = {"Authorization": "APIToken " + API_TOKEN}
    # Params to create a hauki resource.
    create_params = {
        "name": name,
        "description": description,
        "address": address,
        "resource_type": resource_type,
        "origins": origins,
        "is_public": is_public,
        "timezone": timezone,
        "organization": "tprek:0c71aa86-f76c-466b-b6f3-81143bd9eecc",
    }

    try:
        create_response = requests.post(
            HAUKI_API_URL + "resource/",
            json=create_params,
            headers=authorization_headers,
            timeout=5
        )
        return create_response
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    # If try fails, return 400.
    return Response("Hauki creation failed.", status=status.HTTP_400_BAD_REQUEST)


def copy_hauki_date_periods(from_resource, to_resource):
    # Authorization header.
    authorization_headers = {"Authorization": "APIToken " + API_TOKEN}

    try:
        copy_response = requests.post(
            HAUKI_API_URL + "resource/" + str(from_resource) + "/copy_date_periods/?replace=true&target_resources=" + str(to_resource),
            headers=authorization_headers,
            timeout=5
        )
        return copy_response
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    # If try fails, return 400.
    return Response("Hauki copy failed.", status=status.HTTP_400_BAD_REQUEST)


def delete_hauki_resource(resource):
    # Authorization header.
    authorization_headers = {"Authorization": "APIToken " + API_TOKEN}

    try:
        delete_response = requests.delete(
            HAUKI_API_URL + "resource/" + str(resource), headers=authorization_headers, timeout=5
        )
        return delete_response
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    # If try fails, return 400.
    return Response("Hauki delete failed.", status=status.HTTP_400_BAD_REQUEST)


def partially_update_hauki_resource(url, update_params):
    """
    Function for updating hauki resources
    """
    authorization_headers = {"Authorization": "APIToken " + API_TOKEN}
    errormessage = ""
    try:
        update_response = requests.patch(
            url, json=update_params, headers=authorization_headers, timeout=10
        )
        return update_response
    except requests.exceptions.HTTPError as errh:
        errormessage = errh
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        errormessage = errc
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        errormessage = errt
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        errormessage = err
        print("OOps: Something Else", err)
    # If try fails, return 400.
    return Response(
        "Hauki update failed." + str(errormessage), status=status.HTTP_400_BAD_REQUEST
    )


def log_to_error_log(string):
    """
    Helper function to write stuff to a logfile.
    """
    with open("logfile.txt", "w") as convert_file:
        convert_file.write(json.dumps(string))
