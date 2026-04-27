@echo off
REM demo_runner.bat - Automated demo runner for Windows

echo ============================================================
echo CRUZRTWIN ASEAN - Demo Environment Stabilization
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    pause
    exit /b 1
)

REM Check services
echo [INFO] Checking services...
python demo\reset_demo.py

if errorlevel 1 (
    echo [ERROR] Services not healthy!
    echo.
    echo Backup plan:
    python demo\backup_plan.py
    pause
    exit /b 1
)

echo.
echo [INFO] Starting full demo...
python demo\run_demo.py

if errorlevel 1 (
    echo [ERROR] Demo failed!
    echo Running backup plan...
    python demo\backup_plan.py
) else (
    echo.
    echo ============================================================
    echo DEMO SUCCESSFUL!
    echo ============================================================
)

pause