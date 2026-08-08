@echo off
setlocal
cd /d "%~dp0"
echo Syphon Filter 3 Recompiled will download any missing build tools into this folder.
echo Downloads are pinned and SHA-256 verified. Nothing is installed system-wide.
echo WinGet, Git, pip, and Visual Studio are not required.
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0SETUP.ps1" -InstallDependencies
if errorlevel 1 (
  echo.
  echo Setup failed. Review the message above and setup.log.
  pause
  exit /b 1
)
call "%~dp0PLAY_SF3.cmd"
