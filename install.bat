@echo off
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo python aint installed install first 
    pause
    exit /b
)

echo installing packages
pip install raducord
pip install tls_client
pip install bs4

echo Launching main.py
python main.py

pause
