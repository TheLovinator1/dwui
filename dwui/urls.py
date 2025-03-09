from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import path

if TYPE_CHECKING:
    from django.urls.resolvers import URLResolver

urlpatterns: list[URLResolver] = [
    path("admin/", admin.site.urls),
]

if "test" not in sys.argv:
    urlpatterns = [*urlpatterns, *debug_toolbar_urls()]
