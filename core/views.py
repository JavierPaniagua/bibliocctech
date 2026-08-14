import sqlite3
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.db import connection
from django.http import FileResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from libros.models import Ejemplar, Libro
from prestamos.models import Prestamo


def inicio(request):
    fecha_actual = timezone.localdate()

    contexto = {
        "total_titulos": Libro.objects.filter(activo=True).count(),
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

    return render(request, "core/inicio.html", contexto)


@require_POST
def crear_respaldo(request):
    """Crea una copia consistente de SQLite y la descarga al equipo."""
    base_datos = Path(settings.DATABASES["default"]["NAME"])

    if not base_datos.exists():
        messages.error(request, "No se encontró la base de datos del sistema.")
        return redirect("core:inicio")

    carpeta_respaldos = Path(settings.BASE_DIR) / "backups"
    carpeta_respaldos.mkdir(parents=True, exist_ok=True)

    fecha = timezone.localtime().strftime("%Y-%m-%d_%H-%M-%S")
    nombre_archivo = f"bibliotech_{fecha}.sqlite3"
    ruta_respaldo = carpeta_respaldos / nombre_archivo

    destino = None

    try:
        # Garantiza que Django tenga abierta la conexión SQLite actual.
        connection.ensure_connection()
        origen = connection.connection

        destino = sqlite3.connect(ruta_respaldo)
        origen.backup(destino)
        destino.commit()

    except (OSError, sqlite3.Error) as error:
        if ruta_respaldo.exists():
            ruta_respaldo.unlink(missing_ok=True)

        messages.error(request, f"No se pudo crear el respaldo: {error}")
        return redirect("core:inicio")

    finally:
        if destino is not None:
            destino.close()

    archivo = ruta_respaldo.open("rb")

    return FileResponse(
        archivo,
        as_attachment=True,
        filename=nombre_archivo,
        content_type="application/vnd.sqlite3",
    )


def reportes(request):
    return render(request, "core/reportes.html")