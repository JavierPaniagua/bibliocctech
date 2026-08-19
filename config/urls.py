from django.contrib import admin
from django.urls import include, path
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("alumnos/", include("alumnos.urls")),
    path("docentes/", include("docentes.urls")),
    path("libros/", include("libros.urls")),
    path("prestamos/", include("prestamos.urls")),
    path(
    'cuenta/',
    include('django.contrib.auth.urls'),
),
]