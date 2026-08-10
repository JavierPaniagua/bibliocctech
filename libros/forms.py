from django import forms

from .models import Ejemplar, Libro


def normalizar_estanteria(valor):
    valor = (valor or '').strip()

    if not valor:
        return ''

    if not valor.isdigit() or int(valor) < 1:
        raise forms.ValidationError(
            'La estantería debe ser un número mayor que cero.'
        )

    return str(int(valor))


def normalizar_balda(valor):
    valor = (valor or '').strip().upper()

    if not valor:
        return ''

    if len(valor) != 1 or not valor.isalpha():
        raise forms.ValidationError(
            'La balda debe ser una sola letra. Ejemplo: A.'
        )

    return valor


class LibroNormalizacionMixin:
    def clean_isbn(self):
        isbn = self.cleaned_data.get(
            'isbn',
            '',
        ).strip()

        return (
            isbn
            .replace(' ', '')
            .replace('-', '')
        )

    def clean_clasificacion(self):
        return self.cleaned_data.get(
            'clasificacion',
            '',
        ).strip()

    def clean_clave_autor(self):
        return self.cleaned_data.get(
            'clave_autor',
            '',
        ).strip().upper()

    def clean_clave_titulo(self):
        return self.cleaned_data.get(
            'clave_titulo',
            '',
        ).strip().lower()

    def clean_anio_publicacion(self):
        anio = self.cleaned_data.get(
            'anio_publicacion'
        )

        if anio and (
            anio < 1000
            or anio > 2100
        ):
            raise forms.ValidationError(
                'Ingrese un año válido entre 1000 y 2100.'
            )

        return anio

    def clean(self):
        datos = super().clean()

        area = datos.get('area')
        clasificacion = datos.get(
            'clasificacion',
            '',
        ).strip()

        if not area:
            self.add_error(
                'area',
                'Seleccione el área del libro.',
            )

        if not clasificacion:
            self.add_error(
                'clasificacion',
                'Ingrese el código de clasificación.',
            )

        return datos


class LibroCrearForm(
    LibroNormalizacionMixin,
    forms.ModelForm,
):
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

    estanteria = forms.CharField(
        label='Estantería',
        required=False,
        max_length=20,
        widget=forms.TextInput(
            attrs={
                'class': 'campo',
                'placeholder': 'Ejemplo: 1',
            }
        ),
    )

    balda = forms.CharField(
        label='Balda',
        required=False,
        max_length=1,
        widget=forms.TextInput(
            attrs={
                'class': 'campo',
                'placeholder': 'Ejemplo: A',
                'maxlength': 1,
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
        initial=(
            Ejemplar.FormaAdquisicion.NO_ESPECIFICADA
        ),
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

    proveedor = forms.CharField(
        label='Proveedor o procedencia',
        required=False,
        max_length=200,
        widget=forms.TextInput(
            attrs={
                'class': 'campo',
                'placeholder': (
                    'Proveedor, institución o donante'
                ),
            }
        ),
    )

    observaciones = forms.CharField(
        label='Observaciones del ejemplar',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'campo',
                'rows': 3,
                'placeholder': 'Observaciones opcionales',
            }
        ),
    )

    class Meta:
        model = Libro

        fields = [
            'titulo',
            'autor',
            'editorial',
            'area',
            'clasificacion',
            'clave_autor',
            'clave_titulo',
            'isbn',
            'edicion',
            'anio_publicacion',
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

            'area': forms.Select(
                attrs={
                    'class': 'campo',
                }
            ),

            'clasificacion': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': 'Ejemplo: 516.3',
                }
            ),

            'clave_autor': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': (
                        'Vacío para generar automáticamente'
                    ),
                }
            ),

            'clave_titulo': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': (
                        'Vacío para generar automáticamente'
                    ),
                }
            ),

            'isbn': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': 'ISBN opcional',
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

    def clean_estanteria(self):
        return normalizar_estanteria(
            self.cleaned_data.get(
                'estanteria'
            )
        )

    def clean_balda(self):
        return normalizar_balda(
            self.cleaned_data.get(
                'balda'
            )
        )


