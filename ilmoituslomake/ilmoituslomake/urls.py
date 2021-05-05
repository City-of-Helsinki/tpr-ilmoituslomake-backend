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

urlpatterns = []

# Django Admin
# TODO: Do not include in production deployment
urlpatterns += [
    path("admin/", admin.site.urls),
]


# Authentication
urlpatterns += [
    path("auth/", include("social_django.urls", namespace="social")),
    path("helauth/", include("helusers.urls")),
    path("api/user/logout/", users_views.UserLogout.as_view()),
    path("api/user/", users_views.UserView.as_view()),
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
]


# Notification Form App
urlpatterns += [
    path(
        "api/change_request/",
        notification_form_views.ChangeRequestCreateView.as_view(),
    ),
    path(
        "api/schema/get/<int:id>/",
        notification_form_views.NotificationSchemaRetrieveView.as_view(),
    ),
    path(
        "api/schema/create/",
        notification_form_views.NotificationSchemaCreateView.as_view(),
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
]
