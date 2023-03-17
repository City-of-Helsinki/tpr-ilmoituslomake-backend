from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
import requests
from ilmoituslomake.settings import HAUKI_API_URL
from opening_times.utils import (
    copy_hauki_date_periods,
    create_hauki_resource,
    create_or_update_draft_hauki_data,
    delete_hauki_resource,
    get_hauki_data_from_notification,
    update_name_and_address,
)

from notification_form.models import Notification
from moderation.models import ModerationItem, ModeratedNotification


@receiver(post_save, sender=Notification)
def create_moderation_item(sender, instance, **kwargs):
    # Create ModerationItem if status is not approved or rejected
    if not instance.status in ["rejected", "approved"]:
        moderated_notification = None
        try:
            if instance.moderated_notification_id > 0:
                moderated_notification = ModeratedNotification.objects.get(
                    pk=instance.moderated_notification_id
                )
        except Exception as e:
            moderated_notification = None

        if instance.moderated_notification_id > 0:
            # ids must be string
            published_id = str(instance.moderated_notification_id)
            draft_id = "ilmoitus-" + str(instance.id)

            # Create or update draft opening times in Hauki using the draft notification data and published opening times if possible
            create_or_update_draft_hauki_data(published_id, draft_id, instance.data, False)

        moderation_item = ModerationItem(
            target=moderated_notification,
            target_revision=moderated_notification.revision
            if moderated_notification
            else 0,
            notification_target=instance,
            notification_target_revision=instance.revision,
            category="moderation_task",
            item_type=instance.status,
            data=instance.data,
        )
        moderation_item.save()


@receiver(post_save, sender=ModeratedNotification)
def update_hauki_after_moderation(sender, instance, **kwargs):
    published_id = str(instance.id)
    draft_id = "ilmoitus-" + str(instance.notification_id)

    published_resource = "kaupunkialusta:" + published_id
    draft_resource = "kaupunkialusta:" + draft_id

    if instance.status == "approved" and instance.notification_id > 0:
        # Get the data from the approved notification
        data_response = get_hauki_data_from_notification(published_id, instance.data)

        name = data_response["name"]
        description = data_response["description"]
        address = data_response["address"]
        resource_type = data_response["resource_type"]
        origins = data_response["origins"]
        is_public = data_response["is_public"]
        timezone = data_response["timezone"]

        published_id_response = None
        try:
            # Search for published id from Hauki
            published_id_response = requests.get(
                HAUKI_API_URL + "resource/" + published_resource + "/", timeout=10
            )
        except Exception as e:
            pass

        if published_id_response != None and published_id_response.status_code == 200:
            # Published kaupunkialusta id already exists in Hauki, so just update the name and address
            update_response = update_name_and_address(
                name, address, published_resource
            )
        elif published_id_response != None:
            # Published kaupunkialusta id does not exist in Hauki, so create it
            create_response = create_hauki_resource(
                name,
                description,
                address,
                resource_type,
                origins,
                is_public,
                timezone,
            )

        if instance.hauki_id > 0:
            # The date periods themselves were approved, so copy the draft date periods to the published resource
            copy_response = copy_hauki_date_periods(draft_resource, published_resource)

    if instance.notification_id > 0:
        # Check if the draft resource is still needed by an open moderation item
        # There may be two or more moderation items for the same notification target, so the draft date periods are needed for all of them
        moderation_item_count = 0
        try:
            moderation_item_count = ModerationItem.objects.filter(notification_target_id = instance.notification_id, status = "open").count()
        except Exception as e:
            pass

        if moderation_item_count <= 1:
            # There are no open moderation items for this draft resource (apart from this one), so delete it
            delete_hauki_resource(draft_resource)
