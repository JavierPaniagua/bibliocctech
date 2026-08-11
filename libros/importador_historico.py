import re
import unicodedata
from datetime import date, datetime

from django.db import transaction
from openpyxl import load_workbook

from .models import Ejemplar, ImportacionLibros, Libro


def limpiar_texto(valor):
    if valor is None:
        return ''

    if isinstance(valor, float) and valor.is_integer():
        valor = int(valor)

    return ' '.join(
        str(valor).strip().split()
    )


def normalizar_texto(valor):
    texto = limpiar_texto(valor).lower()

    texto = unicodedata.normalize(
        'NFD',
        texto,
    )

    texto = ''.join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != 'Mn'
    )

    texto = re.sub(
        r'\s+',
        ' ',
        texto,
    )

    return texto.strip()


def normalizar_encabezado(valor):
    texto = normalizar_texto(valor)

    texto = re.sub(
        r'[^a-z0-9 ]',
        '',
        texto,
    )

    return texto.strip()


def obtener_numero_inventario(valor):
    if valor in (None, ''):
        return None

    if isinstance(valor, int):
        return valor if valor > 0 else None

    if (
        isinstance(valor, float)
        and valor.is_integer()
    ):
        numero = int(valor)

        return numero if numero > 0 else None

    texto = limpiar_texto(valor)

    if not texto.isdigit():
        return None

    numero = int(texto)

    return numero if numero > 0 else None


def convertir_entero(valor):
    if valor in (None, ''):
        return None

    if isinstance(valor, int):
        return valor

    if (
        isinstance(valor, float)
        and valor.is_integer()
    ):
        return int(valor)

    try:
        return int(limpiar_texto(valor))
    except (TypeError, ValueError):
        return None


def convertir_fecha(valor):
    if valor in (None, ''):
        return None

    if isinstance(valor, datetime):
        return valor.date()

    if isinstance(valor, date):
        return valor

    texto = limpiar_texto(valor)

    formatos = [
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%d-%m-%Y',
        '%d/%m/%y',
        '%d-%m-%y',
    ]

    for formato in formatos:
        try:
            return datetime.strptime(
                texto,
                formato,
            ).date()
        except ValueError:
            continue

    return None


def limpiar_isbn(valor):
    isbn = limpiar_texto(valor)

    return (
        isbn
        .replace(' ', '')
        .replace('-', '')
    )


def normalizar_area(valor):
    texto = normalizar_texto(valor)

    equivalencias = {
        'generalidades': Libro.Area.GENERALIDADES,

        'filosofia': Libro.Area.FILOSOFIA,
        'filosofia y psicologia': (
            Libro.Area.FILOSOFIA
        ),

        'religion': Libro.Area.RELIGION,

        'ciencias sociales': (
            Libro.Area.CIENCIAS_SOCIALES
        ),

        'lengua e idiomas': (
            Libro.Area.LENGUA_IDIOMAS
        ),
        'lengua': Libro.Area.LENGUA_IDIOMAS,
        'idiomas': Libro.Area.LENGUA_IDIOMAS,

        'ciencias naturales': (
            Libro.Area.CIENCIAS_NATURALES
        ),
        'ciencias': (
            Libro.Area.CIENCIAS_NATURALES
        ),

        'matematica': Libro.Area.MATEMATICA,

        'tecnologia': Libro.Area.TECNOLOGIA,

        'electricidad': Libro.Area.ELECTRICIDAD,

        'electronica': Libro.Area.ELECTRONICA,

        'informatica': Libro.Area.INFORMATICA,

        'artes': Libro.Area.ARTES,

        'literatura': Libro.Area.LITERATURA,

        'historia y geografia': (
            Libro.Area.HISTORIA_GEOGRAFIA
        ),
        'historia': Libro.Area.HISTORIA_GEOGRAFIA,
        'geografia': Libro.Area.HISTORIA_GEOGRAFIA,

        'referencia': Libro.Area.REFERENCIA,

        'otro': Libro.Area.OTRO,
    }

    return equivalencias.get(texto)


