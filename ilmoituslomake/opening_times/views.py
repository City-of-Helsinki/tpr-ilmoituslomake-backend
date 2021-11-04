from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import response, status
from rest_framework import permissions
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView
import requests
from datetime import datetime, timedelta
# Permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from opening_times.utils import create_url, update_origin
from dateutil import tz
from ilmoituslomake.settings import API_TOKEN, HAUKI_SECRET_KEY

# Create your views here.
REQUEST_URL = "https://hauki-api.dev.hel.ninja/v1/resource/"

class CreateLink(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    #permission_classes = (permissions.AllowAny,)

    def post(self, request, id=None, *args, **kwargs):

        # Auth headers
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
        id = str(id)
        
        # Check if resource exists
        response = requests.get(REQUEST_URL + "kaupunkialusta:" + id + "/")

        if response.status_code == 200:
            # Update data at v1_resource_partial_update
            update_params = {
                "name": name,
                "address": address,
            }
            update_response = requests.patch(REQUEST_URL + "kaupunkialusta:" + id + "/", 
                                             data=update_params, headers=authorization_headers)
            if update_response.status_code != 200:
                return Response(update_response.json(), status=status.HTTP_400_BAD_REQUEST)
        else:
            visithelsinki_response = requests.get(REQUEST_URL + "visithelsinki:" + id + "/")
            if visithelsinki_response.status_code == 200: # or temporary_response == 200:
                update_origin(origin_id=id)
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
                create_response = requests.post("https://hauki-api.dev.hel.ninja/v1/resource/", 
                                                json=create_params, headers=authorization_headers)

                if create_response.status_code != 201:
                    return Response(create_response.json(), status=status.HTTP_400_BAD_REQUEST)
        
        # Now time used for link expiration and creation time
        now = datetime.utcnow().replace(microsecond=0)

        # Construct the url
        url_data = {
            "hsa_source": "kaupunkialusta", 
            "hsa_username": request.user.email, 
            "hsa_created_at": now.isoformat() + 'Z',
            "hsa_valid_until": (now + timedelta(hours=1)).isoformat() + 'Z',
            "hsa_organization": "tprek:0c71aa86-f76c-466b-b6f3-81143bd9eecc",
            "hsa_resource": "kaupunkialusta:" + id,
            "hsa_has_organization_rights": ""
        }
        url = create_url(url_data)

        return Response(url, status=status.HTTP_200_OK)


class GetTimes(RetrieveAPIView):
    queryset = ""

    def get(self, request, id=None, *args, **kwargs):
        if not request.user:
            return Response(None, status=status.HTTP_403_FORBIDDEN)
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)
        response = requests.get(REQUEST_URL + id + "/opening_hours/" + "?start_date=" + start_date + "&end_date=" + end_date)
        return Response(response.json(), status=status.HTTP_200_OK)
