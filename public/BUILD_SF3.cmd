@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Build-SF3.ps1" -Interactive
if errorlevel 1 (
  echo.
  echo SF3 local build failed. Review the message above.
  pause
  exit /b 1
)
echo.
echo SF3 local build completed.
pause
