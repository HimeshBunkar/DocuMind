@echo off
set "ROOT=%~dp0.."
start "DocuMind API" /B "%ROOT%\scripts\backend-dev-log.cmd"
start "DocuMind Web" /B "%ROOT%\scripts\frontend-dev-log.cmd"
echo DocuMind API: http://127.0.0.1:8000
echo DocuMind Web: http://127.0.0.1:3000
echo Logs: %ROOT%\work
