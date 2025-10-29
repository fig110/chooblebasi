@echo off
call .\.venv\Scripts\activate.bat
set PYTHONPATH=%CD%
uvicorn services.agent_core.main:app --reload --host 0.0.0.0 --port 8001
