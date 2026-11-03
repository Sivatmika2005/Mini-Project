@echo off
setlocal enabledelayedexpansion
echo =========================================================
echo       Starting AI Mental Wellness Companion...
echo =========================================================
echo.

cd /d "%~dp0"

if exist ".venv\Scripts\activate.bat" goto ACTIVATE

echo [WARNING] Python 3.12 virtual environment (.venv) not found.
echo Running installer first...
call "%~dp0install.bat"

if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Environment setup failed. Cannot start application.
    pause
    exit /b 1
)

:ACTIVATE
echo [INFO] Activating Python 3.12 Virtual Environment...
call .venv\Scripts\activate.bat

echo [INFO] Launching Streamlit App on http://localhost:8501 ...
python -m streamlit run app.py