def sugerir_area_por_clasificacion(clasificacion):
    valor = limpiar_texto(
        clasificacion
    ).replace(',', '.')

    if not valor:
        return None

    if valor.startswith(('004', '005')):
        return Libro.Area.INFORMATICA

    if valor.startswith(('020', '030')):
        return Libro.Area.REFERENCIA

    parte_principal = valor.split('.', 1)[0]

    if not parte_principal.isdigit():
        return None

    numero = int(parte_principal)

    if 0 <= numero <= 99:
        return Libro.Area.GENERALIDADES

    if 100 <= numero <= 199:
        return Libro.Area.FILOSOFIA

    if 200 <= numero <= 299:
        return Libro.Area.RELIGION

    if 300 <= numero <= 399:
        return Libro.Area.CIENCIAS_SOCIALES

    if 400 <= numero <= 499:
        return Libro.Area.LENGUA_IDIOMAS

    if 510 <= numero <= 519:
        return Libro.Area.MATEMATICA

    if 500 <= numero <= 599:
        return Libro.Area.CIENCIAS_NATURALES

    if 600 <= numero <= 699:
        return Libro.Area.TECNOLOGIA

    if 700 <= numero <= 799:
        return Libro.Area.ARTES

    if 800 <= numero <= 899:
        return Libro.Area.LITERATURA

    if 900 <= numero <= 999:
        return Libro.Area.HISTORIA_GEOGRAFIA

    return None


def areas_compatibles_con_clasificacion(
    clasificacion,
):
    valor = limpiar_texto(
        clasificacion
    ).replace(',', '.')

    if valor.startswith('621.3'):
        return {
            Libro.Area.TECNOLOGIA,
            Libro.Area.ELECTRICIDAD,
            Libro.Area.ELECTRONICA,
        }

    area_sugerida = (
        sugerir_area_por_clasificacion(valor)
    )

    if area_sugerida is None:
        return set()

    return {area_sugerida}


def normalizar_condicion(valor):
    texto = normalizar_texto(valor)

    equivalencias = {
        'nuevo': Ejemplar.Condicion.NUEVO,
        'bueno': Ejemplar.Condicion.BUENO,
        'regular': Ejemplar.Condicion.REGULAR,
        'deteriorado': (
            Ejemplar.Condicion.DETERIORADO
        ),
    }

    return equivalencias.get(texto)


def normalizar_estado(valor):
    texto = normalizar_texto(valor)

    if not texto:
        return Ejemplar.Estado.DISPONIBLE

    equivalencias = {
        'disponible': Ejemplar.Estado.DISPONIBLE,
        'prestado': Ejemplar.Estado.PRESTADO,

        'en reparacion': (
            Ejemplar.Estado.REPARACION
        ),
        'reparacion': Ejemplar.Estado.REPARACION,

        'deteriorado': (
            Ejemplar.Estado.DETERIORADO
        ),

        'perdido': Ejemplar.Estado.EXTRAVIADO,
        'extraviado': Ejemplar.Estado.EXTRAVIADO,

        'baja': Ejemplar.Estado.BAJA,
        'dado de baja': Ejemplar.Estado.BAJA,
    }

    return equivalencias.get(texto)


def normalizar_adquisicion(valor):
    texto = normalizar_texto(valor)

    if not texto:
        return (
            Ejemplar.FormaAdquisicion.NO_ESPECIFICADA
        )

    equivalencias = {
        'compra': Ejemplar.FormaAdquisicion.COMPRA,
        'donacion': (
            Ejemplar.FormaAdquisicion.DONACION
        ),
        'transferencia': (
            Ejemplar.FormaAdquisicion.TRANSFERENCIA
        ),
        'otro': Ejemplar.FormaAdquisicion.OTRO,
        'no especificada': (
            Ejemplar.FormaAdquisicion.NO_ESPECIFICADA
        ),
    }

    return equivalencias.get(texto)


def convertir_verificado(valor):
    texto = normalizar_texto(valor)

    return texto in {
        'si',
        's',
        'true',
        'verdadero',
        '1',
    }


