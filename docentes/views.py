from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DocenteForm
from .models import Docente


def docente_lista(request):
    busqueda = request.GET.get('buscar', '').strip()

    docentes = Docente.objects.all()

    if busqueda:
        docentes = docentes.filter(
            Q(cedula__icontains=busqueda)
            | Q(nombres__icontains=busqueda)
            | Q(apellidos__icontains=busqueda)
            | Q(area__icontains=busqueda)
        )

    contexto = {
        'docentes': docentes,
        'busqueda': busqueda,
    }

    return render(
        request,
        'docentes/docente_lista.html',
        contexto,
    )


def docente_crear(request):
    if request.method == 'POST':
        formulario = DocenteForm(request.POST)

        if formulario.is_valid():
            docente = formulario.save()

            messages.success(
                request,
                (
                    f'El docente {docente.nombres} '
                    f'{docente.apellidos} fue registrado correctamente.'
                ),
            )

            return redirect('docentes:lista')
    else:
        formulario = DocenteForm()

    contexto = {
        'formulario': formulario,
        'titulo': 'Registrar docente',
        'texto_boton': 'Guardar docente',
    }

    return render(
        request,
        'docentes/docente_formulario.html',
        contexto,
    )


def docente_editar(request, docente_id):
    docente = get_object_or_404(
        Docente,
        id=docente_id,
    )

    if request.method == 'POST':
        formulario = DocenteForm(
            request.POST,
            instance=docente,
        )

        if formulario.is_valid():
            formulario.save()

            messages.success(
                request,
                'Los datos del docente fueron actualizados.',
            )

            return redirect('docentes:lista')
    else:
        formulario = DocenteForm(instance=docente)

    contexto = {
        'formulario': formulario,
        'titulo': 'Editar docente',
        'texto_boton': 'Actualizar docente',
        'docente': docente,
    }

    return render(
        request,
        'docentes/docente_formulario.html',
        contexto,
    )