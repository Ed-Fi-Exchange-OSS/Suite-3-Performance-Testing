call C:\virtualenv\EDFI_PERFORMANCE\Scripts\activate.bat
SET PYTHONWARNINGS=ignore:DEPRECATION
pip install -r requirements.txt
python generate.py %*
call deactivate