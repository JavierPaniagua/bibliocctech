from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AlumnoForm
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