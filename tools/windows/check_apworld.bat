@echo off
rem Prove AP generates from dist\th11.apworld, not the dev junction (as tools/mac/check_apworld.sh).
rem Needs tools\windows\setup_dev.bat first. Python runs by a relative path: for /f mangles quoted paths.
setlocal
rem Keep a double-clicked window open; skipped when another script calls this one (TH11_NESTED).
if defined TH11_NESTED (set "pause_at_end=") else (set "pause_at_end=1")
set "rc=1"
cd /d "%~dp0..\.."
set "root=%CD%"
if not exist .venv\Scripts\python.exe goto no_venv
for /f "usebackq delims=" %%i in (`.venv\Scripts\python -c "import json; print(json.load(open('th11/archipelago.json'))['game'])"`) do set "game=%%i"
set "TH11_NESTED=1"
call "%~dp0build_apworld.bat" || goto end
set "tmp_dir=%TEMP%\th11_check_%RANDOM%"
mkdir "%tmp_dir%"

rem AP refuses a game registered twice, so the junction must go.
if exist .ap\worlds\th11 rmdir .ap\worlds\th11
copy /y dist\th11.apworld .ap\custom_worlds\ >nul
rem Its own players dir, so only this YAML is generated.
copy /y examples\th11.yaml "%tmp_dir%\" >nul
type nul > "%tmp_dir%\marker"

cd .ap
rem Skip ModuleUpdate: it prompts to pip-install other worlds' requirements.
set SKIP_REQUIREMENTS_UPDATE=1
..\.venv\Scripts\python Generate.py --player_files_path "%tmp_dir%" <nul
if errorlevel 1 goto generate_failed

set "file="
for /f "usebackq delims=" %%i in (`..\.venv\Scripts\python -c "import sys, worlds; print(worlds.AutoWorld.AutoWorldRegister.world_types[sys.argv[1]].__file__)" "%game%"`) do set "file=%%i"
echo %file% | findstr /c:"custom_worlds" >nul
if errorlevel 1 goto wrong_world
echo apworld loaded from custom_worlds: %file%

set "out="
for /f "usebackq delims=" %%i in (`..\.venv\Scripts\python -c "import os, glob; m = os.path.getmtime(r'%tmp_dir%\marker'); print(next((f for f in glob.glob('output/AP_*.zip') if os.path.getmtime(f) > m), ''))"`) do set "out=%%i"
if "%out%"=="" goto no_output
echo .ap\%out%
set "rc=0"
goto restore

:no_venv
echo No .venv: run tools\windows\setup_dev.bat first 1>&2
goto end

:generate_failed
echo Generate.py failed 1>&2
goto restore

:wrong_world
echo th11 world loaded from %file%, not custom_worlds 1>&2
goto restore

:no_output
echo no new AP_*.zip in .ap\output 1>&2
goto restore

:restore
cd /d "%root%"
if exist .ap\worlds\th11 rmdir .ap\worlds\th11
mklink /j .ap\worlds\th11 "%root%\th11" >nul
if exist .ap\custom_worlds\th11.apworld del /f /q .ap\custom_worlds\th11.apworld
if exist "%tmp_dir%" rmdir /s /q "%tmp_dir%"
goto end

:end
if defined pause_at_end (
    echo.
    echo Press any key to close...
    pause >nul
)
exit /b %rc%
