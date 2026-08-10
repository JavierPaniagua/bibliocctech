import hashlib
from pathlib import Path
from tempfile import gettempdir

from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .forms import (
    EjemplarForm,
    ImportarLibrosForm,
    LibroCrearForm,
    LibroEditarForm,
)
from .importador_historico import (
    analizar_archivo,
    importar_archivo,
)
from .models import Ejemplar, Libro


def libro_lista(request):
    busqueda = request.GET.get(
        'buscar',
        '',
    ).strip()

    libros = Libro.objects.prefetch_related(
        'ejemplares',
    ).all()

    if busqueda:
        libros = libros.filter(
            Q(titulo__icontains=busqueda)
            | Q(autor__icontains=busqueda)
            | Q(editorial__icontains=busqueda)
            | Q(area__icontains=busqueda)
            | Q(clasificacion__icontains=busqueda)
            | Q(
                signatura_topografica__icontains=(
                    busqueda
                )
            )
            | Q(isbn__icontains=busqueda)
            | Q(
                ejemplares__numero_inventario__icontains=(
                    busqueda
                )
            )
            | Q(
                ejemplares__codigo_anterior__icontains=(
                    busqueda
                )
            )
            | Q(
                ejemplares__estanteria__icontains=(
                    busqueda
                )
            )
            | Q(
                ejemplares__balda__icontains=(
                    busqueda
                )
            )
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
        formulario = LibroCrearForm(
            request.POST
        )

        if formulario.is_valid():
            libro = formulario.save()

            cantidad = formulario.cleaned_data[
                'cantidad_ejemplares'
            ]

            condicion = formulario.cleaned_data[
                'condicion_inicial'
            ]

            forma_adquisicion = (
                formulario.cleaned_data[
                    'forma_adquisicion'
                ]
            )

            fecha_adquisicion = (
                formulario.cleaned_data[
                    'fecha_adquisicion'
                ]
            )

            estanteria = formulario.cleaned_data[
                'estanteria'
            ]

            balda = formulario.cleaned_data[
                'balda'
            ]

            proveedor = formulario.cleaned_data[
                'proveedor'
            ]

            observaciones = (
                formulario.cleaned_data[
                    'observaciones'
                ]
            )

            numeros_generados = []

            for _ in range(cantidad):
                ejemplar = Ejemplar.objects.create(
                    libro=libro,
                    estanteria=estanteria,
                    balda=balda,
                    proveedor=proveedor,
                    condicion=condicion,
                    forma_adquisicion=(
                        forma_adquisicion
                    ),
                    fecha_adquisicion=(
                        fecha_adquisicion
                    ),
                    observaciones=observaciones,
                )

                numeros_generados.append(
                    ejemplar.numero_inventario
                )

            if len(numeros_generados) == 1:
                detalle_inventario = (
                    'Número de inventario: '
                    f'{numeros_generados[0]}.'
                )
            else:
                detalle_inventario = (
                    'Inventarios generados: '
                    f'{numeros_generados[0]} al '
                    f'{numeros_generados[-1]}.'
                )

            messages.success(
                request,
                (
                    f'El libro {libro.titulo} fue '
                    f'registrado con {cantidad} '
                    f'ejemplar(es). '
                    f'{detalle_inventario}'
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
        Libro.objects.prefetch_related(
            'ejemplares'
        ),
        id=libro_id,
    )

    contexto = {
        'libro': libro,
        'ejemplares': (
            libro.ejemplares.all()
        ),
    }

    return render(
        request,
        'libros/libro_detalle.html',
        contexto,
    )


@transaction.atomic
def libro_editar(request, libro_id):
    libro = get_object_or_404(
        Libro,
        id=libro_id,
    )

    if request.method == 'POST':
        signatura_anterior = (
            libro.signatura_topografica
        )

        formulario = LibroEditarForm(
            request.POST,
            instance=libro,
        )

        if formulario.is_valid():
            libro = formulario.save()

            if (
                signatura_anterior
                != libro.signatura_topografica
            ):
                libro.ejemplares.update(
                    etiqueta_impresa=False,
                    fecha_impresion_etiqueta=None,
                )

            messages.success(
                request,
                (
                    'Los datos del libro fueron '
                    'actualizados.'
                ),
            )

            return redirect(
                'libros:detalle',
                libro_id=libro.id,
            )
    else:
        formulario = LibroEditarForm(
            instance=libro
        )

    contexto = {
        'formulario': formulario,
        'libro': libro,
    }

    return render(
        request,
        'libros/libro_editar.html',
        contexto,
    )


@transaction.atomic
def ejemplar_crear(request, libro_id):
    libro = get_object_or_404(
        Libro,
        id=libro_id,
    )

    if request.method == 'POST':
        formulario = EjemplarForm(
            request.POST
        )

        if formulario.is_valid():
            ejemplar = formulario.save(
                commit=False
            )

            ejemplar.libro = libro
            ejemplar.save()

            messages.success(
                request,
                (
                    'El ejemplar fue registrado '
                    'con el número de inventario '
                    f'{ejemplar.numero_inventario}.'
                ),
            )

            return redirect(
                'libros:detalle',
                libro_id=libro.id,
            )
    else:
        formulario = EjemplarForm()

    contexto = {
        'formulario': formulario,
        'libro': libro,
        'titulo_pagina': (
            'Agregar ejemplar'
        ),
    }

    return render(
        request,
        'libros/ejemplar_formulario.html',
        contexto,
    )


@transaction.atomic
def ejemplar_editar(
    request,
    ejemplar_id,
):
    ejemplar = get_object_or_404(
        Ejemplar.objects.select_related(
            'libro'
        ),
        id=ejemplar_id,
    )

    if request.method == 'POST':
        numero_anterior = (
            ejemplar.numero_inventario
        )

        estanteria_anterior = (
            ejemplar.estanteria
        )

        balda_anterior = ejemplar.balda

        formulario = EjemplarForm(
            request.POST,
            instance=ejemplar,
        )

        if formulario.is_valid():
            ejemplar = formulario.save(
                commit=False
            )

            cambio_etiqueta = (
                numero_anterior
                != ejemplar.numero_inventario
                or estanteria_anterior
                != ejemplar.estanteria
                or balda_anterior
                != ejemplar.balda
            )

            if cambio_etiqueta:
                ejemplar.etiqueta_impresa = False
                ejemplar.fecha_impresion_etiqueta = None

            ejemplar.save()

            messages.success(
                request,
                (
                    'Los datos del ejemplar fueron '
                    'actualizados.'
                ),
            )

            return redirect(
                'libros:detalle',
                libro_id=ejemplar.libro_id,
            )
    else:
        formulario = EjemplarForm(
            instance=ejemplar
        )

    contexto = {
        'formulario': formulario,
        'ejemplar': ejemplar,
        'libro': ejemplar.libro,
        'titulo_pagina': (
            'Editar ejemplar'
        ),
    }

    return render(
        request,
        'libros/ejemplar_formulario.html',
        contexto,
    )


def guardar_archivo_temporal(archivo):
    carpeta_temporal = (
        Path(gettempdir())
        / 'bibliocctech_importaciones'
    )

    carpeta_temporal.mkdir(
        parents=True,
        exist_ok=True,
    )

    huella = hashlib.sha256()

    nombre_seguro = Path(
        archivo.name
    ).name

    ruta_temporal = (
        carpeta_temporal
        / f'importacion_{nombre_seguro}'
    )

    contador = 1

    while ruta_temporal.exists():
        ruta_temporal = (
            carpeta_temporal
            / (
                f'importacion_{contador}_'
                f'{nombre_seguro}'
            )
        )

        contador += 1

    with open(
        ruta_temporal,
        'wb',
    ) as destino:
        for bloque in archivo.chunks():
            destino.write(bloque)
            huella.update(bloque)

    return (
        str(ruta_temporal),
        huella.hexdigest(),
    )


def eliminar_archivo_temporal(ruta):
    if not ruta:
        return

    try:
        archivo = Path(ruta)

        if archivo.exists():
            archivo.unlink()

    except OSError:
        pass


def limpiar_importacion_temporal(
    request,
):
    ruta = request.session.pop(
        'importacion_libros_ruta',
        None,
    )

    request.session.pop(
        'importacion_libros_nombre',
        None,
    )

    request.session.pop(
        'importacion_libros_huella',
        None,
    )

    eliminar_archivo_temporal(ruta)


def libro_importar(request):
    vista_previa = None
    resultados = None

    if request.method == 'POST':
        accion = request.POST.get(
            'accion',
            'analizar',
        )

        if accion == 'analizar':
            limpiar_importacion_temporal(
                request
            )

            formulario = ImportarLibrosForm(
                request.POST,
                request.FILES,
            )

            if formulario.is_valid():
                archivo = (
                    formulario.cleaned_data[
                        'archivo'
                    ]
                )

                ruta_temporal = None

                try:
                    (
                        ruta_temporal,
                        huella_archivo,
                    ) = guardar_archivo_temporal(
                        archivo
                    )

                    vista_previa = (
                        analizar_archivo(
                            ruta_temporal
                        )
                    )

                    if (
                        vista_previa['registros']
                        == 0
                    ):
                        eliminar_archivo_temporal(
                            ruta_temporal
                        )

                        formulario.add_error(
                            'archivo',
                            (
                                'No se encontraron '
                                'ejemplares listos '
                                'para importar.'
                            ),
                        )

                    else:
                        request.session[
                            'importacion_libros_ruta'
                        ] = ruta_temporal

                        request.session[
                            'importacion_libros_nombre'
                        ] = archivo.name

                        request.session[
                            'importacion_libros_huella'
                        ] = huella_archivo

                except Exception as error:
                    eliminar_archivo_temporal(
                        ruta_temporal
                    )

                    formulario.add_error(
                        'archivo',
                        (
                            'No se pudo analizar '
                            'el archivo. '
                            f'Detalle: {error}'
                        ),
                    )

        elif accion == 'confirmar':
            formulario = (
                ImportarLibrosForm()
            )

            ruta_temporal = (
                request.session.get(
                    'importacion_libros_ruta'
                )
            )

            nombre_archivo = (
                request.session.get(
                    'importacion_libros_nombre'
                )
            )

            huella_archivo = (
                request.session.get(
                    'importacion_libros_huella'
                )
            )

            if (
                not ruta_temporal
                or not Path(
                    ruta_temporal
                ).exists()
                or not nombre_archivo
                or not huella_archivo
            ):
                messages.error(
                    request,
                    (
                        'La vista previa venció. '
                        'Seleccione nuevamente '
                        'el archivo Excel.'
                    ),
                )

                limpiar_importacion_temporal(
                    request
                )

            else:
                try:
                    resultados = importar_archivo(
                        ruta_archivo=(
                            ruta_temporal
                        ),
                        nombre_archivo=(
                            nombre_archivo
                        ),
                        huella_archivo=(
                            huella_archivo
                        ),
                    )

                    messages.success(
                        request,
                        (
                            'El inventario maestro '
                            'se importó correctamente.'
                        ),
                    )

                    limpiar_importacion_temporal(
                        request
                    )

                except ValueError as error:
                    messages.error(
                        request,
                        str(error),
                    )

                    limpiar_importacion_temporal(
                        request
                    )

                except Exception as error:
                    messages.error(
                        request,
                        (
                            'No se pudo completar '
                            'la importación. '
                            f'Detalle: {error}'
                        ),
                    )

                    limpiar_importacion_temporal(
                        request
                    )

        elif accion == 'cancelar':
            formulario = (
                ImportarLibrosForm()
            )

            limpiar_importacion_temporal(
                request
            )

            messages.info(
                request,
                'La importación fue cancelada.',
            )

        else:
            formulario = (
                ImportarLibrosForm()
            )

    else:
        formulario = ImportarLibrosForm()

        limpiar_importacion_temporal(
            request
        )

    contexto = {
        'formulario': formulario,
        'vista_previa': vista_previa,
        'resultados': resultados,
    }

    return render(
        request,
        'libros/libro_importar.html',
        contexto,
    )