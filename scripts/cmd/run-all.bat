@echo off
start "Gateway" cmd /k scripts\cmd\run-gateway.bat
start "Agent" cmd /k scripts\cmd\run-agent.bat
start "Cart Worker" cmd /k scripts\cmd\run-worker-cart.bat
start "GMaaS" cmd /k scripts\cmd\run-gmaas.bat
