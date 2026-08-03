from django.urls import path

from . import views


app_name = 'libros'


urlpatterns = [
    path(
        '',
        views.libro_lista,
        name='lista',
    ),

    path(
        'nuevo/',
        views.libro_crear,
        name='crear',
    ),

    path(
        '<int:libro_id>/',
        views.libro_detalle,
        name='detalle',
    ),

    path(
        '<int:libro_id>/editar/',
        views.libro_editar,
        name='editar',
    ),
]