#!/usr/bin/env python3
"""
Integration script for the processing page to generate recommendations.

This script is called by the processing page and generates recommendations
using the available data and existing recommender system.
"""

import os
import sys
import pandas as pd
import csv

# Add project root to path
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(PROJECT_DIR)

from src.utils.utils import OUTPUT_FILES_DIR

def get_user_data_from_input():
    """Extract user data from input files"""
    try:
        # Load user input data
        input_file = os.path.join(PROJECT_DIR, "data", "input_files", "input_info_recommendation.csv")
        if os.path.exists(input_file):
            user_df = pd.read_csv(input_file)
            user_data = user_df.iloc[0].to_dict()
        else:
            # Default fallback data
            user_data = {
                'Name': 'User',
                'Age': 25,
                'Goal': 'Maintain Weight',
                'Activity_Level': 'Moderately active'
            }
        
        # Load body measurements
        measurements_file = os.path.join(OUTPUT_FILES_DIR, "output_data_avatar_male_fromImg.csv")
        body_data = {'weight_kg': 70, 'height_cm': 175}  # defaults
        
        if os.path.exists(measurements_file):
            try:
                # Parse the pipe-separated format
                with open(measurements_file, 'r') as f:
                    lines = f.readlines()
                
                for line in lines[2:]:  # Skip header lines
                    if '|' in line:
                        parts = [p.strip() for p in line.split('|')]
                        if len(parts) >= 4:
                            measurement = parts[0]
                            avatar_output = parts[3]
                            try:
                                if measurement == 'weight_kg':
                                    body_data['weight_kg'] = float(avatar_output)
                                elif measurement == 'stature_cm':
                                    body_data['height_cm'] = float(avatar_output)
                            except:
                                pass
            except:
                print("Could not parse body measurements, using defaults")
        
        return user_data, body_data
        
    except Exception as e:
        print(f"Error loading user data: {e}")
        # Return safe defaults
        return {
            'Name': 'User',
            'Age': 25,
            'Goal': 'Maintain Weight',
            'Activity_Level': 'Moderately active'
        }, {'weight_kg': 70, 'height_cm': 175}

def get_somatotype():
    """Get somatotype classification"""
    try:
        classification_file = os.path.join(OUTPUT_FILES_DIR, "output_classification.csv")
        if os.path.exists(classification_file):
            df = pd.read_csv(classification_file)
            somatotype = df['Somatotype'].iloc[0].lower()
            return somatotype
        else:
            return 'mesomorph'  # default
    except Exception as e:
        print(f"Error loading somatotype: {e}")
        return 'mesomorph'

def calculate_bmr(weight, height, age, gender='male'):
    """Calculate BMR using Mifflin-St Jeor equation"""
    if gender.lower() == 'male':
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161

def calculate_tdee(bmr, activity_level):
    """Calculate TDEE based on activity level"""
    multipliers = {
        'sedentary': 1.2,
        'lightly active': 1.375,
        'moderately active': 1.55,
        'very active': 1.725,
        'extremely active': 1.9
    }
    
    key = activity_level.lower()
    multiplier = multipliers.get(key, 1.55)
    return bmr * multiplier

