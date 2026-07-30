@echo off
REM Generate all test data .aep files using After Effects.
REM Detects installed AE versions and runs against the first found.

setlocal

set "SCRIPT_PATH=%~dp0run_all.jsx"
set "SCRIPT_PATH=%SCRIPT_PATH:\=/%"

REM Search for AfterFX.exe in common install paths
set "AE_EXE="

for %%V in (2026 2025 2024) do (
    if exist "C:\Program Files\Adobe\Adobe After Effects %%V\Support Files\AfterFX.exe" (
        set "AE_EXE=C:\Program Files\Adobe\Adobe After Effects %%V\Support Files\AfterFX.exe"
        echo Found After Effects %%V
        goto :found
    )
)

:found
if "%AE_EXE%"=="" (
    echo ERROR: Could not find After Effects installation.
    echo Manually specify: AfterFX.exe -s "$.evalFile('%SCRIPT_PATH%')"
    exit /b 1
)

echo Running test data generation...
echo AE Path: %AE_EXE%
echo Script: %SCRIPT_PATH%
echo.

"%AE_EXE%" -s "$.evalFile('%SCRIPT_PATH%')"

echo.
echo Done. Check test_data\output\ for generated .aep files.
echo Check test_data\output\generation_log.txt for results.
