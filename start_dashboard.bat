@echo off
cd /d C:\Users\vasil\Desktop\kucni_dashboard\backend
call ..\venv\Scripts\activate.bat
python -m uvicorn main:app --host 0.0.0.0 --port 8000