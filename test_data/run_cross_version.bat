@echo off
REM Generate test data across ALL installed After Effects versions.
REM Creates separate output folders per AE version for comparison testing.

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:\=/%"
set "FOUND=0"

for %%V in (2024 2025 2026) do (
    set "AE_PATH=C:\Program Files\Adobe\Adobe After Effects %%V\Support Files\AfterFX.exe"
    if exist "!AE_PATH!" (
        set /a FOUND+=1
        echo.
        echo ============================================================
        echo  Generating test data with After Effects %%V
        echo ============================================================
        echo.

        REM Run each generator individually for this AE version
        for %%F in ("%SCRIPT_DIR%generators\*.jsx") do (
            echo   Running: %%~nxF
            "!AE_PATH!" -s "$.evalFile('%%F')"
        )

        REM Rename output folder to include version
        if exist "%SCRIPT_DIR%output" (
            echo   Copying results to output_AE%%V...
            xcopy /E /I /Y "%SCRIPT_DIR:\=/%output" "%SCRIPT_DIR:\=/%output_AE%%V" >nul 2>&1
        )
    ) else (
        echo [SKIP] After Effects %%V not found
    )
)

if %FOUND%==0 (
    echo ERROR: No After Effects installations found.
    exit /b 1
)

echo.
echo ============================================================
echo  Complete. Generated test data for %FOUND% AE version(s).
echo  Check test_data\output_AE20XX\ folders for version-specific results.
echo ============================================================
