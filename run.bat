@echo off
setlocal enabledelayedexpansion
rem Ensure this file is saved with ANSI/Shift-JIS encoding

rem Initialize environment
set "VENV_PATH=.\env"
set "PYTHON_CMD=python"
set "PIP_CMD=pip"
set "LATEST_PIP_VERSION=24.3.1"
set "DEFAULT_SCRIPT=src\main.py"
set "SRC_DIR=src"

rem Default environment
set "APP_ENV=development"
set "SCRIPT_TO_RUN=%DEFAULT_SCRIPT%"

rem Parse arguments
set "MODE="
set "ENV_ARG="

rem Remove leading backslash from script path if present
if "%~1" neq "" (
    set "ARG1=%~1"
    if "!ARG1:~0,1!"=="\" set "ARG1=!ARG1:~1!"

    rem Check for test mode
    for %%A in (%*) do (
        if "%%A"=="--test" (
            set "MODE=test"
        ) else if "%%A"=="--env" (
            set "MODE=env"
        ) else if defined MODE (
            if "!MODE!"=="env" set "ENV_ARG=%%A"
        ) else (
            set "SCRIPT_PATH=%%A"
            if "!SCRIPT_PATH:~0,1!"=="\" set "SCRIPT_PATH=!SCRIPT_PATH:~1!"
            set "SCRIPT_TO_RUN=!SCRIPT_PATH!"
        )
    )
)

rem Create virtual environment if it doesn't exist
if not exist "%VENV_PATH%\Scripts\activate.bat" (
    echo Creating virtual environment...
    %PYTHON_CMD% -m venv %VENV_PATH%
    if errorlevel 1 (
        echo Error: Failed to create virtual environment.
        pause
        exit /b 1
    )
)

rem Activate virtual environment
call %VENV_PATH%\Scripts\activate
if errorlevel 1 (
    echo Error: Failed to activate virtual environment.
    pause
    exit /b 1
)

rem Silently update pip if needed
%PIP_CMD% install --quiet --upgrade pip==%LATEST_PIP_VERSION% >nul 2>nul

rem Check requirements.txt
if not exist requirements.txt (
    echo Error: requirements.txt not found.
    pause
    exit /b 1
)

rem Calculate hash
for /f "skip=1 delims=" %%a in ('certutil -hashfile requirements.txt SHA256') do if not defined CURRENT_HASH set "CURRENT_HASH=%%a"

rem Read stored hash
if exist .req_hash (
    set /p STORED_HASH=<.req_hash
) else (
    set "STORED_HASH="
)

rem Install requirements if needed
if not "%CURRENT_HASH%"=="%STORED_HASH%" (
    echo Installing packages...
    %PIP_CMD% install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install packages.
        pause
        exit /b 1
    )
    echo %CURRENT_HASH%>.req_hash
)

rem Process mode and run script
if defined MODE (
    if "%MODE%"=="env" (
        if "%ENV_ARG%"=="" (
            echo Error: Missing environment argument. Use --env [dev|prod|test].
            exit /b 1
        )
        set "APP_ENV=%ENV_ARG%"
        echo [LOG] Environment set to %APP_ENV%.
    ) else if "%MODE%"=="test" (
        set "APP_ENV=test"
        echo [LOG] Running test script: %SCRIPT_TO_RUN%
        if exist "%SCRIPT_TO_RUN%" (
            %PYTHON_CMD% "%SCRIPT_TO_RUN%"
            if errorlevel 1 (
                echo Error: Test execution failed.
                pause
                exit /b 1
            )
        ) else (
            echo Error: Test script not found at: %SCRIPT_TO_RUN%
            echo Current directory: %CD%
            dir "%SCRIPT_TO_RUN%" 2>nul
            pause
            exit /b 1
        )
        goto :END
    )
)

rem Check if script exists
if exist "%SCRIPT_TO_RUN%" (
    echo [LOG] Running script in %APP_ENV% environment...
    %PYTHON_CMD% "%SCRIPT_TO_RUN%"
) else (
    echo Error: Script not found - %SCRIPT_TO_RUN%
    pause
    exit /b 1
)

if errorlevel 1 (
    echo Error: Failed to run %SCRIPT_TO_RUN%
    pause
    exit /b 1
)

:END
endlocal