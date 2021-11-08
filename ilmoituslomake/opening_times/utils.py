from os import error
from ilmoituslomake.settings import API_TOKEN, HAUKI_SECRET_KEY
import hashlib 
import hmac 
import requests

REQUEST_URL = "https://hauki-api.dev.hel.ninja/v1/resource/"

REQUIRED_AUTH_PARAM_NAMES = [
    "hsa_source",
    "hsa_username",
    "hsa_created_at",
    "hsa_valid_until",
    "hsa_signature"
]

OPTIONAL_AUTH_PARAM_NAMES = [
    "hsa_organization",
    "hsa_resource",
    "hsa_has_organization_rights"
]

def calculate_signature(source_string):
    '''
    Calculates the hmac signature
    '''
    return hmac.new(
        key=HAUKI_SECRET_KEY.encode("utf-8"), 
        msg=source_string.encode("utf-8"), 
        digestmod=hashlib.sha256, 
    ).hexdigest() 


def create_url(url_data):
    data_fields = [
        i
        for i in (REQUIRED_AUTH_PARAM_NAMES + OPTIONAL_AUTH_PARAM_NAMES)
        if i != "hsa_signature"
    ]
    data_string = ''.join([url_data.get(field_name, "") for field_name in data_fields]) 

    # Calculate the signature from the data string
    calculated_signature = calculate_signature(data_string)

    param_string = "hsa_source=" + url_data.get("hsa_source") + "&hsa_username=" + url_data.get("hsa_username")
    
    if url_data.get("hsa_organization") != "":
        param_string = param_string + "&hsa_organization=" + url_data.get("hsa_organization")
    if url_data.get("hsa_resource") != "":
        param_string = param_string + "&hsa_resource=" + url_data.get("hsa_resource")
        
    param_string = param_string + "&hsa_created_at=" + url_data.get("hsa_created_at") + "&hsa_valid_until=" + url_data.get("hsa_valid_until") + "&hsa_signature=" + calculated_signature

    return "https://hauki-admin-ui.dev.hel.ninja/" + url_data.get("hsa_resource") + "?" + param_string


def update_origin(origin_id, id="kaupunkialusta", old_id="visithelsinki", name_fi=None, name_sv=None, name_en=None):  
    '''
    Update origin of the given target.
    Returns the response json
    '''
    # Get the existing data
    try:
        response = requests.get(REQUEST_URL + old_id + ":" + origin_id + "/")
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else", err)

    if response.status_code != 200:
        return response.json()

    authorization_headers = {'Authorization': 'APIToken ' + API_TOKEN}

    # Add the new origin to existing origins.
    origin = {
            "data_source": {
                "id": id,
            },
            "origin_id": origin_id
        }
    origins = []
    for item in response.json()["origins"]:
        origins.append(item)
        
    origins.append(origin)

    update_params = {
        "origins": origins
    }

    # Partially update the resource
    try: 
        update_response = requests.patch(REQUEST_URL + old_id + ":" 
            + origin_id + "/", json=update_params, headers=authorization_headers)
        update_response.raise_for_status()
        return update_response.json()
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else", err)


def create_hauki_resource(name, description, address, resource_type, origins, is_public, timezone):
    authorization_headers = {'Authorization': 'APIToken ' + API_TOKEN}
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
        create_response = requests.post("https://hauki-api.dev.hel.ninja/v1/resource/", json=create_params, headers=authorization_headers)
        create_response.raise_for_status()
        return create_response.json()
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else", err)
