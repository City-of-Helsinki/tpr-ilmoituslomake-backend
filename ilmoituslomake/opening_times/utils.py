from ilmoituslomake.settings import API_TOKEN, HAUKI_SECRET_KEY
import hashlib 
import hmac 
import urllib.parse
import requests
import json

REQUEST_URL = "https://hauki-api.test.hel.ninja/v1/resource/"

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
    

    calculated_signature = calculate_signature(data_string)


    param_string = "hsa_source=" + url_data.get("hsa_source") + "&hsa_username=" + url_data.get("hsa_username")
    
    if url_data.get("hsa_organization") != "":
        param_string = param_string + "&hsa_organization=" + url_data.get("hsa_organization")
    if url_data.get("hsa_resource") != "":
        param_string = param_string + "&hsa_resource=" + url_data.get("hsa_resource")
        
    param_string = param_string + "&hsa_created_at=" + url_data.get("hsa_created_at") + "&hsa_valid_until=" + url_data.get("hsa_valid_until") + "&hsa_signature=" + calculated_signature

    # return "https://aukioloajat.hel.fi/" + param_string
    return "https://hauki-admin-ui.dev.hel.ninja/?" + param_string


def update_origin(origin_id, id="kaupunkialusta", name_fi=None, name_sv=None, name_en=None):  
    '''
    Update origin of the given target.
    Returns the response json if successful otherwise {}
    '''
    # Get the existing data
    response = requests.get(REQUEST_URL + "visithelsinki:" + str(origin_id) + "/")
    if response.status_code != 200:
        return response.json()
    authorization_headers = {'Authorization': 'APIToken ' + API_TOKEN}

    origin = {
            "data_source": {
                "id": id,
                "name": {
                    "fi": name_fi,
                    "sv": name_sv,
                    "en": name_en
                }
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

    update_response = requests.patch(REQUEST_URL + "visithelsinki:" + origin_id + "/", data=update_params, headers=authorization_headers)
    if update_response.status_code != 200:
        return update_response.json()
    return update_response.json()
