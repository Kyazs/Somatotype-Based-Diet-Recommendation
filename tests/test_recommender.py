# Contents of /diet-recommendation-somatotype/diet-recommendation-somatotype/tests/test_recommender.py

import unittest
from src.recommendation.recommender import Recommender

class TestRecommender(unittest.TestCase):

    def setUp(self):
        self.recommender = Recommender()

    def test_generate_recommendations(self):
        user_preferences = {
            'diet_type': 'vegetarian',
            'caloric_intake': 2000,
            'allergies': ['nuts']
        }
        cnn_output = {
            'somatotype': 'mesomorph',
            'measurements': [30, 25, 35]  # Example measurements
        }
        recommendations = self.recommender.generate_recommendations(user_preferences, cnn_output)
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)

    def test_handle_no_preferences(self):
        user_preferences = {}
        cnn_output = {
            'somatotype': 'ectomorph',
            'measurements': [28, 22, 30]
        }
        recommendations = self.recommender.generate_recommendations(user_preferences, cnn_output)
        self.assertEqual(recommendations, [])

    def test_invalid_cnn_output(self):
        user_preferences = {
            'diet_type': 'keto',
            'caloric_intake': 1800,
            'allergies': []
        }
        cnn_output = None
        with self.assertRaises(ValueError):
            self.recommender.generate_recommendations(user_preferences, cnn_output)

if __name__ == '__main__':
    unittest.main()