def buscar_encabezados(hoja):
    equivalencias = {
        'numero_inventario': {
            'numero de inventario',
            'numero inventario',
            'inventario',
        },

        'codigo_anterior': {
            'codigo anterior',
        },

        'titulo': {
            'titulo',
        },

        'autor': {
            'autor',
        },

        'area': {
            'area',
        },

        'clasificacion': {
            'clasificacion',
        },

        'clave_autor': {
            'clave autor',
            'clave del autor',
        },

        'clave_titulo': {
            'clave titulo',
            'clave del titulo',
        },

        'editorial': {
            'editorial',
        },

        'edicion': {
            'edicion',
        },

        'anio_publicacion': {
            'ano',
            'ano de publicacion',
        },

        'isbn': {
            'isbn',
        },

        'estanteria': {
            'estanteria',
        },

        'balda': {
            'balda',
        },

        'proveedor': {
            'proveedor procedencia',
            'proveedor',
            'procedencia',
        },

        'forma_adquisicion': {
            'forma de adquisicion',
            'forma adquisicion',
            'adquisicion',
        },

        'fecha_adquisicion': {
            'fecha de adquisicion',
            'fecha adquisicion',
        },

        'condicion': {
            'condicion',
        },

        'estado': {
            'estado',
        },

        'observaciones': {
            'observacion',
            'observaciones',
        },

        'verificado': {
            'verificado',
            'verificado fisicamente',
        },

        'fecha_verificacion': {
            'fecha de verificacion',
            'fecha verificacion',
        },
    }

    maximo_filas = min(
        hoja.max_row,
        20,
    )

    for numero_fila in range(
        1,
        maximo_filas + 1,
    ):
        columnas = {}

        for numero_columna in range(
            1,
            hoja.max_column + 1,
        ):
            encabezado = normalizar_encabezado(
                hoja.cell(
                    row=numero_fila,
                    column=numero_columna,
                ).value
            )

            if not encabezado:
                continue

            for campo, opciones in (
                equivalencias.items()
            ):
                if encabezado in opciones:
                    columnas[campo] = (
                        numero_columna
                    )
                    break

        campos_obligatorios = {
            'numero_inventario',
            'titulo',
            'area',
            'clasificacion',
            'verificado',
        }

        if campos_obligatorios.issubset(
            columnas.keys()
        ):
            return numero_fila, columnas

    return None, {}


def valor_columna(
    hoja,
    numero_fila,
    columnas,
    campo,
):
    numero_columna = columnas.get(campo)

    if numero_columna is None:
        return None

    return hoja.cell(
        row=numero_fila,
        column=numero_columna,
    ).value


def validar_estanteria(valor):
    texto = limpiar_texto(valor)

    if not texto:
        return ''

    if not texto.isdigit() or int(texto) < 1:
        return None

    return str(int(texto))


def validar_balda(valor):
    texto = limpiar_texto(
        valor
    ).upper()

    if not texto:
        return ''

    if (
        len(texto) != 1
        or not texto.isalpha()
    ):
        return None

    return texto


