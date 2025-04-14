import numpy as np
import pandas as pd
import os
import sys

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(PROJECT_DIR)

from src.utils.utils import OUTPUT_FILES_DIR  # Correct import path


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

def calculate_somatotype(
    weight, stature, chest, waist, hips, shoulder, thigh, calf, neck
):
    """
    Calculate the somatotype based on anthropometric measurements.

    Description:
        The somatotype is a classification of body type into three categories:
        Endomorph (fatness), Mesomorph (muscularity), and Ectomorph (linearity).
        This function computes the values for each category and determines the dominant somatotype.

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
            - somatotype (str): The dominant somatotype category
              ("Endomorph", "Mesomorph", "Ectomorph", or "Balanced").
    """
    k = 0.5
    sum_skinfold = waist * k
    endomorphy = (
        -0.7182
        + 0.1451 * sum_skinfold
        - 0.00068 * (sum_skinfold**2)
        + 0.0000014 * (sum_skinfold**3)
    )

    mesomorphy = 2.0 * ((shoulder + chest + thigh) / stature) - 1.0

    cube_root_weight = weight ** (1 / 3)
    HWR = stature / cube_root_weight

    if HWR > 40.75:
        ectomorphy = 0.732 * HWR - 28.58
    elif HWR >= 38.25:
        ectomorphy = 0.463 * HWR - 17.63
    else:
        ectomorphy = 0.1

    if endomorphy > mesomorphy and endomorphy > ectomorphy:
        somatotype = "Endomorph"
    elif mesomorphy > endomorphy and mesomorphy > ectomorphy:
        somatotype = "Mesomorph"
    elif ectomorphy > endomorphy and ectomorphy > mesomorphy:
        somatotype = "Ectomorph"
    else:
        somatotype = "Balanced"

    # Save results to a CSV file
    output_file = os.path.join(OUTPUT_FILES_DIR, "output_classification.csv")
    result_df = pd.DataFrame(
        {
            "Endomorphy": [endomorphy],
            "Mesomorphy": [mesomorphy],
            "Ectomorphy": [ectomorphy],
            "Somatotype": [somatotype],
        }
    )
    result_df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")

    return endomorphy, mesomorphy, ectomorphy, somatotype

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
    csv_file_path = f"{OUTPUT_FILES_DIR}/output_data_avatar_male_fromImg.csv"
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

    endomorphy, mesomorphy, ectomorphy, somatotype = calculate_somatotype(
        weight, stature, chest, waist, hips, shoulder, thigh, calf, neck
    )

    print(f"Endomorphy: {endomorphy:.2f}")
    print(f"Mesomorphy: {mesomorphy:.2f}")
    print(f"Ectomorphy: {ectomorphy:.2f}")
    print(f"Somatotype: {somatotype}")


if __name__ == "__main__":
    main()
