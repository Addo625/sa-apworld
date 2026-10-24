@echo off
rem Dev Archipelago checkout + venv for the th11 world (as tools/mac/setup_dev.sh). Safe to re-run.
setlocal
rem Keep a double-clicked window open; skipped when another script calls this one (TH11_NESTED).
if defined TH11_NESTED (set "pause_at_end=") else (set "pause_at_end=1")
set "rc=1"
cd /d "%~dp0..\.."
set /p tag=<tools\AP_VERSION
if not exist .ap git clone --depth 1 --branch %tag% https://github.com/ArchipelagoMW/Archipelago .ap || goto end
rem Python 3.12 through the launcher when it has it, else the python on PATH.
if not exist .venv py -3.12 -m venv .venv 2>nul || python -m venv .venv || goto end
.venv\Scripts\python -m pip install -q -r .ap\requirements.txt pytest || goto end
rem A junction (no admin rights needed) where the .sh makes a symlink.
if exist .ap\worlds\th11 rmdir .ap\worlds\th11
mklink /j .ap\worlds\th11 "%CD%\th11" >nul || goto end
echo Dev setup ready: .ap (Archipelago %tag%) and .venv
set "rc=0"
goto end

:end
if defined pause_at_end (
    echo.
    echo Press any key to close...
    pause >nul
)
exit /b %rc%
