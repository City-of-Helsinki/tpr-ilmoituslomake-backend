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
from rest_framework.permissions import IsAuthenticated


class CreateLink(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    # permission_classes = (permissions.AllowAny,)

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
            return Response("Hauki link creation failed, notification does not exist.", status=status.HTTP_400_BAD_REQUEST)

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
        published_id_response = requests.get(
            HAUKI_API_URL + "resource/" + published_resource + "/", timeout=10
        )
        # Search for draft id from Hauki
        draft_id_response = requests.get(
            HAUKI_API_URL + "resource/" + draft_resource + "/", timeout=10
        )

        if draft_id_response.status_code == 200:
            # Draft kaupunkialusta id already exists in Hauki, so just update the name and address
            update_response = update_name_and_address(
                name, address, draft_resource
            )

            if update_response.status_code != 200:
                return Response(update_response)
        else:
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

        # CASE PUBLISHED
        # IF MODERATION ID IN HAUKI -> UPDATE NAME -> hsa_resource = kaupunkialusta:id
        # IF HAUKI ID IN HAUKI -> UPDATE ORIGIN AND NAME -> hsa_resource = kaupunkialusta:id
        # IF NEITHER IN HAUKI -> CREATE RESOURCE -> hsa_resource = kaupunkialusta:id
        # if published:
        #     if id_response.status_code == 200:
        #         hsa_resource = "kaupunkialusta:" + id
        #         update_response = update_name_and_address(
        #             name, address, HAUKI_API_URL + "resource/kaupunkialusta:" + id + "/"
        #         )
        #         if update_response.status_code != 200:
        #             return update_response
        #     elif hauki_id_response.status_code == 200:
        #         hsa_resource = "kaupunkialusta:" + id
        #         update_response = update_origin(id, hauki_id)
        #         if update_response.status_code != 200:
        #             return Response(update_response)
        #         update_response = update_name_and_address(
        #             name, address, HAUKI_API_URL + "resource/" + hauki_id + "/"
        #         )
        #         if update_response.status_code != 200:
        #             return Response(update_response)
        #     else:
        #         moderated_notification = ModeratedNotification.objects.get(pk=id)
        #         hsa_resource = "kaupunkialusta:" + id
        #         # Create new hauki resource
        #         origins = [
        #             {
        #                 "data_source": {
        #                     "id": "kaupunkialusta",
        #                 },
        #                 "origin_id": id,
        #             }
        #         ]

        #         create_response = create_hauki_resource(
        #             name,
        #             description,
        #             address,
        #             resource_type,
        #             origins,
        #             is_public,
        #             timezone,
        #         )
        #         if create_response.status_code != 201:
        #             return Response(create_response)
        #         moderated_notification.hauki_id = create_response.json()["id"]
        #         moderated_notification.save()

        # CASE NOT PUBLISHED
        # IF DRAFT IN HAUKI -> UPDATE NAME -> hsa_resource = kaupunkialusta:draft-id
        # IF HAUKI ID IN HAUKI -> UPDATE ORIGIN AND NAME -> hsa_resource = hauki_id
        # ELSE -> CREATE DRAFT -> hsa_resource = hauki_id
        # else:
        #     hauki_draft_response = requests.get(
        #         HAUKI_API_URL + "resource/kaupunkialusta:draft-" + id + "/", timeout=10
        #     )
        #     if hauki_draft_response.status_code == 200:
        #         hsa_resource = "kaupunkialusta:draft-" + id
        #         update_response = update_name_and_address(
        #             name, address, HAUKI_API_URL + "resource/kaupunkialusta:draft-" + id + "/"
        #         )
        #         if update_response.status_code != 200:
        #             return Response(update_response)
        #     elif hauki_id_response.status_code == 200:
        #         hsa_resource = hauki_id
        #         update_response = update_origin(id, hauki_id)
        #         if update_response.status_code != 200:
        #             return Response(update_response)
        #         update_response = update_name_and_address(
        #             name, address, HAUKI_API_URL + "resource/" + hauki_id + "/"
        #         )
        #         if update_response.status_code != 200:
        #             return Response(update_response)
        #     else:
        #         origins = [
        #             {
        #                 "data_source": {
        #                     "id": "kaupunkialusta",
        #                 },
        #                 "origin_id": "draft-" + id,
        #             }
        #         ]
        #         create_response = create_hauki_resource(
        #             name,
        #             description,
        #             address,
        #             resource_type,
        #             origins,
        #             is_public,
        #             timezone,
        #         )
        #         notification = Notification.objects.filter(pk=id)
        #         if create_response.status_code != 201:
        #             return Response(create_response)
        #         notification.update(hauki_id=create_response.json()["id"])
        #         # FOR SOME REASON .save() CREATES A NEW INSTANCE INSTEAD OF UPDATING THE CURRENT ONE
        #         # notification.hauki_id = create_response.json()["id"]
        #         # notification.save()
        #         hsa_resource = str(create_response.json()["id"])

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
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None, *args, **kwargs):
        response = requests.get(
            HAUKI_API_URL
            + "date_periods_as_text_for_tprek/?resource="
            + "kaupunkialusta:" + id,
            timeout=10,
        )
        return Response(response.json(), status=status.HTTP_200_OK)
