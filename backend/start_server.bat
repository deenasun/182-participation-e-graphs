@echo off
REM Startup script for EECS 182 Post Graph API (Windows)

echo ==================================================
echo Starting EECS 182 Post Graph API Server
echo ==================================================

REM Check if virtual environment exists
if not exist ".venv" (
    echo Error: Virtual environment not found at .venv
    echo Please run: python -m venv .venv ^&^& .venv\Scripts\activate ^&^& pip install -r requirements.txt
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check if .env file exists
if not exist ".env" (
    echo Warning: .env file not found
    echo Please copy .env.example to .env and configure it
    echo.
    set /p continue="Continue anyway? (y/N) "
    if /i not "%continue%"=="y" exit /b 1
)

REM Start the server
echo Starting FastAPI server...
echo API will be available at: http://localhost:8000
echo Interactive docs at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ==================================================

python main.py
