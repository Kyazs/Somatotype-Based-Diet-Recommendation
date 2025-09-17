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
        This function computes the values for each category on a scale of 1-7 and determines 
        the somatotype classification based on the triangle somatochart.

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
            - endomorphy (float): The calculated endomorphy value (1-7 scale).
            - mesomorphy (float): The calculated mesomorphy value (1-7 scale).
            - ectomorphy (float): The calculated ectomorphy value (1-7 scale).
            - somatotype (str): The somatotype classification based on triangle somatochart.
    """
    # Calculate raw values first
    k = 0.5
    sum_skinfold = waist * k
    raw_endomorphy = (
        -0.7182
        + 0.1451 * sum_skinfold
        - 0.00068 * (sum_skinfold**2)
        + 0.0000014 * (sum_skinfold**3)
    )

    raw_mesomorphy = 2.0 * ((shoulder + chest + thigh) / stature) - 1.0

    cube_root_weight = weight ** (1 / 3)
    HWR = stature / cube_root_weight

    if HWR > 40.75:
        raw_ectomorphy = 0.732 * HWR - 28.58
    elif HWR >= 38.25:
        raw_ectomorphy = 0.463 * HWR - 17.63
    else:
        raw_ectomorphy = 0.1

    # Scale values to 1-7 range and ensure they're within bounds
    def scale_to_range(value, min_val=-3, max_val=10):
        """Scale a value to 1-7 range"""
        scaled = ((value - min_val) / (max_val - min_val)) * 6 + 1
        return max(1.0, min(7.0, scaled))

    endomorphy = scale_to_range(raw_endomorphy)
    mesomorphy = scale_to_range(raw_mesomorphy)
    ectomorphy = scale_to_range(raw_ectomorphy)

    # Determine somatotype classification based on triangle somatochart
    def classify_somatotype(endo, meso, ecto):
        """Classify somatotype based on the three component values"""
        # Round to nearest 0.5 for classification
        e = round(endo * 2) / 2
        m = round(meso * 2) / 2
        c = round(ecto * 2) / 2
        
        # Determine dominant components
        max_val = max(e, m, c)
        min_val = min(e, m, c)
        
        # Check for balanced type (all values within 1 point of each other)
        if max_val - min_val <= 1.0:
            if max_val <= 3.5:
                return "Central"
            else:
                return "Balanced"
        
        # Determine primary and secondary components
        components = [("Endo", e), ("Meso", m), ("Ecto", c)]
        components.sort(key=lambda x: x[1], reverse=True)
        
        primary = components[0]
        secondary = components[1]
        
        # If primary is significantly higher than secondary (>1.5 points)
        if primary[1] - secondary[1] > 1.5:
            if primary[0] == "Endo":
                return "Endomorph"
            elif primary[0] == "Meso":
                return "Mesomorph"
            else:
                return "Ectomorph"
        
        # Mixed types based on two highest components
        primary_name = primary[0]
        secondary_name = secondary[0]
        
        if "Endo" in [primary_name, secondary_name] and "Meso" in [primary_name, secondary_name]:
            return "Endo-Mesomorph" if e > m else "Meso-Endomorph"
        elif "Meso" in [primary_name, secondary_name] and "Ecto" in [primary_name, secondary_name]:
            return "Meso-Ectomorph" if m > c else "Ecto-Mesomorph"
        elif "Endo" in [primary_name, secondary_name] and "Ecto" in [primary_name, secondary_name]:
            return "Endo-Ectomorph" if e > c else "Ecto-Endomorph"
        
        return "Balanced"

    somatotype = classify_somatotype(endomorphy, mesomorphy, ectomorphy)

    # Save results to a CSV file
    output_file = os.path.join(OUTPUT_FILES_DIR, "output_classification.csv")
    result_df = pd.DataFrame(
        {
            "Endomorphy": [round(endomorphy, 1)],
            "Mesomorphy": [round(mesomorphy, 1)],
            "Ectomorphy": [round(ectomorphy, 1)],
            "Somatotype": [somatotype],
        }
    )
    result_df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")

    return round(endomorphy, 1), round(mesomorphy, 1), round(ectomorphy, 1), somatotype

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
