@echo off
title BIBLIOTECH - Biblioteca Escolar CCTL
color 1F

cd /d "%~dp0"

echo.
echo ==========================================
echo          BIBLIOTECH - CCTL
echo ==========================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo ERROR: No se encontro el entorno virtual.
    echo Ruta esperada: venv\Scripts\python.exe
    echo.
    pause
    exit /b 1
)

if not exist "manage.py" (
    echo ERROR: No se encontro manage.py.
    echo.
    pause
    exit /b 1
)

if not exist "backups" (
    mkdir "backups"
)

if exist "db.sqlite3" (
    for /f %%F in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HH-mm-ss"') do set FECHA=%%F

    echo Creando respaldo de seguridad...

    copy /Y "db.sqlite3" "backups\db_inicio_%FECHA%.sqlite3" >nul

    if errorlevel 1 (
        echo ADVERTENCIA: No se pudo crear el respaldo.
        echo El sistema continuara iniciando.
    ) else (
        echo Respaldo creado correctamente.
    )
)

echo.
echo Verificando migraciones...

"venv\Scripts\python.exe" manage.py migrate --noinput

if errorlevel 1 (
    echo.
    echo ERROR: No se pudieron aplicar las migraciones.
    pause
    exit /b 1
)

echo.
echo Verificando el sistema...

"venv\Scripts\python.exe" manage.py check

if errorlevel 1 (
    echo.
    echo ERROR: Django encontro problemas.
    pause
    exit /b 1
)

echo.
echo Iniciando BIBLIOTECH...
echo.
echo Para cerrar el sistema presione CTRL+C.
echo No cierre esta ventana mientras utiliza BIBLIOTECH.
echo.

start "" powershell -WindowStyle Hidden -Command "Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:8000/'"

"venv\Scripts\python.exe" manage.py runserver 127.0.0.1:8000

echo.
echo BIBLIOTECH fue detenido.
pause