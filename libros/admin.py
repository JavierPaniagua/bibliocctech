from django.contrib import admin

from .models import Ejemplar, Libro


class EjemplarInline(admin.TabularInline):
    model = Ejemplar
    extra = 0

    fields = (
        'numero_inventario',
        'estanteria',
        'balda',
        'estado',
        'condicion',
        'forma_adquisicion',
        'fecha_adquisicion',
        'proveedor',
        'observaciones',
        'etiqueta_impresa',
    )

    readonly_fields = (
        'numero_inventario',
    )


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = (
        'titulo',
        'autor',
        'categoria',
        'isbn',
        'cantidad_total',
        'cantidad_disponible',
        'cantidad_prestada',
        'activo',
    )

    search_fields = (
        'titulo',
        'autor',
        'editorial',
        'isbn',
        'ejemplares__numero_inventario',
    )

    list_filter = (
        'categoria',
        'activo',
    )

    ordering = (
        'titulo',
        'autor',
    )

    inlines = [
        EjemplarInline,
    ]


@admin.register(Ejemplar)
class EjemplarAdmin(admin.ModelAdmin):
    list_display = (
        'numero_inventario',
        'libro',
        'ubicacion_mostrada',
        'estado',
        'condicion',
        'forma_adquisicion',
        'fecha_adquisicion',
        'etiqueta_impresa',
    )

    search_fields = (
        'numero_inventario',
        'codigo_anterior',
        'libro__titulo',
        'libro__autor',
        'libro__isbn',
        'proveedor',
    )

    list_filter = (
        'estado',
        'condicion',
        'forma_adquisicion',
        'etiqueta_impresa',
        'estanteria',
        'libro__categoria',
    )

    ordering = (
        'numero_inventario',
    )

    readonly_fields = (
        'numero_inventario',
        'fecha_registro',
        'fecha_impresion_etiqueta',
    )

    fieldsets = (
        (
            'Identificación',
            {
                'fields': (
                    'libro',
                    'numero_inventario',
                    'codigo_anterior',
                )
            },
        ),
        (
            'Ubicación',
            {
                'fields': (
                    'estanteria',
                    'balda',
                )
            },
        ),
        (
            'Estado del ejemplar',
            {
                'fields': (
                    'estado',
                    'condicion',
                )
            },
        ),
        (
            'Adquisición',
            {
                'fields': (
                    'forma_adquisicion',
                    'fecha_adquisicion',
                    'proveedor',
                )
            },
        ),
        (
            'Información adicional',
            {
                'fields': (
                    'observaciones',
                    'etiqueta_impresa',
                    'fecha_impresion_etiqueta',
                    'fecha_registro',
                )
            },
        ),
    )

    @admin.display(
        description='Ubicación',
        ordering='estanteria',
    )
    def ubicacion_mostrada(self, ejemplar):
        return ejemplar.ubicacion