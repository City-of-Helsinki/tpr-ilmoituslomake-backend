from django.shortcuts import render, get_object_or_404

from base.image_utils import preprocess_images, process_images

# Permissions
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser

# Create your views here.
from django.contrib.auth.models import User
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import (
    RetrieveAPIView,
    ListAPIView,
    CreateAPIView,
    UpdateAPIView,
)
from rest_framework import filters

#
from moderation.models import ModerationItem
from moderation.serializers import ChangeRequestSerializer

from notification_form.models import Notification, NotificationImage
from moderation.models import ModeratedNotification
from base.models import (
    NotificationSchema,
    OntologyWord,
    MatkoWord,
    IdMappingAll,
    IdMappingKaupunkialustaMaster,
    Certificate,
)

# from notification_form.serializers import NotificationImageSerializer
from base.serializers import (
    NotificationSchemaSerializer,
    OntologyWordSerializer,
    MatkoWordSerializer,
    IdMappingAllSerializer,
    IdMappingKaupunkialustaMasterSerializer,
    CertificateSerializer,
)
from moderation.serializers import (
    PublicModeratedNotificationSerializer,
    ModerationNotificationSerializer,
)

from django.db.models import Q
# from image_utils import preprocess_images, process_images   
from moderation.certificate_utils import enrich_certificates_data, save_customer_certificates   

from notification_form.utils import (
    add_accessibility_external_reference,
    get_accessibility_url,
    get_valid_tpr_internal_id,
)


class NotificationSchemaCreateView(CreateAPIView):
    """
    Create a Notification schema instance
    """

    permission_classes = [IsAdminUser]
    queryset = NotificationSchema.objects.all()
    serializer_class = NotificationSchemaSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class NotificationSchemaUpdateView(UpdateAPIView):
    """
    Update a Notification schema instance
    """

    permission_classes = [IsAdminUser]
    lookup_field = "id"
    queryset = NotificationSchema.objects.all()
    serializer_class = NotificationSchemaSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            serializer.data
        )

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class NotificationSchemaRetrieveView(RetrieveAPIView):
    """
    Returns the schema for form data
    """

    permission_classes = [AllowAny]
    lookup_field = "id"
    queryset = NotificationSchema.objects.all()
    serializer_class = NotificationSchemaSerializer


class ChangeRequestCreateView(CreateAPIView):
    """
    Create a ModerationItem of type change_request
    """

    permission_classes = [AllowAny]
    queryset = ModerationItem.objects.all()
    serializer_class = ChangeRequestSerializer

    def create(self, request, *args, **kwargs):
        headers = None

        copy_data = request.data.copy()
        copy_data["category"] = "change_request"

        serializer = self.get_serializer(data=copy_data)
        serializer.is_valid(raise_exception=True)

        if copy_data["item_type"] != "add":
            target_moderated_notification = get_object_or_404(
                ModeratedNotification, pk=copy_data["target"]
            )

        # set revision

        if copy_data["item_type"] not in ["change", "add", "delete"]:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

        # request.data[]
        copy_data["status"] = "open"

        # Revalidate
        serializer = self.get_serializer(data=copy_data)
        serializer.is_valid(raise_exception=True)

        # Create
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class NotificationCreateView(CreateAPIView):
    """
    Create a Notification instance
    """

    permission_classes = [IsAuthenticated]
    queryset = Notification.objects.all()
    serializer_class = ModerationNotificationSerializer

    def create(self, request, *args, **kwargs):
        headers = None
        images = []

        moderated_notification = None
        target_notification = None
        item_status = "created"
        try:
            # TODO: In the future check permission
            if request.data["id"]:
                moderated_notification = ModeratedNotification.objects.get(
                    pk=request.data["id"]
                )
                if moderated_notification.notification_id > 0:
                    target_notification = Notification.objects.get(
                        pk=moderated_notification.notification_id
                    )
                    item_status = "modified"
        except Exception as e:
            target_notification = None

        # Serialize
        serializer = ModerationNotificationSerializer(
            instance=target_notification, data=request.data
        )  # self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Preprocess images
        images = preprocess_images(request)

        # Create
        self.perform_create(serializer, item_status, images)
        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer, item_status, images):
        instance = serializer.save(user=self.request.user, status=item_status)
        
        # Enrich certificate data from database - frontend only sends IDs
        if 'certificates' in instance.data:
            instance.data['certificates'] = enrich_certificates_data(
                instance.data['certificates']
            )
            instance.save()  # Save updated data with enriched certificates
        
        try:
            process_images(NotificationImage, instance, images)
        except Exception as e:
            pass
        
        # Save certificates if present in the data
        try:
            if 'certificates' in instance.data:
                save_customer_certificates(instance.pk, instance.data['certificates'])
        except Exception as e:
            print(f"Error saving certificates: {str(e)}")
            pass

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class NotificationRetrieveView(RetrieveAPIView):
    """
    Returns a single ModeratedNotification instance
    """

    permission_classes = [AllowAny]
    lookup_field = "id"
    queryset = ModeratedNotification.objects.all().filter(Q(published=True))
    serializer_class = PublicModeratedNotificationSerializer


