@echo off
title EstateOps ERP/CRM Launcher
color 0f

echo =======================================================================
echo               EstateOps ERP/CRM - Launcher ^& Installer
echo =======================================================================
echo.

:: Initialize command variable
set PY_CMD=

:: 1. Check if 'python' is in PATH
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PY_CMD=python
    goto python_found
)

:: 2. Check in Local AppData directories (default Windows installation path)
if exist "%LocalAppData%\Programs\Python" (
    for /d %%d in ("%LocalAppData%\Programs\Python\Python*") do (
        if exist "%%d\python.exe" (
            set PY_CMD="%%d\python.exe"
            goto python_found
        )
    )
)

:: 3. Check in Program Files
if exist "%ProgramFiles%\Python" (
    for /d %%d in ("%ProgramFiles%\Python\Python*") do (
        if exist "%%d\python.exe" (
            set PY_CMD="%%d\python.exe"
            goto python_found
        )
    )
)

:: If python is not found, prompt to download
echo [CRITICAL ERROR] Python was not found on your system!
echo.
echo 1. Opening the official Python download page in your web browser...
echo 2. Please download and install Python (Python 3.12 recommended).
echo 3. IMPORTANT: Make sure to check "Add Python to PATH" during installation.
echo.
start https://www.python.org/downloads/
pause
exit /b 1

:python_found
echo [SUCCESS] Python detected. Using: %PY_CMD%
echo.

:: Check if virtual environment folder exists, if not create it
if not exist "venv" (
    echo [INFO] Creating Python virtual environment (venv)...
    %PY_CMD% -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
)

:: Activate the virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate

:: Install/Upgrade dependencies
echo [INFO] Installing required libraries from requirements.txt...
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)

:: Check database and run migrations
echo [INFO] Checking database migrations...
python manage.py migrate

:: Seed initial demo data
echo [INFO] Seeding initial demonstration data...
python manage.py seed_demo

echo.
echo =======================================================================
echo [SUCCESS] Server setup is complete!
echo.
echo Opening browser to: http://127.0.0.1:8000/
echo =======================================================================
echo.

:: Auto-launch browser to the project URL
start http://127.0.0.1:8000/

:: Start the Django development server
python manage.py runserver

pause
