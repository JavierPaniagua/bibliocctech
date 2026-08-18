from django import forms

from .models import Alumno
from django.utils import timezone


class AlumnoForm(forms.ModelForm):
    class Meta:
        model = Alumno

        fields = [
            'cedula',
            'nombres',
            'apellidos',
            'curso',
            'seccion',
            'especialidad',
            'turno',
            'telefono',
            'activo',
        ]

        widgets = {
            'cedula': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': 'Ejemplo: 5123456',
                    'autofocus': True,
                }
            ),

            'nombres': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': 'Nombres del alumno',
                }
            ),

            'apellidos': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': 'Apellidos del alumno',
                }
            ),

            'curso': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': 'Ejemplo: 1° BTI',
                }
            ),

            'seccion': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': 'Ejemplo: A',
                }
            ),

            'especialidad': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': 'Ejemplo: Informática',
                }
            ),

            'turno': forms.Select(
                attrs={
                    'class': 'campo',
                }
            ),

            'telefono': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': 'Opcional',
                }
            ),

            'activo': forms.CheckboxInput(
                attrs={
                    'class': 'casilla',
                }
            ),
        }

    def clean_cedula(self):
        cedula = self.cleaned_data['cedula']

        cedula = (
            cedula
            .replace('.', '')
            .replace(' ', '')
            .replace('-', '')
        )

        if not cedula.isdigit():
            raise forms.ValidationError(
                'La cédula debe contener solamente números.'
            )

        return cedula

class ImportarAlumnosForm(forms.Form):
    anio_lectivo = forms.IntegerField(
        label='Año lectivo',
        min_value=2026,
        max_value=2100,
        initial=lambda: timezone.localdate().year,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: 2027',
            }
        ),
        help_text=(
            'Indique el año al que pertenece la lista '
            'oficial de alumnos.'
        ),
    )

    archivo = forms.FileField(
        label='Planilla Excel',
        widget=forms.ClearableFileInput(
            attrs={
                'class': 'form-control',
                'accept': '.xlsx',
            }
        ),
    )

    def clean_archivo(self):
        archivo = self.cleaned_data['archivo']

        if not archivo.name.lower().endswith('.xlsx'):
            raise forms.ValidationError(
                'Seleccione un archivo de Excel '
                'con extensión .xlsx.'
            )

        if archivo.size > 5 * 1024 * 1024:
            raise forms.ValidationError(
                'El archivo no puede superar los 5 MB.'
            )

        return archivo