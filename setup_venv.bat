:: Create virtual environments
python -m venv .venv/cnn_env
python -m venv .venv/capture_env
:: python -m venv .venv/recommendation_env

:: Activate and install dependencies for CNN
call .venv\cnn_env\Scripts\activate
pip install -r requirements\cnn_requirements.txt
deactivate

:: Activate and install dependencies for Classification
call .venv\capture_venv\Scripts\activate
pip install -r requirements\capture_requirements.txt
deactivate

:: Activate and install dependencies for Recommendation
:: call .venv\recommendation_env\Scripts\activate
:: pip install -r requirements\recommendation_requirements.txt
:: deactivate