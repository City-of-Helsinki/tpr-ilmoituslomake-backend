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
    create_or_update_draft_hauki_data,
    create_url,
    delete_hauki_resource,
    get_hauki_data_from_notification,
    partially_update_hauki_resource,
    update_name_and_address,
)
from ilmoituslomake.settings import HAUKI_API_URL

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny


class CreateLink(UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id=None, *args, **kwargs):
        # Use cases with examples:
        #
        # 1. Add notification for new place - published_id '0', draft_id 'ilmoitus-143'
        #   a. User adds opening times or sends notification -> 'kaupunkialusta:ilmoitus-143' added to hauki
        #   b. Moderator changes opening times -> 'kaupunkialusta:ilmoitus-143' updated in hauki
        # 2. Update notification for existing place - published_id '5103', draft_id 'ilmoitus-143'
        #   a. User changes opening times or sends notification -> 'kaupunkialusta:ilmoitus-143' added to hauki
        #   b. Moderator changes opening times -> 'kaupunkialusta:ilmoitus-143' updated in hauki
        # 3. Change request for new place - published_id '0', draft_id '0'
        #   a. No user changes
        #   b. No moderator changes
        # 4. Change request for existing place - published_id '5103', draft_id '0'
        #   a. No user changes
        #   b. Moderator changes opening times -> 'kaupunkialusta:5103' updated in hauki

        # Request params
        request_params = request.data

        # ids must be string
        # hauki_id = str(request_params["hauki_id"])
        published = request_params["published"]
        notification_id = str(id)
        published_id = str(request_params["published_id"])
        draft_id = "ilmoitus-" + notification_id

        published_resource = "kaupunkialusta:" + published_id
        draft_resource = "kaupunkialusta:" + draft_id
        if id > 0:
            hsa_resource = draft_resource
        else:
            hsa_resource = published_resource

        # Fetch the draft notification data if there is a notification id
        # For change requests, notification id may be 0
        notification_data = None
        if id > 0:
            try:
                notification = Notification.objects.get(pk = notification_id)
                notification_data = notification.data
            except Exception as e:
                return Response("Hauki link creation failed, notification " + notification_id + " does not exist.", status=status.HTTP_400_BAD_REQUEST)

        if id > 0:
            # Create or update draft opening times in Hauki using the draft notification data and published opening times if possible
            create_or_update_response = create_or_update_draft_hauki_data(published, published_id, draft_id, notification_data, True)

            if create_or_update_response != None:
                return create_or_update_response

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
    permission_classes = [AllowAny]

    def get(self, request, id=None, *args, **kwargs):
        response = requests.get(
            HAUKI_API_URL
            + "date_periods_as_text_for_tprek/?resource="
            + "kaupunkialusta:" + id,
            timeout=10,
        )
        return Response(response.json(), status=status.HTTP_200_OK)
