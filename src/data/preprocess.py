def preprocess_data(data):
    # Normalize the data
    normalized_data = (data - data.mean()) / data.std()
    return normalized_data

def transform_data(data):
    # Apply any necessary transformations to the data
    transformed_data = data.apply(lambda x: x**2)  # Example transformation
    return transformed_data

def load_and_preprocess_data(file_path):
    import pandas as pd
    # Load data from a CSV file
    data = pd.read_csv(file_path)
    # Preprocess the data
    data = preprocess_data(data)
    data = transform_data(data)
    return data