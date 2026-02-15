@echo off
REM Alpha Swarm Startup Script for Windows

echo.
echo 🚀 Starting Alpha Swarm Dashboard...
echo ==================================

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo 📚 Installing dependencies...
pip install -q -r requirements.txt

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Start Streamlit app
echo ✅ Configuration complete. Starting Streamlit...
echo 📊 Dashboard available at: http://localhost:8501
echo.

streamlit run app.py

pause
