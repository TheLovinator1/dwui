from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import admin
from django.urls import path

if TYPE_CHECKING:
    from django.urls.resolvers import URLResolver

urlpatterns: list[URLResolver] = [
    path("admin/", admin.site.urls),
]
