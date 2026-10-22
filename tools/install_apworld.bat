@echo off
rem Build dist\th11.apworld and copy it into Archipelago's custom_worlds folder.
rem Usage: tools\install_apworld.bat ["path\to\Archipelago"]
rem Without a path it uses %ProgramData%\Archipelago, where the Archipelago installer puts it.
setlocal
set "ap=%~1"
if "%ap%"=="" set "ap=%ProgramData%\Archipelago"
if not exist "%ap%\custom_worlds\" goto no_ap
call "%~dp0build_apworld.bat" || exit /b 1
copy /y "%~dp0..\dist\th11.apworld" "%ap%\custom_worlds\" >nul || exit /b 1
echo Installed "%ap%\custom_worlds\th11.apworld"
exit /b 0

:no_ap
echo No custom_worlds folder in "%ap%". 1>&2
echo Usage: tools\install_apworld.bat "C:\path\to\Archipelago" 1>&2
exit /b 1
