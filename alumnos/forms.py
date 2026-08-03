from django import forms

from .models import Alumno


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