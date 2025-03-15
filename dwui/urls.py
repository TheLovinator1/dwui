from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import URLPattern, include, path

from dwui import views
from dwui.views import (
    get_containers,
    image_config,
    new_container,
)

if TYPE_CHECKING:
    from django.urls.resolvers import URLResolver

urlpatterns: list[URLResolver | URLPattern] = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("containers/new/", views.new_container, name="new_container"),
    path("container/<str:container_id>/", views.container_details, name="container_details"),
    path("container/<str:container_id>/start/", views.start_container, name="start_container"),
    path("container/<str:container_id>/stop/", views.stop_container, name="stop_container"),
    path("container/<str:container_id>/restart/", views.restart_container, name="restart_container"),
    path("container/<str:container_id>/remove/", views.remove_container, name="remove_container"),
    path("new-container/", new_container, name="new_container"),
    path("image-config/", image_config, name="image_config"),
    path("get-containers/", get_containers, name="get_containers"),
    path("accounts/", include("allauth.urls")),
    path("accounts/password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("accounts/password_reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("accounts/reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("accounts/reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
]

if "test" not in sys.argv:
    urlpatterns = [*urlpatterns, *debug_toolbar_urls()]
