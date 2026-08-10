from datetime import datetime
from pathlib import Path
from shutil import copy2

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from libros.models import Ejemplar, Libro
from prestamos.models import Prestamo


def inicio(request):
    fecha_actual = timezone.localdate()

    contexto = {
        "total_titulos": Libro.objects.filter(
            activo=True
        ).count(),

        "total_ejemplares": Ejemplar.objects.count(),

        "ejemplares_disponibles": Ejemplar.objects.filter(
            estado=Ejemplar.Estado.DISPONIBLE
        ).count(),

        "prestamos_activos": Prestamo.objects.filter(
            estado=Prestamo.Estado.ACTIVO
        ).count(),

        "prestamos_vencidos": Prestamo.objects.filter(
            estado=Prestamo.Estado.ACTIVO,
            fecha_devolucion_prevista__lt=fecha_actual,
        ).count(),
    }

    return render(
        request,
        "core/inicio.html",
        contexto,
    )


@require_POST
def crear_respaldo(request):
    base_datos = Path(
        settings.DATABASES["default"]["NAME"]
    )

    if not base_datos.exists():
        messages.error(
            request,
            "No se encontró la base de datos.",
        )

        return redirect("core:inicio")

    carpeta_respaldos = (
        Path(settings.BASE_DIR)
        / "backups"
    )

    carpeta_respaldos.mkdir(
        parents=True,
        exist_ok=True,
    )

    fecha = datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    nombre_archivo = (
        f"bibliocctech_respaldo_{fecha}.sqlite3"
    )

    ruta_respaldo = (
        carpeta_respaldos
        / nombre_archivo
    )

    try:
        copy2(
            base_datos,
            ruta_respaldo,
        )

    except OSError as error:
        messages.error(
            request,
            f"No se pudo crear el respaldo: {error}",
        )

    else:
        messages.success(
            request,
            (
                "Copia de seguridad creada correctamente: "
                f"{nombre_archivo}"
            ),
        )

    return redirect("core:inicio")

def reportes(request):
    return render(
        request,
        "core/reportes.html",
    )

def reportes(request):
    return render(
        request,
        "core/reportes.html",
    )