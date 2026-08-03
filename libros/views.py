from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LibroCrearForm, LibroEditarForm
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