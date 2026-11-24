@echo off
title Intelligent Water Distribution System - Server
echo =====================================================================
echo       INTELLIGENT WATER DISTRIBUTION SYSTEM (IWDS) SERVER
echo =====================================================================
echo.

cd /d "%~dp0backend"

REM Find python
where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set PY=python
    goto RUN
)

REM Check WindowsApps Python 3.13
if exist "C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\python3.13.exe" (
    set "PY=C:\Program Files\WindowsApps\PythonSoftwareFoundation.Python.3.13_3.13.3824.0_x64__qbz5n2kfra8p0\python3.13.exe"
    goto RUN
)

set PY=python

:RUN
echo [1/3] Applying Database Migrations...
"%PY%" manage.py migrate --noinput

echo [2/3] Seeding Initial Operational Data...
"%PY%" seed_data.py

echo [3/3] Starting Django REST Web Server on http://127.0.0.1:8000/ ...
echo.
echo =====================================================================
echo   Default Credentials:
echo   - Citizen Portal : ramya@gmail.com / ramya123
echo   - Admin Control  : admin@water.gov / admin123
echo =====================================================================
echo.

"%PY%" manage.py runserver 0.0.0.0:8000
pause
