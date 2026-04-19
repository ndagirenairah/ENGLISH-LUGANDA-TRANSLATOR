@echo off
REM ============================================================================
REM ENGLISH-LUGANDA TRANSLATOR WEB APP
REM Startup Script for Windows
REM ============================================================================

echo.
echo ============================================================================
echo 🚀 ENGLISH-LUGANDA TRANSLATOR WEB APP (STARTUP)
echo ============================================================================
echo.

REM Activate virtual environment
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo ✅ Virtual environment activated
) else (
    echo ⚠️  Virtual environment not found. Using system Python.
)

echo.
echo 📱 Starting web server...
echo.

REM Start the Flask app
python app.py

echo.
echo ============================================================================
echo ⏹️  Web app stopped
echo ============================================================================
pause
