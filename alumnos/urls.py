from django.urls import path

from . import views


app_name = 'alumnos'


urlpatterns = [
    path(
        '',
        views.alumno_lista,
        name='lista',
    ),

    path(
        'nuevo/',
        views.alumno_crear,
        name='crear',
    ),

    path(
        'importar/',
        views.alumno_importar,
        name='importar',
    ),

    path(
        '<int:alumno_id>/editar/',
        views.alumno_editar,
        name='editar',
    ),
]