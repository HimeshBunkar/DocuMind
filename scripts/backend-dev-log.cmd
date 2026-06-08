@echo off
set "ROOT=%~dp0.."
if not exist "%ROOT%\work" mkdir "%ROOT%\work"
cd /d "%ROOT%\backend"
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 > "%ROOT%\work\backend.out.log" 2> "%ROOT%\work\backend.err.log"
