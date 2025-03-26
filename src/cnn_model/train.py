import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.model_selection import train_test_split

def load_data(data_directory, image_size=(224, 224), test_size=0.2):
    # Load images and labels from the specified directory
    images = []
    labels = []
    
    for label in os.listdir(data_directory):
        label_dir = os.path.join(data_directory, label)
        if os.path.isdir(label_dir):
            for img_file in os.listdir(label_dir):
                img_path = os.path.join(label_dir, img_file)
                img = tf.keras.preprocessing.image.load_img(img_path, target_size=image_size)
                img_array = tf.keras.preprocessing.image.img_to_array(img)
                images.append(img_array)
                labels.append(label)

    images = np.array(images) / 255.0  # Normalize images
    labels = np.array(labels)

    return train_test_split(images, labels, test_size=test_size, random_state=42)

def train_model(model, train_data, train_labels, epochs=10, batch_size=32):
    # Compile the model
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    
    # Create an ImageDataGenerator for data augmentation
    datagen = ImageDataGenerator(rotation_range=20, width_shift_range=0.2,
                                 height_shift_range=0.2, shear_range=0.2,
                                 zoom_range=0.2, horizontal_flip=True,
                                 fill_mode='nearest')

    # Fit the model
    model.fit(datagen.flow(train_data, train_labels, batch_size=batch_size), 
              epochs=epochs)

def save_model(model, model_path):
    model.save(model_path)

if __name__ == "__main__":
    data_directory = 'path/to/your/data'  # Update with your data path
    model_path = 'path/to/save/model.h5'  # Update with your desired model save path

    # Load data
    X_train, X_test, y_train, y_test = load_data(data_directory)

    # Import the model
    from model import create_model  # Assuming create_model is a function in model.py that returns a compiled model
    cnn_model = create_model()

    # Train the model
    train_model(cnn_model, X_train, y_train, epochs=20, batch_size=32)

    # Save the trained model
    save_model(cnn_model, model_path)