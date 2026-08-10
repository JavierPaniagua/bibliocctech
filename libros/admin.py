from django.contrib import admin

from .models import (
    Ejemplar,
    ImportacionLibros,
    Libro,
)


class EjemplarInline(admin.TabularInline):
    model = Ejemplar
    extra = 0

    fields = (
        'numero_inventario',
        'codigo_anterior',
        'estanteria',
        'balda',
        'estado',
        'condicion',
        'forma_adquisicion',
        'etiqueta_impresa',
    )

    show_change_link = True


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = (
        'titulo',
        'autor',
        'mostrar_area',
        'clasificacion',
        'signatura_topografica',
        'cantidad_total',
        'cantidad_disponible',
        'cantidad_prestada',
        'activo',
    )

    search_fields = (
        'titulo',
        'autor',
        'editorial',
        'clasificacion',
        'signatura_topografica',
        'isbn',
        'ejemplares__numero_inventario',
        'ejemplares__codigo_anterior',
    )

    list_filter = (
        'area',
        'activo',
    )

    readonly_fields = (
        'signatura_topografica',
        'fecha_registro',
    )

    fieldsets = (
        (
            'Datos bibliográficos',
            {
                'fields': (
                    'titulo',
                    'autor',
                    'editorial',
                    'isbn',
                    'edicion',
                    'anio_publicacion',
                ),
            },
        ),
        (
            'Clasificación',
            {
                'fields': (
                    'area',
                    'clasificacion',
                    'clave_autor',
                    'clave_titulo',
                    'signatura_topografica',
                ),
            },
        ),
        (
            'Información adicional',
            {
                'fields': (
                    'descripcion',
                    'activo',
                    'fecha_registro',
                ),
            },
        ),
    )

    inlines = [
        EjemplarInline,
    ]

    @admin.display(
        description='Área',
        ordering='area',
    )
    def mostrar_area(self, libro):
        if not libro.area:
            return 'Pendiente'

        return libro.get_area_display()


@admin.register(Ejemplar)
class EjemplarAdmin(admin.ModelAdmin):
    list_display = (
        'numero_inventario',
        'libro',
        'mostrar_signatura',
        'mostrar_ubicacion',
        'estado',
        'condicion',
        'forma_adquisicion',
        'etiqueta_impresa',
    )

    search_fields = (
        'numero_inventario',
        'codigo_anterior',
        'libro__titulo',
        'libro__autor',
        'libro__isbn',
        'libro__clasificacion',
        'libro__signatura_topografica',
        'estanteria',
        'balda',
    )

    list_filter = (
        'estado',
        'condicion',
        'forma_adquisicion',
        'libro__area',
        'etiqueta_impresa',
    )

    readonly_fields = (
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
                ),
            },
        ),
        (
            'Ubicación',
            {
                'fields': (
                    'estanteria',
                    'balda',
                ),
            },
        ),
        (
            'Estado del ejemplar',
            {
                'fields': (
                    'estado',
                    'condicion',
                    'observaciones',
                ),
            },
        ),
        (
            'Adquisición',
            {
                'fields': (
                    'forma_adquisicion',
                    'fecha_adquisicion',
                    'proveedor',
                ),
            },
        ),
        (
            'Etiqueta',
            {
                'fields': (
                    'etiqueta_impresa',
                    'fecha_impresion_etiqueta',
                    'fecha_registro',
                ),
            },
        ),
    )

    @admin.display(
        description='Signatura',
        ordering='libro__signatura_topografica',
    )
    def mostrar_signatura(self, ejemplar):
        return (
            ejemplar.libro.signatura_topografica
            or 'Pendiente'
        )

    @admin.display(
        description='Ubicación',
    )
    def mostrar_ubicacion(self, ejemplar):
        return ejemplar.ubicacion


@admin.register(ImportacionLibros)
class ImportacionLibrosAdmin(admin.ModelAdmin):
    list_display = (
        'nombre_archivo',
        'titulos_creados',
        'ejemplares_creados',
        'codigos_reasignados',
        'registros_sin_ubicacion',
        'fecha_importacion',
    )

    search_fields = (
        'nombre_archivo',
        'huella_archivo',
    )

    readonly_fields = (
        'nombre_archivo',
        'huella_archivo',
        'titulos_creados',
        'ejemplares_creados',
        'codigos_reasignados',
        'registros_sin_ubicacion',
        'fecha_importacion',
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(
        self,
        request,
        obj=None,
    ):
        return False