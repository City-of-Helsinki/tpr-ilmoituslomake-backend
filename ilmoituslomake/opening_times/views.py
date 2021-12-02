from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
import requests
from datetime import datetime, timedelta
from notification_form.models import Notification
from opening_times.utils import (
    create_hauki_resource,
    create_url,
    partially_update_hauki_resource,
    update_origin,
)
from ilmoituslomake.settings import HAUKI_API_URL

# Permissions
from rest_framework.permissions import IsAuthenticated


class CreateLink(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    # permission_classes = (permissions.AllowAny,)

    def post(self, request, id=None, *args, **kwargs):

        # Request params
        request_params = request.data
        name = request_params["name"]
        description = request_params["description"]
        address = request_params["address"]
        resource_type = request_params["resource_type"]
        is_public = True
        timezone = request_params["timezone"]

        # id and hauki_id must be string
        hauki_id = str(request_params["hauki_id"])
        id = str(id)

        # hsa_resource is hauki_id if "kaupunkialusta:id" does not exist in hauki.
        hsa_resource = hauki_id

        # Check if resource exists
        response = requests.get(HAUKI_API_URL + "kaupunkialusta:" + id + "/", timeout=5)

        if response.status_code == 200:
            # Update hsa_resource for the url creation.
            hsa_resource = "kaupunkialusta:" + id
            # Update data at v1_resource_partial_update
            update_params = {
                "name": name,
                "address": address,
            }
            update_response = partially_update_hauki_resource(
                HAUKI_API_URL + "kaupunkialusta:" + id + "/", update_params
            )

            # If the update fails, return the response
            if update_response.status_code != 200:
                return update_response
        else:
            # If kaupunkialusta:id cannot be found in hauki, search for the pure hauki_id.
            hauki_id_response = requests.get(HAUKI_API_URL + hauki_id + "/", timeout=5)
            # Find the notification from the kaupunkialusta db.
            notification = get_object_or_404(Notification, pk=id)
            # If the hauki_id can be found from hauki and the notification is moderated,
            # update the origin of the hauki resource, otherwise create a new hauki resource.
            if (
                hauki_id_response.status_code == 200
                and notification.moderated_notification_id > 0
            ):
                update_origin(id, notification.moderated_notification_id)
                # Update hsa_resource for the url creation.
                hsa_resource = "kaupunkialusta:" + str(
                    notification.moderated_notification_id
                )
            elif notification.moderated_notification_id > 0:
                # Create data at v1_resource_create
                origins = {
                    "data_source": {
                        "id": "kaupunkialusta",
                    },
                    "origin_id": notification.moderated_notification_id,
                }
                create_response = create_hauki_resource(
                    name,
                    description,
                    address,
                    resource_type,
                    origins,
                    is_public,
                    timezone,
                )
                hsa_resource = "kaupunkialusta:" + str(
                    notification.moderated_notification_id
                )
                if create_response.status_code != 201:
                    return create_response

        # Now time used for link expiration and creation time
        now = datetime.utcnow().replace(microsecond=0)

        # Construct the url
        url_data = {
            "hsa_source": "kaupunkialusta",
            "hsa_username": request.user.email,
            "hsa_created_at": now.isoformat() + "Z",
            "hsa_valid_until": (now + timedelta(hours=1)).isoformat() + "Z",
            "hsa_organization": "tprek:0c71aa86-f76c-466b-b6f3-81143bd9eecc",
            "hsa_resource": hsa_resource,
            "hsa_has_organization_rights": "false",
        }
        url = create_url(url_data)

        return Response(url, status=status.HTTP_200_OK)


class GetTimes(RetrieveAPIView):
    """
    Endpoint for getting opening hours of a hauki resource.
    """

    queryset = ""
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None, *args, **kwargs):
        start_date = self.request.query_params.get("start_date", None)
        end_date = self.request.query_params.get("end_date", None)
        response = requests.get(
            HAUKI_API_URL
            + id
            + "/opening_hours/"
            + "?start_date="
            + start_date
            + "&end_date="
            + end_date,
            timeout=5,
        )
        return Response(response.json(), status=status.HTTP_200_OK)
