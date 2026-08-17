from django import forms
from django.utils import timezone

from alumnos.models import Alumno
from docentes.models import Docente
from libros.models import Ejemplar

from .models import Prestamo


def limpiar_cedula(valor):
    """
    Permite cédulas paraguayas y extranjeras.
    Elimina puntos, espacios y guiones.
    """
    return (
        str(valor or "")
        .strip()
        .replace(".", "")
        .replace("-", "")
        .replace(" ", "")
    )


class PrestamoForm(forms.Form):
    TIPO_BENEFICIARIO = [
        ("ALUMNO", "Alumno"),
        ("DOCENTE", "Docente"),
    ]

    tipo_beneficiario = forms.ChoiceField(
        label="Tipo de beneficiario",
        choices=TIPO_BENEFICIARIO,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    cedula = forms.CharField(
        label="Cédula",
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ingrese la cédula",
                "autocomplete": "off",
                "autofocus": True,
            }
        ),
    )

    numero_inventario = forms.IntegerField(
        label="Número de inventario del libro",
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Ejemplo: 5011",
                "autocomplete": "off",
            }
        ),
    )

    fecha_prestamo = forms.DateField(
        label="Fecha del préstamo",
        initial=timezone.localdate,
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            }
        ),
    )

    observaciones = forms.CharField(
        label="Observaciones",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Observaciones opcionales",
            }
        ),
    )

    def clean_cedula(self):
        cedula = limpiar_cedula(self.cleaned_data["cedula"])

        if not cedula:
            raise forms.ValidationError("Ingrese la cédula.")

        if len(cedula) > 20:
            raise forms.ValidationError(
                "La cédula no puede superar los 20 caracteres."
            )

        return cedula

    def clean_fecha_prestamo(self):
        fecha = self.cleaned_data["fecha_prestamo"]

        if fecha > timezone.localdate():
            raise forms.ValidationError(
                "La fecha del préstamo no puede ser futura."
            )

        return fecha

    def clean(self):
        cleaned_data = super().clean()

        tipo = cleaned_data.get("tipo_beneficiario")
        cedula = cleaned_data.get("cedula")
        numero_inventario = cleaned_data.get("numero_inventario")

        if not tipo or not cedula or not numero_inventario:
            return cleaned_data

        alumno = None
        docente = None

        if tipo == "ALUMNO":
            try:
                alumno = Alumno.objects.get(cedula=cedula)
            except Alumno.DoesNotExist:
                self.add_error(
                    "cedula",
                    "No se encontró un alumno con esta cédula.",
                )
            except Alumno.MultipleObjectsReturned:
                self.add_error(
                    "cedula",
                    "Existen varios alumnos con esta cédula. Revise la base de datos.",
                )
            else:
                if hasattr(alumno, "activo") and not alumno.activo:
                    self.add_error(
                        "cedula",
                        "El alumno está inactivo o figura como exalumno.",
                    )

        elif tipo == "DOCENTE":
            try:
                docente = Docente.objects.get(cedula=cedula)
            except Docente.DoesNotExist:
                self.add_error(
                    "cedula",
                    "No se encontró un docente con esta cédula.",
                )
            except Docente.MultipleObjectsReturned:
                self.add_error(
                    "cedula",
                    "Existen varios docentes con esta cédula. Revise la base de datos.",
                )
            else:
                if hasattr(docente, "activo") and not docente.activo:
                    self.add_error(
                        "cedula",
                        "El docente está inactivo.",
                    )

        # Una persona con libros vencidos debe devolverlos antes
        # de recibir otro ejemplar.
        if alumno is not None or docente is not None:
            prestamos_vencidos = Prestamo.objects.filter(
                estado=Prestamo.Estado.ACTIVO,
                fecha_devolucion_prevista__lt=timezone.localdate(),
            )

            if alumno is not None:
                prestamos_vencidos = prestamos_vencidos.filter(
                    alumno=alumno
                )
            else:
                prestamos_vencidos = prestamos_vencidos.filter(
                    docente=docente
                )

            if prestamos_vencidos.exists():
                self.add_error(
                    "cedula",
                    (
                        "El beneficiario posee uno o más préstamos "
                        "vencidos. Registre primero la devolución."
                    ),
                )

        try:
            ejemplar = Ejemplar.objects.select_related("libro").get(
                numero_inventario=numero_inventario
            )
        except Ejemplar.DoesNotExist:
            self.add_error(
                "numero_inventario",
                "No existe un libro con este número de inventario.",
            )
            ejemplar = None

        if ejemplar is not None:
            if ejemplar.estado != Ejemplar.Estado.DISPONIBLE:
                self.add_error(
                    "numero_inventario",
                    (
                        f'El ejemplar "{ejemplar.libro.titulo}" '
                        f"no está disponible. Estado actual: "
                        f"{ejemplar.get_estado_display()}."
                    ),
                )

            prestamo_activo = Prestamo.objects.filter(
                ejemplar=ejemplar,
                estado=Prestamo.Estado.ACTIVO,
            ).exists()

            if prestamo_activo:
                self.add_error(
                    "numero_inventario",
                    "Este ejemplar ya tiene un préstamo activo.",
                )

        cleaned_data["alumno"] = alumno
        cleaned_data["docente"] = docente
        cleaned_data["ejemplar"] = ejemplar

        return cleaned_data


class DevolucionForm(forms.Form):
    fecha_devolucion_real = forms.DateField(
        label="Fecha de devolución",
        initial=timezone.localdate,
        widget=forms.DateInput(
            attrs={
                "class": "campo",
                "type": "date",
            }
        ),
    )

    condicion = forms.ChoiceField(
        label="Condición del libro",
        choices=Ejemplar.Condicion.choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    observaciones = forms.CharField(
        label="Observaciones de la devolución",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": (
                    "Ejemplo: devuelto correctamente o presenta daños"
                ),
            }
        ),
    )

    def __init__(self, *args, prestamo=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.prestamo = prestamo

        if prestamo is not None and not self.is_bound:
            self.fields["condicion"].initial = prestamo.ejemplar.condicion

        self.fields["fecha_devolucion_real"].widget.attrs.update(
            {
                "class": "form-control",
                "max": timezone.localdate().isoformat(),
            }
        )

    def clean_fecha_devolucion_real(self):
        fecha = self.cleaned_data["fecha_devolucion_real"]

        if self.prestamo and fecha < self.prestamo.fecha_prestamo:
            raise forms.ValidationError(
                "La devolución no puede ser anterior a la fecha del préstamo."
            )

        if fecha > timezone.localdate():
            raise forms.ValidationError(
                "La fecha de devolución no puede ser futura."
            )

        return fecha