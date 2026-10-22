@echo off
rem Build dist\th11.apworld and copy it into Archipelago's custom_worlds folder.
rem Usage: tools\windows\install_apworld.bat ["path\to\Archipelago"]
rem Without a path it uses %ProgramData%\Archipelago, where the Archipelago installer puts it.
setlocal
rem Keep a double-clicked window open; skipped when another script calls this one (TH11_NESTED).
if defined TH11_NESTED (set "pause_at_end=") else (set "pause_at_end=1")
set "rc=1"
set "ap=%~1"
if "%ap%"=="" set "ap=%ProgramData%\Archipelago"
if not exist "%ap%\custom_worlds\" goto no_ap
set "TH11_NESTED=1"
call "%~dp0build_apworld.bat" || goto end
copy /y "%~dp0..\..\dist\th11.apworld" "%ap%\custom_worlds\" >nul || goto end
echo Installed "%ap%\custom_worlds\th11.apworld"
set "rc=0"
goto end

:no_ap
echo No custom_worlds folder in "%ap%". 1>&2
echo Usage: tools\windows\install_apworld.bat "C:\path\to\Archipelago" 1>&2
goto end

:end
if defined pause_at_end (
    echo.
    echo Press any key to close...
    pause >nul
)
exit /b %rc%
