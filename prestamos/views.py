from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import DevolucionForm, PrestamoForm
from .models import Prestamo


def prestamo_lista(request):
    """
    Muestra todos los préstamos y permite buscar por:
    - Cédula
    - Alumno
    - Docente
    - Título
    - Número de inventario
    """
    busqueda = request.GET.get("q", "").strip()
    filtro = request.GET.get("estado", "activos")

    prestamos = Prestamo.objects.select_related(
        "alumno",
        "docente",
        "ejemplar",
        "ejemplar__libro",
    )

    if filtro == "activos":
        prestamos = prestamos.filter(estado=Prestamo.Estado.ACTIVO)

    elif filtro == "vencidos":
        prestamos = prestamos.filter(
            estado=Prestamo.Estado.ACTIVO,
            fecha_devolucion_prevista__lt=timezone.localdate(),
        )

    elif filtro == "devueltos":
        prestamos = prestamos.filter(estado=Prestamo.Estado.DEVUELTO)

    if busqueda:
        filtros_busqueda = (
            Q(alumno__cedula__icontains=busqueda)
            | Q(docente__cedula__icontains=busqueda)
            | Q(ejemplar__libro__titulo__icontains=busqueda)
            | Q(ejemplar__libro__autor__icontains=busqueda)
        )

        if busqueda.isdigit():
            filtros_busqueda |= Q(
                ejemplar__numero_inventario=int(busqueda)
            )

        # Campos antiguos y nuevos del módulo de alumnos.
        campos_alumno = {
            campo.name
            for campo in Prestamo._meta.get_field("alumno")
            .related_model._meta.get_fields()
        }

        if "nombre_completo" in campos_alumno:
            filtros_busqueda |= Q(
                alumno__nombre_completo__icontains=busqueda
            )

        if "nombres" in campos_alumno:
            filtros_busqueda |= Q(alumno__nombres__icontains=busqueda)

        if "apellidos" in campos_alumno:
            filtros_busqueda |= Q(alumno__apellidos__icontains=busqueda)

        campos_docente = {
            campo.name
            for campo in Prestamo._meta.get_field("docente")
            .related_model._meta.get_fields()
        }

        if "nombre_completo" in campos_docente:
            filtros_busqueda |= Q(
                docente__nombre_completo__icontains=busqueda
            )

        if "nombres" in campos_docente:
            filtros_busqueda |= Q(docente__nombres__icontains=busqueda)

        if "apellidos" in campos_docente:
            filtros_busqueda |= Q(docente__apellidos__icontains=busqueda)

        prestamos = prestamos.filter(filtros_busqueda)

    prestamos = prestamos.order_by(
        "estado",
        "fecha_devolucion_prevista",
        "-fecha_prestamo",
    )

    contexto = {
        "prestamos": prestamos,
        "busqueda": busqueda,
        "filtro": filtro,
        "fecha_actual": timezone.localdate(),
    }

    return render(
        request,
        "prestamos/prestamo_lista.html",
        contexto,
    )


@transaction.atomic
def prestamo_crear(request):
    """
    Registra un préstamo utilizando:
    - Tipo de beneficiario
    - Cédula
    - Número de inventario

    La devolución prevista se calcula automáticamente
    a cinco días hábiles.
    """
    if request.method == "POST":
        formulario = PrestamoForm(request.POST)

        if formulario.is_valid():
            alumno = formulario.cleaned_data["alumno"]
            docente = formulario.cleaned_data["docente"]
            ejemplar = formulario.cleaned_data["ejemplar"]

            prestamo = Prestamo(
                alumno=alumno,
                docente=docente,
                ejemplar=ejemplar,
                fecha_prestamo=formulario.cleaned_data["fecha_prestamo"],
                observaciones=formulario.cleaned_data["observaciones"],
                estado=Prestamo.Estado.ACTIVO,
            )

            prestamo.save()

            messages.success(
                request,
                (
                    "Préstamo registrado correctamente. "
                    f"El libro debe devolverse el "
                    f"{prestamo.fecha_devolucion_prevista.strftime('%d/%m/%Y')}."
                ),
            )

            return redirect("prestamos:lista")

    else:
        formulario = PrestamoForm()

    return render(
        request,
        "prestamos/prestamo_formulario.html",
        {
            "formulario": formulario,
        },
    )


