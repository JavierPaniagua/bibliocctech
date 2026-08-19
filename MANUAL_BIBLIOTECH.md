# BIBLIOTECH

## Biblioteca Escolar CCTL

BIBLIOTECH es el sistema utilizado para registrar libros, alumnos,
docentes, préstamos, devoluciones, etiquetas, reportes y respaldos de
la Biblioteca Escolar CCTL.

---

## 1. Iniciar el sistema

1. Hacer doble clic en el acceso directo **BIBLIOTECH**.
2. Esperar mientras se crea el respaldo automático.
3. El sistema se abrirá en el navegador.
4. No cerrar la ventana azul mientras se utiliza BIBLIOTECH.

Dirección del sistema:

http://127.0.0.1:8000/

---

## 2. Cerrar el sistema

1. Cerrar la pestaña del navegador.
2. Volver a la ventana azul de BIBLIOTECH.
3. Presionar `CTRL + C`.
4. Confirmar si el sistema lo solicita.
5. Cerrar la ventana.

---

## 3. Registrar un alumno

1. Entrar en **Alumnos**.
2. Presionar **Registrar alumno**.
3. Completar cédula, nombres, apellidos, curso, sección,
   especialidad y turno.
4. Presionar **Guardar alumno**.

No puede registrarse dos veces la misma cédula.

---

## 4. Importar alumnos desde Excel

1. Entrar en **Alumnos**.
2. Presionar **Importar Excel**.
3. Seleccionar el año lectivo.
4. Seleccionar la plantilla oficial.
5. Presionar **Importar alumnos**.
6. Revisar los resultados.

El Excel debe tener una hoja llamada `Alumnos`.

Los alumnos existentes se actualizan por cédula.
Los alumnos nuevos se crean.
Los alumnos ausentes no se eliminan automáticamente.

---

## 5. Registrar un docente

1. Entrar en **Docentes**.
2. Presionar **Registrar docente**.
3. Completar cédula, nombres, apellidos y área.
4. El teléfono y el correo son opcionales.
5. Presionar **Guardar docente**.

---

## 6. Registrar un libro nuevo

1. Entrar en **Libros**.
2. Presionar **Registrar libro**.
3. Completar los datos bibliográficos.
4. Indicar clasificación y signatura.
5. Registrar el ejemplar físico.
6. El sistema propondrá el siguiente número de inventario.

Cada ejemplar físico debe tener un número de inventario único.

---

## 7. Agregar otro ejemplar del mismo libro

Si existen varios ejemplares del mismo título:

1. Buscar el libro.
2. Presionar **Ver ejemplares**.
3. Presionar **Agregar ejemplar**.
4. Confirmar el número de inventario.
5. Completar estantería, balda, condición y adquisición.
6. Guardar.

No se debe crear nuevamente el título si se trata del mismo libro.

---

## 8. Importar libros desde Excel

1. Entrar en **Libros**.
2. Presionar **Importar desde Excel**.
3. Seleccionar la plantilla oficial.
4. Revisar la vista previa.
5. Corregir las filas señaladas si existen errores.
6. Confirmar la importación.

Los ejemplares se identifican por su número de inventario.

---

## 9. Registrar un préstamo

1. Presionar **Registrar préstamo**.
2. Seleccionar alumno o docente.
3. Ingresar la cédula.
4. Verificar los datos mostrados.
5. Ingresar el número de inventario del libro.
6. Verificar que el libro esté disponible.
7. Confirmar la fecha del préstamo.
8. Presionar **Registrar préstamo**.

La devolución se calcula automáticamente a cinco días hábiles.

---

## 10. Registrar una devolución

1. Entrar en **Préstamos**.
2. Buscar por cédula, persona, libro o inventario.
3. Presionar **Devolver**.
4. Revisar la fecha real de devolución.
5. Seleccionar la condición en que fue devuelto el libro.
6. Agregar una observación si presenta daños.
7. Confirmar la devolución.

La fecha actual aparece automáticamente, pero puede modificarse.
No se permiten fechas futuras ni anteriores al préstamo.

---

## 11. Préstamos vencidos

1. Desde el panel principal, entrar en **Préstamos vencidos**.
2. Revisar las personas y libros pendientes.
3. Registrar la devolución cuando corresponda.