class LibroEditarForm(
    LibroNormalizacionMixin,
    forms.ModelForm,
):
    class Meta:
        model = Libro

        fields = [
            'titulo',
            'autor',
            'editorial',
            'area',
            'clasificacion',
            'clave_autor',
            'clave_titulo',
            'isbn',
            'edicion',
            'anio_publicacion',
            'descripcion',
            'activo',
        ]

        widgets = {
            'titulo': forms.TextInput(
                attrs={'class': 'campo'}
            ),

            'autor': forms.TextInput(
                attrs={'class': 'campo'}
            ),

            'editorial': forms.TextInput(
                attrs={'class': 'campo'}
            ),

            'area': forms.Select(
                attrs={'class': 'campo'}
            ),

            'clasificacion': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': 'Ejemplo: 516.3',
                }
            ),

            'clave_autor': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': (
                        'Ejemplo: BAL'
                    ),
                }
            ),

            'clave_titulo': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': (
                        'Ejemplo: geo'
                    ),
                }
            ),

            'isbn': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': 'ISBN opcional',
                }
            ),

            'edicion': forms.TextInput(
                attrs={'class': 'campo'}
            ),

            'anio_publicacion': forms.NumberInput(
                attrs={
                    'class': 'campo',
                    'min': 1000,
                    'max': 2100,
                }
            ),

            'descripcion': forms.Textarea(
                attrs={
                    'class': 'campo',
                    'rows': 4,
                }
            ),

            'activo': forms.CheckboxInput(
                attrs={'class': 'casilla'}
            ),
        }


class EjemplarForm(forms.ModelForm):
    class Meta:
        model = Ejemplar

        fields = [
            'numero_inventario',
            'codigo_anterior',
            'estanteria',
            'balda',
            'proveedor',
            'estado',
            'condicion',
            'forma_adquisicion',
            'fecha_adquisicion',
            'observaciones',
        ]

        widgets = {
            'numero_inventario': forms.NumberInput(
                attrs={
                    'class': 'campo',
                    'min': 1,
                    'placeholder': (
                        'Vacío para generar automáticamente'
                    ),
                }
            ),

            'codigo_anterior': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': (
                        'Código histórico opcional'
                    ),
                }
            ),

            'estanteria': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': 'Ejemplo: 1',
                }
            ),

            'balda': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': 'Ejemplo: A',
                    'maxlength': 1,
                }
            ),

            'proveedor': forms.TextInput(
                attrs={
                    'class': 'campo',
                    'placeholder': (
                        'Proveedor, institución o donante'
                    ),
                }
            ),

            'estado': forms.Select(
                attrs={'class': 'campo'}
            ),

            'condicion': forms.Select(
                attrs={'class': 'campo'}
            ),

            'forma_adquisicion': forms.Select(
                attrs={'class': 'campo'}
            ),

            'fecha_adquisicion': forms.DateInput(
                attrs={
                    'class': 'campo',
                    'type': 'date',
                }
            ),

            'observaciones': forms.Textarea(
                attrs={
                    'class': 'campo',
                    'rows': 4,
                }
            ),
        }

    def clean_estanteria(self):
        return normalizar_estanteria(
            self.cleaned_data.get(
                'estanteria'
            )
        )

    def clean_balda(self):
        return normalizar_balda(
            self.cleaned_data.get(
                'balda'
            )
        )


class ImportarLibrosForm(forms.Form):
    archivo = forms.FileField(
        label='Inventario maestro Excel',
        widget=forms.ClearableFileInput(
            attrs={
                'class': 'campo',
                'accept': '.xlsx',
            }
        ),
    )

    def clean_archivo(self):
        archivo = self.cleaned_data['archivo']

        if not archivo.name.lower().endswith(
            '.xlsx'
        ):
            raise forms.ValidationError(
                'Seleccione un archivo Excel .xlsx.'
            )

        if archivo.size > 10 * 1024 * 1024:
            raise forms.ValidationError(
                'El archivo no puede superar los 10 MB.'
            )

        return archivo