def extraer_registros(ruta_archivo):
    libro_excel = load_workbook(
        ruta_archivo,
        read_only=True,
        data_only=True,
    )

    try:
        if 'Inventario' not in (
            libro_excel.sheetnames
        ):
            raise ValueError(
                'El Excel debe contener una hoja '
                'llamada Inventario.'
            )

        hoja = libro_excel['Inventario']

        fila_encabezado, columnas = (
            buscar_encabezados(hoja)
        )

        if fila_encabezado is None:
            raise ValueError(
                'No se reconocieron las columnas '
                'oficiales del inventario maestro.'
            )

        registros = []
        errores = []
        codigos_utilizados = set()

        codigos_repetidos = 0
        sin_codigo = 0
        sin_ubicacion = 0
        pendientes_verificacion = 0

        for numero_fila in range(
            fila_encabezado + 1,
            hoja.max_row + 1,
        ):
            numero_original = valor_columna(
                hoja,
                numero_fila,
                columnas,
                'numero_inventario',
            )

            titulo_original = valor_columna(
                hoja,
                numero_fila,
                columnas,
                'titulo',
            )

            if (
                numero_original in (None, '')
                and titulo_original in (None, '')
            ):
                continue

            numero_inventario = (
                obtener_numero_inventario(
                    numero_original
                )
            )

            titulo = limpiar_texto(
                titulo_original
            )

            autor = limpiar_texto(
                valor_columna(
                    hoja,
                    numero_fila,
                    columnas,
                    'autor',
                )
            )

            area_original = valor_columna(
                hoja,
                numero_fila,
                columnas,
                'area',
            )

            clasificacion = limpiar_texto(
                valor_columna(
                    hoja,
                    numero_fila,
                    columnas,
                    'clasificacion',
                )
            ).replace(',', '.')

            area = normalizar_area(
                area_original
            )

            if (
                not normalizar_texto(area_original)
                and clasificacion
            ):
                area = (
                    sugerir_area_por_clasificacion(
                        clasificacion
                    )
                )

            areas_compatibles = (
                areas_compatibles_con_clasificacion(
                    clasificacion
                )
            )

            area_incompatible = (
                area is not None
                and bool(areas_compatibles)
                and area not in areas_compatibles
            )

            clave_autor = limpiar_texto(
                valor_columna(
                    hoja,
                    numero_fila,
                    columnas,
                    'clave_autor',
                )
            ).upper()

            clave_titulo = limpiar_texto(
                valor_columna(
                    hoja,
                    numero_fila,
                    columnas,
                    'clave_titulo',
                )
            ).lower()

            editorial = limpiar_texto(
                valor_columna(
                    hoja,
                    numero_fila,
                    columnas,
                    'editorial',
                )
            )

            edicion = limpiar_texto(
                valor_columna(
                    hoja,
                    numero_fila,
                    columnas,
                    'edicion',
                )
            )

            anio_original = valor_columna(
                hoja,
                numero_fila,
                columnas,
                'anio_publicacion',
            )

            anio_publicacion = convertir_entero(
                anio_original
            )

            isbn = limpiar_isbn(
                valor_columna(
                    hoja,
                    numero_fila,
                    columnas,
                    'isbn',
                )
            )

            codigo_anterior = limpiar_texto(
                valor_columna(
                    hoja,
                    numero_fila,
                    columnas,
                    'codigo_anterior',
                )
            )

            estanteria = validar_estanteria(
                valor_columna(
                    hoja,
                    numero_fila,
                    columnas,
                    'estanteria',
                )
            )

            balda = validar_balda(
                valor_columna(
                    hoja,
                    numero_fila,
                    columnas,
                    'balda',
                )
            )

            proveedor = limpiar_texto(
                valor_columna(
                    hoja,
                    numero_fila,
                    columnas,
                    'proveedor',
                )
            )

            adquisicion = normalizar_adquisicion(
                valor_columna(
                    hoja,
                    numero_fila,
                    columnas,
                    'forma_adquisicion',
                )
            )

            fecha_original = valor_columna(
                hoja,
                numero_fila,
                columnas,
                'fecha_adquisicion',
            )

            fecha_adquisicion = convertir_fecha(
                fecha_original
            )

            condicion = normalizar_condicion(
                valor_columna(
                    hoja,
                    numero_fila,
                    columnas,
                    'condicion',
                )
            )

            estado = normalizar_estado(
                valor_columna(
                    hoja,
                    numero_fila,
                    columnas,
                    'estado',
                )
            )

            observaciones = limpiar_texto(
                valor_columna(
                    hoja,
                    numero_fila,
                    columnas,
                    'observaciones',
                )
            )

            verificado = convertir_verificado(
                valor_columna(
                    hoja,
                    numero_fila,
                    columnas,
                    'verificado',
                )
            )

            fecha_verificacion_original = (
                valor_columna(
                    hoja,
                    numero_fila,
                    columnas,
                    'fecha_verificacion',
                )
            )

            fecha_verificacion = convertir_fecha(
                fecha_verificacion_original
            )

            errores_fila = []

            if numero_inventario is None:
                sin_codigo += 1
                errores_fila.append(
                    'número de inventario incorrecto'
                )

            if not titulo:
                errores_fila.append(
                    'falta el título'
                )

            if area is None:
                errores_fila.append(
                    'área incorrecta'
                )

            if area_incompatible:
                nombres_areas = dict(
                    Libro.Area.choices
                )

                sugerencias = ', '.join(
                    nombres_areas[valor]
                    for valor in sorted(
                        areas_compatibles
                    )
                )

                errores_fila.append(
                    (
                        'el área no coincide con la '
                        'clasificación; use '
                        f'{sugerencias}'
                    )
                )

            if not clasificacion:
                errores_fila.append(
                    'falta la clasificación'
                )

            if numero_inventario is not None:
                if numero_inventario in (
                    codigos_utilizados
                ):
                    codigos_repetidos += 1
                    errores_fila.append(
                        (
                            'número de inventario '
                            'repetido'
                        )
                    )
                else:
                    codigos_utilizados.add(
                        numero_inventario
                    )

            if estanteria is None:
                errores_fila.append(
                    'estantería incorrecta'
                )

            if balda is None:
                errores_fila.append(
                    'balda incorrecta'
                )

            if not estanteria or not balda:
                sin_ubicacion += 1

            if condicion is None:
                errores_fila.append(
                    'condición incorrecta'
                )

            if estado is None:
                errores_fila.append(
                    'estado incorrecto'
                )

            if adquisicion is None:
                errores_fila.append(
                    (
                        'forma de adquisición '
                        'incorrecta'
                    )
                )

            if (
                anio_original not in (None, '')
                and (
                    anio_publicacion is None
                    or anio_publicacion < 1000
                    or anio_publicacion > 2100
                )
            ):
                errores_fila.append(
                    (
                        'año de publicación '
                        'incorrecto'
                    )
                )

            if (
                fecha_original not in (None, '')
                and fecha_adquisicion is None
            ):
                errores_fila.append(
                    (
                        'fecha de adquisición '
                        'incorrecta'
                    )
                )

            if not verificado:
                pendientes_verificacion += 1
                errores_fila.append(
                    'ejemplar no verificado'
                )

            if (
                fecha_verificacion_original
                not in (None, '')
                and fecha_verificacion is None
            ):
                errores_fila.append(
                    (
                        'fecha de verificación '
                        'incorrecta'
                    )
                )

            if errores_fila:
                errores.append(
                    (
                        f'Fila {numero_fila}: '
                        + ', '.join(errores_fila)
                        + '.'
                    )
                )
                continue

            registros.append(
                {
                    'fila': numero_fila,
                    'numero_inventario': (
                        numero_inventario
                    ),
                    'codigo_anterior': (
                        codigo_anterior
                    ),
                    'titulo': titulo,
                    'autor': autor,
                    'area': area,
                    'clasificacion': (
                        clasificacion
                    ),
                    'clave_autor': clave_autor,
                    'clave_titulo': clave_titulo,
                    'editorial': editorial,
                    'edicion': edicion,
                    'anio_publicacion': (
                        anio_publicacion
                    ),
                    'isbn': isbn,
                    'estanteria': estanteria,
                    'balda': balda,
                    'proveedor': proveedor,
                    'forma_adquisicion': (
                        adquisicion
                    ),
                    'fecha_adquisicion': (
                        fecha_adquisicion
                    ),
                    'condicion': condicion,
                    'estado': estado,
                    'observaciones': observaciones,
                    'fecha_verificacion': (
                        fecha_verificacion
                    ),
                }
            )

        estadisticas = {
            'codigos_repetidos': (
                codigos_repetidos
            ),
            'sin_codigo': sin_codigo,
            'sin_ubicacion': sin_ubicacion,
            'pendientes_verificacion': (
                pendientes_verificacion
            ),
        }

        return registros, errores, estadisticas

    finally:
        libro_excel.close()


