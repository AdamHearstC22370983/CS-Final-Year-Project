@echo off

echo Activating virtual environment...
call ..\venv\Scripts\activate.bat

echo Starting Skillgap Backend...
python -m uvicorn app.main:app --reload

pause
