from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
import requests
from ilmoituslomake.settings import HAUKI_API_URL
from opening_times.utils import (
    _get_resource_numeric_id,
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
            create_or_update_draft_hauki_data(True, published_id, draft_id, instance.data, False)

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
    # Use cases with examples:
    #
    # 1. Add notification for new place - published_id '0', draft_id 'ilmoitus-143'
    #   - Moderator approves opening times -> 'kaupunkialusta:5103' added to hauki, 'kaupunkialusta:ilmoitus-143' deleted from hauki
    # 2. Update notification for existing place - published_id '5103', draft_id 'ilmoitus-143'
    #   - Moderator approves opening times -> 'kaupunkialusta:5103' updated in hauki, 'kaupunkialusta:ilmoitus-143' deleted from hauki
    # 3. Change request for new place - published_id '0', draft_id '0'
    #   - Moderator approves opening times -> 'kaupunkialusta:5104' added to hauki but opening times are empty
    # 4. Change request for existing place - published_id '5103', draft_id '0'
    #   - Moderator approves opening times -> 'kaupunkialusta:5103' updated in hauki

    published_id = str(instance.id)
    draft_id = "ilmoitus-" + str(instance.notification_id)

    published_resource = "kaupunkialusta:" + published_id
    draft_resource = "kaupunkialusta:" + draft_id

    if instance.status == "approved":
        # Get the data from the approved notification
        data_response = get_hauki_data_from_notification(published_id, instance.data)

        name = data_response["name"]
        description = data_response["description"]
        address = data_response["address"]
        resource_type = data_response["resource_type"]
        origins = data_response["origins"]
        is_public = data_response["is_public"]
        timezone = data_response["timezone"]

        # Look up published resource — non-ilmoitus origins still work with direct GET
        published_numeric_id = None
        try:
            published_id_response = requests.get(
                HAUKI_API_URL + "resource/" + published_resource + "/", timeout=10
            )
            if published_id_response.status_code == 200:
                published_numeric_id = published_id_response.json().get("id")
                update_response = update_name_and_address(
                    name, address, str(published_numeric_id)
                )
            else:
                create_response = create_hauki_resource(
                    name, description, address, resource_type, origins, is_public, timezone
                )
                if create_response.status_code == 201:
                    published_numeric_id = create_response.json().get("id")
        except Exception as e:
            pass

        # If the notification times are rejected, or this is a change request or moderator edit, then hauki_id is 0
        if instance.hauki_id > 0:
            # The date periods themselves were approved, so copy the draft date periods to the published resource
            # Use numeric IDs (Hauki v1.11.0 broke origin-string path lookups for ilmoitus- resources)
            draft_numeric_id = _get_resource_numeric_id(draft_resource)
            if draft_numeric_id is None:
                # Fallback: check the Notification record for a stored hauki_id
                try:
                    notif = Notification.objects.get(pk=instance.notification_id)
                    if notif.hauki_id > 0:
                        draft_numeric_id = notif.hauki_id
                except Exception:
                    pass
            if draft_numeric_id and published_numeric_id:
                copy_response = copy_hauki_date_periods(draft_numeric_id, published_numeric_id)

    if instance.notification_id > 0:
        # Check if the draft resource is still needed by an open moderation item
        # There may be two or more moderation items for the same notification target, so the draft date periods are needed for all of them
        moderation_item_count = 0
        try:
            moderation_item_count = ModerationItem.objects.filter(notification_target_id = instance.notification_id, status = "open").count()
        except Exception as e:
            pass

        if moderation_item_count <= 1:
            # Look up the numeric ID before deleting, and store it in the Notification
            # record so future re-edits can find the resource even after soft-delete.
            draft_numeric_id_for_delete = _get_resource_numeric_id(draft_resource)
            try:
                notif = Notification.objects.get(pk=instance.notification_id)
                if draft_numeric_id_for_delete and notif.hauki_id != draft_numeric_id_for_delete:
                    # Use filter().update() instead of .save() to avoid triggering
                    # the Notification post_save signal (which would create a duplicate ModerationItem)
                    Notification.objects.filter(pk=instance.notification_id).update(hauki_id=draft_numeric_id_for_delete)
                elif draft_numeric_id_for_delete is None and notif.hauki_id > 0:
                    draft_numeric_id_for_delete = notif.hauki_id
            except Exception:
                pass
            # Delete by numeric ID if available, otherwise fall back to origin string
            if draft_numeric_id_for_delete:
                delete_hauki_resource(str(draft_numeric_id_for_delete))
            else:
                delete_hauki_resource(draft_resource)
