@echo off
rem Zip th11\ into dist\th11.apworld, without tests and caches (as tools/mac/build_apworld.sh).
rem Uses Windows' own tar.exe (bsdtar, Windows 10 and later): its zips use forward slashes, which AP needs.
rem The full path skips other tars on PATH (Git for Windows ships GNU tar, which can't write zips).
setlocal
rem Keep a double-clicked window open; skipped when another script calls this one (TH11_NESTED).
if defined TH11_NESTED (set "pause_at_end=") else (set "pause_at_end=1")
set "rc=1"
cd /d "%~dp0..\.."
if not exist dist mkdir dist
if exist dist\th11.apworld del /f /q dist\th11.apworld
"%SystemRoot%\System32\tar.exe" --format zip -c -f dist\th11.apworld --exclude __pycache__ --exclude th11/test --exclude .DS_Store th11
if errorlevel 1 goto failed
echo dist\th11.apworld
set "rc=0"
goto end

:failed
echo tar.exe could not build dist\th11.apworld 1>&2
goto end

:end
if defined pause_at_end (
    echo.
    echo Press any key to close...
    pause >nul
)
exit /b %rc%
