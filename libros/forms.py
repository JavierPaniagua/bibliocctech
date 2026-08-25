from django import forms

from .models import Ejemplar, Libro


CLASIFICACIONES_SUGERIDAS = [
    (
        '',
        'Seleccione un tema para recibir una sugerencia',
    ),

    (
        'Informática y computación',
        [
            ('004', '004 — Informática y computación'),
            ('004.6', '004.6 — Redes de computadoras'),
            ('005', '005 — Programación y programas'),
            ('005.1', '005.1 — Programación'),
            ('005.43', '005.43 — Sistemas operativos'),
            ('005.74', '005.74 — Bases de datos'),
            ('006', '006 — Métodos especiales de computación'),
            ('006.7', '006.7 — Multimedia y desarrollo web'),
        ],
    ),

    (
        'Filosofía y psicología',
        [
            ('100', '100 — Filosofía'),
            ('150', '150 — Psicología'),
            ('160', '160 — Lógica'),
            ('170', '170 — Ética'),
        ],
    ),

    (
        'Ciencias sociales y educación',
        [
            ('300', '300 — Ciencias sociales'),
            ('330', '330 — Economía'),
            ('334', '334 — Cooperativismo'),
            ('337', '337 — Economía internacional'),
            ('370', '370 — Educación'),
            ('373', '373 — Educación secundaria'),
            ('380', '380 — Comercio y comunicaciones'),
            ('382', '382 — Comercio internacional'),
        ],
    ),

    (
        'Administración y contabilidad',
        [
            ('650', '650 — Administración y servicios auxiliares'),
            ('651', '651 — Servicios de oficina'),
            ('657', '657 — Contabilidad'),
            ('658', '658 — Administración general'),
            ('659', '659 — Publicidad y relaciones públicas'),
        ],
    ),

    (
        'Lengua y literatura',
        [
            ('400', '400 — Lenguas'),
            ('460', '460 — Lengua española'),
            ('800', '800 — Literatura'),
            ('860', '860 — Literatura española'),
        ],
    ),

    (
        'Matemática',
        [
            ('510', '510 — Matemática general'),
            ('511', '511 — Principios generales de matemática'),
            ('512', '512 — Álgebra'),
            ('513', '513 — Aritmética'),
            ('515', '515 — Cálculo y análisis'),
            ('516', '516 — Geometría'),
            ('516.2', '516.2 — Geometría euclidiana'),
            ('516.22', '516.22 — Geometría plana'),
            ('516.23', '516.23 — Geometría del espacio'),
            ('516.24', '516.24 — Trigonometría'),
            ('516.3', '516.3 — Geometría analítica'),
            ('519', '519 — Probabilidad y matemática aplicada'),
        ],
    ),

      (
        'Ciencias naturales',
        [
            ('500', '500 — Ciencias naturales'),
            ('520', '520 — Astronomía'),
            ('530', '530 — Física'),
            ('537', '537 — Electricidad y electrónica'),
            ('540', '540 — Química'),
            ('550', '550 — Ciencias de la Tierra'),
            ('570', '570 — Ciencias de la vida'),
            ('574', '574 — Biología'),
            ('580', '580 — Ciencias botánicas'),
            ('581', '581 — Botánica'),
            ('590', '590 — Ciencias zoológicas'),
            ('591', '591 — Zoología'),
        ],
    ),

    (
        'Tecnología, electricidad y electrónica',
        [
            ('600', '600 — Tecnología'),
            ('620', '620 — Ingeniería'),
            ('621', '621 — Física aplicada'),
            ('621.3', '621.3 — Ingeniería eléctrica y electrónica'),
            ('621.31', '621.31 — Generación y distribución eléctrica'),
            ('621.381', '621.381 — Electrónica'),
            ('621.382', '621.382 — Telecomunicaciones'),
            ('621.39', '621.39 — Ingeniería de computadoras'),
        ],
    ),

    (
        'Artes, geografía e historia',
        [
            ('700', '700 — Artes'),
            ('740', '740 — Dibujo y artes decorativas'),
            ('900', '900 — Geografía e historia'),
            ('910', '910 — Geografía y viajes'),
            ('980', '980 — Historia de América del Sur'),
            ('989', '989 — Historia del Paraguay'),
        ],
    ),
]


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
        tema_sugerido = datos.get(
            'tema_sugerido',
            '',
        )

        clasificacion = (
            datos.get('clasificacion', '')
            or ''
        ).strip()

        if tema_sugerido:
            clasificacion = tema_sugerido
            datos['clasificacion'] = tema_sugerido

        if not area:
            self.add_error(
                'area',
                'Seleccione el área del libro.',
            )

        if not clasificacion:
            self.add_error(
                'clasificacion',
                (
                    'Seleccione un tema sugerido o ingrese '
                    'el código de clasificación.'
                ),
            )

        return datos


class LibroCrearForm(
    LibroNormalizacionMixin,
    forms.ModelForm,
):
    tema_sugerido = forms.ChoiceField(
        label='Ayuda para elegir la clasificación',
        required=False,
        choices=CLASIFICACIONES_SUGERIDAS,
        widget=forms.Select(
            attrs={
                'class': 'campo',
            }
        ),
        help_text=(
            'Seleccione el tema principal. '
            'El código sugerido reemplazará la clasificación escrita.'
        ),
    )
    codigo_existente = forms.CharField(
        label='Código existente del libro',
        required=False,
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'class': 'campo',
                'placeholder': 'Ejemplo: 1, 200 o 1000',
            }
        ),
        help_text=(
            'Ingrese el código que ya aparece en el libro. '
            'Déjelo vacío si el libro no posee uno.'
        ),
    )

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

    def clean_codigo_existente(self):
        return self.cleaned_data.get(
            'codigo_existente',
            '',
        ).strip()
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

    field_order = [
        'titulo',
        'autor',
        'editorial',
        'area',
        'tema_sugerido',
        'clasificacion',
        'clave_autor',
        'clave_titulo',
        'isbn',
        'edicion',
        'anio_publicacion',
        'descripcion',
        'cantidad_ejemplares',
        'estanteria',
        'balda',
        'condicion_inicial',
        'forma_adquisicion',
        'fecha_adquisicion',
        'proveedor',
        'observaciones',
        'activo',
    ]

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
    tema_sugerido = forms.ChoiceField(
        label='Ayuda para elegir la clasificación',
        required=False,
        choices=CLASIFICACIONES_SUGERIDAS,
        widget=forms.Select(
            attrs={
                'class': 'campo',
            }
        ),
        help_text=(
            'Es opcional. Déjelo vacío para conservar '
            'la clasificación actual.'
        ),
    )

    field_order = [
        'titulo',
        'autor',
        'editorial',
        'area',
        'tema_sugerido',
        'clasificacion',
        'clave_autor',
        'clave_titulo',
        'isbn',
        'edicion',
        'anio_publicacion',
        'descripcion',
        'activo',
    ]

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