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
        'importar/',
        views.docente_importar,
        name='importar',
    ),

path(
    '<int:docente_id>/historial/',
    views.docente_historial,
    name='historial',
),


    path(
        '<int:docente_id>/editar/',
        views.docente_editar,
        name='editar',
    ),
    
    
    path(
    '<int:docente_id>/eliminar/',
    views.docente_eliminar,
    name='eliminar',
),
]