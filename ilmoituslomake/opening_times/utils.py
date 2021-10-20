from ilmoituslomake.settings import API_TOKEN, HAUKI_SECRET_KEY
import hashlib 
import hmac 
import urllib.parse
import requests
import json
REQUEST_URL = "https://hauki-api.test.hel.ninja/v1/resource/"

def create_url(hsa_source, hsa_username, hsa_created_at, hsa_valid_until, hsa_organization, hsa_resource, hsa_has_organization_rights):
    secret_key = HAUKI_SECRET_KEY
    data_fields = [hsa_source, hsa_username, hsa_created_at, hsa_valid_until, hsa_organization, hsa_resource, hsa_has_organization_rights]
    data_string = ''.join(filter(None, data_fields)) 
    
    calculated_signature = hmac.new(
        key=secret_key.encode("utf-8"), 
        msg=data_string.encode("utf-8"), 
        digestmod=hashlib.sha256, 
    ).hexdigest() 


    param_string = "hsa_username=" + hsa_username 
    
    if hsa_organization != "":
        param_string = param_string + "&hsa_organization=" + hsa_organization
    if hsa_resource != "":
        param_string = param_string + "&hsa_resource=" + hsa_resource 
        
    param_string = param_string + "&hsa_created_at=" + hsa_created_at + "&hsa_valid_until=" + hsa_valid_until + "&hsa_signature=" + calculated_signature

    return "https://hauki-admin.example.com/?" + param_string


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
    return update_params
