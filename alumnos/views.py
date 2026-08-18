import re

from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.utils import timezone
from openpyxl import load_workbook

from .forms import (
    AlumnoForm,
    ImportarAlumnosForm,
)
from .models import (
    Alumno,
    PromocionAnual,
)


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def limpiar_texto(valor):
    if valor is None:
        return ''

    return ' '.join(
        str(valor).strip().split()
    )


def limpiar_cedula(valor):
    if valor is None:
        return ''

    if (
        isinstance(valor, float)
        and valor.is_integer()
    ):
        valor = int(valor)

    return (
        str(valor)
        .strip()
        .replace('.', '')
        .replace(' ', '')
        .replace('-', '')
    )


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


def obtener_numero_curso(curso):
    """
    Convierte valores como 1°, 1º, 1° CURSO o 1
    en el número correspondiente.
    """
    texto = limpiar_texto(curso)

    coincidencia = re.match(
        r'^([123])',
        texto,
    )

    if not coincidencia:
        return None

    return int(coincidencia.group(1))


# ============================================================
# LISTADO
# ============================================================

def alumno_lista(request):
    busqueda = request.GET.get(
        'buscar',
        '',
    ).strip()

    estado = request.GET.get(
        'estado',
        'activos',
    ).strip()

    anio = request.GET.get(
        'anio',
        '',
    ).strip()

    alumnos = Alumno.objects.all()

    if estado == 'activos':
        alumnos = alumnos.filter(
            activo=True
        )
    elif estado == 'inactivos':
        alumnos = alumnos.filter(
            activo=False
        )

    if anio.isdigit():
        alumnos = alumnos.filter(
            anio_lectivo=int(anio)
        )

    if busqueda:
        alumnos = alumnos.filter(
            Q(cedula__icontains=busqueda)
            | Q(
                nombre_completo__icontains=(
                    busqueda
                )
            )
            | Q(nombres__icontains=busqueda)
            | Q(apellidos__icontains=busqueda)
            | Q(curso__icontains=busqueda)
            | Q(seccion__icontains=busqueda)
            | Q(
                especialidad__icontains=(
                    busqueda
                )
            )
        )

    alumnos = alumnos.order_by(
        'curso',
        'seccion',
        'apellidos',
        'nombres',
    )

    paginador = Paginator(
        alumnos,
        25,
    )

    pagina = paginador.get_page(
        request.GET.get('pagina')
    )

    anios_disponibles = (
        Alumno.objects
        .values_list(
            'anio_lectivo',
            flat=True,
        )
        .distinct()
        .order_by(
            '-anio_lectivo'
        )
    )

    contexto = {
        # Se mantienen ambos nombres para que funcione
        # con las versiones anteriores de la plantilla.
        'alumnos': pagina,
        'pagina': pagina,
        'busqueda': busqueda,
        'estado': estado,
        'anio': anio,
        'anios_disponibles': (
            anios_disponibles
        ),
    }

    return render(
        request,
        'alumnos/alumno_lista.html',
        contexto,
    )


# ============================================================
# REGISTRO
# ============================================================

def alumno_crear(request):
    if request.method == 'POST':
        formulario = AlumnoForm(
            request.POST
        )

        if formulario.is_valid():
            alumno = formulario.save()

            messages.success(
                request,
                (
                    f'El alumno '
                    f'{alumno.nombre_visible} '
                    f'fue registrado correctamente.'
                ),
            )

            return redirect(
                'alumnos:lista'
            )
    else:
        formulario = AlumnoForm()

    contexto = {
        'formulario': formulario,
        'titulo': 'Registrar alumno',
        'texto_boton': 'Guardar alumno',
    }

    return render(
        request,
        'alumnos/alumno_formulario.html',
        contexto,
    )


# ============================================================
# EDICIÓN
# ============================================================