@transaction.atomic
def prestamo_devolver(request, prestamo_id):
    """
    Registra la devolución y vuelve a dejar disponible
    el ejemplar.
    """
    prestamo = get_object_or_404(
        Prestamo.objects.select_related(
            "alumno",
            "docente",
            "ejemplar",
            "ejemplar__libro",
        ),
        pk=prestamo_id,
    )

    if prestamo.estado == Prestamo.Estado.DEVUELTO:
        messages.info(
            request,
            "Este préstamo ya fue devuelto anteriormente.",
        )
        return redirect("prestamos:lista")

    if request.method == "POST":
        formulario = DevolucionForm(
            request.POST,
            prestamo=prestamo,
        )

        if formulario.is_valid():
            fecha_devolucion = formulario.cleaned_data[
                "fecha_devolucion_real"
            ]
            condicion = formulario.cleaned_data["condicion"]
            observacion_devolucion = formulario.cleaned_data[
                "observaciones"
            ].strip()

            prestamo.fecha_devolucion_real = fecha_devolucion
            prestamo.estado = Prestamo.Estado.DEVUELTO

            if observacion_devolucion:
                texto_devolucion = (
                    f"Devolución {fecha_devolucion.strftime('%d/%m/%Y')}: "
                    f"{observacion_devolucion}"
                )

                if prestamo.observaciones:
                    prestamo.observaciones = (
                        f"{prestamo.observaciones}\n{texto_devolucion}"
                    )
                else:
                    prestamo.observaciones = texto_devolucion

            prestamo.ejemplar.condicion = condicion
            prestamo.ejemplar.save(update_fields=["condicion"])

            # El método save() del modelo Prestamo también cambia
            # el estado del ejemplar nuevamente a DISPONIBLE.
            prestamo.save()

            messages.success(
                request,
                (
                    "Devolución registrada correctamente. "
                    f'El ejemplar "{prestamo.ejemplar.libro.titulo}" '
                    "está disponible nuevamente."
                ),
            )

            return redirect("prestamos:lista")

    else:
        formulario = DevolucionForm(prestamo=prestamo)

    return render(
        request,
        "prestamos/prestamo_devolver.html",
        {
            "formulario": formulario,
            "prestamo": prestamo,
        },
    )

def prestamo_reporte(request):
    fecha_actual = timezone.localdate()

    prestamos = Prestamo.objects.select_related(
        "alumno",
        "docente",
        "ejemplar",
        "ejemplar__libro",
    ).order_by(
        "estado",
        "fecha_devolucion_prevista",
        "-fecha_prestamo",
    )

    total_prestamos = prestamos.count()

    prestamos_activos = prestamos.filter(
        estado=Prestamo.Estado.ACTIVO
    ).count()

    prestamos_devueltos = prestamos.filter(
        estado=Prestamo.Estado.DEVUELTO
    ).count()

    prestamos_vencidos = prestamos.filter(
        estado=Prestamo.Estado.ACTIVO,
        fecha_devolucion_prevista__lt=fecha_actual,
    ).count()

    contexto = {
        "prestamos": prestamos,
        "fecha_actual": fecha_actual,
        "total_prestamos": total_prestamos,
        "prestamos_activos": prestamos_activos,
        "prestamos_devueltos": prestamos_devueltos,
        "prestamos_vencidos": prestamos_vencidos,
    }

    return render(
        request,
        "prestamos/prestamo_reporte.html",
        contexto,
    )