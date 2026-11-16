@echo off
setlocal EnableExtensions

REM Run Playwright tests against the local site, then push if everything passes.
cd /d "%~dp0"
set "SITE_TARGET=local"
set "LOCAL_PORT=8080"
set "LOCAL_URL=http://localhost:%LOCAL_PORT%/"
if not defined SLOWMO set "SLOWMO=0"
if not defined WORKERS set "WORKERS=5"

REM Start a local static server from the project root if the site is not already up.
call :site_up
if not errorlevel 1 (
    echo Local site already running at %LOCAL_URL%
    goto :run_tests
)

echo Local site not running - starting server at %LOCAL_URL% ...
start "portfolio-local-server" /min /D "%~dp0." python -m http.server %LOCAL_PORT%

set /a "WAIT_SECS=0"
:wait_for_site
call :site_up
if not errorlevel 1 goto :site_ready
set /a "WAIT_SECS+=1"
if %WAIT_SECS% GEQ 30 (
    echo Local server did not come up within 30 seconds.
    exit /b 1
)
ping -n 2 127.0.0.1 >nul
goto :wait_for_site

:site_ready
echo Local site is up.

:run_tests
echo Running Playwright tests with SITE_TARGET=%SITE_TARGET% (SLOWMO=%SLOWMO%ms, WORKERS=%WORKERS%)...
call npx playwright test --headed --workers=%WORKERS% %*
REM Example: run-tests-headed.bat --project=chromium -g "CV download link"
if errorlevel 1 (
    echo.
    echo Tests failed - not pushing.
    exit /b 1
)

echo.
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

:site_up
curl.exe -s -o nul -f "%LOCAL_URL%"
exit /b %errorlevel%
