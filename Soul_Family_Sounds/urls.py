from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from Soul_Family_Sounds import settings

schema_view = get_schema_view(
    openapi.Info(
        title="SFS API",
        default_version="v1",
        description="SFS-API description",
        terms_of_service="sfs-api-terms",
        contact=openapi.Contact(email="contact@sfs-app.com"),
        license=openapi.License(name="SFS License"),
    ),
    public=True,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("User_Management.urls")),
    path("app/", include("Product_Management.urls")),
    path("beatsapi/", include("Beats_Management.urls")),
    path("plan/", include("Plan_Management.urls")),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path(
        "swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
