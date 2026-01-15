"""ilmoituslomake URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from users import views as users_views
from notification_form import views as notification_form_views
from moderation import views as moderation_views
from translation import views as translation_views
from opening_times import views as opening_times_views

from api import views as api_views

from ilmoituslomake.settings import DEBUG

urlpatterns = []

# Django Admin
# TODO: Do not include in production deployment
if DEBUG:
    urlpatterns += [
        path("admin/", admin.site.urls),
        path(
            "api/schema/get/<int:id>/",
            notification_form_views.NotificationSchemaRetrieveView.as_view(),
        ),
        path(
            "api/schema/create/",
            notification_form_views.NotificationSchemaCreateView.as_view(),
        ),
        path(
            "api/schema/update/<int:id>/",
            notification_form_views.NotificationSchemaUpdateView.as_view(),
        ),
    ]


# Authentication
urlpatterns += [
    path("auth/", include("social_django.urls", namespace="social")),
    path("helauth/", include("helusers.urls")),
    path("api/user/logout/", users_views.UserLogout.as_view()),
    #path("api/user/", users_views.UserView.as_view()),
    path("api/gdpr-api/", include("helsinki_gdpr.urls")),
    path("api/user/", users_views.UserView.as_view()),
]

urlpatterns += [
    path("api/proxy/<str:id>/<str:image>", moderation_views.image_proxy),
]

# Moderation App
urlpatterns += [
    path(
        "api/moderation/todos/find/",
        moderation_views.ModerationItemSearchListView.as_view(),
    ),
    path(
        "api/moderation/todos/my/",
        moderation_views.MyModerationItemListView.as_view(),
    ),
    path(
        "api/moderation/todos/recent/",
        moderation_views.NewModerationItemListView.as_view(),
    ),
    path(
        "api/moderation/todos/",
        moderation_views.ModerationItemListView.as_view(),
    ),
    path(
        "api/moderation/todos/<int:id>/",
        moderation_views.ModerationItemRetrieveUpdateView.as_view(),
    ),
    path(
        "api/moderation/get/<int:id>/",
        moderation_views.ModerationNotificationRetrieveView.as_view(),
    ),
    path(
        "api/moderation/moderator_edit/",
        moderation_views.ModeratorEditCreateView.as_view(),
    ),
    path("api/moderation/assign/", moderation_views.AssignModerationItemView.as_view()),
    path(
        "api/moderation/assign/<int:id>/",
        moderation_views.AssignModerationItemView.as_view(),
    ),
    path(
        "api/moderation/unassign/",
        moderation_views.UnassignModerationItemView.as_view(),
    ),
    path(
        "api/moderation/unassign/<int:id>/",
        moderation_views.UnassignModerationItemView.as_view(),
    ),
    path("api/moderation/reject/", moderation_views.RejectModerationItemView.as_view()),
    path(
        "api/moderation/reject/<int:id>/",
        moderation_views.RejectModerationItemView.as_view(),
    ),
    path(
        "api/moderation/approve/", moderation_views.ModerationItemUpdateView.as_view()
    ),
    path(
        "api/moderation/approve/<int:id>/",
        moderation_views.ModerationItemUpdateView.as_view(),
    ),
    path("api/moderation/delete/", moderation_views.ModerationItemUpdateView.as_view()),
    path(
        "api/moderation/delete/<int:id>/",
        moderation_views.DeleteNotificationView.as_view(),
    ),
    path(
        "api/moderation/search/",
        moderation_views.ModeratedNotificationSearchListView.as_view(),
    ),
    path(
        "api/moderation/send_accessibility_email/<int:id>/",
        moderation_views.SendAccessibilityEmail.as_view(),
    ),
]


# Notification Form App
urlpatterns += [
    path(
        "api/change_request/",
        notification_form_views.ChangeRequestCreateView.as_view(),
    ),
    # notifications
    path(
        "api/notification/create/",
        notification_form_views.NotificationCreateView.as_view(),
    ),
    path(
        "api/notification/get/<int:id>/",
        notification_form_views.NotificationRetrieveView.as_view(),
    ),
    path(
        "api/notification/list/", notification_form_views.NotificationListView.as_view()
    ),
    # ontology words
    path("api/ontologywords/", notification_form_views.OntologyWordListView.as_view()),
    # matko words
    path("api/matkowords/", notification_form_views.MatkoWordListView.as_view()),
]


# Open API
urlpatterns += [
    path(
        "api/open/v1/target/",
        api_views.ApiListViewV1.as_view(),
    ),
    path(
        "api/open/v1/target/<int:id>/",
        api_views.ApiRetrieveViewV1.as_view(),
    ),
    path(
        "api/open/v1/auxiliarytourismcode/",
        api_views.ApiMatkoWordListViewV1.as_view(),
    ),
    path(
        "api/open/v1/ontologyword/",
        api_views.ApiOntologyWordListViewV1.as_view(),
    ),
]

# Translation
urlpatterns += [
    # path("api/moderation/translation/task/",
    #      translation_views.TranslationTaskListView.as_view()),
    path(
        "api/moderation/translation/task/<int:id>/",
        translation_views.TranslationTaskRetrieveView.as_view(),
    ),
    path(
        "api/moderation/translation/save_request/",
        translation_views.TranslationRequestEditCreateView.as_view(),
    ),
    path(
        "api/moderation/translation/request/<int:request_id>/",
        translation_views.TranslationRequestRetrieveView.as_view(),
    ),
    path(
        "api/moderation/translation/task/find/",
        translation_views.ModerationTranslationTaskSearchListView.as_view(),
    ),
    path(
        "api/moderation/translation/request/find/",
        translation_views.TranslationRequestSearchListView.as_view(),
    ),
    # path("api/moderation/translationdata/",
    #      translation_views.TranslationDataListView.as_view()),
    path(
        "api/moderation/translation/save_task/<int:id>/",
        translation_views.ModerationTranslationTaskEditCreateView.as_view(),
    ),
    path(
        "api/translation/todos/<int:id>/",
        translation_views.TranslationTodoRetrieveView.as_view(),
    ),
    path(
        "api/translation/todos/find/",
        translation_views.TranslationTaskSearchListView.as_view(),
    ),
    path(
        "api/translation/save/<int:id>/",
        translation_views.TranslationTaskEditCreateView.as_view(),
    ),
    path(
        "api/moderation/translation/cancel_request/<int:id>/",
        translation_views.ModerationTranslationRequestDeleteView.as_view(),
    ),
    path(
        "api/moderation/translation/translators/",
        translation_views.TranslationUsersListView.as_view(),
    ),
]

# Opening times
urlpatterns += [
    path(
        "api/openingtimes/createlink/<int:id>/",
        opening_times_views.CreateLink.as_view(),
    ),
    path("api/openingtimes/get/<str:id>/", opening_times_views.GetTimes.as_view()),
]

# Esteettömyyssovellus integration
urlpatterns += [
    path(
        "api/accessibility/id_mapping_all/get/<int:kaupunkialusta_id>/",
        notification_form_views.IdMappingAllRetrieveView.as_view(),
    ),
    path(
        "api/accessibility/id_mapping_kaupunkialusta_master/get/<int:kaupunkialusta_id>/",
        notification_form_views.IdMappingKaupunkialustaMasterRetrieveView.as_view(),
    ),
    path(
        "api/accessibility/get_valid_internal_id/<int:kaupunkialusta_id>/",
        notification_form_views.GetValidAccessibilityId.as_view(),
    ),
    path(
        "api/accessibility/create_link/<int:kaupunkialusta_id>/",
        notification_form_views.CreateAccessibilityLink.as_view(),
    ),
]
