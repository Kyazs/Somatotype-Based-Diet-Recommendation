import pandas as pd
import math

def calculate_heath_carter_somatotype(height_cm, weight_kg, triceps_mm, subscapular_mm, supraspinale_mm, calf_skinfold_mm, humerus_breadth_cm, femur_breadth_cm, arm_girth_cm, calf_girth_cm):
    """
    Calculate Heath-Carter anthropometric somatotype using Method B equations.
    
    Parameters:
    - height_cm: Height in centimeters
    - weight_kg: Weight in kilograms
    - triceps_mm: Triceps skinfold in millimeters
    - subscapular_mm: Subscapular skinfold in millimeters
    - supraspinale_mm: Supraspinale skinfold in millimeters
    - calf_skinfold_mm: Calf skinfold in millimeters
    - humerus_breadth_cm: Humerus biepicondylar breadth in centimeters
    - femur_breadth_cm: Femur bicondylar breadth in centimeters
    - arm_girth_cm: Flexed arm circumference in centimeters
    - calf_girth_cm: Calf circumference in centimeters
    
    Returns:
    - Dictionary with endomorphy, mesomorphy, ectomorphy values and classification
    """
    
    # Convert skinfolds to cm for calculations
    triceps_cm = triceps_mm / 10
    calf_skinfold_cm = calf_skinfold_mm / 10
    
    # Calculate corrected girths
    corrected_arm_girth = arm_girth_cm - triceps_cm
    corrected_calf_girth = calf_girth_cm - calf_skinfold_cm
    
    # 1. ENDOMORPHY CALCULATION
    # Sum of three skinfolds (triceps, subscapular, supraspinale) in mm
    sum_3_skinfolds = triceps_mm + subscapular_mm + supraspinale_mm
    
    # Height-corrected endomorphy
    X = sum_3_skinfolds * (170.18 / height_cm)
    
    # Endomorphy equation
    endomorphy = -0.7182 + 0.1451 * X - 0.00068 * (X**2) + 0.0000014 * (X**3)
    
    # Ensure minimum value of 0.1
    if endomorphy <= 0:
        endomorphy = 0.1
    
    # 2. MESOMORPHY CALCULATION
    mesomorphy = (0.858 * humerus_breadth_cm + 
                 0.601 * femur_breadth_cm + 
                 0.188 * corrected_arm_girth + 
                 0.161 * corrected_calf_girth - 
                 height_cm * 0.131 + 4.5)
    
    # Ensure minimum value of 0.1
    if mesomorphy <= 0:
        mesomorphy = 0.1
    
    # 3. ECTOMORPHY CALCULATION
    # Calculate Height-Weight Ratio (HWR)
    hwr = height_cm / (weight_kg ** (1/3))
    
    # Apply conditional equations for ectomorphy
    if hwr >= 40.75:
        ectomorphy = 0.732 * hwr - 28.58
    elif hwr > 38.25:
        ectomorphy = 0.463 * hwr - 17.63
    else:
        ectomorphy = 0.1
    
    # Ensure minimum value of 0.1
    if ectomorphy <= 0:
        ectomorphy = 0.1
    
    return {
        'endomorphy': round(endomorphy, 1),
        'mesomorphy': round(mesomorphy, 1),
        'ectomorphy': round(ectomorphy, 1),
        'hwr': round(hwr, 2),
        'corrected_arm_girth': round(corrected_arm_girth, 1),
        'corrected_calf_girth': round(corrected_calf_girth, 1)
    }

def classify_somatotype(endomorphy, mesomorphy, ectomorphy):
    """
    Classify somatotype into one of the 6 simplified categories based on Heath-Carter rules.
    
    The 6 categories are:
    1. Endomorph - endomorphy dominant, other components >0.5 units lower
    2. Mesomorph - mesomorphy dominant, other components >0.5 units lower
    3. Ectomorph - ectomorphy dominant, other components >0.5 units lower
    4. Endo-Meso - endomorphy and mesomorphy both higher than ectomorphy
    5. Meso-Ecto - mesomorphy and ectomorphy both higher than endomorphy
    6. Ecto-Endo - ectomorphy and endomorphy both higher than mesomorphy
    """
    
    # Find the highest component(s)
    max_component = max(endomorphy, mesomorphy, ectomorphy)
    
    # Check for pure types first (dominant component with others >0.5 units lower)
    if endomorphy == max_component and mesomorphy <= (endomorphy - 0.5) and ectomorphy <= (endomorphy - 0.5):
        return "Endomorph"
    elif mesomorphy == max_component and endomorphy <= (mesomorphy - 0.5) and ectomorphy <= (mesomorphy - 0.5):
        return "Mesomorph"
    elif ectomorphy == max_component and endomorphy <= (ectomorphy - 0.5) and mesomorphy <= (ectomorphy - 0.5):
        return "Ectomorph"
    
    # Check for combined types
    # If no single dominant component, determine which two are highest
    components = [
        (endomorphy, "Endo"),
        (mesomorphy, "Meso"), 
        (ectomorphy, "Ecto")
    ]
    
    # Sort by value (highest first)
    components.sort(key=lambda x: x[0], reverse=True)
    
    # Take the two highest components
    first_comp = components[0][1]
    second_comp = components[1][1]
    third_comp = components[2][1]
    
    # Check if the two highest are significantly higher than the third
    if components[0][0] > components[2][0] and components[1][0] > components[2][0]:
        # Create the combined classification
        if first_comp == "Endo" and second_comp == "Meso":
            return "Endo-Meso"
        elif first_comp == "Meso" and second_comp == "Endo":
            return "Endo-Meso"
        elif first_comp == "Meso" and second_comp == "Ecto":
            return "Meso-Ecto"
        elif first_comp == "Ecto" and second_comp == "Meso":
            return "Meso-Ecto"
        elif first_comp == "Ecto" and second_comp == "Endo":
            return "Ecto-Endo"
        elif first_comp == "Endo" and second_comp == "Ecto":
            return "Ecto-Endo"
    
    # If no clear pattern, default to the highest single component
    if endomorphy >= mesomorphy and endomorphy >= ectomorphy:
        return "Endomorph"
    elif mesomorphy >= ectomorphy:
        return "Mesomorph"
    else:
        return "Ectomorph"

# Load the data and calculate somatotype
def main():
    # Read the CSV file
    df = pd.read_csv('sample_anthropometric_data.csv')
    
    # Extract values
    measurements = {}
    for _, row in df.iterrows():
        measurements[row['Measurement']] = row['Value']
    
    # Calculate somatotype
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
    
    # Print results
    print("Heath-Carter Anthropometric Somatotype Results:")
    print(f"Endomorphy: {result['endomorphy']}")
    print(f"Mesomorphy: {result['mesomorphy']}")
    print(f"Ectomorphy: {result['ectomorphy']}")
    print(f"Somatotype: {result['endomorphy']}-{result['mesomorphy']}-{result['ectomorphy']}")
    print(f"Classification: {classification}")
    print(f"Height-Weight Ratio (HWR): {result['hwr']}")
    print(f"Corrected Arm Girth: {result['corrected_arm_girth']} cm")
    print(f"Corrected Calf Girth: {result['corrected_calf_girth']} cm")
    
    return result, classification

if __name__ == "__main__":
    result, classification = main()