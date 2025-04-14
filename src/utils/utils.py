
# In utils.py
import os

# Your path definitions
UTILS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
PROJECT_DIR = os.path.abspath(os.path.join(UTILS_DIR, '../'))
VENV_DIR = os.path.join(PROJECT_DIR, '.venv')
INPUT_FILES_DIR = os.path.join(PROJECT_DIR, 'data/input_files')
OUTPUT_FILES_DIR = os.path.join(PROJECT_DIR, 'data/output_files')
CNN_DIR = os.path.join(PROJECT_DIR, 'src/cnn_model/src/')
CAPTURE_DIR = os.path.join(PROJECT_DIR, 'src/image-capture')
CLASSIFIER_DIR = os.path.join(PROJECT_DIR, 'src/classification')
RECOMMENDER_DIR = os.path.join(PROJECT_DIR, 'src/recommendation')


# Expose constants for direct import
__all__ = [
    "UTILS_DIR",
    "PROJECT_DIR",
    "VENV_DIR",
    "INPUT_FILES_DIR",
    "OUTPUT_FILES_DIR",
    "CAPTURE_DIR",
    "CNN_DIR",
    "CLASSIFIER_DIR",
    "RECOMMENDER_DIR",
]

if __name__ == "__main__":
    print("Utility module loaded successfully.")