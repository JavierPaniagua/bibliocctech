from django.db import models


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

    nombres = models.CharField(
        max_length=100,
        verbose_name='Nombres',
    )

    apellidos = models.CharField(
        max_length=100,
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

    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de registro',
    )

    class Meta:
        verbose_name = 'Alumno'
        verbose_name_plural = 'Alumnos'
        ordering = ['apellidos', 'nombres']

    def __str__(self):
        return f'{self.apellidos}, {self.nombres} - {self.cedula}'