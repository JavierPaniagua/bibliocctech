from django.db import models
from django.db.models import Max, Min


class Libro(models.Model):
    titulo = models.CharField(
        max_length=200,
        verbose_name='Título',
    )

    autor = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Autor',
    )

    editorial = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Editorial',
    )

    categoria = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Categoría',
    )

    isbn = models.CharField(
        max_length=30,
        blank=True,
        db_index=True,
        verbose_name='ISBN',
    )

    edicion = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Edición',
    )

    anio_publicacion = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Año de publicación',
    )

    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción o resumen',
    )

    activo = models.BooleanField(
        default=True,
        verbose_name='Libro activo',
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de registro',
    )

    class Meta:
        verbose_name = 'Libro'
        verbose_name_plural = 'Libros'
        ordering = [
            'titulo',
            'autor',
        ]

    def __str__(self):
        return self.titulo

    @property
    def cantidad_total(self):
        return self.ejemplares.exclude(
            estado=Ejemplar.Estado.BAJA,
        ).count()

    @property
    def cantidad_registrada(self):
        return self.ejemplares.count()

    @property
    def cantidad_disponible(self):
        return self.ejemplares.filter(
            estado=Ejemplar.Estado.DISPONIBLE,
        ).count()

    @property
    def cantidad_prestada(self):
        return self.ejemplares.filter(
            estado=Ejemplar.Estado.PRESTADO,
        ).count()


class Ejemplar(models.Model):
    class Estado(models.TextChoices):
        DISPONIBLE = 'DISPONIBLE', 'Disponible'
        PRESTADO = 'PRESTADO', 'Prestado'
        DETERIORADO = 'DETERIORADO', 'Deteriorado'
        EXTRAVIADO = 'EXTRAVIADO', 'Extraviado'
        BAJA = 'BAJA', 'Dado de baja'

    class Condicion(models.TextChoices):
        NUEVO = 'NUEVO', 'Nuevo'
        BUENO = 'BUENO', 'Bueno'
        REGULAR = 'REGULAR', 'Regular'
        DETERIORADO = 'DETERIORADO', 'Deteriorado'

    class FormaAdquisicion(models.TextChoices):
        COMPRA = 'COMPRA', 'Compra'
        DONACION = 'DONACION', 'Donación'
        TRANSFERENCIA = 'TRANSFERENCIA', 'Transferencia'
        OTRO = 'OTRO', 'Otro'
        NO_ESPECIFICADA = (
            'NO_ESPECIFICADA',
            'No especificada',
        )

    libro = models.ForeignKey(
        Libro,
        on_delete=models.PROTECT,
        related_name='ejemplares',
        verbose_name='Libro',
    )

    numero_inventario = models.PositiveIntegerField(
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        verbose_name='Número de inventario',
    )

    codigo_anterior = models.CharField(
        max_length=30,
        blank=True,
        db_index=True,
        verbose_name='Código anterior',
    )

    estanteria = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Estantería',
    )

    balda = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Balda',
    )

    proveedor = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Proveedor',
    )

    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.DISPONIBLE,
        verbose_name='Estado de circulación',
    )

    condicion = models.CharField(
        max_length=20,
        choices=Condicion.choices,
        default=Condicion.BUENO,
        verbose_name='Condición física',
    )

    forma_adquisicion = models.CharField(
        max_length=20,
        choices=FormaAdquisicion.choices,
        default=FormaAdquisicion.NO_ESPECIFICADA,
        verbose_name='Forma de adquisición',
    )

    fecha_adquisicion = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de adquisición',
    )

    observaciones = models.TextField(
        blank=True,
        verbose_name='Observaciones',
    )

    etiqueta_impresa = models.BooleanField(
        default=False,
        verbose_name='Etiqueta impresa',
    )

    fecha_impresion_etiqueta = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de impresión de etiqueta',
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de registro',
    )

    class Meta:
        verbose_name = 'Ejemplar'
        verbose_name_plural = 'Ejemplares'
        ordering = ['numero_inventario']

    def __str__(self):
        if self.numero_inventario is None:
            numero = 'Sin número'
        else:
            numero = self.numero_inventario

        return f'{numero} - {self.libro.titulo}'

    @property
    def codigo(self):
        """
        Compatibilidad temporal con el módulo de préstamos
        y las plantillas anteriores.
        """
        return self.numero_inventario

    @property
    def ubicacion(self):
        if self.estanteria and self.balda:
            return f'{self.estanteria}-{self.balda}'

        if self.estanteria:
            return self.estanteria

        if self.balda:
            return f'Balda {self.balda}'

        return 'Ubicación pendiente'

    @classmethod
    def siguiente_numero_disponible(cls):
        limites = cls.objects.aggregate(
            menor=Min('numero_inventario'),
            mayor=Max('numero_inventario'),
        )

        menor = limites['menor']
        mayor = limites['mayor']

        if menor is None or mayor is None:
            return 1

        numeros_utilizados = set(
            cls.objects.filter(
                numero_inventario__range=(
                    menor,
                    mayor,
                ),
            ).values_list(
                'numero_inventario',
                flat=True,
            )
        )

        for numero in range(menor, mayor + 1):
            if numero not in numeros_utilizados:
                return numero

        return mayor + 1

    def save(self, *args, **kwargs):
        if self.numero_inventario is None:
            self.numero_inventario = (
                type(self).siguiente_numero_disponible()
            )

        self.estanteria = (
            self.estanteria or ''
        ).strip().upper()

        self.balda = (
            self.balda or ''
        ).strip().upper()

        self.codigo_anterior = (
            self.codigo_anterior or ''
        ).strip()

        self.proveedor = (
            self.proveedor or ''
        ).strip()

        super().save(*args, **kwargs)


class ImportacionLibros(models.Model):
    nombre_archivo = models.CharField(
        max_length=255,
        verbose_name='Nombre del archivo',
    )

    huella_archivo = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        verbose_name='Identificador del archivo',
    )

    titulos_creados = models.PositiveIntegerField(
        default=0,
        verbose_name='Títulos creados',
    )

    ejemplares_creados = models.PositiveIntegerField(
        default=0,
        verbose_name='Ejemplares creados',
    )

    codigos_reasignados = models.PositiveIntegerField(
        default=0,
        verbose_name='Códigos reasignados',
    )

    registros_sin_ubicacion = models.PositiveIntegerField(
        default=0,
        verbose_name='Registros sin ubicación',
    )

    fecha_importacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de importación',
    )

    class Meta:
        verbose_name = 'Importación de libros'
        verbose_name_plural = 'Importaciones de libros'
        ordering = ['-fecha_importacion']

    def __str__(self):
        return (
            f'{self.nombre_archivo} - '
            f'{self.fecha_importacion:%d/%m/%Y %H:%M}'
        )