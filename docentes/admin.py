from django.contrib import admin

from .models import Docente


@admin.register(Docente)
class DocenteAdmin(admin.ModelAdmin):
    list_display = (
        'cedula',
        'apellidos',
        'nombres',
        'area',
        'especialidad',
        'turno',
        'activo',
    )

    search_fields = (
        'cedula',
        'nombres',
        'apellidos',
        'area',
    )

    list_filter = (
        'especialidad',
        'turno',
        'activo',
    )