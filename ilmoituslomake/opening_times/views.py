from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import response, status
from rest_framework import permissions
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
import requests
import hashlib 
import hmac 
import urllib.parse
import datetime
import uuid
# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from opening_times.utils import create_url, update_origin
from dateutil import tz
from ilmoituslomake.settings import API_TOKEN, HAUKI_SECRET_KEY

# Create your views here.
REQUEST_URL = "https://hauki-api.test.hel.ninja/v1/resource/"

class CreateLink(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    #permission_classes = (permissions.AllowAny,)

    def post(self, request, id=None, *args, **kwargs):

        authorization_headers = {'Authorization': 'APIToken ' + API_TOKEN}
        # Request params
        request_params = request.data
        name = request_params["name"]
        description = request_params["description"]
        address = request_params["address"]
        resource_type = request_params["resource_type"]
        origins = request_params["origins"]
        is_public = True
        timezone = request_params["timezone"]
        id = "2916"
        # Check if resource exists
        response = requests.get(REQUEST_URL + "kaupunkialusta:" + str(id) + "/")
        post_response = {}

        if response.status_code == 200:
            # Update data at v1_resource_partial_update
            update_params = {
                "name": name,
                "address": address,
            }
            update_response = requests.put(REQUEST_URL + "tprek:" + str(id) + "/", params=update_params, headers=authorization_headers)
            if update_response.status_code != 200:
                return Response(update_response.json(), status=status.HTTP_400_BAD_REQUEST)
            post_response = update_response.json()
        else:
            visithelsinki_response = requests.get(REQUEST_URL + "visithelsinki:" + str(id) + "/")
            if visithelsinki_response.status_code == 200: # or temporary_response == 200:
                post_response = update_origin(origin_id=id)
            else:
                # Create data at v1_resource_create
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
                create_response = requests.post("https://hauki-api.test.hel.ninja/v1/resource/", params=create_params, headers=authorization_headers)
                if create_response.status_code != 201:
                    return Response(create_response.json(), status=status.HTTP_400_BAD_REQUEST)
                post_response = create_response.json()
        
        valid_until = datetime.datetime.strptime(post_response["modified"], '%Y-%m-%dT%H:%M:%S.%f%z') + datetime.timedelta(hours = 1)
        created_at = datetime.datetime.strptime(post_response["created"], '%Y-%m-%dT%H:%M:%S.%f%z')

        from_zone = tz.gettz(post_response["timezone"])
        to_zone = tz.gettz("EET")

        valid_until.replace(tzinfo=from_zone)
        valid_until_in_EET = valid_until.astimezone(to_zone)
        created_at.replace(tzinfo=from_zone)
        created_at_in_EET = created_at.astimezone(to_zone)

        # Construct the url
        url_data = {
            "hsa_source": "tprek", 
            "hsa_username": request.user.username, 
            "hsa_created_at": created_at.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            # TODO: Check whether this is correct
            "hsa_valid_until": valid_until.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z", 
            "hsa_organization": "tprek:0c71aa86-f76c-466b-b6f3-81143bd9eecc",
            "hsa_resource": "tprek:8215",
            "hsa_has_organization_rights": ""
        }
        url = create_url(url_data)

        return Response(url, status=status.HTTP_200_OK)
