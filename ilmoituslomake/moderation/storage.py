from storages.backends.azure_storage import AzureStorage

from ilmoituslomake.settings import PUBLIC_AZURE_CONTAINER
from ilmoituslomake.settings import PUBLIC_AZURE_CONNECTION_STRING


class PublicAzureStorage(AzureStorage):
    azure_container = PUBLIC_AZURE_CONTAINER
    connection_string = PUBLIC_AZURE_CONNECTION_STRING