def clave_libro(registro):
    if registro['isbn']:
        return (
            'isbn',
            registro['isbn'].lower(),
        )

    return (
        normalizar_texto(
            registro['titulo']
        ),
        normalizar_texto(
            registro['autor']
        ),
        normalizar_texto(
            registro['edicion']
        ),
    )


def analizar_archivo(ruta_archivo):
    registros, errores, estadisticas = (
        extraer_registros(ruta_archivo)
    )

    titulos = {
        clave_libro(registro)
        for registro in registros
    }

    inventarios_planilla = {
        registro['numero_inventario']
        for registro in registros
    }

    no_incluidos = (
        Ejemplar.objects.exclude(
            numero_inventario__isnull=True,
        )
        .exclude(
            numero_inventario__in=(
                inventarios_planilla
            ),
        )
        .count()
    )

    return {
        'registros': len(registros),
        'titulos_estimados': len(titulos),
        'ejemplares_estimados': len(registros),
        'codigos_repetidos': estadisticas[
            'codigos_repetidos'
        ],
        'sin_codigo': estadisticas[
            'sin_codigo'
        ],
        'sin_ubicacion': estadisticas[
            'sin_ubicacion'
        ],
        'pendientes_verificacion': (
            estadisticas[
                'pendientes_verificacion'
            ]
        ),
        'registros_no_incluidos': no_incluidos,
        'errores': errores,
        'cantidad_errores': len(errores),
        'hojas_omitidas': [],
    }


def buscar_libro_existente(registro):
    if registro['isbn']:
        libro = Libro.objects.filter(
            isbn__iexact=registro['isbn'],
        ).first()

        if libro is not None:
            return libro

    return Libro.objects.filter(
        titulo__iexact=registro['titulo'],
        autor__iexact=registro['autor'],
        edicion__iexact=registro['edicion'],
    ).first()


