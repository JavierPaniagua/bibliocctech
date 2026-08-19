@echo off
setlocal EnableExtensions DisableDelayedExpansion

title Restaurar BIBLIOTECH - Solo administrador
color 4F

cd /d "%~dp0"

echo.
echo ==============================================
echo     RESTAURACION ADMINISTRATIVA BIBLIOTECH
echo ==============================================
echo.
echo ADVERTENCIA:
echo Esta operacion reemplazara la base de datos actual.
echo Los cambios posteriores al respaldo se perderan.
echo.
echo BIBLIOTECH debe estar completamente cerrado.
echo.

if not exist "manage.py" (
    echo ERROR: No se encontro manage.py.
    echo Ejecute este archivo desde la carpeta del proyecto.
    pause
    exit /b 1
)

if not exist "venv\Scripts\python.exe" (
    echo ERROR: No se encontro el entorno virtual.
    echo Ruta esperada: venv\Scripts\python.exe
    pause
    exit /b 1
)

if not exist "db.sqlite3" (
    echo ERROR: No se encontro la base de datos actual.
    pause
    exit /b 1
)

netstat -ano | findstr /R /C:":8000 .*LISTENING" >nul

if not errorlevel 1 (
    echo ERROR: BIBLIOTECH parece estar funcionando en el puerto 8000.
    echo Cierre el sistema con CTRL+C antes de restaurar.
    pause
    exit /b 1
)

set /p CONFIRMAR=Escriba RESTAURAR para continuar: 

if /I not "%CONFIRMAR%"=="RESTAURAR" (
    echo.
    echo Operacion cancelada. No se modifico la base de datos.
    pause
    exit /b 0
)

echo.
echo Puede arrastrar el archivo de respaldo a esta ventana.
set /p RUTA_RESPALDO=Ruta completa del respaldo: 

set "RUTA_RESPALDO=%RUTA_RESPALDO:"=%"

if not defined RUTA_RESPALDO (
    echo.
    echo ERROR: No se indico ningun archivo.
    pause
    exit /b 1
)

if not exist "%RUTA_RESPALDO%" (
    echo.
    echo ERROR: El archivo indicado no existe.
    pause
    exit /b 1
)

for %%I in ("%RUTA_RESPALDO%") do set "RUTA_RESPALDO=%%~fI"
for %%I in ("db.sqlite3") do set "RUTA_ACTUAL=%%~fI"

if /I "%RUTA_RESPALDO%"=="%RUTA_ACTUAL%" (
    echo.
    echo ERROR: No puede seleccionar la base de datos actual.
    echo Seleccione un archivo ubicado en backups o en otro dispositivo.
    pause
    exit /b 1
)

echo.
echo Verificando la integridad del respaldo...

"venv\Scripts\python.exe" -c "import sqlite3, sys; conexion=sqlite3.connect(sys.argv[1]); resultado=conexion.execute('PRAGMA integrity_check').fetchone()[0]; conexion.close(); sys.exit(0 if resultado == 'ok' else 1)" "%RUTA_RESPALDO%"

if errorlevel 1 (
    echo.
    echo ERROR: El archivo seleccionado no es un respaldo SQLite valido.
    echo No se modifico la base de datos actual.
    pause
    exit /b 1
)

if not exist "backups" (
    mkdir "backups"
)

for /f %%F in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HH-mm-ss"') do set "FECHA=%%F"

set "RESPALDO_EMERGENCIA=backups\db_antes_restaurar_%FECHA%.sqlite3"

echo.
echo Creando respaldo de emergencia de la base actual...

copy /Y "db.sqlite3" "%RESPALDO_EMERGENCIA%" >nul

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo crear el respaldo de emergencia.
    echo La restauracion fue cancelada.
    pause
    exit /b 1
)

echo Respaldo de emergencia creado:
echo %RESPALDO_EMERGENCIA%
echo.
echo Restaurando la base seleccionada...

copy /Y "%RUTA_RESPALDO%" "db.sqlite3" >nul

if errorlevel 1 (
    echo.
    echo ERROR: No se pudo reemplazar la base de datos.
    echo Se intentara conservar la base anterior.
    copy /Y "%RESPALDO_EMERGENCIA%" "db.sqlite3" >nul
    pause
    exit /b 1
)

echo.
echo Aplicando migraciones existentes...

"venv\Scripts\python.exe" manage.py migrate --noinput

if errorlevel 1 (
    echo.
    echo ERROR: Fallaron las migraciones.
    echo Restaurando nuevamente la base anterior...
    copy /Y "%RESPALDO_EMERGENCIA%" "db.sqlite3" >nul
    pause
    exit /b 1
)

echo.
echo Verificando BIBLIOTECH...

"venv\Scripts\python.exe" manage.py check

if errorlevel 1 (
    echo.
    echo ERROR: Django encontro problemas.
    echo Restaurando nuevamente la base anterior...
    copy /Y "%RESPALDO_EMERGENCIA%" "db.sqlite3" >nul
    pause
    exit /b 1
)

echo.
echo ==============================================
echo       RESTAURACION COMPLETADA CORRECTAMENTE
echo ==============================================
echo.
echo Base restaurada desde:
echo %RUTA_RESPALDO%
echo.
echo Base anterior guardada en:
echo %RESPALDO_EMERGENCIA%
echo.
echo Ahora puede iniciar BIBLIOTECH normalmente.
echo.

pause
exit /b 0