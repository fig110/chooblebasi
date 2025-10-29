@echo off
call .\.venv\Scripts\activate.bat
set PYTHONPATH=%CD%
python -m services.workers.cart.worker
