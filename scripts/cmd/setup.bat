@echo off
REM === AI Shopping v3 Windows setup (CMD) ===
REM Usage: double-click or run from repo root.

REM 1) Check for Python
where python >nul 2>nul
if errorlevel 1 (
  echo Python not found in PATH. Install Python 3.x and retry.
  exit /b 1
)

REM 2) Create venv if missing
if not exist .venv (
  echo Creating virtual environment at .venv ...
  python -m venv .venv
)

REM 3) Activate venv
call .\.venv\Scripts\activate.bat

REM 4) Upgrade pip
python -m pip install --upgrade pip

REM 5) Install service requirements
pip install -r services\gateway\requirements.txt
pip install -r services\agent_core\requirements.txt
pip install -r services\workers\cart\requirements.txt
pip install -r services\gmaas\requirements.txt

REM 6) Pydantic settings (safety)
pip install pydantic-settings

echo Setup complete.
