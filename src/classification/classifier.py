import numpy as np
import pandas as pd
import os
import sys

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(PROJECT_DIR)

from src.utils.utils import OUTPUT_FILES_DIR  # Correct import path
from src.classification.calculate_somatotype import calculate_heath_carter_somatotype, classify_somatotype


def load_csv_data(file_path):
    """
    Load and clean data from the CSV file.

    Description:
        This function reads a CSV file, cleans the column names, and ensures the presence of a specific column.
        It also processes the "3D Avatar-Output" column to extract numeric values.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        pd.DataFrame: A cleaned DataFrame with numeric values in the "Measurement Output" column.
    """
    df = pd.read_csv(file_path, sep="|", skiprows=1, skipinitialspace=True)
    df.columns = [col.strip() for col in df.columns]

    if "3D Avatar-Output" not in df.columns:
        print("Available columns:", df.columns)
        raise KeyError("Expected column '3D Avatar-Output' not found in the CSV file.")

    df = df.rename(columns={"3D Avatar-Output": "Measurement Output"})
    df["Measurement Output"] = (
        df["Measurement Output"].astype(str).str.extract(r"([\d.]+)").astype(float)
    )

    return df

def get_measurement(df, name):
    """
    Retrieve a specific measurement value by name.

    Description:
        This function searches for a specific measurement in the DataFrame and returns its value.

    Args:
        df (pd.DataFrame): The DataFrame containing measurement data.
        name (str): The name of the measurement to retrieve.

    Returns:
        float: The value of the requested measurement.

    Raises:
        ValueError: If the requested measurement is not found in the DataFrame.
    """
    df["Measurement"] = df["Measurement"].str.strip().str.lower()
    name = name.strip().lower()

    matching_rows = df.loc[df["Measurement"] == name, "Measurement Output"]
    if matching_rows.empty:
        raise ValueError(f"Measurement '{name}' not found in the DataFrame.")
    return matching_rows.values[0]

def calculate_somatotype_from_measurements(
    weight, stature, chest, waist, hips, shoulder, thigh, calf, neck
):
    """
    Calculate the somatotype using Heath-Carter method from body measurements.
    
    This function converts body measurements to approximate skinfold and breadth
    measurements for use with the Heath-Carter calculation.
    
    Args:
        weight (float): Body weight in kilograms.
        stature (float): Height in centimeters.
        chest (float): Chest circumference in centimeters.
        waist (float): Waist circumference in centimeters.
        hips (float): Hip circumference in centimeters.
        shoulder (float): Shoulder circumference in centimeters.
        thigh (float): Thigh circumference in centimeters.
        calf (float): Calf circumference in centimeters.
        neck (float): Neck circumference in centimeters.

    Returns:
        tuple: A tuple containing:
            - endomorphy (float): The calculated endomorphy value.
            - mesomorphy (float): The calculated mesomorphy value.
            - ectomorphy (float): The calculated ectomorphy value.
            - somatotype (str): The somatotype classification.
    """
    # Convert circumferences to approximate skinfold and breadth measurements
    # These are approximations based on typical ratios
    
    # Skinfold approximations (in mm) - based on circumference ratios
    triceps_mm = max(5, min(40, (chest - 85) * 0.3 + 12))  # approximate triceps skinfold
    subscapular_mm = max(5, min(40, (waist - 70) * 0.25 + 10))  # approximate subscapular
    supraspinale_mm = max(5, min(40, (waist - 70) * 0.2 + 8))  # approximate supraspinale
    calf_skinfold_mm = max(3, min(25, (calf - 30) * 0.2 + 7))  # approximate calf skinfold
    
    # Breadth approximations (in cm) - based on circumferences and typical ratios
    humerus_breadth_cm = max(4, min(8, chest * 0.08))  # approximate humerus breadth
    femur_breadth_cm = max(7, min(12, hips * 0.1))  # approximate femur breadth
    
    # Use actual circumferences for arm and calf girths
    arm_girth_cm = max(chest * 0.35, 20)  # approximate flexed arm girth
    calf_girth_cm = calf
    
    # Calculate Heath-Carter somatotype
    result = calculate_heath_carter_somatotype(
        height_cm=stature,
        weight_kg=weight,
        triceps_mm=triceps_mm,
        subscapular_mm=subscapular_mm,
        supraspinale_mm=supraspinale_mm,
        calf_skinfold_mm=calf_skinfold_mm,
        humerus_breadth_cm=humerus_breadth_cm,
        femur_breadth_cm=femur_breadth_cm,
        arm_girth_cm=arm_girth_cm,
        calf_girth_cm=calf_girth_cm
    )
    
    # Classify the somatotype
    somatotype_class = classify_somatotype(
        result['endomorphy'], 
        result['mesomorphy'], 
        result['ectomorphy']
    )

    # Save results to a CSV file
    output_file = os.path.join(OUTPUT_FILES_DIR, "output_classification.csv")
    result_df = pd.DataFrame(
        {
            "Endomorphy": [result['endomorphy']],
            "Mesomorphy": [result['mesomorphy']],
            "Ectomorphy": [result['ectomorphy']],
            "Somatotype": [somatotype_class],
            "HWR": [result['hwr']]
        }
    )
    result_df.to_csv(output_file, index=False)
    print(f"Heath-Carter somatotype results saved to {output_file}")

    return result['endomorphy'], result['mesomorphy'], result['ectomorphy'], somatotype_class

