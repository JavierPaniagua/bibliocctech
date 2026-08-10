from django.shortcuts import render
from django.utils import timezone

from libros.models import Ejemplar, Libro
from prestamos.models import Prestamo


def inicio(request):
    fecha_actual = timezone.localdate()

    total_titulos = Libro.objects.filter(
        activo=True
    ).count()

    total_ejemplares = Ejemplar.objects.count()

    ejemplares_disponibles = Ejemplar.objects.filter(
        estado=Ejemplar.Estado.DISPONIBLE
    ).count()

    prestamos_activos = Prestamo.objects.filter(
        estado=Prestamo.Estado.ACTIVO
    ).count()

    prestamos_vencidos = Prestamo.objects.filter(
        estado=Prestamo.Estado.ACTIVO,
        fecha_devolucion_prevista__lt=fecha_actual,
    ).count()

    contexto = {
        "total_titulos": total_titulos,
        "total_ejemplares": total_ejemplares,
        "ejemplares_disponibles": ejemplares_disponibles,
        "prestamos_activos": prestamos_activos,
        "prestamos_vencidos": prestamos_vencidos,
    }

    return render(
        request,
        "core/inicio.html",
        contexto,
    )