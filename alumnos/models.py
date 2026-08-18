from django.db import models
from django.utils import timezone


def anio_actual():
    return timezone.localdate().year


class Alumno(models.Model):
    TURNO_CHOICES = [
        ('MAÑANA', 'Mañana'),
        ('TARDE', 'Tarde'),
        ('NOCHE', 'Noche'),
    ]

    cedula = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Número de cédula',
    )

    nombre_completo = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Nombre completo',
    )

    nombres = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Nombres',
    )

    apellidos = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Apellidos',
    )

    curso = models.CharField(
        max_length=50,
        verbose_name='Curso',
    )

    seccion = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Sección',
    )

    especialidad = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Especialidad',
    )

    turno = models.CharField(
        max_length=10,
        choices=TURNO_CHOICES,
        default='MAÑANA',
        verbose_name='Turno',
    )

    telefono = models.CharField(
        max_length=30,
        blank=True,
        verbose_name='Teléfono',
    )

    activo = models.BooleanField(
        default=True,
        verbose_name='Alumno activo',
    )

    anio_lectivo = models.PositiveSmallIntegerField(
        default=anio_actual,
        db_index=True,
        verbose_name='Año lectivo',
    )

    anio_egreso = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name='Año de egreso',
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de registro',
    )

    class Meta:
        ordering = [
            'nombre_completo',
            'apellidos',
            'nombres',
        ]
        verbose_name = 'Alumno'
        verbose_name_plural = 'Alumnos'

    @property
    def nombre_visible(self):
        nombre_separado = ' '.join(
            parte.strip()
            for parte in [self.apellidos, self.nombres]
            if parte and parte.strip()
        )

        if nombre_separado:
            return nombre_separado

        if self.nombre_completo:
            return self.nombre_completo.strip()

        return 'SIN NOMBRE'

    def save(self, *args, **kwargs):
        self.cedula = (self.cedula or '').strip()
        self.nombres = (self.nombres or '').strip().upper()
        self.apellidos = (self.apellidos or '').strip().upper()
        self.nombre_completo = (
            self.nombre_completo or ''
        ).strip().upper()
        self.curso = (self.curso or '').strip().upper()
        self.seccion = (self.seccion or '').strip().upper()
        self.especialidad = (
            self.especialidad or ''
        ).strip().upper()
        self.telefono = (self.telefono or '').strip()

        if self.nombres or self.apellidos:
            self.nombre_completo = ' '.join(
                parte
                for parte in [self.apellidos, self.nombres]
                if parte
            )

        if self.activo:
            self.anio_egreso = None

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.cedula} - {self.nombre_visible}'


class PromocionAnual(models.Model):
    anio_origen = models.PositiveSmallIntegerField(
        verbose_name='Año de origen',
    )

    anio_destino = models.PositiveSmallIntegerField(
        unique=True,
        verbose_name='Año de destino',
    )

    alumnos_primero_a_segundo = models.PositiveIntegerField(
        default=0,
        verbose_name='Promovidos de primero a segundo',
    )

    alumnos_segundo_a_tercero = models.PositiveIntegerField(
        default=0,
        verbose_name='Promovidos de segundo a tercero',
    )

    alumnos_egresados = models.PositiveIntegerField(
        default=0,
        verbose_name='Alumnos egresados',
    )

    fecha_ejecucion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de ejecución',
    )

    class Meta:
        ordering = ['-anio_destino']
        verbose_name = 'Promoción anual'
        verbose_name_plural = 'Promociones anuales'

    def __str__(self):
        return (
            f'Promoción {self.anio_origen} '
            f'→ {self.anio_destino}'
        )