def test_with_sample_data():
    """
    Test the Heath-Carter somatotype calculation with sample anthropometric data.
    """
    # Load sample data from the CSV file
    sample_file = os.path.join(os.path.dirname(__file__), "sample_anthropometric_data.csv")
    
    try:
        df = pd.read_csv(sample_file)
        
        # Extract measurements from the CSV
        measurements = {}
        for _, row in df.iterrows():
            measurements[row['Measurement']] = row['Value']
        
        # Calculate Heath-Carter somatotype directly
        result = calculate_heath_carter_somatotype(
            height_cm=measurements['Height'],
            weight_kg=measurements['Weight'],
            triceps_mm=measurements['Triceps_Skinfold'],
            subscapular_mm=measurements['Subscapular_Skinfold'],
            supraspinale_mm=measurements['Supraspinale_Skinfold'],
            calf_skinfold_mm=measurements['Calf_Skinfold'],
            humerus_breadth_cm=measurements['Humerus_Breadth'],
            femur_breadth_cm=measurements['Femur_Breadth'],
            arm_girth_cm=measurements['Arm_Circumference_Flexed'],
            calf_girth_cm=measurements['Calf_Circumference']
        )
        
        # Classify the somatotype
        classification = classify_somatotype(
            result['endomorphy'], 
            result['mesomorphy'], 
            result['ectomorphy']
        )
        
        print("=== HEATH-CARTER SOMATOTYPE TEST ===")
        print(f"Height: {measurements['Height']} cm")
        print(f"Weight: {measurements['Weight']} kg")
        print(f"Endomorphy: {result['endomorphy']}")
        print(f"Mesomorphy: {result['mesomorphy']}")
        print(f"Ectomorphy: {result['ectomorphy']}")
        print(f"Somatotype: {result['endomorphy']}-{result['mesomorphy']}-{result['ectomorphy']}")
        print(f"Classification: {classification}")
        print(f"Height-Weight Ratio: {result['hwr']}")
        
        # Save results to output file
        output_file = os.path.join(OUTPUT_FILES_DIR, "output_classification.csv")
        result_df = pd.DataFrame({
            "Endomorphy": [result['endomorphy']],
            "Mesomorphy": [result['mesomorphy']],
            "Ectomorphy": [result['ectomorphy']],
            "Somatotype": [classification],
            "HWR": [result['hwr']]
        })
        result_df.to_csv(output_file, index=False)
        print(f"Results saved to {output_file}")
        
        return result['endomorphy'], result['mesomorphy'], result['ectomorphy'], classification
        
    except Exception as e:
        print(f"Error testing with sample data: {e}")
        return None

def main():
    """
    Main function to process anthropometric data, calculate somatotype, and display results.

    Description:
        This function loads anthropometric data from a CSV file, extracts relevant body measurements,
        calculates the somatotype components (endomorphy, mesomorphy, ectomorphy), and prints the results.

    Args:
        None

    Returns:
        None
    """
    # First test with sample data if available
    sample_result = test_with_sample_data()
    if sample_result:
        print("\n" + "="*50)
        print("Sample data test completed successfully!")
        print("="*50)
        return
    
    # Fallback to original method if sample data not available
    csv_file_path = f"{OUTPUT_FILES_DIR}/output_data_avatar_male_fromImg.csv"
    
    if not os.path.exists(csv_file_path):
        print(f"Avatar data file not found: {csv_file_path}")
        print("Please run the CNN model first to generate avatar measurements.")
        return
        
    df = load_csv_data(csv_file_path)

    weight = get_measurement(df, "weight_kg")  # in kg
    stature = get_measurement(df, "stature_cm")  # in cm
    chest = get_measurement(df, "chest_girth")  # in cm
    waist = get_measurement(df, "waist_girth")  # in cm
    hips = get_measurement(df, "hips_buttock_girth")  # in cm
    shoulder = get_measurement(df, "shoulder_girth")  # in cm
    thigh = get_measurement(df, "thigh_girth")  # in cm
    calf = get_measurement(df, "calf_girth")  # in cm
    neck = get_measurement(df, "neck_base_girth")  # in cm

    print(f"Weight: {weight} kg")
    print(f"Stature: {stature} cm")
    print(f"Chest: {chest} cm")
    print(f"Waist: {waist} cm")
    print(f"Hips: {hips} cm")
    print(f"Shoulder: {shoulder} cm")
    print(f"Thigh: {thigh} cm")
    print(f"Calf: {calf} cm")
    print(f"Neck: {neck} cm")

    endomorphy, mesomorphy, ectomorphy, somatotype = calculate_somatotype_from_measurements(
        weight, stature, chest, waist, hips, shoulder, thigh, calf, neck
    )

    print(f"Endomorphy: {endomorphy:.2f}")
    print(f"Mesomorphy: {mesomorphy:.2f}")
    print(f"Ectomorphy: {ectomorphy:.2f}")
    print(f"Somatotype: {somatotype}")


if __name__ == "__main__":
    main()
