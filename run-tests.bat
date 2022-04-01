@echo off

echo "Running tests from %CD%"

REM Launch the test run.
powershell -NoProfile -ExecutionPolicy Bypass -Command ". .\TestRunner.ps1; Invoke-%1Tests"

