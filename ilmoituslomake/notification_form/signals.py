from django.db.models.signals import pre_save
from django.dispatch import receiver
from opening_times.utils import create_hauki_resource
from notification_form.models import Notification


@receiver(pre_save, sender=Notification)
def pre_save_create_hauki_resource(sender, instance, **kwargs):
    if instance.id is None:
        try:
            resource = create_hauki_resource(
                instance.data["name"],
                instance.data["description"]["short"],
                {
                    "fi": instance.data["address"]["fi"]["street"],
                    "sv": instance.data["address"]["sv"]["street"],
                    "en": instance.data["address"]["fi"]["street"],
                },
                "unit",
                None,
                True,
                "Europe/Helsinki",
            )
            if resource.json() is not None:
                instance.hauki_id = resource.json()["id"]
        except Exception as e:
            pass
