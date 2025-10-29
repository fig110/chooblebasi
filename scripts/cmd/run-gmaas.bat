@echo off
call .\.venv\Scripts\activate.bat
set PYTHONPATH=%CD%
uvicorn services.gmaas.main:app --reload --host 0.0.0.0 --port 8003
