@echo off
cd /d "%~dp0"
py -3 -m national.restore
if errorlevel 1 pause
py -3 -m national.serve --open
pause
