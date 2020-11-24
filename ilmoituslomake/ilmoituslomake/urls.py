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
        "api/moderation/open/",
        moderation_views.ModerationNotificationListView.as_view(),
    ),
    path(
        "api/changerequests/",
        moderation_views.ChangeRequestListView.as_view(),
    ),
]


# Notification Form App
urlpatterns += [
    path("api/demo/", notification_form_views.ApiDemoView.as_view()),
    path("api/hello/", notification_form_views.HelloView.as_view()),
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
    # change request
    path(
        "api/changerequest/",
        notification_form_views.ChangeRequestCreateView.as_view(),
    ),
]