def actualizar_datos_libro(
    libro,
    registro,
):
    libro.titulo = registro['titulo']
    libro.autor = registro['autor']
    libro.editorial = registro['editorial']
    libro.area = registro['area']

    libro.clasificacion = (
        registro['clasificacion']
    )

    libro.clave_autor = (
        registro['clave_autor']
    )

    libro.clave_titulo = (
        registro['clave_titulo']
    )

    libro.isbn = registro['isbn']
    libro.edicion = registro['edicion']

    libro.anio_publicacion = (
        registro['anio_publicacion']
    )

    libro.activo = True
    libro.save()


@transaction.atomic
def importar_archivo(
    ruta_archivo,
    nombre_archivo,
    huella_archivo,
):
    if ImportacionLibros.objects.filter(
        huella_archivo=huella_archivo,
    ).exists():
        raise ValueError(
            'Este archivo ya fue importado anteriormente.'
        )

    registros, errores, estadisticas = (
        extraer_registros(ruta_archivo)
    )

    if errores:
        primeros_errores = ' '.join(
            errores[:5]
        )

        raise ValueError(
            (
                'No se puede importar porque existen '
                f'{len(errores)} fila(s) para corregir. '
                f'{primeros_errores}'
            )
        )

    if not registros:
        raise ValueError(
            'No se encontraron ejemplares listos para importar.'
        )

    inventarios_planilla = {
        registro['numero_inventario']
        for registro in registros
    }

    registros_no_incluidos = (
        Ejemplar.objects.exclude(
            numero_inventario__isnull=True,
        )
        .exclude(
            numero_inventario__in=(
                inventarios_planilla
            ),
        )
        .count()
    )

    titulos_creados = 0
    titulos_actualizados = 0
    ejemplares_creados = 0
    ejemplares_actualizados = 0
    sin_ubicacion = 0

    libros_procesados = {}
    libros_actualizados = set()

    for registro in registros:
        clave = clave_libro(registro)

        libro = libros_procesados.get(clave)

        if libro is None:
            libro = buscar_libro_existente(
                registro
            )

            if libro is None:
                libro = Libro()
                creado = True
            else:
                creado = False

            actualizar_datos_libro(
                libro,
                registro,
            )

            libros_procesados[clave] = libro

            if creado:
                titulos_creados += 1

            elif libro.id not in libros_actualizados:
                titulos_actualizados += 1
                libros_actualizados.add(
                    libro.id
                )

        ejemplar = Ejemplar.objects.filter(
            numero_inventario=registro[
                'numero_inventario'
            ],
        ).first()

        if ejemplar is None:
            ejemplar = Ejemplar(
                numero_inventario=registro[
                    'numero_inventario'
                ],
            )

            creado = True
        else:
            creado = False

        ejemplar.libro = libro

        ejemplar.codigo_anterior = registro[
            'codigo_anterior'
        ]

        ejemplar.estanteria = registro[
            'estanteria'
        ]

        ejemplar.balda = registro['balda']

        ejemplar.proveedor = registro[
            'proveedor'
        ]

        ejemplar.estado = registro['estado']

        ejemplar.condicion = registro[
            'condicion'
        ]

        ejemplar.forma_adquisicion = registro[
            'forma_adquisicion'
        ]

        ejemplar.fecha_adquisicion = registro[
            'fecha_adquisicion'
        ]

        ejemplar.observaciones = registro[
            'observaciones'
        ]

        # La nueva clasificación y ubicación requieren
        # imprimir nuevamente la etiqueta.
        ejemplar.etiqueta_impresa = False
        ejemplar.fecha_impresion_etiqueta = None

        ejemplar.save()

        if creado:
            ejemplares_creados += 1
        else:
            ejemplares_actualizados += 1

        if (
            not ejemplar.estanteria
            or not ejemplar.balda
        ):
            sin_ubicacion += 1

    importacion = ImportacionLibros.objects.create(
        nombre_archivo=nombre_archivo,
        huella_archivo=huella_archivo,
        titulos_creados=titulos_creados,
        ejemplares_creados=ejemplares_creados,
        codigos_reasignados=0,
        registros_sin_ubicacion=sin_ubicacion,
    )

    return {
        'importacion': importacion,
        'titulos_creados': titulos_creados,
        'titulos_actualizados': (
            titulos_actualizados
        ),
        'ejemplares_creados': ejemplares_creados,
        'ejemplares_actualizados': (
            ejemplares_actualizados
        ),
        'codigos_reasignados': 0,
        'sin_ubicacion': sin_ubicacion,
        'registros_no_incluidos': (
            registros_no_incluidos
        ),
        'errores': [],
        'hojas_omitidas': [],
    }