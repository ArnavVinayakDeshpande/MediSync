@echo off
setlocal EnableDelayedExpansion

REM Get ANSI escape character
for /F %%a in ('echo prompt $E^| cmd') do set "ESC=%%a"

REM ANSI color codes
set "GREEN=%ESC%[32m"
set "RED=%ESC%[31m"
set "WHITE=%ESC%[37m"
set "RESET=%ESC%[0m"

REM Unique temp file
set "TMPFILE=%TEMP%\py_compile_%RANDOM%_%RANDOM%.tmp"

echo.
echo ============================================
echo        Python Compilation Check
echo ============================================
echo.

for /R %%F in (*.py) do (

    REM Skip anything inside .venv
    echo %%F | findstr /I /C:"\.venv\" >nul
    if errorlevel 1 (

        python -m py_compile "%%F" >nul 2>"%TMPFILE%"

        if !errorlevel! EQU 0 (
            <nul set /p="%%F "
            echo %GREEN%PASSED%RESET%
        ) else (
            <nul set /p="%%F "
            <nul set /p="%RED%FAILED%RESET% "

            if exist "%TMPFILE%" (
                type "%TMPFILE%"
            ) else (
                echo %WHITE%Unknown compilation error.%RESET%
            )
        )
    )
)

if exist "%TMPFILE%" del "%TMPFILE%"

echo.
echo ============================================
echo               Compilation Complete
echo ============================================
echo.

pause
