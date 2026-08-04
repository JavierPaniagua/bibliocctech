from django.contrib import admin

from .models import Ejemplar, Libro


class EjemplarInline(admin.TabularInline):
    model = Ejemplar
    extra = 0

    fields = (
        'codigo',
        'estado',
        'condicion',
        'forma_adquisicion',
        'fecha_adquisicion',
        'observaciones',
    )

    readonly_fields = (
        'codigo',
    )


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = (
        'titulo',
        'autor',
        'categoria',
        'isbn',
        'ubicacion',
        'cantidad_total',
        'cantidad_disponible',
    )

    search_fields = (
        'titulo',
        'autor',
        'editorial',
        'isbn',
        'ejemplares__codigo',
    )

    list_filter = (
        'categoria',
        'activo',
    )

    inlines = [
        EjemplarInline,
    ]


@admin.register(Ejemplar)
class EjemplarAdmin(admin.ModelAdmin):
    list_display = (
        'codigo',
        'libro',
        'estado',
        'condicion',
        'forma_adquisicion',
        'fecha_adquisicion',
    )

    search_fields = (
        'codigo',
        'libro__titulo',
        'libro__autor',
        'libro__isbn',
    )

    list_filter = (
        'estado',
        'condicion',
        'forma_adquisicion',
        'libro__categoria',
    )

    readonly_fields = (
        'codigo',
    )