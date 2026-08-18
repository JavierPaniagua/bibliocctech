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
    "buscar-beneficiario/",
    views.buscar_beneficiario,
    name="buscar_beneficiario",
),
    
path(
    "buscar-ejemplar/",
    views.buscar_ejemplar,
    name="buscar_ejemplar",
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