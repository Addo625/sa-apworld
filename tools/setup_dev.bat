@echo off
rem Dev Archipelago checkout + venv for the th11 world (as tools/setup_dev.sh). Safe to re-run.
setlocal
cd /d "%~dp0.."
set /p tag=<tools\AP_VERSION
if not exist .ap git clone --depth 1 --branch %tag% https://github.com/ArchipelagoMW/Archipelago .ap || exit /b 1
rem Python 3.12 through the launcher when it has it, else the python on PATH.
if not exist .venv py -3.12 -m venv .venv 2>nul || python -m venv .venv || exit /b 1
.venv\Scripts\python -m pip install -q -r .ap\requirements.txt pytest || exit /b 1
rem A junction (no admin rights needed) where the .sh makes a symlink.
if exist .ap\worlds\th11 rmdir .ap\worlds\th11
mklink /j .ap\worlds\th11 "%CD%\th11" >nul || exit /b 1
echo Dev setup ready: .ap (Archipelago %tag%) and .venv
