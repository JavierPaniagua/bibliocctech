from django.urls import path

from . import views


app_name = 'docentes'


urlpatterns = [
    path(
        '',
        views.docente_lista,
        name='lista',
    ),

    path(
        'nuevo/',
        views.docente_crear,
        name='crear',
    ),

    path(
        '<int:docente_id>/editar/',
        views.docente_editar,
        name='editar',
    ),
]