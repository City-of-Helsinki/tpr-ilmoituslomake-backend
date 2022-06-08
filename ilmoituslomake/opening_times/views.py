from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
import requests
from datetime import datetime, timedelta
from moderation.models import ModeratedNotification
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


def update_name_and_address(name, address, url):
    update_params = {
        "name": name,
        "address": address,
    }
    update_response = partially_update_hauki_resource(url, update_params)
    return update_response


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
        published = request_params["published"]
        # id and hauki_id must be string
        hauki_id = str(request_params["hauki_id"])
        id = str(id)

        hsa_resource = hauki_id

        # Search for the pure hauki_id from Hauki.
        hauki_id_response = requests.get(HAUKI_API_URL + hauki_id + "/", timeout=10)
        # Search for id from Hauki
        id_response = requests.get(
            HAUKI_API_URL + "kaupunkialusta:" + id + "/", timeout=10
        )

        # CASE PUBLISHED
        # IF MODERATION ID IN HAUKI -> UPDATE NAME -> hsa_resource = kaupunkialusta:id
        # IF HAUKI ID IN HAUKI -> UPDATE ORIGIN AND NAME -> hsa_resource = kaupunkialusta:id
        # IF NEITHER IN HAUKI -> CREATE RESOURCE -> hsa_resource = kaupunkialusta:id
        if published:
            if id_response.status_code == 200:
                hsa_resource = "kaupunkialusta:" + id
                update_response = update_name_and_address(
                    name, address, HAUKI_API_URL + "kaupunkialusta:" + id + "/"
                )
                if update_response.status_code != 200:
                    return update_response
            elif hauki_id_response.status_code == 200:
                hsa_resource = "kaupunkialusta:" + id
                update_response = update_origin(id, hauki_id)
                if update_response.status_code != 200:
                    return Response(update_response)
                update_response = update_name_and_address(
                    name, address, HAUKI_API_URL + hauki_id + "/"
                )
                if update_response.status_code != 200:
                    return Response(update_response)
            else:
                moderated_notification = ModeratedNotification.objects.get(pk=id)
                hsa_resource = "kaupunkialusta:" + id
                # Create new hauki resource
                origins = [
                    {
                        "data_source": {
                            "id": "kaupunkialusta",
                        },
                        "origin_id": id,
                    }
                ]

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
                moderated_notification.hauki_id = create_response.json()["id"]
                moderated_notification.save()

        # CASE NOT PUBLISHED
        # IF DRAFT IN HAUKI -> UPDATE NAME -> hsa_resource = kaupunkialusta:draft-id
        # IF HAUKI ID IN HAUKI -> UPDATE ORIGIN AND NAME -> hsa_resource = hauki_id
        # ELSE -> CREATE DRAFT -> hsa_resource = hauki_id
        else:
            hauki_draft_response = requests.get(
                HAUKI_API_URL + "kaupunkialusta:draft-" + id + "/", timeout=10
            )
            if hauki_draft_response.status_code == 200:
                hsa_resource = "kaupunkialusta:draft-" + id
                update_response = update_name_and_address(
                    name, address, HAUKI_API_URL + "kaupunkialusta:draft-" + id + "/"
                )
                if update_response.status_code != 200:
                    return Response(update_response)
            elif hauki_id_response.status_code == 200:
                hsa_resource = hauki_id
                update_response = update_origin(id, hauki_id)
                if update_response.status_code != 200:
                    return Response(update_response)
                update_response = update_name_and_address(
                    name, address, HAUKI_API_URL + hauki_id + "/"
                )
                if update_response.status_code != 200:
                    return Response(update_response)
            else:
                origins = [
                    {
                        "data_source": {
                            "id": "kaupunkialusta",
                        },
                        "origin_id": "draft-" + id,
                    }
                ]
                create_response = create_hauki_resource(
                    name,
                    description,
                    address,
                    resource_type,
                    origins,
                    is_public,
                    timezone,
                )
                notification = Notification.objects.filter(pk=id)
                if create_response.status_code != 201:
                    return Response(create_response)
                notification.update(hauki_id=create_response.json()["id"])
                # FOR SOME REASON .save() CREATES A NEW INSTANCE INSTEAD OF UPDATING THE CURRENT ONE
                # notification.hauki_id = create_response.json()["id"]
                # notification.save()
                hsa_resource = str(create_response.json()["id"])

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
            timeout=10,
        )
        return Response(response.json(), status=status.HTTP_200_OK)
