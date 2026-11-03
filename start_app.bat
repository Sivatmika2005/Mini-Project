@echo off
setlocal
cd /d "%~dp0"

echo =========================================================
echo   Starting AI Mental Wellness Companion (React + FastAPI)
echo =========================================================
echo.

echo [1/2] Starting Python FastAPI Backend on http://localhost:8001 ...
start "AI Wellness - Backend" /min "%~dp0.venv\Scripts\python.exe" -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload

echo [2/2] Starting React Vite Frontend on http://localhost:5173 ...
cd /d "%~dp0frontend"
start "AI Wellness - Frontend" cmd /c "npm run dev"

echo.
echo =========================================================
echo   App is running!
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8001
echo =========================================================
echo.
ping 127.0.0.1 -n 3 >nul
start http://localhost:5173