def alumno_editar(
    request,
    alumno_id,
):
    alumno = get_object_or_404(
        Alumno,
        id=alumno_id,
    )

    if request.method == 'POST':
        formulario = AlumnoForm(
            request.POST,
            instance=alumno,
        )

        if formulario.is_valid():
            alumno = formulario.save()

            messages.success(
                request,
                (
                    f'Los datos de '
                    f'{alumno.nombre_visible} '
                    f'fueron actualizados.'
                ),
            )

            return redirect(
                'alumnos:lista'
            )
    else:
        formulario = AlumnoForm(
            instance=alumno
        )

    contexto = {
        'formulario': formulario,
        'titulo': 'Editar alumno',
        'texto_boton': 'Actualizar alumno',
        'alumno': alumno,
    }

    return render(
        request,
        'alumnos/alumno_formulario.html',
        contexto,
    )

def alumno_historial(
    request,
    alumno_id,
):
    alumno = get_object_or_404(
        Alumno,
        id=alumno_id,
    )

    prestamos = (
        alumno.prestamos
        .select_related(
            'ejemplar',
            'ejemplar__libro',
        )
        .order_by(
            '-fecha_prestamo',
            '-id',
        )
    )

    cantidad_total = prestamos.count()

    cantidad_activos = prestamos.filter(
        estado='ACTIVO',
    ).count()

    cantidad_devueltos = prestamos.filter(
        estado='DEVUELTO',
    ).count()

    cantidad_vencidos = sum(
        1
        for prestamo in prestamos
        if prestamo.esta_vencido
    )

    paginador = Paginator(
        prestamos,
        20,
    )

    pagina = paginador.get_page(
        request.GET.get('pagina')
    )

    contexto = {
        'alumno': alumno,
        'prestamos': pagina,
        'pagina': pagina,
        'cantidad_total': cantidad_total,
        'cantidad_activos': cantidad_activos,
        'cantidad_devueltos': (
            cantidad_devueltos
        ),
        'cantidad_vencidos': (
            cantidad_vencidos
        ),
    }

    return render(
        request,
        'alumnos/alumno_historial.html',
        contexto,
    )
# ============================================================
# ELIMINACIÓN SEGURA
# ============================================================

def alumno_eliminar(
    request,
    alumno_id,
):
    alumno = get_object_or_404(
        Alumno,
        id=alumno_id,
    )

    tiene_prestamos = (
        alumno.prestamos.exists()
    )

    tiene_prestamos_activos = (
        alumno.prestamos.filter(
            estado='ACTIVO'
        ).exists()
    )

    if request.method == 'POST':
        accion = request.POST.get(
            'accion',
            '',
        )

        if accion == 'desactivar':
            if tiene_prestamos_activos:
                messages.error(
                    request,
                    (
                        'El alumno no puede desactivarse '
                        'porque tiene préstamos activos. '
                        'Registre primero las devoluciones.'
                    ),
                )

                return redirect(
                    'alumnos:eliminar',
                    alumno_id=alumno.id,
                )

            alumno.activo = False
            alumno.save(
                update_fields=[
                    'activo',
                ]
            )

            messages.success(
                request,
                (
                    f'El alumno '
                    f'{alumno.nombre_visible} '
                    f'fue marcado como inactivo.'
                ),
            )

            return redirect(
                'alumnos:lista'
            )

        if accion != 'eliminar':
            messages.error(
                request,
                (
                    'No se reconoció la operación '
                    'solicitada.'
                ),
            )

            return redirect(
                'alumnos:eliminar',
                alumno_id=alumno.id,
            )

        if tiene_prestamos:
            messages.error(
                request,
                (
                    'El alumno no puede eliminarse '
                    'porque posee historial de préstamos. '
                    'Puede marcarlo como inactivo.'
                ),
            )

            return redirect(
                'alumnos:eliminar',
                alumno_id=alumno.id,
            )

        nombre_alumno = (
            alumno.nombre_visible
        )

        alumno.delete()

        messages.success(
            request,
            (
                f'El alumno {nombre_alumno} '
                f'fue eliminado correctamente.'
            ),
        )

        return redirect(
            'alumnos:lista'
        )

    contexto = {
        'alumno': alumno,
        'tiene_prestamos': (
            tiene_prestamos
        ),
        'tiene_prestamos_activos': (
            tiene_prestamos_activos
        ),
    }

    return render(
        request,
        (
            'alumnos/'
            'alumno_confirmar_eliminar.html'
        ),
        contexto,
    )


