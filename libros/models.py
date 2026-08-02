from django.db import models


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

    ubicacion = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Estante o ubicación',
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

    codigo = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True,
        editable=False,
        verbose_name='Código CCTL',
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

    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de registro',
    )

    class Meta:
        verbose_name = 'Ejemplar'
        verbose_name_plural = 'Ejemplares'
        ordering = ['codigo']

    def __str__(self):
        return f'{self.codigo} - {self.libro.titulo}'

    def save(self, *args, **kwargs):
        es_nuevo = self.pk is None

        super().save(*args, **kwargs)

        if es_nuevo and not self.codigo:
            self.codigo = f'CCTL-LIB-{self.pk:06d}'

            type(self).objects.filter(
                pk=self.pk,
            ).update(
                codigo=self.codigo,
            )