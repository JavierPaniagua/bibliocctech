import re
import unicodedata

from django.db import models
from django.db.models import Max


def quitar_acentos(texto):
    texto = unicodedata.normalize(
        'NFKD',
        texto or '',
    )

    return ''.join(
        caracter
        for caracter in texto
        if not unicodedata.combining(caracter)
    )


def generar_clave_autor(autor):
    autor = ' '.join((autor or '').strip().split())

    if not autor:
        return ''

    if ',' in autor:
        apellido = autor.split(',', 1)[0].strip()
    else:
        apellido = autor.split()[-1]

    apellido = quitar_acentos(apellido).upper()
    apellido = re.sub(r'[^A-Z0-9]', '', apellido)

    return apellido[:3]


def generar_clave_titulo(titulo):
    titulo = quitar_acentos(titulo).upper()

    palabras_omitidas = {
        'EL',
        'LA',
        'LOS',
        'LAS',
        'UN',
        'UNA',
        'UNOS',
        'UNAS',
        'DE',
        'DEL',
        'AL',
    }

    palabras = re.findall(
        r'[A-Z0-9]+',
        titulo,
    )

    for palabra in palabras:
        if (
            palabra not in palabras_omitidas
            and not palabra.isdigit()
        ):
            return palabra[:3].lower()

    return ''


class Libro(models.Model):
    class Area(models.TextChoices):
        GENERALIDADES = (
            'GENERALIDADES',
            'Generalidades',
        )
        FILOSOFIA = (
            'FILOSOFIA',
            'Filosofía y Psicología',
        )
        RELIGION = (
            'RELIGION',
            'Religión',
        )
        CIENCIAS_SOCIALES = (
            'CIENCIAS_SOCIALES',
            'Ciencias Sociales',
        )
        LENGUA_IDIOMAS = (
            'LENGUA_IDIOMAS',
            'Lengua e Idiomas',
        )
        CIENCIAS_NATURALES = (
            'CIENCIAS_NATURALES',
            'Ciencias Naturales',
        )
        MATEMATICA = (
            'MATEMATICA',
            'Matemática',
        )
        TECNOLOGIA = (
            'TECNOLOGIA',
            'Tecnología',
        )
        ELECTRICIDAD = (
            'ELECTRICIDAD',
            'Electricidad',
        )
        ELECTRONICA = (
            'ELECTRONICA',
            'Electrónica',
        )
        INFORMATICA = (
            'INFORMATICA',
            'Informática',
        )
        ARTES = (
            'ARTES',
            'Artes',
        )
        LITERATURA = (
            'LITERATURA',
            'Literatura',
        )
        HISTORIA_GEOGRAFIA = (
            'HISTORIA_GEOGRAFIA',
            'Historia y Geografía',
        )
        REFERENCIA = (
            'REFERENCIA',
            'Referencia',
        )
        OTRO = (
            'OTRO',
            'Otro',
        )

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

    area = models.CharField(
        max_length=30,
        choices=Area.choices,
        blank=True,
        verbose_name='Área',
    )

    clasificacion = models.CharField(
        max_length=30,
        blank=True,
        db_index=True,
        verbose_name='Clasificación',
    )

    clave_autor = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Clave del autor',
    )

    clave_titulo = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Clave del título',
    )

    signatura_topografica = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        editable=False,
        verbose_name='Signatura topográfica',
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

    def generar_signatura(self):
        clasificacion = (
            self.clasificacion or ''
        ).strip()

        clave_autor = (
            self.clave_autor or ''
        ).strip().upper()

        clave_titulo = (
            self.clave_titulo or ''
        ).strip().lower()

        signatura = clasificacion

        if clave_autor:
            signatura = (
                f'{signatura} {clave_autor}'
            ).strip()

        if clave_titulo:
            if signatura:
                signatura = (
                    f'{signatura}.{clave_titulo}'
                )
            else:
                signatura = clave_titulo

        return signatura

    def save(self, *args, **kwargs):
        self.titulo = ' '.join(
            (self.titulo or '').strip().split()
        )

        self.autor = ' '.join(
            (self.autor or '').strip().split()
        )

        self.editorial = ' '.join(
            (self.editorial or '').strip().split()
        )

        self.clasificacion = (
            self.clasificacion or ''
        ).strip()

        if not self.clave_autor:
            self.clave_autor = generar_clave_autor(
                self.autor
            )

        if not self.clave_titulo:
            self.clave_titulo = generar_clave_titulo(
                self.titulo
            )

        self.clave_autor = (
            self.clave_autor or ''
        ).strip().upper()

        self.clave_titulo = (
            self.clave_titulo or ''
        ).strip().lower()

        self.signatura_topografica = (
            self.generar_signatura()
        )

        self.isbn = (
            self.isbn or ''
        ).replace(' ', '').replace('-', '')

        super().save(*args, **kwargs)

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
        REPARACION = (
            'REPARACION',
            'En reparación',
        )
        DETERIORADO = (
            'DETERIORADO',
            'Deteriorado',
        )
        EXTRAVIADO = (
            'EXTRAVIADO',
            'Extraviado',
        )
        BAJA = (
            'BAJA',
            'Dado de baja',
        )

    class Condicion(models.TextChoices):
        NUEVO = 'NUEVO', 'Nuevo'
        BUENO = 'BUENO', 'Bueno'
        REGULAR = 'REGULAR', 'Regular'
        DETERIORADO = (
            'DETERIORADO',
            'Deteriorado',
        )

    class FormaAdquisicion(models.TextChoices):
        COMPRA = 'COMPRA', 'Compra'
        DONACION = 'DONACION', 'Donación'
        TRANSFERENCIA = (
            'TRANSFERENCIA',
            'Transferencia',
        )
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
        verbose_name='Proveedor o procedencia',
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
        verbose_name="Etiqueta interior impresa",
    )
   
    fecha_impresion_etiqueta = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de impresión de etiqueta interior",
    )

    etiqueta_lomo_impresa = models.BooleanField(
        default=False,
        verbose_name="Etiqueta de lomo impresa",
    )

    fecha_impresion_etiqueta_lomo = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de impresión de etiqueta de lomo",
    )
    etiqueta_lomo_impresa = models.BooleanField(
        default=False,
        verbose_name="Etiqueta de lomo impresa",
    )

    fecha_impresion_etiqueta_lomo = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de impresión de etiqueta de lomo",
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
        numero = (
            self.numero_inventario
            if self.numero_inventario is not None
            else 'Sin número'
        )

        return f'{numero} - {self.libro.titulo}'

    @property
    def codigo(self):
        return self.numero_inventario

    @property
    def ubicacion(self):
        estanteria = (
            self.estanteria or ''
        ).strip()

        balda = (
            self.balda or ''
        ).strip().upper()

        if estanteria and balda:
            return (
                f'Estantería {estanteria} - '
                f'Balda {estanteria}{balda}'
            )

        if estanteria:
            return f'Estantería {estanteria}'

        if balda:
            return f'Balda {balda}'

        return 'Ubicación pendiente'

    @classmethod
    def siguiente_numero_disponible(cls):
        mayor = cls.objects.aggregate(
            mayor=Max('numero_inventario'),
        )['mayor']

        if mayor is None:
            return 1

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

        self.proveedor = ' '.join(
            (self.proveedor or '').strip().split()
        )

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