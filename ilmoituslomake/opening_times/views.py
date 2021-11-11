from django.shortcuts import get_object_or_404, render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
import requests
from datetime import datetime, timedelta
# Permissions
from rest_framework.permissions import IsAuthenticated
from notification_form.models import Notification
from opening_times.utils import create_hauki_resource, create_url, partially_update_hauki_resource, update_origin
from dateutil import tz
from ilmoituslomake.settings import HAUKI_API_URL

class CreateLink(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    #permission_classes = (permissions.AllowAny,)

    def post(self, request, id=None, *args, **kwargs):

        # Request params
        request_params = request.data
        name = request_params["name"]
        description = request_params["description"]
        address = request_params["address"]
        resource_type = request_params["resource_type"]
        is_public = True
        timezone = request_params["timezone"]
        hauki_id = str(request_params["hauki_id"])
        # Check if resource exists

        id = str(id)
        response = requests.get(HAUKI_API_URL + "kaupunkialusta:" + id + "/")

        if response.status_code == 200:
            # Update data at v1_resource_partial_update
            update_params = {
                "name": name,
                "address": address,
            }
            update_response = partially_update_hauki_resource(HAUKI_API_URL + "kaupunkialusta:" + id + "/", update_params)
            if update_response.status_code != 200:
                return Response(update_response.json(), status=status.HTTP_400_BAD_REQUEST)
        else:
            hauki_id_response = requests.get(HAUKI_API_URL + hauki_id + "/")
            notification = get_object_or_404(Notification, pk=id)
            if hauki_id_response.status_code == 200 and notification.moderated_notification_id != 0: 
                update_origin(id, notification.moderated_notification_id )
            elif notification.moderated_notification_id > 0:
                # Create data at v1_resource_create
                origins = {
                    "data_source": {
                        "id": "kaupunkialusta",
                    },
                    "origin_id": notification.moderated_notification_id
                }
                create_response = create_hauki_resource(name, description, address, resource_type, origins, is_public, timezone)
                if create_response.status_code != 201:
                    return Response(create_response.json(), status=status.HTTP_400_BAD_REQUEST)
        
        # Now time used for link expiration and creation time
        now = datetime.utcnow().replace(microsecond=0)

        hsa_resource = hauki_id
        # Construct the url
        url_data = {
            "hsa_source": "kaupunkialusta", 
            "hsa_username": request.user.email, 
            "hsa_created_at": now.isoformat() + 'Z',
            "hsa_valid_until": (now + timedelta(hours=1)).isoformat() + 'Z',
            "hsa_organization": "tprek:0c71aa86-f76c-466b-b6f3-81143bd9eecc",
            "hsa_resource": hsa_resource,
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
        response = requests.get(HAUKI_API_URL + id + "/opening_hours/" + "?start_date=" + start_date + "&end_date=" + end_date)
        return Response(response.json(), status=status.HTTP_200_OK)
 