@echo off
setlocal
cd /d "%~dp0\.."

set /p tag=<tools\AP_VERSION

if not exist .ap git clone --depth 1 --branch %tag% https://github.com/ArchipelagoMW/Archipelago .ap
if not exist .venv python -m venv .venv
.venv\Scripts\pip install -q -r .ap\requirements.txt pytest

if exist .ap\worlds\th11 rmdir .ap\worlds\th11
mklink /j .ap\worlds\th11 th11