from tensorflow.keras.models import load_model
import numpy as np
import cv2
import os

class CNNModelPredictor:
    def __init__(self, model_path):
        self.model_path = model_path
        self.model = self.load_model()

    def load_model(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found at {self.model_path}")
        return load_model(self.model_path)

    def preprocess_image(self, image_path):
        image = cv2.imread(image_path)
        image = cv2.resize(image, (224, 224))  # Resize to match model input
        image = image.astype('float32') / 255.0  # Normalize to [0, 1]
        image = np.expand_dims(image, axis=0)  # Add batch dimension
        return image

    def predict(self, image_path):
        image = self.preprocess_image(image_path)
        predictions = self.model.predict(image)
        return predictions

# Example usage:
# predictor = CNNModelPredictor('path/to/your/model.h5')
# result = predictor.predict('path/to/image.jpg')
# print(result)