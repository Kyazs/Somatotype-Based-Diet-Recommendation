import unittest
from src.cnn_model.model import CNNModel
from src.cnn_model.train import train_model
from src.cnn_model.predict import predict
from src.cnn_model.utils import preprocess_image

class TestCNNModel(unittest.TestCase):

    def setUp(self):
        self.model = CNNModel()
        self.sample_image = 'path/to/sample/image.jpg'  # Replace with a valid image path
        self.preprocessed_image = preprocess_image(self.sample_image)

    def test_model_initialization(self):
        self.assertIsNotNone(self.model)

    def test_model_training(self):
        # Assuming train_model returns a trained model
        trained_model = train_model(self.preprocessed_image)
        self.assertIsNotNone(trained_model)

    def test_model_prediction(self):
        predictions = predict(self.preprocessed_image)
        self.assertIsInstance(predictions, list)  # Assuming predictions are returned as a list

if __name__ == '__main__':
    unittest.main()