@echo off

cd .\src\perf-test-analyis

echo "Running %1 jupyter notebook from %CD%"
echo %2>notebook_input.txt

REM Launch the notebook run.
powershell -NoProfile -ExecutionPolicy Bypass -Command "poetry run jupyter nbconvert --output-dir='.\..\..\' --to html --execute '%1 Test Analysis.ipynb' --no-input"
