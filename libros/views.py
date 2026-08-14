import hashlib
from pathlib import Path
from tempfile import gettempdir
from django.utils import timezone

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
        siguiente_numero = (
            Ejemplar.siguiente_numero_disponible()
        )

        formulario = EjemplarForm(
            initial={
                'numero_inventario': siguiente_numero,
            }
        )

    contexto = {
        'formulario': formulario,
        'libro': libro,
        'titulo_pagina': 'Agregar ejemplar',
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

def etiqueta_individual(request, numero_inventario):
    ejemplar = get_object_or_404(
        Ejemplar.objects.select_related("libro"),
        numero_inventario=numero_inventario,
    )

    datos_faltantes = []

    if not ejemplar.libro.signatura_topografica:
        datos_faltantes.append(
            "clasificación o signatura topográfica"
        )

    if not ejemplar.estanteria:
        datos_faltantes.append("estantería")

    if not ejemplar.balda:
        datos_faltantes.append("balda")

    if datos_faltantes:
        messages.warning(
            request,
            (
                "No se puede imprimir la etiqueta del ejemplar "
                f"{ejemplar.numero_inventario}. "
                "Complete: "
                + ", ".join(datos_faltantes)
                + "."
            ),
        )

        return redirect(
            "libros:detalle",
            libro_id=ejemplar.libro_id,
        )

    if request.method == "POST":
        ejemplar.etiqueta_impresa = True
        ejemplar.fecha_impresion_etiqueta = (
            timezone.now()
        )

        ejemplar.save(
            update_fields=[
                "etiqueta_impresa",
                "fecha_impresion_etiqueta",
            ]
        )

        messages.success(
            request,
            (
                "La etiqueta del ejemplar "
                f"{ejemplar.numero_inventario} "
                "fue marcada como impresa."
            ),
        )

        return redirect(
            "libros:detalle",
            libro_id=ejemplar.libro_id,
        )

    contexto = {
        "ejemplar": ejemplar,
        "libro": ejemplar.libro,
    }

    return render(
        request,
        "libros/etiqueta_individual.html",
        contexto,
    )

def etiquetas_mosaico(request):
    etiquetas = []
    etiquetas_omitidas = 0
    numero_desde = ""
    cantidad = 14
    solo_pendientes = True

    filtro_incompleto = (
        Q(libro__signatura_topografica="")
        | Q(estanteria="")
        | Q(balda="")
    )

    if request.method == "POST":
        accion = request.POST.get(
            "accion",
            "preparar",
        )

        try:
            numero_desde = int(
                request.POST.get(
                    "numero_desde",
                    1,
                )
            )
        except (TypeError, ValueError):
            numero_desde = 1

        try:
            cantidad = int(
                request.POST.get(
                    "cantidad",
                    14,
                )
            )
        except (TypeError, ValueError):
            cantidad = 14

        cantidad = max(
            1,
            min(cantidad, 280),
        )

        solo_pendientes = (
            request.POST.get(
                "solo_pendientes"
            )
            == "si"
        )

        ejemplares = (
            Ejemplar.objects
            .select_related("libro")
            .filter(
                numero_inventario__gte=numero_desde
            )
        )

        if solo_pendientes:
            ejemplares = ejemplares.filter(
                etiqueta_impresa=False
            )

        etiquetas_omitidas = ejemplares.filter(
            filtro_incompleto
        ).count()

        ejemplares_completos = ejemplares.exclude(
            filtro_incompleto
        )

        etiquetas = list(
            ejemplares_completos.order_by(
                "numero_inventario"
            )[:cantidad]
        )

        if accion == "marcar_impresas":
            numeros_seleccionados = (
                request.POST.getlist(
                    "ejemplares_seleccionados"
                )
            )

            cantidad_marcada = 0

            if numeros_seleccionados:
                cantidad_marcada = (
                    Ejemplar.objects
                    .filter(
                        numero_inventario__in=(
                            numeros_seleccionados
                        )
                    )
                    .exclude(
                        filtro_incompleto
                    )
                    .update(
                        etiqueta_impresa=True,
                        fecha_impresion_etiqueta=(
                            timezone.now()
                        ),
                    )
                )

            if cantidad_marcada:
                messages.success(
                    request,
                    (
                        f"{cantidad_marcada} etiquetas "
                        "fueron marcadas como impresas."
                    ),
                )
            else:
                messages.warning(
                    request,
                    (
                        "No se marcaron etiquetas. "
                        "Revise que los ejemplares tengan "
                        "signatura, estantería y balda."
                    ),
                )

            return redirect(
                "libros:etiquetas_mosaico"
            )

    primer_ejemplar = (
        Ejemplar.objects
        .order_by("numero_inventario")
        .first()
    )

    primer_pendiente = (
        Ejemplar.objects
        .filter(etiqueta_impresa=False)
        .exclude(filtro_incompleto)
        .order_by("numero_inventario")
        .first()
    )

    contexto = {
        "etiquetas": etiquetas,
        "etiquetas_omitidas": etiquetas_omitidas,
        "numero_desde": numero_desde,
        "cantidad": cantidad,
        "solo_pendientes": solo_pendientes,

        "primer_inventario": (
            primer_ejemplar.numero_inventario
            if primer_ejemplar
            else None
        ),

        "primer_pendiente": (
            primer_pendiente.numero_inventario
            if primer_pendiente
            else None
        ),
    }

    return render(
        request,
        "libros/etiquetas_mosaico.html",
        contexto,
    )
    
def reporte_inventario(request):
    ejemplares = (
        Ejemplar.objects
        .select_related("libro")
        .order_by(
            "libro__area",
            "libro__clasificacion",
            "numero_inventario",
        )
    )

    filtro_incompleto = (
        Q(libro__signatura_topografica="")
        | Q(estanteria="")
        | Q(balda="")
    )

    contexto = {
        "ejemplares": ejemplares,
        "fecha_actual": timezone.localdate(),

        "total_titulos": Libro.objects.filter(
            activo=True
        ).count(),

        "total_ejemplares": ejemplares.count(),

        "total_disponibles": ejemplares.filter(
            estado=Ejemplar.Estado.DISPONIBLE
        ).count(),

        "total_prestados": ejemplares.filter(
            estado=Ejemplar.Estado.PRESTADO
        ).count(),

        "total_incompletos": ejemplares.filter(
            filtro_incompleto
        ).count(),
    }

    return render(
        request,
        "libros/reporte_inventario.html",
        contexto,
    )
    
def etiqueta_lomo_individual(request, numero_inventario):
    ejemplar = get_object_or_404(
        Ejemplar.objects.select_related("libro"),
        numero_inventario=numero_inventario,
    )

    if not ejemplar.libro.signatura_topografica:
        messages.warning(
            request,
            (
                "No se puede imprimir la etiqueta de lomo "
                f"del ejemplar {ejemplar.numero_inventario}. "
                "Complete primero la clasificación y la "
                "signatura topográfica."
            ),
        )
        return redirect(
            "libros:detalle",
            libro_id=ejemplar.libro_id,
        )

    if request.method == "POST":
        ejemplar.etiqueta_lomo_impresa = True
        ejemplar.fecha_impresion_etiqueta_lomo = timezone.now()
        ejemplar.save(
            update_fields=[
                "etiqueta_lomo_impresa",
                "fecha_impresion_etiqueta_lomo",
            ]
        )

        messages.success(
            request,
            "La etiqueta de lomo fue marcada como impresa.",
        )
        return redirect(
            "libros:detalle",
            libro_id=ejemplar.libro_id,
        )

    return render(
        request,
        "libros/etiqueta_lomo_individual.html",
        {
            "ejemplar": ejemplar,
            "libro_id": ejemplar.libro_id,
        },
    )

def etiquetas_lomo_mosaico(request):
    """Prepara, imprime y confirma etiquetas de lomo en hoja oficio."""
    datos = request.POST if request.method == "POST" else request.GET

    numero_inicio_texto = datos.get("numero_inicio", "").strip()
    cantidad_texto = datos.get("cantidad", "48").strip()
    incluir_impresas = datos.get("incluir_impresas") == "si"
    accion = datos.get("accion", "")

    try:
        cantidad = int(cantidad_texto)
    except (TypeError, ValueError):
        cantidad = 48
    cantidad = max(1, min(cantidad, 48))

    numero_inicio = None
    if numero_inicio_texto:
        try:
            numero_inicio = int(numero_inicio_texto)
            if numero_inicio < 1:
                raise ValueError
        except (TypeError, ValueError):
            numero_inicio = None
            numero_inicio_texto = ""
            messages.warning(
                request,
                "El número de inventario inicial debe ser un número mayor que cero.",
            )

    # La confirmación afecta exclusivamente las casillas seleccionadas.
    if request.method == "POST" and accion == "confirmar":
        ids_seleccionados = request.POST.getlist("ejemplares_seleccionados")

        ejemplares_seleccionados = (
            Ejemplar.objects
            .filter(
                pk__in=ids_seleccionados,
                numero_inventario__isnull=False,
            )
            .exclude(libro__signatura_topografica="")
        )

        total_actualizados = ejemplares_seleccionados.update(
            etiqueta_lomo_impresa=True,
            fecha_impresion_etiqueta_lomo=timezone.now(),
        )

        if total_actualizados:
            messages.success(
                request,
                f"Se marcaron {total_actualizados} etiquetas de lomo como impresas.",
            )
        else:
            messages.warning(
                request,
                "No se seleccionaron etiquetas válidas para confirmar.",
            )

        return redirect("libros:etiquetas_lomo_mosaico")

    base = (
        Ejemplar.objects
        .select_related("libro")
        .filter(numero_inventario__isnull=False)
        .order_by("numero_inventario")
    )

    if numero_inicio is not None:
        base = base.filter(numero_inventario__gte=numero_inicio)

    if not incluir_impresas:
        base = base.filter(etiqueta_lomo_impresa=False)

    etiquetas_omitidas = base.filter(libro__signatura_topografica="").count()
    ejemplares = list(
        base.exclude(libro__signatura_topografica="")[:cantidad]
    )

    contexto = {
        "ejemplares": ejemplares,
        "numero_inicio": numero_inicio_texto,
        "cantidad": cantidad,
        "incluir_impresas": incluir_impresas,
        "total_etiquetas": len(ejemplares),
        "etiquetas_omitidas": etiquetas_omitidas,
    }

    return render(
        request,
        "libros/etiquetas_lomo_mosaico.html",
        contexto,
    )