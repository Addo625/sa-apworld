@echo off
setlocal
cd /d "%~dp0\.."
set "root=%CD%"

for /f "delims=" %%i in ('.venv\Scripts\python -c "import json; print(json.load(open('th11/archipelago.json'))['game'])"') do set "game=%%i"

call tools\build_apworld.bat

set "tmp_dir=%TEMP%\ap_test_%RANDOM%"
mkdir "%tmp_dir%"

rem AP refuses a game registered twice, so the symlink must go.
if exist .ap\worlds\th11 rmdir .ap\worlds\th11
copy dist\th11.apworld .ap\custom_worlds\
copy examples\th11.yaml "%tmp_dir%\"
type nul > "%tmp_dir%\marker"

cd .ap
set SKIP_REQUIREMENTS_UPDATE=1
..\.venv\Scripts\python Generate.py --player_files_path "%tmp_dir%" <nul

for /f "delims=" %%i in ('..\.venv\Scripts\python -c "import sys, worlds; print(worlds.AutoWorld.AutoWorldRegister.world_types[sys.argv[1]].__file__)" "%game%"') do set "file=%%i"

echo %file% | findstr /c:"custom_worlds" >nul
if errorlevel 1 (
    echo th11 world loaded from %file%, not custom_worlds 1>&2
    cd ..
    call :restore
    exit /b 1
) else (
    echo apworld loaded from custom_worlds: %file%
)

for /f "delims=" %%i in ('..\.venv\Scripts\python -c "import os, glob; marker = r'%tmp_dir%\marker'; mtime = os.path.getmtime(marker); matches = [f for f in glob.glob('output/AP_*.zip') if os.path.getmtime(f) > mtime]; print(matches[0] if matches else '')"') do set "out=%%i"

if "%out%"=="" (
    echo no new AP_*.zip in .ap/output 1>&2
    cd ..
    call :restore
    exit /b 1
)

echo .ap\%out%
cd ..
call :restore
exit /b 0

:restore
if exist "%root%\.ap\worlds\th11" rmdir "%root%\.ap\worlds\th11"
mklink /j "%root%\.ap\worlds\th11" "%root%\th11"
if exist "%root%\.ap\custom_worlds\th11.apworld" del /f /q "%root%\.ap\custom_worlds\th11.apworld"
if exist "%tmp_dir%" rmdir /s /q "%tmp_dir%"
exit /b