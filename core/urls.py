from django.urls import path

from . import views


app_name = "core"


urlpatterns = [
    path(
        "",
        views.inicio,
        name="inicio",
    ),

    path(
        "crear-respaldo/",
        views.crear_respaldo,
        name="crear_respaldo",
    ),
    
    path(
    "reportes/",
    views.reportes,
    name="reportes",
),
    
path(
    "reportes/",
    views.reportes,
    name="reportes",
),
]