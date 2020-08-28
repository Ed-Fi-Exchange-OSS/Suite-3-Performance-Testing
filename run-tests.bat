@echo off

echo "Running tests from %CD%"

REM Activate the EDFI_PERFORMANCE virtual environment for the remainder of this batch script.
call C:\virtualenv\EDFI_PERFORMANCE\Scripts\activate.bat

REM Install test suite dependencies.
SET PYTHONWARNINGS=ignore:DEPRECATION
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Launch the test run.
powershell -NoProfile -ExecutionPolicy Bypass -Command ". .\TestRunner.ps1; Invoke-%1Tests"

REM Deactivate the EDFI_PERFORMANCE virtual environment.
call deactivate