class NotificationListView(ListAPIView):
    """
    Returns a collection of ModeratedNotification instances. Search support
    """

    permission_classes = [AllowAny]
    queryset = ModeratedNotification.objects.all().filter(Q(published=True))
    serializer_class = PublicModeratedNotificationSerializer
    filter_backends = [filters.SearchFilter]
    # TODO: Create migration which generates indices for JSON data
    search_fields = ["data__name__fi", "data__name__sv", "data__name__en"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        queryset = queryset.order_by('-updated_at')  # change is here  >> sorted with order of 'updated_at'

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class OntologyWordListView(ListAPIView):
    """
    Returns a collection of ontology words instances.
    """

    permission_classes = [AllowAny]
    queryset = OntologyWord.objects.all()
    serializer_class = OntologyWordSerializer
    pagination_class = None


class MatkoWordListView(ListAPIView):
    """
    Returns a collection of matko words instances.
    """

    permission_classes = [AllowAny]
    queryset = MatkoWord.objects.all()
    serializer_class = MatkoWordSerializer
    pagination_class = None


class CertificateListView(ListAPIView):
    """
    Returns a collection of certificates and labels.
    """

    permission_classes = [AllowAny]
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
    pagination_class = None


class IdMappingAllRetrieveView(RetrieveAPIView):
    """
    Returns a single IdMappingAll instance
    """

    permission_classes = [AllowAny]
    lookup_field = "kaupunkialusta_id"
    queryset = IdMappingAll.objects.all()
    serializer_class = IdMappingAllSerializer


class IdMappingKaupunkialustaMasterRetrieveView(RetrieveAPIView):
    """
    Returns a single IdMappingKaupunkialustaMaster instance
    """

    permission_classes = [AllowAny]
    lookup_field = "kaupunkialusta_id"
    queryset = IdMappingKaupunkialustaMaster.objects.all()
    serializer_class = IdMappingKaupunkialustaMasterSerializer


class GetValidAccessibilityId(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, kaupunkialusta_id=None, *args, **kwargs):
        # Get the tpr internal id corresponding to the published notification id (kaupunkialusta id)
        # If an error occurs due to the validation, just return -1
        tpr_internal_id_response = get_valid_tpr_internal_id(kaupunkialusta_id)

        return tpr_internal_id_response


class CreateAccessibilityLink(UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, kaupunkialusta_id=None, *args, **kwargs):
        # The rules for creating the accessibility link to access esteettömyyssovellus are as follows:
        #
        # 1. If the moderated notification is not published, then the accessibility info cannot be added for this place yet.
        # 2. If the moderated notification id (kaupunkialusta id) exists in id_mapping_all, but not in id_mapping_kaupunkialusta_master, then the
        #    accessibility info cannot be added via kaupunkialusta, since it is not the master of the place, for example 'Helsingin kaupunginmuseo'.
        # 3. Otherwise the accessibility info can be added.

        # Get the request params
        published = request.data["published"]
        notification_id = str(request.data["notification_id"])
        kaupunkialusta_user = str(request.user)

        # Get the moderated notification to check the published status
        moderated_notification = None
        moderated_data = None
        if kaupunkialusta_id > 0:
            try:
                moderated_notification = ModeratedNotification.objects.get(pk = kaupunkialusta_id)
                moderated_data = moderated_notification.data
            except Exception as e:
                return Response("Esteettömyyssovellus link creation failed, id " + str(kaupunkialusta_id) + " does not exist.", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Esteettömyyssovellus link creation failed, id " + str(kaupunkialusta_id) + " is not valid.", status=status.HTTP_400_BAD_REQUEST)

        if moderated_notification == None or moderated_notification.published != True or published != True:
            return Response("Esteettömyyssovellus link creation failed, id " + str(kaupunkialusta_id) + " is not published.", status=status.HTTP_400_BAD_REQUEST)

        # Get the tpr internal id corresponding to the published notification id (kaupunkialusta id)
        tpr_internal_id_response = get_valid_tpr_internal_id(kaupunkialusta_id)
        if tpr_internal_id_response != None and tpr_internal_id_response.status_code != 200:
            return tpr_internal_id_response

        # Add the published notification id to Esteettömyyssovellus as an external reference
        # If the tpr internal id is -1, then this is a valid but new notification id, so don't add an external reference
        tpr_internal_id = tpr_internal_id_response.data
        if tpr_internal_id > 0:
            create_response = add_accessibility_external_reference(kaupunkialusta_id, kaupunkialusta_user, tpr_internal_id)
            if create_response != None and create_response.status_code != 200:
                return create_response

        # Return the url for opening Esteettömyyssovellus to show and edit accessibility info
        accessibility_url = get_accessibility_url(kaupunkialusta_id, kaupunkialusta_user, moderated_data)

        return Response(accessibility_url, status=status.HTTP_200_OK)
