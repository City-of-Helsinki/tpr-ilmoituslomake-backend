from storages.backends.azure_storage import AzureStorage

from ilmoituslomake.settings import PRIVATE_AZURE_CONTAINER
from ilmoituslomake.settings import PRIVATE_AZURE_CONNECTION_STRING


class PrivateAzureStorage(AzureStorage):
    azure_container = PRIVATE_AZURE_CONTAINER
    connection_string = PRIVATE_AZURE_CONNECTION_STRING
