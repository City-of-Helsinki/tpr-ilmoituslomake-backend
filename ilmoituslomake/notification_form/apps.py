from django.apps import AppConfig


class NotificationFormConfig(AppConfig):
    name = "notification_form"

    def ready(self):
        import notification_form.signals