from typing import TYPE_CHECKING

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from dmr.openapi import build_schema
from dmr.openapi.views import SwaggerView
from dmr.plugins.pydantic import PydanticSerializer
from dmr.routing import Router, build_404_handler, build_500_handler, path

from django_project.controllers import OpenAPIJsonDownloadController
from services.api import urls as api_urls

if TYPE_CHECKING:
    from django.urls import URLPattern, URLResolver

router = Router(
    prefix="api/",
    urls=api_urls.router.urls,
)

schema = build_schema(router)
handler404 = build_404_handler(router.prefix, serializer=PydanticSerializer)
handler500 = build_500_handler(router.prefix, serializer=PydanticSerializer)

urlpatterns: list[URLPattern | URLResolver] = [
    path("admin/", admin.site.urls),
    path(
        router.prefix,
        include(
            (router.urls, "api"),
            namespace="api",
        ),
    ),
    path(
        f"{router.prefix}docs/",
        SwaggerView.as_view(schema),
        name="docs",
    ),
    path(
        f"{router.prefix}schema.json",
        OpenAPIJsonDownloadController.as_view(schema),
        name="schema-json",
    ),
]

# media files are served by Django in DEBUG only
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
