from storages.backends.azure_storage import AzureStorage

from ilmoituslomake.settings import AZURE_CONTAINER
from ilmoituslomake.settings import AZURE_CONNECTION_STRING


class PublicAzureStorage(AzureStorage):
    azure_container = AZURE_CONTAINER
    connection_string = AZURE_CONNECTION_STRING
