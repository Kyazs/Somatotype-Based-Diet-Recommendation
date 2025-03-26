# main.py

import sys
from cnn_model.train import train_model
from cnn_model.predict import predict
from classification.classifier import Classifier
from recommendation.recommender import Recommender
from data.dataset_loader import load_data
from data.preprocess import preprocess_data

def main():
    # Load and preprocess data
    data = load_data()
    preprocessed_data = preprocess_data(data)

    # Train CNN model
    cnn_model = train_model(preprocessed_data)

    # Make predictions using the trained CNN model
    measurements = predict(cnn_model)

    # Classify somatotype based on extracted measurements
    classifier = Classifier()
    somatotype = classifier.predict(measurements)

    # Generate diet recommendations based on user preferences and somatotype
    recommender = Recommender()
    recommendations = recommender.generate(somatotype)

    # Output recommendations
    print("Diet Recommendations:")
    for recommendation in recommendations:
        print(f"- {recommendation}")

if __name__ == "__main__":
    main()