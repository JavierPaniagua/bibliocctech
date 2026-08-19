# Instalación de BIBLIOTECH en otra computadora

## Biblioteca Escolar CCTL

Esta guía explica cómo instalar BIBLIOTECH en una computadora nueva,
recuperar la base de datos existente y crear el acceso directo para la
bibliotecaria.

## 1. Requisitos previos

La computadora debe tener instalados:

- Windows 10 u 11.
- Git.
- Python 3.14.
- Conexión a Internet solamente durante la clonación e instalación inicial.

Para comprobar las instalaciones, abrir PowerShell y ejecutar:

```powershell
git --version
py --version
```

Python debe mostrar una versión 3.14.x.

## 2. Preparar la base de datos en la computadora anterior

Antes de copiar la base de datos:

1. Cerrar BIBLIOTECH con `Ctrl + C`.
2. Confirmar que la ventana del servidor se haya cerrado.
3. Abrir la carpeta del proyecto:

```text
C:\sistemas\bibliocctech
```

4. Copiar al pendrive el archivo:

```text
db.sqlite3
```

También se recomienda copiar el respaldo más reciente de la carpeta:

```text
C:\sistemas\bibliocctech\backups
```

No copiar `db.sqlite3` mientras BIBLIOTECH esté funcionando.

## 3. Crear la carpeta de sistemas

En la computadora nueva, abrir PowerShell como usuario normal y ejecutar:

```powershell
New-Item -ItemType Directory -Path C:\sistemas -Force
Set-Location C:\sistemas
```

## 4. Clonar el repositorio

Ejecutar:

```powershell
git clone --branch desarrollo-inventario --single-branch https://github.com/JavierPaniagua/bibliocctech.git
Set-Location C:\sistemas\bibliocctech
```

Comprobar la rama y el último commit:

```powershell
git branch --show-current
git log -1 --oneline
```

La rama debe ser:

```text
desarrollo-inventario
```

## 5. Crear el entorno virtual

Dentro de `C:\sistemas\bibliocctech`, ejecutar:

```powershell
py -3.14 -m venv venv
```

Activar el entorno:

```powershell
venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación, ejecutar una sola vez:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Aceptar el cambio y volver a ejecutar:

```powershell
venv\Scripts\Activate.ps1
```

## 6. Instalar las dependencias

Con el entorno virtual activo, ejecutar:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check
```

El último comando debe mostrar:

```text
No broken requirements found.
```

## 7. Copiar la base de datos

Antes de copiarla, BIBLIOTECH debe permanecer cerrado.

1. Conectar el pendrive.
2. Copiar `db.sqlite3` desde el pendrive.
3. Pegar el archivo directamente en:

```text
C:\sistemas\bibliocctech\db.sqlite3
```

El archivo debe quedar al mismo nivel que `manage.py`.

No colocarlo dentro de `config`, `backups` ni ninguna aplicación Django.

## 8. Verificar la instalación

En PowerShell, dentro del proyecto y con el entorno activo, ejecutar:

```powershell
python manage.py migrate --noinput
python manage.py check
python manage.py makemigrations --check
python manage.py test
```

Resultados esperados:

- `migrate`: sin errores.
- `check`: `System check identified no issues`.
- `makemigrations --check`: `No changes detected`.
- `test`: actualmente puede indicar `NO TESTS RAN` porque el proyecto no tiene
  pruebas automatizadas.

## 9. Iniciar BIBLIOTECH

Cerrar PowerShell y abrir esta carpeta en el Explorador de archivos:

```text
C:\sistemas\bibliocctech
```

Hacer doble clic en:

```text
iniciar_bibliotech.bat
```

El iniciador debe:

1. Crear un respaldo automático.
2. Aplicar las migraciones existentes.
3. Comprobar Django.
4. Abrir `http://127.0.0.1:8000/` en el navegador.

No cerrar la ventana de BIBLIOTECH mientras se utiliza el sistema.
Para detenerlo correctamente, presionar `Ctrl + C`.

## 10. Comprobar los datos

Iniciar sesión y verificar:

- Alumnos.
- Docentes.
- Libros y ejemplares.
- Préstamos e historiales.
- Usuarios `administrador` y `Bibliotecaria`.

Si las listas están vacías, comprobar que `db.sqlite3` fue pegado en la raíz
correcta del proyecto.

## 11. Crear el acceso directo

1. Abrir `C:\sistemas\bibliocctech`.
2. Hacer clic derecho en `iniciar_bibliotech.bat`.
3. Seleccionar **Enviar a > Escritorio (crear acceso directo)**.
4. En el escritorio, hacer clic derecho sobre el acceso directo.
5. Seleccionar **Propiedades**.
6. Presionar **Cambiar icono**.
7. Buscar el archivo:

```text
C:\sistemas\bibliocctech\static\img\bibliotech.ico
```

8. Aceptar los cambios.
9. Cambiar el nombre del acceso directo a:

```text
BIBLIOTECH
```

## 12. Prueba final

Realizar esta comprobación:

1. Abrir BIBLIOTECH desde el acceso directo.
2. Iniciar sesión como bibliotecaria.
3. Abrir Alumnos, Docentes, Libros y Préstamos.
4. Confirmar que los datos anteriores estén disponibles.
5. Cerrar sesión.
6. Confirmar que una página protegida redirija al login.
7. Cerrar el servidor con `Ctrl + C`.
8. Confirmar que exista un respaldo nuevo en `backups`.

## 13. Restaurar un respaldo

La restauración debe realizarla únicamente el administrador.

1. Cerrar completamente BIBLIOTECH.
2. Ejecutar `restaurar_bibliotech.bat`.
3. Escribir `RESTAURAR` cuando se solicite.
4. Arrastrar el archivo de respaldo `.sqlite3` a la ventana.
5. Presionar `Enter` y esperar la verificación.

Antes de restaurar, el script crea una copia de emergencia de la base actual.

## 14. Actualizaciones futuras

Antes de actualizar, cerrar BIBLIOTECH y crear un respaldo. Luego ejecutar:

```powershell
Set-Location C:\sistemas\bibliocctech
git switch desarrollo-inventario
git pull origin desarrollo-inventario
venv\Scripts\python.exe -m pip install -r requirements.txt
venv\Scripts\python.exe manage.py migrate --noinput
venv\Scripts\python.exe manage.py check
```

Después, iniciar normalmente con `iniciar_bibliotech.bat`.

## 15. Archivos que no deben subirse a GitHub

No agregar al repositorio:

- `db.sqlite3`
- `venv`
- `backups`
- `.env`
- archivos con datos reales de la biblioteca

Estos elementos ya están excluidos mediante `.gitignore`.

---

Responsable del sistema: **Prof. Pedro Paniagua**  
Institución: **Centro de Capacitación Técnica de Luque (CCTL)**