Una persona con préstamos vencidos no debe recibir otro libro.

---

## 12. Imprimir etiquetas

### Etiqueta individual

1. Buscar el libro.
2. Entrar en **Ver ejemplares**.
3. Presionar **Imprimir**.
4. Seleccionar la etiqueta correspondiente.
5. Confirmar la impresión.

### Etiquetas en mosaico

1. Entrar en **Libros**.
2. Presionar **Imprimir etiquetas**.
3. Seleccionar los ejemplares.
4. Preparar la hoja oficio.
5. Imprimir y cortar las etiquetas.

---

## 13. Ubicación de los libros

La ubicación se registra mediante:

- Estantería.
- Balda.

Ejemplo:

- Estantería: `1`
- Balda: `A`

En el sistema aparecerá como:

`Estantería 1 - Balda A`

---

## 14. Reportes

Desde **Reportes** pueden consultarse:

- Inventario de libros.
- Ejemplares físicos.
- Préstamos activos.
- Préstamos devueltos.
- Préstamos vencidos.
- Movimientos realizados.

Antes de imprimir, revisar los filtros y las fechas.

---

## 15. Respaldo y restauración de seguridad

### Crear un respaldo

El sistema crea automáticamente un respaldo cada vez que se inicia
mediante `iniciar_bibliotech.bat`.

También puede utilizarse la opción **Crear respaldo** de la pantalla
de inicio. Esta opción guarda una copia en la carpeta `backups` y
descarga otra mediante el navegador.

Debe crearse un respaldo antes de:

- Importar alumnos, docentes o libros.
- Realizar la promoción anual.
- Efectuar cambios importantes.
- Copiar la base de datos a otra computadora.

No eliminar todos los respaldos. Conservar siempre varias copias y
guardar periódicamente una copia en un dispositivo externo.

### Restaurar un respaldo

La restauración debe realizarla solamente el administrador mediante:

`restaurar_bibliotech.bat`

Este procedimiento reemplaza la base de datos actual por una copia
anterior. Los cambios realizados después de ese respaldo se perderán.

Procedimiento:

1. Cerrar completamente BIBLIOTECH con `Ctrl + C`.
2. Ejecutar `restaurar_bibliotech.bat`.
3. Escribir `RESTAURAR` cuando el sistema solicite confirmación.
4. Arrastrar a la ventana el archivo `.sqlite3` que se desea recuperar.
5. Presionar `Enter`.
6. Esperar la verificación y la restauración.
7. Iniciar BIBLIOTECH normalmente.

Antes de reemplazar la base, el script guarda automáticamente la base
actual en la carpeta `backups` con un nombre similar a:

`db_antes_restaurar_2026-08-19_11-30-00.sqlite3`

No ejecutar la restauración mientras BIBLIOTECH esté abierto y no
seleccionar directamente el archivo activo `db.sqlite3`.

---

## 16. Promoción anual de alumnos

La promoción anual debe realizarse solamente al finalizar el año
lectivo.

Orden correcto:

1. Registrar todas las devoluciones pendientes.
2. Crear un respaldo de la base de datos.
3. Entrar en **Alumnos**.
4. Presionar **Promoción anual**.
5. Revisar las cantidades.
6. Confirmar la promoción.
7. Importar la lista oficial del nuevo año.

El sistema realizará:

- 1° pasa a 2°.
- 2° pasa a 3°.
- 3° queda como egresado e inactivo.
- Los alumnos no se eliminan.
- La sección y especialidad se conservan.

La promoción no puede confirmarse si un alumno de tercer curso
tiene un préstamo activo.

---

## 17. Recomendaciones importantes

- No modificar manualmente `db.sqlite3`.
- No borrar la carpeta `backups`.
- No prestar un libro sin registrar la operación.
- No recibir un libro sin registrar la devolución.
- No reutilizar números de inventario.
- Utilizar siempre las plantillas oficiales de Excel.
- Crear un respaldo antes de importaciones grandes.
- No confirmar la promoción anual como prueba.

---

## 18. Soporte técnico

Responsable del sistema:

**Prof. Pedro Paniagua**

Institución:

**Centro de Capacitación Técnica de Luque**