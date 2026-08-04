from django.contrib import admin

from .models import Prestamo


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = (
        'ejemplar',
        'nombre_beneficiario',
        'tipo_beneficiario',
        'fecha_prestamo',
        'fecha_devolucion_prevista',
        'estado',
        'mostrar_atraso',
    )

    search_fields = (
        'ejemplar__codigo',
        'ejemplar__libro__titulo',
        'alumno__cedula',
        'alumno__nombres',
        'alumno__apellidos',
        'docente__cedula',
        'docente__nombres',
        'docente__apellidos',
    )

    list_filter = (
        'estado',
        'fecha_prestamo',
        'fecha_devolucion_prevista',
    )

    autocomplete_fields = (
        'ejemplar',
        'alumno',
        'docente',
    )

    readonly_fields = (
        'fecha_registro',
    )

    @admin.display(
        description='Días de atraso',
    )
    def mostrar_atraso(self, prestamo):
        return prestamo.dias_atraso