@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM Navigate to the script's directory
cd /d "%~dp0"

set "DO_PUSH=0"
set "COMMIT_MSG="
set "PW_ARGS="

:parse_args
if "%~1"=="" goto :args_done
if /I "%~1"=="--push" (
    set "DO_PUSH=1"
    REM Check if next parameter is a custom commit message (not starting with -)
    if not "%~2"=="" (
        set "NEXT_PARAM=%~2"
        if not "!NEXT_PARAM:~0,1!"=="-" (
            set "COMMIT_MSG=%~2"
            shift
        )
    )
    shift
    goto :parse_args
)
set "PW_ARGS=!PW_ARGS! %1"
shift
goto :parse_args

:args_done

if not defined COMMIT_MSG (
    set "COMMIT_MSG=Auto Push: tests passed successfully"
)

echo ========================================================
echo Running Playwright Test Suite...
if "!DO_PUSH!"=="1" (
    echo Mode: Run tests and PUSH on success
) else (
    echo Mode: Run tests only [pass --push to commit and push]
)
echo ========================================================

REM Run the tests using Playwright
call npx playwright test !PW_ARGS!
set TEST_EXIT_CODE=%ERRORLEVEL%

if not "%TEST_EXIT_CODE%"=="0" (
    echo.
    echo ========================================================
    echo [ERROR] Tests failed with exit code %TEST_EXIT_CODE%.
    echo Changes will NOT be committed or pushed.
    echo ========================================================
    exit /b %TEST_EXIT_CODE%
)

echo.
echo ========================================================
echo [SUCCESS] All tests passed.
echo ========================================================

if not "!DO_PUSH!"=="1" (
    echo.
    echo Not pushing. To run tests and push automatically, run:
    echo   runNpush.bat --push
    exit /b 0
)

echo.
echo Staging changes...
git add -A

REM Check if there are staged changes to commit
git diff --cached --quiet
if errorlevel 1 (
    echo Committing changes: "!COMMIT_MSG!"...
    git commit -m "!COMMIT_MSG!"
    if errorlevel 1 (
        echo [ERROR] Git commit failed.
        exit /b 1
    )
) else (
    echo No local changes to commit.
)

echo Pushing to remote...
git push
if errorlevel 1 (
    echo [ERROR] Git push failed.
    exit /b 1
)

echo.
echo ========================================================
echo [SUCCESS] Successfully tested, committed, and pushed.
echo ========================================================
exit /b 0
