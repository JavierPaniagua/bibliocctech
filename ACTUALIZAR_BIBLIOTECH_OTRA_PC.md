# Actualización de BIBLIOTECH en otra computadora

Este manual explica cómo publicar una actualización de BIBLIOTECH y aplicarla en la computadora de la biblioteca sin perder los datos almacenados.

## Datos del proyecto

- Repositorio: `https://github.com/JavierPaniagua/bibliocctech.git`
- Rama de trabajo: `desarrollo-inventario`
- Carpeta en la PC de la biblioteca: `C:\sistemas\bibliocctech`
- Base de datos local: `db.sqlite3`
- Carpeta de respaldos: `backups`

> **Importante:** `db.sqlite3` contiene los datos reales de la biblioteca. No debe copiarse desde GitHub ni reemplazarse durante una actualización.

---

## Parte 1. Publicar la actualización desde la PC de trabajo

Realizar estos pasos únicamente después de terminar los cambios y comprobar que el sistema funciona.

### 1. Abrir PowerShell en el proyecto

Ubicarse en la carpeta donde se está desarrollando BIBLIOTECH.

Ejemplo:

```powershell
cd C:\sistemas\bibliocctech
```

### 2. Activar el entorno virtual

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Ejecutar las verificaciones

```powershell
py manage.py check
py manage.py makemigrations --check
py manage.py test
git diff --check
git status
```

Los comandos no deben mostrar errores. Antes de continuar, revisar que `db.sqlite3`, `venv` y `backups` no aparezcan entre los archivos que se subirán.

### 4. Confirmar la rama

```powershell
git branch --show-current
```

Debe mostrar:

```text
desarrollo-inventario
```

### 5. Preparar y guardar los cambios

Primero revisar:

```powershell
git status
```

Agregar solamente los archivos modificados. Ejemplo:

```powershell
git add libros/forms.py libros/views.py
```

Crear el commit:

```powershell
git commit -m "Actualizar registro y clasificacion de libros"
```

### 6. Subir la actualización a GitHub

```powershell
git push origin desarrollo-inventario
```

Confirmar el resultado:

```powershell
git status
```

Debe indicar que la rama está actualizada y que no hay cambios pendientes.

---

## Parte 2. Actualizar la PC de la biblioteca

### 1. Cerrar BIBLIOTECH

Cerrar el navegador y la ventana donde se está ejecutando el servidor. Si el servidor está activo en PowerShell, presionar:

```text
Ctrl + C
```

### 2. Abrir PowerShell en el proyecto

```powershell
cd C:\sistemas\bibliocctech
```

### 3. Activar el entorno virtual

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Comprobar el estado antes de actualizar

```powershell
git status
git branch --show-current
```

El resultado esperado es:

```text
On branch desarrollo-inventario
nothing to commit, working tree clean
```

> Si aparecen archivos modificados o la rama es diferente, detener la actualización. No ejecutar `git pull` hasta revisar esos cambios.

### 5. Crear un respaldo de la base de datos

Crear la carpeta de respaldos si todavía no existe:

```powershell
New-Item -ItemType Directory -Path backups -Force
```

Crear un respaldo con fecha y hora:

```powershell
$fechaActualizacion = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
Copy-Item db.sqlite3 "backups\db_antes_actualizacion_$fechaActualizacion.sqlite3"
```

Comprobar que el respaldo fue creado:

```powershell
Get-ChildItem backups | Sort-Object LastWriteTime -Descending | Select-Object -First 3
```

### 6. Descargar la versión nueva

```powershell
git switch desarrollo-inventario
git pull origin desarrollo-inventario
```

### 7. Actualizar las dependencias

```powershell
py -m pip install -r requirements.txt
```

### 8. Aplicar las migraciones publicadas

```powershell
py manage.py migrate
```

Este comando conserva los registros existentes y aplica únicamente las migraciones pendientes.

### 9. Verificar el sistema actualizado

```powershell
py manage.py check
py manage.py makemigrations --check
py manage.py test
```

No iniciar el uso diario si alguno de estos comandos muestra errores.

### 10. Iniciar BIBLIOTECH

Usar el archivo de inicio habitual:

```powershell
.\iniciar_bibliotech.bat
```

Si fuera necesario, también puede iniciarse manualmente:

```powershell
py manage.py runserver
```

---

## Parte 3. Pruebas después de actualizar

Realizar estas comprobaciones antes de entregar nuevamente el sistema a la bibliotecaria:

- Iniciar sesión.
- Abrir el listado de alumnos.
- Abrir el listado de docentes.
- Abrir y buscar libros existentes.
- Comprobar el menú de clasificación Dewey.
- Buscar por inventario BIBLIOTECH y por código existente.
- Registrar un libro de prueba solamente si la actualización ya está terminada.
- Registrar y devolver un préstamo de prueba.
- Crear un nuevo respaldo desde el sistema.
- Cerrar sesión.

## Parte 4. Comprobación final

```powershell
git status
git log -1 --oneline
```

`git status` debe mostrar:

```text
nothing to commit, working tree clean
```

El último commit debe coincidir con la actualización publicada desde la PC de trabajo.

---

## Problemas frecuentes

### Git informa que existen cambios locales

No ejecutar comandos para borrar o descartar los cambios. Copiar el resultado completo de:

```powershell
git status
git diff
```

y revisarlo antes de continuar.

### No se puede activar el entorno virtual

Ejecutar temporalmente:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### Aparece un error de migraciones

No eliminar `db.sqlite3` ni archivos de migración. Guardar el mensaje completo y revisar primero:

```powershell
py manage.py showmigrations
py manage.py check
```

### La actualización no se ve en el navegador

Actualizar la página con:

```text
Ctrl + Shift + R
```

### El sistema no inicia después de actualizar

Ejecutar:

```powershell
py manage.py check
py manage.py migrate
py manage.py runserver
```

Conservar el mensaje de error completo para diagnosticarlo.

---

## Reglas de seguridad

1. Crear siempre un respaldo antes de actualizar.
2. No reemplazar ni subir `db.sqlite3` a GitHub.
3. No subir las carpetas `venv` ni `backups`.
4. No ejecutar `git pull` si `git status` muestra cambios locales.
5. No eliminar migraciones para solucionar errores.
6. No usar `git reset --hard` ni comandos destructivos.
7. Probar el sistema antes de permitir su uso diario.

---

**Sistema:** BIBLIOTECH  
**Institución:** Biblioteca Escolar CCTL  
**Responsable:** Prof. Pedro Paniagua
