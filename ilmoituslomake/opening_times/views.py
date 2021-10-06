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

from ilmoituslomake.settings import API_TOKEN, HAUKI_SECRET_KEY

# Create your views here.
REQUEST_URL = "https://hauki-api.test.hel.ninja/v1/resource/tprek:", id, "/"

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