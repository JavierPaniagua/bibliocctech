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

from alumnos.models import Alumno
from docentes.models import Docente

def inicio(request):
    fecha_actual = timezone.localdate()

    contexto = {
        
        "alumnos_activos": Alumno.objects.filter(
        activo=True
        ).count(),

        "docentes_activos": Docente.objects.filter(
         activo=True
        ).count(),
        
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

def estadisticas_biblioteca(request):
    """Resumen estadístico del uso y composición de la biblioteca."""
    from django.db.models import Count

    fecha_actual = timezone.localdate()

    libros_solicitados = (
        Libro.objects
        .filter(activo=True)
        .annotate(
            total_prestamos=Count("ejemplares__prestamos", distinct=True),
            total_ejemplares=Count("ejemplares", distinct=True),
        )
        .order_by("-total_prestamos", "titulo")[:20]
    )

    cantidades_por_area = list(
        Libro.objects
        .filter(activo=True)
        .values("area")
        .annotate(
            total_titulos=Count("id", distinct=True),
            total_ejemplares=Count("ejemplares", distinct=True),
            total_prestamos=Count("ejemplares__prestamos", distinct=True),
        )
        .order_by("area")
    )

    nombres_area = {
        str(valor): nombre
        for valor, nombre in Libro._meta.get_field("area").choices
    }

    for fila in cantidades_por_area:
        valor_area = str(fila["area"] or "")
        fila["nombre_area"] = nombres_area.get(valor_area, "Sin clasificar")

    prestamos = Prestamo.objects.all()

    contexto = {
        "fecha_actual": fecha_actual,
        "libros_solicitados": libros_solicitados,
        "cantidades_por_area": cantidades_por_area,
        "total_titulos": Libro.objects.filter(activo=True).count(),
        "total_ejemplares": Ejemplar.objects.count(),
        "total_prestamos": prestamos.count(),
        "total_activos": prestamos.filter(
            estado=Prestamo.Estado.ACTIVO
        ).count(),
        "total_devueltos": prestamos.filter(
            estado=Prestamo.Estado.DEVUELTO
        ).count(),
        "total_vencidos": prestamos.filter(
            estado=Prestamo.Estado.ACTIVO,
            fecha_devolucion_prevista__lt=fecha_actual,
        ).count(),
    }

    return render(request, "core/estadisticas_biblioteca.html", contexto)