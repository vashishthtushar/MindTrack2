@echo off
REM MindTrack Setup and Run Script for Anaconda (Windows)

echo 🧠 Setting up MindTrack...

cd /d "%~dp0"

REM Create conda environment
echo Creating conda environment 'mindtrack'...
call conda create -n mindtrack python=3.10 -y

REM Activate environment
echo Activating mindtrack environment...
call conda activate mindtrack

REM Install backend dependencies
echo Installing backend dependencies...
cd backend
pip install -r requirements.txt
cd ..

REM Install frontend dependencies
echo Installing frontend dependencies...
cd frontend
pip install -r requirements.txt
cd ..

echo.
echo ✅ Setup complete!
echo.
echo To run the application:
echo 1. Start backend: cd backend && python app/main.py
echo 2. Start frontend: cd frontend && streamlit run MindTracker_frontend/app.py
echo.

pause

