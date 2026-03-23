from django.core.management.base import BaseCommand
from moderation.models import ModeratedNotification, ModerationItem
from notification_form.models import Notification

DEFAULTS = {
    "label_ids": [],
    "other_certificates": {"fi": "", "sv": "", "en": ""},
    "other_certificates_url": {"fi": "", "sv": "", "en": ""},
    "no_certificate": False,
}


class Command(BaseCommand):
    help = "Backfill certificate-related fields into existing Notification, ModeratedNotification and ModerationItem records that are missing them"

    def handle(self, *args, **options):
        self._backfill(Notification, "Notification")
        self._backfill(ModeratedNotification, "ModeratedNotification")
        self._backfill(ModerationItem, "ModerationItem")

    def _backfill(self, model, label):
        updated = 0
        for obj in model.objects.all():
            changed = False

            # Derive certificate_ids from existing enriched certificates if missing or empty
            existing_certs = obj.data.get("certificates", [])
            if "certificate_ids" not in obj.data or (obj.data["certificate_ids"] == [] and existing_certs):
                obj.data["certificate_ids"] = [
                    c["id"] for c in existing_certs if "id" in c
                ]
                changed = True

            for field, default in DEFAULTS.items():
                if field not in obj.data or not isinstance(obj.data[field], type(default)):
                    obj.data[field] = default
                    changed = True

            if changed:
                obj.save(update_fields=["data"])
                updated += 1
        self.stdout.write(
            self.style.SUCCESS(f"{label}: updated {updated} records")
        )
