import os
import sqlite3
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connections
from django.utils import timezone


class Command(BaseCommand):
    help = (
        "Restaura BIBLIOTECH desde un respaldo SQLite válido. "
        "Antes de restaurar, conserva una copia de la base actual."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "archivo",
            help=(
                "Nombre del respaldo guardado en backups o ruta completa "
                "del archivo .sqlite3"
            ),
        )
        parser.add_argument(
            "--confirmar",
            action="store_true",
            help="Confirma que se desea reemplazar la base de datos actual.",
        )

    def handle(self, *args, **options):
        if settings.DATABASES["default"]["ENGINE"] != "django.db.backends.sqlite3":
            raise CommandError("Este comando solamente admite bases de datos SQLite.")

        base_dir = Path(settings.BASE_DIR)
        carpeta_respaldos = base_dir / "backups"
        carpeta_respaldos.mkdir(parents=True, exist_ok=True)

        archivo_indicado = Path(options["archivo"]).expanduser()
        if not archivo_indicado.is_absolute():
            archivo_indicado = carpeta_respaldos / archivo_indicado

        archivo_respaldo = archivo_indicado.resolve()
        base_actual = Path(settings.DATABASES["default"]["NAME"]).resolve()

        if not archivo_respaldo.exists() or not archivo_respaldo.is_file():
            raise CommandError(f"No se encontró el respaldo: {archivo_respaldo}")

        if archivo_respaldo == base_actual:
            raise CommandError("El respaldo seleccionado es la base de datos actual.")

        if archivo_respaldo.suffix.lower() not in {".sqlite3", ".sqlite", ".db"}:
            raise CommandError("Seleccione un archivo SQLite válido.")

        self._verificar_integridad(archivo_respaldo)

        self.stdout.write(self.style.SUCCESS("El respaldo es válido."))
        self.stdout.write(f"Origen: {archivo_respaldo}")
        self.stdout.write(f"Destino: {base_actual}")

        if not options["confirmar"]:
            self.stdout.write(
                self.style.WARNING(
                    "No se modificó la base de datos. Para restaurarla, "
                    "repita el comando agregando --confirmar."
                )
            )
            return

        fecha = timezone.localtime().strftime("%Y-%m-%d_%H-%M-%S")
        respaldo_previo = carpeta_respaldos / f"antes_de_restaurar_{fecha}.sqlite3"
        archivo_temporal = base_actual.with_name(f"{base_actual.name}.restaurando")

        # Cierra cualquier conexión abierta por Django antes del reemplazo.
        connections.close_all()

        try:
            if base_actual.exists():
                self._copiar_sqlite(base_actual, respaldo_previo)
                self._verificar_integridad(respaldo_previo)

            if archivo_temporal.exists():
                archivo_temporal.unlink()

            self._copiar_sqlite(archivo_respaldo, archivo_temporal)
            self._verificar_integridad(archivo_temporal)

            # os.replace realiza el reemplazo final en una sola operación.
            os.replace(archivo_temporal, base_actual)

        except (OSError, sqlite3.Error) as error:
            if archivo_temporal.exists():
                archivo_temporal.unlink(missing_ok=True)
            raise CommandError(f"No se pudo restaurar el respaldo: {error}") from error

        self.stdout.write(
            self.style.SUCCESS("La base de datos fue restaurada correctamente.")
        )

        if respaldo_previo.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"La base anterior quedó guardada en: {respaldo_previo}"
                )
            )

    def _verificar_integridad(self, ruta):
        try:
            with sqlite3.connect(ruta) as conexion:
                resultado = conexion.execute("PRAGMA integrity_check").fetchone()
        except sqlite3.Error as error:
            raise CommandError(f"No se pudo leer el archivo SQLite: {error}") from error

        if not resultado or resultado[0].lower() != "ok":
            detalle = resultado[0] if resultado else "sin respuesta"
            raise CommandError(f"El respaldo no superó la verificación: {detalle}")

    def _copiar_sqlite(self, origen, destino):
        with sqlite3.connect(origen) as conexion_origen:
            with sqlite3.connect(destino) as conexion_destino:
                conexion_origen.backup(conexion_destino)
                conexion_destino.commit()