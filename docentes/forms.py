from django import forms

from .models import Docente


class DocenteForm(forms.ModelForm):
    class Meta:
        model = Docente

        fields = [
            'cedula',
            'nombres',
            'apellidos',
            'area',
            'especialidad',
            'telefono',
            'correo',
            'turno',
            'activo',
        ]

        widgets = {
            'cedula': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': 'Ejemplo: 3456789',
                    'autofocus': True,
                }
            ),

            'nombres': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': 'Nombres del docente',
                }
            ),

            'apellidos': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': 'Apellidos del docente',
                }
            ),

            'area': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': 'Ejemplo: Área técnica',
                }
            ),

            'especialidad': forms.Select(
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

            'correo': forms.EmailInput(
                attrs={
                    'class': 'campo',
                    'placeholder': 'correo@ejemplo.com',
                }
            ),

            'turno': forms.Select(
                attrs={
                    'class': 'campo',
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