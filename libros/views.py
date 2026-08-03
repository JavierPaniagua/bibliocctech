from datetime import date, datetime

from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date
from openpyxl import load_workbook

from .forms import (
    ImportarLibrosForm,
    LibroCrearForm,
    LibroEditarForm,
)
from .models import Ejemplar, Libro

def libro_lista(request):
    busqueda = request.GET.get('buscar', '').strip()

    libros = Libro.objects.prefetch_related(
        'ejemplares',
    ).all()

    if busqueda:
        libros = libros.filter(
            Q(titulo__icontains=busqueda)
            | Q(autor__icontains=busqueda)
            | Q(editorial__icontains=busqueda)
            | Q(categoria__icontains=busqueda)
            | Q(isbn__icontains=busqueda)
            | Q(ejemplares__codigo__icontains=busqueda)
        ).distinct()

    contexto = {
        'libros': libros,
        'busqueda': busqueda,
    }

    return render(
        request,
        'libros/libro_lista.html',
        contexto,
    )


@transaction.atomic
def libro_crear(request):
    if request.method == 'POST':
        formulario = LibroCrearForm(request.POST)

        if formulario.is_valid():
            libro = formulario.save()

            cantidad = formulario.cleaned_data[
                'cantidad_ejemplares'
            ]

            condicion = formulario.cleaned_data[
                'condicion_inicial'
            ]

            forma_adquisicion = formulario.cleaned_data[
                'forma_adquisicion'
            ]

            fecha_adquisicion = formulario.cleaned_data[
                'fecha_adquisicion'
            ]

            for _ in range(cantidad):
                Ejemplar.objects.create(
                    libro=libro,
                    condicion=condicion,
                    forma_adquisicion=forma_adquisicion,
                    fecha_adquisicion=fecha_adquisicion,
                )

            messages.success(
                request,
                (
                    f'El libro {libro.titulo} fue registrado '
                    f'con {cantidad} ejemplar(es).'
                ),
            )

            return redirect(
                'libros:detalle',
                libro_id=libro.id,
            )
    else:
        formulario = LibroCrearForm()

    contexto = {
        'formulario': formulario,
    }

    return render(
        request,
        'libros/libro_formulario.html',
        contexto,
    )


def libro_detalle(request, libro_id):
    libro = get_object_or_404(
        Libro.objects.prefetch_related('ejemplares'),
        id=libro_id,
    )

    contexto = {
        'libro': libro,
        'ejemplares': libro.ejemplares.all(),
    }

    return render(
        request,
        'libros/libro_detalle.html',
        contexto,
    )


def libro_editar(request, libro_id):
    libro = get_object_or_404(
        Libro,
        id=libro_id,
    )

    if request.method == 'POST':
        formulario = LibroEditarForm(
            request.POST,
            instance=libro,
        )

        if formulario.is_valid():
            formulario.save()

            messages.success(
                request,
                'Los datos del libro fueron actualizados.',
            )

            return redirect(
                'libros:detalle',
                libro_id=libro.id,
            )
    else:
        formulario = LibroEditarForm(instance=libro)

    contexto = {
        'formulario': formulario,
        'libro': libro,
    }

    return render(
        request,
        'libros/libro_editar.html',
        contexto,
    )

def limpiar_texto(valor):
    if valor is None:
        return ''

    return str(valor).strip()


def limpiar_isbn(valor):
    if valor is None:
        return ''

    if isinstance(valor, float) and valor.is_integer():
        valor = int(valor)

    isbn = str(valor).strip()

    return (
        isbn
        .replace(' ', '')
        .replace('-', '')
    )


def convertir_entero(valor):
    if valor is None or valor == '':
        return None

    if isinstance(valor, float):
        if not valor.is_integer():
            return None

        return int(valor)

    try:
        return int(str(valor).strip())
    except (TypeError, ValueError):
        return None


