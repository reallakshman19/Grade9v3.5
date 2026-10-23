@echo off
setlocal
set "PAGE=%~dp0index.html"
echo Launching G9O5-2a Seven-Question Diagnostic Prototype...
echo Page: %PAGE%

:: Locate Chrome executable on Windows
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    start "" "%ProgramFiles%\Google\Chrome\Application\chrome.exe" "%PAGE%"
    exit /b 0
)
if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
    start "" "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" "%PAGE%"
    exit /b 0
)
if exist "%LocalAppData%\Google\Chrome\Application\chrome.exe" (
    start "" "%LocalAppData%\Google\Chrome\Application\chrome.exe" "%PAGE%"
    exit /b 0
)

:: Fallback if in PATH
where chrome >nul 2>&1
if %ERRORLEVEL% equ 0 (
    start "" chrome "%PAGE%"
    exit /b 0
)

:: Fallback to default browser
start "" "%PAGE%"
exit /b 0
