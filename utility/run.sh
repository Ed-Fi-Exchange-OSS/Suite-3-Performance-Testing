source /c/virtualenv/EDFI_PERFORMANCE/Scripts/activate
export PYTHONWARNINGS=ignore:DEPRECATION
pip install -r requirements.txt
python generate.py "$@"