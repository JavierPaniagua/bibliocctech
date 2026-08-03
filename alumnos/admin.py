from django.contrib import admin

from .models import Alumno


@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = (
        'cedula',
        'apellidos',
        'nombres',
        'curso',
        'seccion',
        'turno',
        'activo',
    )

    search_fields = (
        'cedula',
        'nombres',
        'apellidos',
    )

    list_filter = (
        'curso',
        'turno',
        'activo',
    )