from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from alumnos.models import Alumno
from docentes.models import Docente
from libros.models import Ejemplar


class Prestamo(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = 'ACTIVO', 'Activo'
        DEVUELTO = 'DEVUELTO', 'Devuelto'

    ejemplar = models.ForeignKey(
        Ejemplar,
        on_delete=models.PROTECT,
        related_name='prestamos',
        verbose_name='Ejemplar',
    )

    alumno = models.ForeignKey(
        Alumno,
        on_delete=models.PROTECT,
        related_name='prestamos',
        null=True,
        blank=True,
        verbose_name='Alumno',
    )

    docente = models.ForeignKey(
        Docente,
        on_delete=models.PROTECT,
        related_name='prestamos',
        null=True,
        blank=True,
        verbose_name='Docente',
    )

    fecha_prestamo = models.DateField(
        default=timezone.localdate,
        verbose_name='Fecha del préstamo',
    )

    fecha_devolucion_prevista = models.DateField(
        blank=True,
        verbose_name='Fecha prevista de devolución',
    )

    fecha_devolucion_real = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha real de devolución',
    )

    estado = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.ACTIVO,
        verbose_name='Estado',
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
        verbose_name = 'Préstamo'
        verbose_name_plural = 'Préstamos'
        ordering = [
            '-fecha_prestamo',
            '-id',
        ]

        constraints = [
            models.CheckConstraint(
                condition=(
                    (
                        Q(alumno__isnull=False)
                        & Q(docente__isnull=True)
                    )
                    |
                    (
                        Q(alumno__isnull=True)
                        & Q(docente__isnull=False)
                    )
                ),
                name='prestamo_un_solo_beneficiario',
            ),

            models.UniqueConstraint(
                fields=['ejemplar'],
                condition=Q(estado='ACTIVO'),
                name='ejemplar_unico_prestamo_activo',
            ),
        ]

    def __str__(self):
        return (
            f'{self.ejemplar.codigo} - '
            f'{self.nombre_beneficiario}'
        )

    @property
    def nombre_beneficiario(self):
        if self.alumno:
            return (
                f'{self.alumno.apellidos}, '
                f'{self.alumno.nombres}'
            )

        if self.docente:
            return (
                f'{self.docente.apellidos}, '
                f'{self.docente.nombres}'
            )

        return 'Sin beneficiario'

    @property
    def tipo_beneficiario(self):
        if self.alumno:
            return 'Alumno'

        if self.docente:
            return 'Docente'

        return '-'

    @property
    def cedula_beneficiario(self):
        if self.alumno:
            return self.alumno.cedula

        if self.docente:
            return self.docente.cedula

        return '-'

    @property
    def esta_vencido(self):
        return (
            self.estado == self.Estado.ACTIVO
            and self.fecha_devolucion_prevista
            < timezone.localdate()
        )

    @property
    def dias_atraso(self):
        if not self.esta_vencido:
            return 0

        diferencia = (
            timezone.localdate()
            - self.fecha_devolucion_prevista
        )

        return diferencia.days

    def clean(self):
        super().clean()

        tiene_alumno = self.alumno_id is not None
        tiene_docente = self.docente_id is not None

        if tiene_alumno == tiene_docente:
            raise ValidationError(
                (
                    'El préstamo debe pertenecer solamente '
                    'a un alumno o a un docente.'
                )
            )

        if self.fecha_devolucion_prevista:
            if (
                self.fecha_devolucion_prevista
                < self.fecha_prestamo
            ):
                raise ValidationError(
                    {
                        'fecha_devolucion_prevista': (
                            'La devolución prevista no puede '
                            'ser anterior al préstamo.'
                        )
                    }
                )

    def save(self, *args, **kwargs):
        if not self.fecha_devolucion_prevista:
            self.fecha_devolucion_prevista = (
                self.fecha_prestamo
                + timedelta(days=5)
            )

        self.full_clean()

        super().save(*args, **kwargs)