@echo off

echo "Running tests from %CD%"

REM Launch the test run.
powershell -NoProfile -ExecutionPolicy Bypass -Command "Import-Module .\TestRunner.psm1 -Force; Invoke-%1Tests"

