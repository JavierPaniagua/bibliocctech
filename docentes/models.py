from django.db import models


class Docente(models.Model):
    ESPECIALIDAD_CHOICES = [
        ('ELECTRÓNICA', 'Electrónica'),
        ('ELECTRICIDAD', 'Electricidad'),
    ]

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

    area = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Área o departamento',
    )

    especialidad = models.CharField(
        max_length=20,
        choices=ESPECIALIDAD_CHOICES,
        verbose_name='Especialidad',
    )

    telefono = models.CharField(
        max_length=30,
        blank=True,
        verbose_name='Teléfono',
    )

    correo = models.EmailField(
        blank=True,
        verbose_name='Correo electrónico',
    )

    turno = models.CharField(
        max_length=10,
        choices=TURNO_CHOICES,
        verbose_name='Turno',
    )

    activo = models.BooleanField(
        default=True,
        verbose_name='Docente activo',
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de registro',
    )

    class Meta:
        verbose_name = 'Docente'
        verbose_name_plural = 'Docentes'
        ordering = ['apellidos', 'nombres']

    def __str__(self):
        return (
            f'{self.apellidos}, {self.nombres} '
            f'- {self.cedula}'
        )