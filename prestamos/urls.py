from django.urls import path

from . import views


app_name = "prestamos"


urlpatterns = [
    path(
        "",
        views.prestamo_lista,
        name="lista",
    ),
    path(
        "registrar/",
        views.prestamo_crear,
        name="crear",
    ),
    path(
        "<int:prestamo_id>/devolver/",
        views.prestamo_devolver,
        name="devolver",
    ),
    
    path(
    "reporte/",
    views.prestamo_reporte,
    name="reporte",
),
]