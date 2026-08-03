from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from openpyxl import load_workbook
from .forms import AlumnoForm, ImportarAlumnosForm
from .models import Alumno


def alumno_lista(request):
    busqueda = request.GET.get('buscar', '').strip()

    alumnos = Alumno.objects.all()

    if busqueda:
        alumnos = alumnos.filter(
            Q(cedula__icontains=busqueda)
            | Q(nombres__icontains=busqueda)
            | Q(apellidos__icontains=busqueda)
            | Q(curso__icontains=busqueda)
        )

    contexto = {
        'alumnos': alumnos,
        'busqueda': busqueda,
    }

    return render(
        request,
        'alumnos/alumno_lista.html',
        contexto,
    )


def alumno_crear(request):
    if request.method == 'POST':
        formulario = AlumnoForm(request.POST)

        if formulario.is_valid():
            alumno = formulario.save()

            messages.success(
                request,
                f'El alumno {alumno.nombres} '
                f'{alumno.apellidos} fue registrado correctamente.',
            )

            return redirect('alumnos:lista')
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


def alumno_editar(request, alumno_id):
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
            formulario.save()

            messages.success(
                request,
                'Los datos del alumno fueron actualizados.',
            )

            return redirect('alumnos:lista')
    else:
        formulario = AlumnoForm(instance=alumno)

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

def limpiar_texto(valor):
    if valor is None:
        return ''

    return str(valor).strip()


def limpiar_cedula(valor):
    if valor is None:
        return ''

    if isinstance(valor, float) and valor.is_integer():
        valor = int(valor)

    cedula = str(valor).strip()

    cedula = (
        cedula
        .replace('.', '')
        .replace(' ', '')
        .replace('-', '')
    )

    return cedula


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


def alumno_importar(request):
    resultados = None

    if request.method == 'POST':
        formulario = ImportarAlumnosForm(
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

                if 'Alumnos' not in libro_excel.sheetnames:
                    formulario.add_error(
                        'archivo',
                        'El archivo debe contener una hoja llamada Alumnos.',
                    )
                else:
                    hoja = libro_excel['Alumnos']

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
                        for columna in range(1, 10)
                    ]

                    if encabezados_archivo != encabezados_esperados:
                        formulario.add_error(
                            'archivo',
                            (
                                'Las columnas de la planilla fueron '
                                'modificadas. Descargue y utilice la '
                                'plantilla oficial.'
                            ),
                        )
                    else:
                        resultados = procesar_alumnos_excel(hoja)

            except Exception:
                formulario.add_error(
                    'archivo',
                    (
                        'No se pudo leer la planilla. Compruebe que '
                        'sea un archivo Excel válido.'
                    ),
                )
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


def procesar_alumnos_excel(hoja):
    especialidades_validas = {
        'ELECTRÓNICA',
        'ELECTRONICA',
        'ELECTRICIDAD',
    }

    turnos_validos = {
        'MAÑANA',
        'TARDE',
        'NOCHE',
    }

    importados = 0
    duplicados = 0
    errores = []
    cedulas_planilla = set()

    for numero_fila, fila in enumerate(
        hoja.iter_rows(
            min_row=5,
            max_col=9,
            values_only=True,
        ),
        start=5,
    ):
        if all(valor is None for valor in fila):
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

        cedula = limpiar_cedula(cedula)
        nombres = limpiar_texto(nombres)
        apellidos = limpiar_texto(apellidos)
        curso = limpiar_texto(curso)
        seccion = limpiar_texto(seccion).upper()
        especialidad = limpiar_texto(especialidad).upper()
        turno = limpiar_texto(turno).upper()
        telefono = limpiar_texto(telefono)

        if not cedula or not nombres or not apellidos or not curso:
            errores.append(
                f'Fila {numero_fila}: faltan datos obligatorios.'
            )
            continue

        if not cedula.isdigit():
            errores.append(
                f'Fila {numero_fila}: la cédula debe contener '
                f'solamente números.'
            )
            continue

        if especialidad not in especialidades_validas:
            errores.append(
                f'Fila {numero_fila}: especialidad incorrecta.'
            )
            continue

        if especialidad == 'ELECTRONICA':
            especialidad = 'ELECTRÓNICA'

        if turno not in turnos_validos:
            errores.append(
                f'Fila {numero_fila}: turno incorrecto.'
            )
            continue

        if cedula in cedulas_planilla:
            duplicados += 1

            errores.append(
                f'Fila {numero_fila}: la cédula {cedula} '
                f'está repetida en la planilla.'
            )

            continue

        cedulas_planilla.add(cedula)

        if Alumno.objects.filter(cedula=cedula).exists():
            duplicados += 1

            errores.append(
                f'Fila {numero_fila}: el alumno con cédula '
                f'{cedula} ya está registrado.'
            )

            continue

        Alumno.objects.create(
            cedula=cedula,
            nombres=nombres,
            apellidos=apellidos,
            curso=curso,
            seccion=seccion,
            especialidad=especialidad,
            turno=turno,
            telefono=telefono,
            activo=convertir_activo(activo),
        )

        importados += 1

    return {
        'importados': importados,
        'duplicados': duplicados,
        'errores': errores,
        'cantidad_errores': len(errores),
    }