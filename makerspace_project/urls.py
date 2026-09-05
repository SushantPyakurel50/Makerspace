from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("inventory.api_urls")),   # REST API (JSON, DTOs)
    path("", include("inventory.web_urls")),        # Web GUI (HTML templates)
]
