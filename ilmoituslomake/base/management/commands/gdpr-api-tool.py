from django.core.management.base import BaseCommand
from django.apps import apps
from django.conf import settings
from django.utils.module_loading import import_string
from users.gdpr import delete_gdpr_data
from users.serializers import GdprSerializer
from rest_framework.renderers import JSONRenderer
import io
import json

def _try_setting_import(setting_name):
    setting_value = getattr(settings, setting_name, None)
    if setting_value:
        try:
            return import_string(setting_value)
        except ImportError:
            pass

    return setting_value


def _user_from_obj(obj):
    user_provider = _try_setting_import("GDPR_API_USER_PROVIDER")
    if callable(user_provider):
        return user_provider(obj)

    return getattr(obj, "user", None)

class Command(BaseCommand):
	help = "access GDPR-API operations"

	def add_arguments(self, parser):
		parser.add_argument('action', type=str, help ='listall|get|delete')
		parser.add_argument('uuid', type=str, nargs='?', default='', help='Identifies the targeted user')



	def to_json_str(self, str):
		serializer = GdprSerializer(str)
		jsondata = JSONRenderer().render(serializer.data)
		return (jsondata.decode('utf-8'))


	def handle(self, *args, **options):
		uuid = options['uuid']
		action = options['action']
		model = apps.get_model(settings.GDPR_API_MODEL)

		if (action == 'listall'):
			objs = model.objects.all()
			for o in objs:
				self.stdout.write(self.to_json_str(o))
				
			return None


		if (action == 'get'):
			try:
				obj = model.objects.get(uuid=uuid)
				self.stdout.write(self.to_json_str(obj))
				return None
			except:
				self.stdout.write("Error: user with uuid="+uuid+" does not exist")
				return None

		user_provider = _try_setting_import("GDPR_API_USER_PROVIDER")

		if (action == 'list-whatever'):
			objs = model.objects.all()
			for q in objs:
				self.stdout.write(str(q))

		if (action == 'delete'):
			lookup_key = "uuid"
			field_lookups = {lookup_key: uuid}
			try:
				obj = model.objects.get(**field_lookups)
				status = delete_gdpr_data(obj, False)
				if status:
					self.stdout.write("deleting"+str(obj.uuid)+" failed")
				else:
					self.stdout.write("user "+str(obj.uuid)+ "was deleted")
			except:
					self.stdout.write("Error: user with uuid="+uuid+"does not exist")

