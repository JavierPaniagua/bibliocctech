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

    nombre_completo = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Nombre y apellido',
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

    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de registro',
    )

    class Meta:
        verbose_name = 'Alumno'
        verbose_name_plural = 'Alumnos'
        ordering = [
            'nombre_completo',
            'apellidos',
            'nombres',
        ]

    def save(self, *args, **kwargs):
        self.nombre_completo = ' '.join(
            self.nombre_completo.strip().split()
        ).upper()

        self.nombres = ' '.join(
            self.nombres.strip().split()
        ).upper()

        self.apellidos = ' '.join(
            self.apellidos.strip().split()
        ).upper()

        self.curso = self.curso.strip().upper()
        self.seccion = self.seccion.strip().upper()
        self.especialidad = self.especialidad.strip().upper()

        super().save(*args, **kwargs)

    @property
    def nombre_visible(self):
        if self.nombre_completo:
            return self.nombre_completo

        return f'{self.nombres} {self.apellidos}'.strip()

    def __str__(self):
        return f'{self.nombre_visible} - {self.cedula}'