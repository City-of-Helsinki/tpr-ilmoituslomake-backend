from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
import requests
from datetime import datetime, timedelta
from moderation.models import ModeratedNotification
from notification_form.models import Notification
from opening_times.utils import (
    copy_hauki_date_periods,
    create_hauki_resource,
    create_url,
    delete_hauki_resource,
    get_hauki_data_from_notification,
    partially_update_hauki_resource,
    update_name_and_address,
    update_origin,
)
from ilmoituslomake.settings import HAUKI_API_URL, HAUKI_API_DATE_URL

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny


class CreateLink(UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None, *args, **kwargs):

        # Request params
        request_params = request.data

        # ids must be string
        # hauki_id = str(request_params["hauki_id"])
        notification_id = str(id)
        published_id = str(request_params["published_id"])
        draft_id = "ilmoitus-" + notification_id

        published_resource = "kaupunkialusta:" + published_id
        draft_resource = "kaupunkialusta:" + draft_id

        try:
            notification = Notification.objects.get(pk = notification_id)
        except Exception as e:
            return Response("Hauki link creation failed, notification " + notification_id + " does not exist.", status=status.HTTP_400_BAD_REQUEST)

        # Get the data from the draft notification
        data_response = get_hauki_data_from_notification(draft_id, notification.data)

        name = data_response["name"]
        description = data_response["description"]
        address = data_response["address"]
        resource_type = data_response["resource_type"]
        origins = data_response["origins"]
        is_public = data_response["is_public"]
        timezone = data_response["timezone"]

        # Search for the pure hauki_id from Hauki. - TODO - CHECK IF THIS IS NEEDED ?
        # hauki_id_response = requests.get(HAUKI_API_URL + "resource/" + hauki_id + "/", timeout=10)
        # Search for published id from Hauki
        published_id_response = None
        try:
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

            if update_response.status_code != 200:
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

            if create_response.status_code != 201:
                return Response(create_response)

            if published_id_response.status_code == 200:
                # Kaupunkialusta id already exists in Hauki, so copy the existing date periods
                copy_response = copy_hauki_date_periods(published_resource, draft_resource)

                if copy_response.status_code != 200:
                    return Response(copy_response)

        # Now time used for link expiration and creation time
        now = datetime.utcnow().replace(microsecond=0)

        # Construct the url
        url_data = {
            "hsa_source": "kaupunkialusta",
            "hsa_username": request.user.email,
            "hsa_created_at": now.isoformat() + "Z",
            "hsa_valid_until": (now + timedelta(hours=1)).isoformat() + "Z",
            "hsa_organization": "tprek:0c71aa86-f76c-466b-b6f3-81143bd9eecc",
            "hsa_resource": draft_resource,
            "hsa_has_organization_rights": "false",
        }
        url = create_url(url_data)

        return Response(url, status=status.HTTP_200_OK)


class GetTimes(RetrieveAPIView):
    """
    Endpoint for getting opening hours of a hauki resource.
    """

    queryset = ""
    permission_classes = [AllowAny]

    def get(self, request, id=None, *args, **kwargs):
        response = requests.get(
            HAUKI_API_URL
            + "date_periods_as_text_for_tprek/?resource="
            + "kaupunkialusta:" + id,
            timeout=10,
        )
        return Response(response.json(), status=status.HTTP_200_OK)
