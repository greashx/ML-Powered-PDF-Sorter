@echo off
:: Navigate to your project directory
cd /d "C:\Users\4mine\PycharmProjects\FileML"

:: Run the script using the Python executable INSIDE the virtual environment
:: This handles the 'activation' automatically in one line
".venv\Scripts\python.exe" organize_pdfs.py

:: Keep the window open so you can see the results/logs before closing
echo.
echo Operation Complete.
pause