def generate_recommendations():
    """Generate personalized recommendations"""
    try:
        # Get user data
        user_data, body_data = get_user_data_from_input()
        somatotype = get_somatotype()
        
        # Extract key information
        age = int(user_data.get('Age', 25))
        goal = user_data.get('Goal', 'Maintain Weight').lower()
        activity_level = user_data.get('Activity_Level', 'Moderately active')
        weight = body_data.get('weight_kg', 70)
        height = body_data.get('height_cm', 175)
        
        # Calculate metabolic needs
        bmr = calculate_bmr(weight, height, age)
        tdee = calculate_tdee(bmr, activity_level)
        
        # Adjust calories based on goal
        if 'lose' in goal or 'loss' in goal:
            target_calories = tdee - 500
        elif 'gain' in goal:
            target_calories = tdee + 500
        else:
            target_calories = tdee
        
        # Somatotype-based macronutrient ratios
        if 'ecto' in somatotype:
            protein_ratio, carb_ratio, fat_ratio = 0.25, 0.50, 0.25
            target_calories += 200  # Higher calorie needs
        elif 'endo' in somatotype:
            protein_ratio, carb_ratio, fat_ratio = 0.35, 0.30, 0.35
            target_calories -= 100  # Lower calorie needs
        else:  # mesomorph
            protein_ratio, carb_ratio, fat_ratio = 0.30, 0.40, 0.30
        
        # Calculate macros
        protein_g = round((target_calories * protein_ratio) / 4)
        carbs_g = round((target_calories * carb_ratio) / 4)
        fat_g = round((target_calories * fat_ratio) / 9)
        
        # Somatotype-based food recommendations
        food_recommendations = {
            'ectomorph': [
                'Oats', 'Peanut Butter', 'Grilled Chicken', 'Brown Rice', 
                'Protein Shake', 'Salmon', 'Sweet Potatoes', 'Nuts', 
                'Whole Grain Bread', 'Greek Yogurt'
            ],
            'mesomorph': [
                'Greek Yogurt', 'Chicken Breast', 'Quinoa', 'Turkey', 
                'Whole Grain Bread', 'Lean Beef', 'Brown Rice', 'Eggs',
                'Vegetables', 'Fruits'
            ],
            'endomorph': [
                'Boiled Chicken', 'Steamed Vegetables', 'Protein Smoothie', 
                'Grilled Tofu', 'Salad', 'Egg Whites', 'Fish', 'Broccoli',
                'Spinach', 'Lean Proteins'
            ]
        }
        
        # Get food recommendations for this somatotype
        foods = food_recommendations.get(somatotype, food_recommendations['mesomorph'])
        
        # Save recommendations
        output_file = os.path.join(OUTPUT_FILES_DIR, "output_recommendation.csv")
        
        with open(output_file, mode="w", newline="", encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Macronutrients
            writer.writerow(["Macronutrient", "Value"])
            writer.writerow(["calories", int(target_calories)])
            writer.writerow(["protein", protein_g])
            writer.writerow(["carbs", carbs_g])
            writer.writerow(["fat", fat_g])
            writer.writerow(["bmr", int(bmr)])
            writer.writerow(["tdee", int(tdee)])
            writer.writerow(["somatotype", somatotype])
            writer.writerow([])
            
            # Food recommendations
            writer.writerow(["Suggested Foods"])
            for food in foods:
                writer.writerow([food])
            writer.writerow([])
            
            # Nutrition insights
            writer.writerow(["Nutrition Insights"])
            writer.writerow([f"Your {somatotype} body type benefits from {protein_ratio*100:.0f}% protein, {carb_ratio*100:.0f}% carbs, {fat_ratio*100:.0f}% fat"])
            writer.writerow([f"Target: {int(target_calories)} calories daily"])
            
            if 'ecto' in somatotype:
                writer.writerow(["Focus on calorie-dense foods and strength training"])
            elif 'endo' in somatotype:
                writer.writerow(["Emphasize protein and control carbohydrate portions"])
            else:
                writer.writerow(["Maintain balanced nutrition with variety"])
        
        print("[SUCCESS] Recommendations generated successfully!")
        print(f"Somatotype: {somatotype.title()}")
        print(f"Target Calories: {int(target_calories)}")
        print(f"Macros - Protein: {protein_g}g, Carbs: {carbs_g}g, Fat: {fat_g}g")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error generating recommendations: {e}")
        import traceback
        traceback.print_exc()
        
        # Create a minimal fallback recommendation file
        try:
            output_file = os.path.join(OUTPUT_FILES_DIR, "output_recommendation.csv")
            with open(output_file, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Macronutrient", "Value"])
                writer.writerow(["calories", 2000])
                writer.writerow(["protein", 150])
                writer.writerow(["carbs", 200])
                writer.writerow(["fat", 70])
                writer.writerow([])
                writer.writerow(["Suggested Foods"])
                writer.writerow(["Grilled Chicken"])
                writer.writerow(["Brown Rice"])
                writer.writerow(["Vegetables"])
                writer.writerow(["Greek Yogurt"])
                writer.writerow(["Fruits"])
            print("[SUCCESS] Fallback recommendations created")
        except:
            pass
        
        return False

if __name__ == "__main__":
    print("[INFO] Generating diet recommendations...")
    success = generate_recommendations()
    
    if success:
        print("[SUCCESS] Diet recommendation generation completed!")
        sys.exit(0)
    else:
        print("[ERROR] Diet recommendation generation failed!")
        sys.exit(1)
