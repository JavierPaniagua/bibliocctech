from django import forms

from .models import Ejemplar, Libro


class LibroCrearForm(forms.ModelForm):
    cantidad_ejemplares = forms.IntegerField(
        label='Cantidad de ejemplares',
        min_value=1,
        max_value=500,
        initial=1,
        widget=forms.NumberInput(
            attrs={
                'class': 'campo',
                'min': 1,
                'max': 500,
            }
        ),
    )

    condicion_inicial = forms.ChoiceField(
        label='Condición inicial',
        choices=Ejemplar.Condicion.choices,
        initial=Ejemplar.Condicion.BUENO,
        widget=forms.Select(
            attrs={
                'class': 'campo',
            }
        ),
    )

    forma_adquisicion = forms.ChoiceField(
        label='Forma de adquisición',
        choices=Ejemplar.FormaAdquisicion.choices,
        initial=Ejemplar.FormaAdquisicion.NO_ESPECIFICADA,
        widget=forms.Select(
            attrs={
                'class': 'campo',
            }
        ),
    )

    fecha_adquisicion = forms.DateField(
        label='Fecha de adquisición',
        required=False,
        widget=forms.DateInput(
            attrs={
                'class': 'campo',
                'type': 'date',
            }
        ),
    )

    class Meta:
        model = Libro

        fields = [
            'titulo',
            'autor',
            'editorial',
            'categoria',
            'isbn',
            'edicion',
            'anio_publicacion',
            'ubicacion',
            'descripcion',
            'activo',
        ]

        widgets = {
            'titulo': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': 'Título del libro',
                    'autofocus': True,
                }
            ),

            'autor': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': 'Autor o autores',
                }
            ),

            'editorial': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': 'Editorial',
                }
            ),

            'categoria': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': 'Ejemplo: Electricidad',
                }
            ),

            'isbn': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': 'ISBN con o sin guiones',
                }
            ),

            'edicion': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': 'Ejemplo: Segunda edición',
                }
            ),

            'anio_publicacion': forms.NumberInput(
                attrs={
                    'class': 'campo',
                    'min': 1000,
                    'max': 2100,
                    'placeholder': 'Ejemplo: 2024',
                }
            ),

            'ubicacion': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': 'Ejemplo: Estante A-01',
                }
            ),

            'descripcion': forms.Textarea(
                attrs={
                    'class': 'campo',
                    'rows': 4,
                    'placeholder': 'Descripción opcional',
                }
            ),

            'activo': forms.CheckboxInput(
                attrs={
                    'class': 'casilla',
                }
            ),
        }

    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn', '').strip()

        return (
            isbn
            .replace(' ', '')
            .replace('-', '')
        )

    def clean_anio_publicacion(self):
        anio = self.cleaned_data.get('anio_publicacion')

        if anio and (anio < 1000 or anio > 2100):
            raise forms.ValidationError(
                'Ingrese un año válido entre 1000 y 2100.'
            )

        return anio


class LibroEditarForm(forms.ModelForm):
    class Meta:
        model = Libro

        fields = [
            'titulo',
            'autor',
            'editorial',
            'categoria',
            'isbn',
            'edicion',
            'anio_publicacion',
            'ubicacion',
            'descripcion',
            'activo',
        ]

        widgets = {
            'titulo': forms.TextInput(
                attrs={
                    'class': 'campo',
                }
            ),

            'autor': forms.TextInput(
                attrs={
                    'class': 'campo',
                }
            ),

            'editorial': forms.TextInput(
                attrs={
                    'class': 'campo',
                }
            ),

            'categoria': forms.TextInput(
                attrs={
                    'class': 'campo',
                }
            ),

            'isbn': forms.TextInput(
                attrs={
                    'class': 'campo',
                }
            ),

            'edicion': forms.TextInput(
                attrs={
                    'class': 'campo',
                }
            ),

            'anio_publicacion': forms.NumberInput(
                attrs={
                    'class': 'campo',
                    'min': 1000,
                    'max': 2100,
                }
            ),

            'ubicacion': forms.TextInput(
                attrs={
                    'class': 'campo',
                }
            ),

            'descripcion': forms.Textarea(
                attrs={
                    'class': 'campo',
                    'rows': 4,
                }
            ),

            'activo': forms.CheckboxInput(
                attrs={
                    'class': 'casilla',
                }
            ),
        }

    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn', '').strip()

        return (
            isbn
            .replace(' ', '')
            .replace('-', '')
        )

class ImportarLibrosForm(forms.Form):
    archivo = forms.FileField(
        label='Planilla Excel',
        widget=forms.ClearableFileInput(
            attrs={
                'class': 'campo',
                'accept': '.xlsx',
            }
        ),
    )

    def clean_archivo(self):
        archivo = self.cleaned_data['archivo']

        if not archivo.name.lower().endswith('.xlsx'):
            raise forms.ValidationError(
                'Seleccione un archivo Excel con extensión .xlsx.'
            )

        if archivo.size > 10 * 1024 * 1024:
            raise forms.ValidationError(
                'El archivo no puede superar los 10 MB.'
            )

        return archivo