# ============================================================
# IMPORTACIÓN ANUAL DESDE EXCEL
# ============================================================

def alumno_importar(request):
    resultados = None

    if request.method == 'POST':
        formulario = ImportarAlumnosForm(
            request.POST,
            request.FILES,
        )

        if formulario.is_valid():
            archivo = (
                formulario.cleaned_data[
                    'archivo'
                ]
            )

            anio_lectivo = (
                formulario.cleaned_data[
                    'anio_lectivo'
                ]
            )

            anio_actual = (
                timezone.localdate().year
            )

            promocion_requerida = (
                anio_lectivo > anio_actual
            )

            promocion_realizada = (
                PromocionAnual.objects.filter(
                    anio_destino=anio_lectivo
                ).exists()
            )

            if (
                promocion_requerida
                and not promocion_realizada
            ):
                formulario.add_error(
                    'anio_lectivo',
                    (
                        f'Antes de importar la lista '
                        f'{anio_lectivo}, debe realizar '
                        f'la promoción anual '
                        f'{anio_lectivo - 1} → '
                        f'{anio_lectivo}.'
                    ),
                )
            else:
                libro_excel = None

                try:
                    libro_excel = load_workbook(
                        archivo,
                        read_only=True,
                        data_only=True,
                    )

                    if (
                        'Alumnos'
                        not in libro_excel.sheetnames
                    ):
                        formulario.add_error(
                            'archivo',
                            (
                                'El archivo debe contener '
                                'una hoja llamada Alumnos.'
                            ),
                        )
                    else:
                        hoja = libro_excel[
                            'Alumnos'
                        ]

                        encabezados_esperados = [
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

                        encabezados_archivo = [
                            limpiar_texto(
                                hoja.cell(
                                    row=4,
                                    column=columna,
                                ).value
                            ).lower()
                            for columna
                            in range(1, 10)
                        ]

                        if (
                            encabezados_archivo
                            != encabezados_esperados
                        ):
                            formulario.add_error(
                                'archivo',
                                (
                                    'Las columnas de la '
                                    'planilla fueron '
                                    'modificadas. Utilice '
                                    'la plantilla oficial.'
                                ),
                            )
                        else:
                            resultados = (
                                procesar_alumnos_excel(
                                    hoja,
                                    anio_lectivo,
                                )
                            )

                except Exception as error:
                    formulario.add_error(
                        'archivo',
                        (
                            'No se pudo leer la planilla. '
                            f'Detalle: {error}'
                        ),
                    )
                finally:
                    if libro_excel is not None:
                        libro_excel.close()
    else:
        formulario = ImportarAlumnosForm()

    contexto = {
        'formulario': formulario,
        'resultados': resultados,
    }

    return render(
        request,
        'alumnos/alumno_importar.html',
        contexto,
    )


def procesar_alumnos_excel(
    hoja,
    anio_lectivo,
):
    especialidades_validas = {
        'ELECTRÓNICA',
        'ELECTRICIDAD',
    }

    turnos_validos = {
        'MAÑANA',
        'TARDE',
        'NOCHE',
    }

    secciones_validas = {
        'A',
        'B',
    }

    registros_validos = []
    errores = []
    cedulas_planilla = set()

    # Primera etapa: validar toda la planilla.
    for numero_fila, fila in enumerate(
        hoja.iter_rows(
            min_row=5,
            max_col=9,
            values_only=True,
        ),
        start=5,
    ):
        if all(
            valor is None
            for valor in fila
        ):
            continue

        (
            cedula,
            nombres,
            apellidos,
            curso,
            seccion,
            especialidad,
            turno,
            telefono,
            activo,
        ) = fila

        cedula = limpiar_cedula(
            cedula
        )

        nombres = limpiar_texto(
            nombres
        ).upper()

        apellidos = limpiar_texto(
            apellidos
        ).upper()

        curso = limpiar_texto(
            curso
        ).upper()

        seccion = limpiar_texto(
            seccion
        ).upper()

        especialidad = limpiar_texto(
            especialidad
        ).upper()

        turno = limpiar_texto(
            turno
        ).upper()

        telefono = limpiar_texto(
            telefono
        )

        if (
            especialidad
            == 'ELECTRONICA'
        ):
            especialidad = 'ELECTRÓNICA'

        if not cedula:
            errores.append(
                (
                    f'Fila {numero_fila}: '
                    f'falta la cédula.'
                )
            )
            continue

        if not cedula.isdigit():
            errores.append(
                (
                    f'Fila {numero_fila}: '
                    f'la cédula debe contener '
                    f'solamente números.'
                )
            )
            continue

        if len(cedula) > 20:
            errores.append(
                (
                    f'Fila {numero_fila}: '
                    f'la cédula es demasiado extensa.'
                )
            )
            continue

        if not nombres:
            errores.append(
                (
                    f'Fila {numero_fila}: '
                    f'faltan los nombres.'
                )
            )
            continue

        if not apellidos:
            errores.append(
                (
                    f'Fila {numero_fila}: '
                    f'faltan los apellidos.'
                )
            )
            continue

        numero_curso = (
            obtener_numero_curso(
                curso
            )
        )

        if numero_curso not in {
            1,
            2,
            3,
        }:
            errores.append(
                (
                    f'Fila {numero_fila}: '
                    f'el curso “{curso}” '
                    f'no es válido.'
                )
            )
            continue

        curso = f'{numero_curso}°'

        if (
            seccion
            not in secciones_validas
        ):
            errores.append(
                (
                    f'Fila {numero_fila}: '
                    f'la sección debe ser A o B.'
                )
            )
            continue

        if (
            especialidad
            not in especialidades_validas
        ):
            errores.append(
                (
                    f'Fila {numero_fila}: '
                    f'la especialidad debe ser '
                    f'ELECTRÓNICA o ELECTRICIDAD.'
                )
            )
            continue

        if turno not in turnos_validos:
            errores.append(
                (
                    f'Fila {numero_fila}: '
                    f'el turno no es válido.'
                )
            )
            continue

        if cedula in cedulas_planilla:
            errores.append(
                (
                    f'Fila {numero_fila}: '
                    f'la cédula {cedula} '
                    f'está repetida en la planilla.'
                )
            )
            continue

        cedulas_planilla.add(
            cedula
        )

        texto_activo = limpiar_texto(
            activo
        )

        if texto_activo:
            esta_activo = convertir_activo(
                texto_activo
            )
        else:
            # Una lista oficial sin valor en esta columna
            # se interpreta como alumno activo.
            esta_activo = True

        registros_validos.append(
            {
                'cedula': cedula,
                'nombres': nombres,
                'apellidos': apellidos,
                'curso': curso,
                'seccion': seccion,
                'especialidad': especialidad,
                'turno': turno,
                'telefono': telefono,
                'activo': esta_activo,
            }
        )

    # Si una fila tiene errores, no se guarda nada.
    if errores:
        return {
            'importados': 0,
            'creados': 0,
            'actualizados': 0,
            'sin_cambios': 0,
            'ausentes': 0,
            'duplicados': 0,
            'errores': errores,
            'cantidad_errores': len(
                errores
            ),
            'anio_lectivo': anio_lectivo,
            'guardado': False,
        }

    creados = 0
    actualizados = 0
    sin_cambios = 0

    cedulas_importadas = {
        registro['cedula']
        for registro in registros_validos
    }

    # Segunda etapa: crear o actualizar.
    with transaction.atomic():
        for registro in registros_validos:
            alumno = (
                Alumno.objects
                .filter(
                    cedula=registro['cedula']
                )
                .first()
            )

            valores_nuevos = {
                'nombres': (
                    registro['nombres']
                ),
                'apellidos': (
                    registro['apellidos']
                ),
                'curso': (
                    registro['curso']
                ),
                'seccion': (
                    registro['seccion']
                ),
                'especialidad': (
                    registro['especialidad']
                ),
                'turno': (
                    registro['turno']
                ),
                'telefono': (
                    registro['telefono']
                ),
                'activo': (
                    registro['activo']
                ),
                'anio_lectivo': (
                    anio_lectivo
                ),
                'anio_egreso': None,
            }

            if alumno is None:
                Alumno.objects.create(
                    cedula=registro['cedula'],
                    **valores_nuevos,
                )

                creados += 1
                continue

            hay_cambios = any(
                getattr(
                    alumno,
                    campo,
                ) != valor
                for campo, valor
                in valores_nuevos.items()
            )

            if hay_cambios:
                for campo, valor in (
                    valores_nuevos.items()
                ):
                    setattr(
                        alumno,
                        campo,
                        valor,
                    )

                alumno.save()
                actualizados += 1
            else:
                sin_cambios += 1

    # Solo se informa sobre los ausentes.
    # No se eliminan ni se desactivan.
    ausentes = (
        Alumno.objects.filter(
            activo=True,
            anio_lectivo=anio_lectivo,
        )
        .exclude(
            cedula__in=cedulas_importadas
        )
        .count()
    )

    return {
        'importados': creados,
        'creados': creados,
        'actualizados': actualizados,
        'sin_cambios': sin_cambios,
        'ausentes': ausentes,
        'duplicados': 0,
        'errores': [],
        'cantidad_errores': 0,
        'anio_lectivo': anio_lectivo,
        'guardado': True,
    }


# ============================================================
# PROMOCIÓN ANUAL
# ============================================================

def preparar_resumen_promocion(
    anio_origen,
):
    alumnos_activos = list(
        Alumno.objects.filter(
            activo=True,
            anio_lectivo=anio_origen,
        ).order_by(
            'curso',
            'seccion',
            'apellidos',
            'nombres',
        )
    )

    primero = []
    segundo = []
    tercero = []
    cursos_no_reconocidos = []

    for alumno in alumnos_activos:
        numero_curso = (
            obtener_numero_curso(
                alumno.curso
            )
        )

        if numero_curso == 1:
            primero.append(
                alumno
            )
        elif numero_curso == 2:
            segundo.append(
                alumno
            )
        elif numero_curso == 3:
            tercero.append(
                alumno
            )
        else:
            cursos_no_reconocidos.append(
                alumno
            )

    ids_tercero = [
        alumno.id
        for alumno in tercero
    ]

    # Se importa aquí para evitar dependencias
    # circulares durante la carga de Django.
    from prestamos.models import Prestamo

    prestamos_pendientes = list(
        Prestamo.objects.filter(
            alumno_id__in=ids_tercero,
            estado=Prestamo.Estado.ACTIVO,
        ).select_related(
            'alumno',
            'ejemplar',
            'ejemplar__libro',
        ).order_by(
            'alumno__apellidos',
            'alumno__nombres',
        )
    )

    return {
        'primero': primero,
        'segundo': segundo,
        'tercero': tercero,
        'cursos_no_reconocidos': (
            cursos_no_reconocidos
        ),
        'prestamos_pendientes': (
            prestamos_pendientes
        ),
    }


@transaction.atomic
def promocion_anual(request):
    anio_origen = (
        timezone.localdate().year
    )

    anio_destino = (
        anio_origen + 1
    )

    promocion_realizada = (
        PromocionAnual.objects.filter(
            anio_destino=anio_destino
        ).first()
    )

    resumen = preparar_resumen_promocion(
        anio_origen
    )

    if request.method == 'POST':
        if promocion_realizada:
            messages.warning(
                request,
                (
                    f'La promoción al año '
                    f'{anio_destino} ya fue '
                    f'realizada anteriormente.'
                ),
            )

            return redirect(
                'alumnos:promocion_anual'
            )

        if resumen[
            'prestamos_pendientes'
        ]:
            messages.error(
                request,
                (
                    'No se puede confirmar la '
                    'promoción porque existen '
                    'alumnos de tercer curso '
                    'con préstamos activos.'
                ),
            )

            return redirect(
                'alumnos:promocion_anual'
            )

        if resumen[
            'cursos_no_reconocidos'
        ]:
            messages.error(
                request,
                (
                    'No se puede confirmar la '
                    'promoción porque existen '
                    'alumnos con cursos que '
                    'deben corregirse.'
                ),
            )

            return redirect(
                'alumnos:promocion_anual'
            )

        alumnos_bloqueados = list(
            Alumno.objects
            .select_for_update()
            .filter(
                activo=True,
                anio_lectivo=anio_origen,
            )
        )

        cantidad_primero = 0
        cantidad_segundo = 0
        cantidad_egresados = 0

        for alumno in alumnos_bloqueados:
            numero_curso = (
                obtener_numero_curso(
                    alumno.curso
                )
            )

            if numero_curso == 1:
                alumno.curso = '2°'
                alumno.anio_lectivo = (
                    anio_destino
                )
                alumno.anio_egreso = None

                alumno.save(
                    update_fields=[
                        'curso',
                        'anio_lectivo',
                        'anio_egreso',
                    ]
                )

                cantidad_primero += 1

            elif numero_curso == 2:
                alumno.curso = '3°'
                alumno.anio_lectivo = (
                    anio_destino
                )
                alumno.anio_egreso = None

                alumno.save(
                    update_fields=[
                        'curso',
                        'anio_lectivo',
                        'anio_egreso',
                    ]
                )

                cantidad_segundo += 1

            elif numero_curso == 3:
                alumno.activo = False
                alumno.anio_egreso = (
                    anio_origen
                )

                alumno.save(
                    update_fields=[
                        'activo',
                        'anio_egreso',
                    ]
                )

                cantidad_egresados += 1

        PromocionAnual.objects.create(
            anio_origen=anio_origen,
            anio_destino=anio_destino,
            alumnos_primero_a_segundo=(
                cantidad_primero
            ),
            alumnos_segundo_a_tercero=(
                cantidad_segundo
            ),
            alumnos_egresados=(
                cantidad_egresados
            ),
        )

        messages.success(
            request,
            (
                f'Promoción {anio_origen} → '
                f'{anio_destino} realizada '
                f'correctamente. '
                f'{cantidad_primero} alumnos '
                f'pasaron a 2°, '
                f'{cantidad_segundo} pasaron '
                f'a 3° y '
                f'{cantidad_egresados} quedaron '
                f'como egresados.'
            ),
        )

        return redirect(
            'alumnos:lista'
        )

    historial_promociones = (
        PromocionAnual.objects.all()
        .order_by(
            '-anio_destino'
        )
    )

    contexto = {
        'anio_origen': anio_origen,
        'anio_destino': anio_destino,

        'promocion_realizada': (
            promocion_realizada
        ),

        'historial_promociones': (
            historial_promociones
        ),

        'cantidad_primero': len(
            resumen['primero']
        ),

        'cantidad_segundo': len(
            resumen['segundo']
        ),

        'cantidad_tercero': len(
            resumen['tercero']
        ),

        'primero': (
            resumen['primero']
        ),

        'segundo': (
            resumen['segundo']
        ),

        'tercero': (
            resumen['tercero']
        ),

        'cursos_no_reconocidos': (
            resumen[
                'cursos_no_reconocidos'
            ]
        ),

        'prestamos_pendientes': (
            resumen[
                'prestamos_pendientes'
            ]
        ),

        'puede_confirmar': (
            not promocion_realizada
            and not resumen[
                'prestamos_pendientes'
            ]
            and not resumen[
                'cursos_no_reconocidos'
            ]
        ),
    }

    return render(
        request,
        'alumnos/promocion_anual.html',
        contexto,
    )