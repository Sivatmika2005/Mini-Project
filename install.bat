@echo off
setlocal enabledelayedexpansion
echo =========================================================
echo       AI Mental Wellness Companion - Installer
echo =========================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Python installation...

set "PY_CMD="
py -3.12 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PY_CMD=py -3.12"
) else if exist "%LocalAppData%\Programs\Python\Python312\python.exe" (
    set "PY_CMD="%LocalAppData%\Programs\Python\Python312\python.exe""
) else if exist "C:\Program Files\Python312\python.exe" (
    set "PY_CMD="C:\Program Files\Python312\python.exe""
) else (
    python --version >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        set "PY_CMD=python"
    )
)

if "%PY_CMD%"=="" (
    echo [ERROR] Python 3.12 was not found.
    echo Please make sure Python 3.12 is installed on your Windows system.
    pause
    exit /b 1
)

echo [INFO] Found Python engine: %PY_CMD%

echo [2/3] Setting up Python Virtual Environment (.venv)...
if exist ".venv" (
    echo [INFO] Existing .venv found. Re-creating clean virtual environment...
    rmdir /s /q ".venv"
)

%PY_CMD% -m venv .venv
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)

echo [3/3] Upgrading pip ^& installing dependencies...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Package installation failed.
    pause
    exit /b 1
)

echo.
echo =========================================================
echo   Installation Completed Successfully!
echo   You can now launch the app anytime using start.bat
echo =========================================================
echo.