def convertir_fecha(valor):
    if valor in (None, ''):
        return None

    if isinstance(valor, datetime):
        return valor.date()

    if isinstance(valor, date):
        return valor

    texto = str(valor).strip()

    fecha = parse_date(texto)

    if fecha:
        return fecha

    formatos = [
        '%d/%m/%Y',
        '%d-%m-%Y',
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


def convertir_activo(valor):
    texto = limpiar_texto(valor).upper()

    return texto in {
        'SI',
        'SÍ',
        'TRUE',
        'VERDADERO',
        '1',
        'ACTIVO',
    }


def normalizar_adquisicion(valor):
    texto = limpiar_texto(valor).upper()

    equivalencias = {
        'COMPRA': Ejemplar.FormaAdquisicion.COMPRA,
        'DONACION': Ejemplar.FormaAdquisicion.DONACION,
        'DONACIÓN': Ejemplar.FormaAdquisicion.DONACION,
        'TRANSFERENCIA': (
            Ejemplar.FormaAdquisicion.TRANSFERENCIA
        ),
        'OTRO': Ejemplar.FormaAdquisicion.OTRO,
        'NO ESPECIFICADA': (
            Ejemplar.FormaAdquisicion.NO_ESPECIFICADA
        ),
        'NO_ESPECIFICADA': (
            Ejemplar.FormaAdquisicion.NO_ESPECIFICADA
        ),
    }

    return equivalencias.get(texto)


def libro_importar(request):
    resultados = None

    if request.method == 'POST':
        formulario = ImportarLibrosForm(
            request.POST,
            request.FILES,
        )

        if formulario.is_valid():
            archivo = formulario.cleaned_data['archivo']

            try:
                libro_excel = load_workbook(
                    archivo,
                    read_only=True,
                    data_only=True,
                )

                if 'Libros' not in libro_excel.sheetnames:
                    formulario.add_error(
                        'archivo',
                        (
                            'El archivo debe contener una hoja '
                            'llamada Libros.'
                        ),
                    )
                else:
                    hoja = libro_excel['Libros']

                    encabezados_esperados = [
                        'titulo',
                        'autor',
                        'editorial',
                        'categoria',
                        'isbn',
                        'edicion',
                        'anio_publicacion',
                        'ubicacion',
                        'cantidad',
                        'condicion',
                        'forma_adquisicion',
                        'fecha_adquisicion',
                        'activo',
                        'descripcion',
                    ]

                    encabezados_archivo = [
                        limpiar_texto(
                            hoja.cell(
                                row=4,
                                column=columna,
                            ).value
                        ).lower()
                        for columna in range(1, 15)
                    ]

                    if encabezados_archivo != encabezados_esperados:
                        formulario.add_error(
                            'archivo',
                            (
                                'Las columnas fueron modificadas. '
                                'Utilice la plantilla oficial.'
                            ),
                        )
                    else:
                        resultados = procesar_libros_excel(hoja)

            except Exception:
                formulario.add_error(
                    'archivo',
                    (
                        'No se pudo leer la planilla. Compruebe '
                        'que sea un archivo Excel válido.'
                    ),
                )
    else:
        formulario = ImportarLibrosForm()

    contexto = {
        'formulario': formulario,
        'resultados': resultados,
    }

    return render(
        request,
        'libros/libro_importar.html',
        contexto,
    )


def procesar_libros_excel(hoja):
    condiciones_validas = {
        opcion[0]
        for opcion in Ejemplar.Condicion.choices
    }

    importados = 0
    ejemplares_creados = 0
    duplicados = 0
    errores = []
    registros_planilla = set()

    for numero_fila, fila in enumerate(
        hoja.iter_rows(
            min_row=5,
            max_col=14,
            values_only=True,
        ),
        start=5,
    ):
        if all(valor is None for valor in fila):
            continue

        (
            titulo,
            autor,
            editorial,
            categoria,
            isbn,
            edicion,
            anio_publicacion,
            ubicacion,
            cantidad,
            condicion,
            forma_adquisicion,
            fecha_adquisicion,
            activo,
            descripcion,
        ) = fila

        titulo = limpiar_texto(titulo)
        autor = limpiar_texto(autor)
        editorial = limpiar_texto(editorial)
        categoria = limpiar_texto(categoria)
        isbn = limpiar_isbn(isbn)
        edicion = limpiar_texto(edicion)
        ubicacion = limpiar_texto(ubicacion)
        descripcion = limpiar_texto(descripcion)

        anio_publicacion = convertir_entero(
            anio_publicacion
        )

        cantidad = convertir_entero(cantidad)

        condicion = limpiar_texto(
            condicion
        ).upper()

        adquisicion = normalizar_adquisicion(
            forma_adquisicion
        )

        fecha_original = fecha_adquisicion

        fecha_adquisicion = convertir_fecha(
            fecha_adquisicion
        )

        if not titulo or not categoria:
            errores.append(
                f'Fila {numero_fila}: faltan el título '
                f'o la categoría.'
            )
            continue

        if cantidad is None or cantidad < 1 or cantidad > 500:
            errores.append(
                f'Fila {numero_fila}: la cantidad debe ser '
                f'un número entre 1 y 500.'
            )
            continue

        if (
            anio_publicacion is not None
            and (
                anio_publicacion < 1000
                or anio_publicacion > 2100
            )
        ):
            errores.append(
                f'Fila {numero_fila}: año de publicación '
                f'incorrecto.'
            )
            continue

        if condicion not in condiciones_validas:
            errores.append(
                f'Fila {numero_fila}: condición incorrecta.'
            )
            continue

        if adquisicion is None:
            errores.append(
                f'Fila {numero_fila}: forma de adquisición '
                f'incorrecta.'
            )
            continue

        if (
            fecha_original not in (None, '')
            and fecha_adquisicion is None
        ):
            errores.append(
                f'Fila {numero_fila}: fecha de adquisición '
                f'incorrecta.'
            )
            continue

        if isbn:
            clave_planilla = (
                'ISBN',
                isbn.lower(),
            )
        else:
            clave_planilla = (
                titulo.lower(),
                autor.lower(),
                edicion.lower(),
            )

        if clave_planilla in registros_planilla:
            duplicados += 1

            errores.append(
                f'Fila {numero_fila}: el libro está repetido '
                f'en la planilla.'
            )

            continue

        registros_planilla.add(clave_planilla)

        if isbn:
            libro_existente = Libro.objects.filter(
                isbn__iexact=isbn,
            ).exists()
        else:
            libro_existente = Libro.objects.filter(
                titulo__iexact=titulo,
                autor__iexact=autor,
                edicion__iexact=edicion,
            ).exists()

        if libro_existente:
            duplicados += 1

            errores.append(
                f'Fila {numero_fila}: {titulo} ya está '
                f'registrado.'
            )

            continue

        try:
            with transaction.atomic():
                libro = Libro.objects.create(
                    titulo=titulo,
                    autor=autor,
                    editorial=editorial,
                    categoria=categoria,
                    isbn=isbn,
                    edicion=edicion,
                    anio_publicacion=anio_publicacion,
                    ubicacion=ubicacion,
                    descripcion=descripcion,
                    activo=convertir_activo(activo),
                )

                for _ in range(cantidad):
                    Ejemplar.objects.create(
                        libro=libro,
                        condicion=condicion,
                        forma_adquisicion=adquisicion,
                        fecha_adquisicion=fecha_adquisicion,
                    )

            importados += 1
            ejemplares_creados += cantidad

        except Exception:
            errores.append(
                f'Fila {numero_fila}: no se pudo registrar '
                f'el libro {titulo}.'
            )

    return {
        'importados': importados,
        'ejemplares_creados': ejemplares_creados,
        'duplicados': duplicados,
        'errores': errores,
        'cantidad_errores': len(errores),
    }