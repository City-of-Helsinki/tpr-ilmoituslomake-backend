from django.shortcuts import render
from requests.models import Response
from rest_framework import response, status
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
import requests
import hashlib 
import hmac 
import urllib.parse
import datetime

# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

# Create your views here.
REQUEST_URL = "https://hauki-api.test.hel.ninja/v1/resource/tprek:", id, "/"
API_TOKEN = '' # ADD API TOKEN HERE
HAUKI_SECRET_KEY = ''# ADD HAUKI_SECRET_KEY_HERE

class CreateLink(APIView):
    permission_classes = [IsAuthenticated]

    def update(self, request, id=None, *args, **kwargs):

        # Request params
        request_params = request.data
        name = request_params["name"]
        description = request_params["description"]
        address = request_params["address"]
        resource_type = request_params["resource_type"]
        children = [0]
        parents = [0]
        organization = request_params["organization"]
        origins = request_params["origins"]
        extra_data = {"property1": None, "propery2": None}
        is_public = True
        timezone = request_params["timezone"]

        # Check if resource exists
        response = requests.get(REQUEST_URL)
        authorization_headers = {'Authorization': API_TOKEN}

        post_response = {}

        if response.status_code == 200:
            # Update data at v1_resource_partial_update
            update_params = {
                "name": name,
                "address": address,
            }
            update_response = requests.put(REQUEST_URL, params=update_params, headers=authorization_headers)
            if update_response.status_code != 200:
                return Response(None, status=status.HTTP_400_BAD_REQUEST)
            post_response = update_response.json()
        else:
            # Create data at v1_resource_create
            create_params = {                
                "name": name,
                "description": description,
                "address": address,
                "resource_type": resource_type,
                "children": children,
                "parents": parents,
                "organization": organization,
                "origins": origins,
                "extra_data": extra_data, 
                "is_public": is_public, 
                "timezone": timezone,
            }
            create_response = requests.post("https://hauki-api.test.hel.ninja/v1/resource/", params=create_params, headers=authorization_headers)
            if create_response.status_code != 201:
                return Response(None, status=status.HTTP_400_BAD_REQUEST)
            post_response = create_response.json()
        
        valid_until = datetime.datetime.strptime(post_response["updated"], '%Y-%m-%dT%H:%M:%S.%f%z') + datetime.timedelta(hours = 1)

        # Construct the url
        hsa_source = origins[0]["data_source"]["id"]
        hsa_username = request.user.username
        hsa_created_at = post_response["created"]
        # TODO: Chekc whether this is correct
        hsa_valid_until = valid_until.isoformat()
        hsa_organization = organization
        hsa_resource = origins[0]["data_source"]["id"]
        hsa_has_organization_rights = ""

        url = create_url(hsa_source, hsa_username, hsa_created_at, hsa_valid_until, hsa_organization, hsa_resource, hsa_has_organization_rights)

        return Response(url, status=status.HTTP_200_OK)


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


# def create_hash():

#     secret_key = ( 
#     )

#     get_parameters_string = "hsa_source=tprek&hsa_username=liikunnan+p%C3%A4%C3%A4k%C3%A4ytt%C3%A4j%C3%A4&hsa_organization=tprek%3Aa1a3a5ea-39bd-482b-b90d-7dfc436c3afb&hsa_resource=tprek%3A570467&hsa_created_at=2020-10-01T06%3A35%3A00.917Z&hsa_valid_until=2020-10-01T06%3A45%3A00.917Z&hsa_signature=3852119bcdc666da8092b041c1245bcd1ff695df8d1c66dcfdb4e68cfe0ca3f3"  

#     payload = dict(urllib.parse.parse_qsl(get_parameters_string))  

#     data_fields = [ 
#         "hsa_source", 
#         "hsa_username", 
#         "hsa_created_at", 
#         "hsa_valid_until", 
#         "hsa_organization", 
#         "hsa_resource", 
#         "hsa_has_organization_rights", 
#     ] 

#     data_string = "".join([payload[field] for field in data_fields if field in payload]) 

#     payload_signature = payload["hsa_signature"] 

#     calculated_signature = hmac.new(
#         key=secret_key.encode("utf-8"), 
#         msg=data_string.encode("utf-8"), 
#         digestmod=hashlib.sha256, 
#     ).hexdigest() 

#     print("Payload sig   : ", payload_signature) 
#     print("Calculated sig: ", calculated_signature) 

#     if hmac.compare_digest(payload_signature, calculated_signature): 
#         print("Payload ok") 
#     else: 
#         print("Invalid payload") 
