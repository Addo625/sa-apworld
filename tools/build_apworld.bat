@echo off
rem Zip th11\ into dist\th11.apworld, without tests and caches (as tools/build_apworld.sh).
rem Uses Windows' own tar.exe (bsdtar, Windows 10 and later): its zips use forward slashes, which AP needs.
rem The full path skips other tars on PATH (Git for Windows ships GNU tar, which can't write zips).
setlocal
cd /d "%~dp0.."
if not exist dist mkdir dist
if exist dist\th11.apworld del /f /q dist\th11.apworld
"%SystemRoot%\System32\tar.exe" --format zip -c -f dist\th11.apworld --exclude __pycache__ --exclude th11/test --exclude .DS_Store th11
if errorlevel 1 goto failed
echo dist\th11.apworld
exit /b 0

:failed
echo tar.exe could not build dist\th11.apworld 1>&2
exit /b 1
