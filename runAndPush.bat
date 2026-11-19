@echo off
setlocal EnableExtensions

REM Run Playwright tests against the local site; with --push, commit and push if everything passes.
REM Usage: runAndPush.bat [--push] [--headed] [playwright args]
REM Example: runAndPush.bat --headed --project=chromium -g "CV download link"
cd /d "%~dp0"
set "SITE_TARGET=local"
if not defined SLOWMO set "SLOWMO=0"
if not defined WORKERS set "WORKERS=5"

REM Pull out --push; everything else is passed through to Playwright.
set "DO_PUSH=0"
set "PW_ARGS="
:parse_args
if "%~1"=="" goto :args_done
if /I "%~1"=="--push" goto :flag_push
set PW_ARGS=%PW_ARGS% %1
shift
goto :parse_args
:flag_push
set "DO_PUSH=1"
shift
goto :parse_args
:args_done

REM playwright.config.ts webServer starts the local site (or reuses one on :8080).
echo Running Playwright tests with SITE_TARGET=%SITE_TARGET% (SLOWMO=%SLOWMO%ms, WORKERS=%WORKERS%, PUSH=%DO_PUSH%)...
call npx playwright test --workers=%WORKERS%%PW_ARGS%
if errorlevel 1 (
    echo.
    echo Tests failed - not pushing.
    exit /b 1
)

echo.
if "%DO_PUSH%"=="1" goto :push
echo All tests passed - not pushing. Re-run with --push to commit and push.
exit /b 0

:push
echo All tests passed - staging and pushing changes...
git add -A
git diff --cached --quiet
if errorlevel 1 (
    git commit -m "chore: automated commit after passing tests"
    if errorlevel 1 exit /b 1
) else (
    echo No changes to commit.
)

git push
if errorlevel 1 exit /b 1
exit /b 0
