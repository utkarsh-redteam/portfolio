@echo off
setlocal EnableExtensions

REM Run Playwright tests against the local site, then push if everything passes.
cd /d "%~dp0"
set "SITE_TARGET=local"
if not defined SLOWMO set "SLOWMO=0"
if not defined WORKERS set "WORKERS=5"

REM playwright.config.ts webServer starts the local site (or reuses one on :8080).
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
