@echo off
set "ROOT=%~dp0.."
if not exist "%ROOT%\work" mkdir "%ROOT%\work"
cd /d "%ROOT%"
npm.cmd --prefix frontend run dev -- --hostname 127.0.0.1 --port 3000 > "%ROOT%\work\frontend.out.log" 2> "%ROOT%\work\frontend.err.log"
