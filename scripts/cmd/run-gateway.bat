@echo off
call .\.venv\Scripts\activate.bat
set PYTHONPATH=%CD%
uvicorn services.gateway.main:app --reload --host 0.0.0.0 --port 8000
