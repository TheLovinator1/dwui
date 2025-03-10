from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import URLPattern, path

from dwui import views
from dwui.views import (
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
    # Container action URLs
    path("container/<str:container_id>/start/", views.start_container, name="start_container"),
    path("container/<str:container_id>/stop/", views.stop_container, name="stop_container"),
    path("container/<str:container_id>/restart/", views.restart_container, name="restart_container"),
    path("container/<str:container_id>/remove/", views.remove_container, name="remove_container"),
    path("container/<str:container_id>/update/", views.update_container, name="update_container"),
    path("new-container/", new_container, name="new_container"),
    path("image-config/", image_config, name="image_config"),
]

if "test" not in sys.argv:
    urlpatterns = [*urlpatterns, *debug_toolbar_urls()]
