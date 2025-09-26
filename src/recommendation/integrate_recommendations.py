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
    """Generate personalized recommendations using the template system"""
    try:
        print("[INFO] Starting template-based recommendation generation...")
        
        # Import the template diet engine
        from .template_diet_engine import TemplateDietEngine
        
        # Initialize template engine
        template_engine = TemplateDietEngine()
        
        # Get user data and somatotype
        user_data, body_data = get_user_data_from_input()
        somatotype_data = {'Somatotype': get_somatotype()}
        
        print(f"[INFO] User data: {user_data}")
        print(f"[INFO] Body data: {body_data}")
        print(f"[INFO] Somatotype: {somatotype_data}")
        
        # Generate recommendations using template engine
        recommendations = template_engine.create_recommendations()
        
        if not recommendations:
            print("[WARNING] Template engine returned no recommendations, falling back to manual calculation...")
            return generate_fallback_recommendations(user_data, body_data, somatotype_data)
        
        # Save recommendations in the expected format for the diet page
        output_file = os.path.join(OUTPUT_FILES_DIR, "output_recommendation.csv")
        
        with open(output_file, mode="w", newline="") as file:
            writer = csv.writer(file)
            
            # Write macro information
            writer.writerow(["Macronutrient", "Value"])
            writer.writerow(["calories", int(recommendations.get('total_calories', 2000))])
            writer.writerow(["protein", int(recommendations.get('protein_g', 150))])
            writer.writerow(["carbs", int(recommendations.get('carbs_g', 200))])
            writer.writerow(["fat", int(recommendations.get('fats_g', 70))])
            writer.writerow([])
            
            # Write meal recommendations
            writer.writerow(["Meal Plan"])
            
            # Breakfast foods
            if 'meals' in recommendations and 'breakfast' in recommendations['meals']:
                writer.writerow(["Breakfast"])
                for food in recommendations['meals']['breakfast']:
                    food_name = food.get('name', str(food)) if isinstance(food, dict) else str(food)
                    writer.writerow([food_name])
                writer.writerow([])
            
            # Lunch foods
            if 'meals' in recommendations and 'lunch' in recommendations['meals']:
                writer.writerow(["Lunch"])
                for food in recommendations['meals']['lunch']:
                    food_name = food.get('name', str(food)) if isinstance(food, dict) else str(food)
                    writer.writerow([food_name])
                writer.writerow([])
            
            # Dinner foods
            if 'meals' in recommendations and 'dinner' in recommendations['meals']:
                writer.writerow(["Dinner"])
                for food in recommendations['meals']['dinner']:
                    food_name = food.get('name', str(food)) if isinstance(food, dict) else str(food)
                    writer.writerow([food_name])
                writer.writerow([])
            
            # Snack foods
            if 'meals' in recommendations and 'snacks' in recommendations['meals']:
                writer.writerow(["Snacks"])
                for food in recommendations['meals']['snacks']:
                    food_name = food.get('name', str(food)) if isinstance(food, dict) else str(food)
                    writer.writerow([food_name])
                writer.writerow([])
            
            # Diet principles
            writer.writerow(["Diet Principles"])
            diet_principles = recommendations.get('diet_principles', '')
            if diet_principles:
                for principle in diet_principles.split('|'):
                    writer.writerow([principle.strip()])
            
            # Fitness strategy
            if 'fitness_strategy' in recommendations:
                writer.writerow([])
                writer.writerow(["Fitness Strategy"])
                writer.writerow([recommendations['fitness_strategy']])
        
        print("[SUCCESS] Template-based recommendations generated successfully!")
        print(f"Template used: {recommendations.get('template_id', 'Unknown')}")
        print(f"Somatotype: {recommendations.get('somatotype', 'Unknown')}")
        print(f"Target Calories: {int(recommendations.get('total_calories', 2000))}")
        print(f"Macros - Protein: {recommendations.get('protein_g', 0)}g, Carbs: {recommendations.get('carbs_g', 0)}g, Fat: {recommendations.get('fats_g', 0)}g")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error generating template-based recommendations: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback to manual calculation
        try:
            print("[INFO] Attempting fallback recommendation generation...")
            user_data, body_data = get_user_data_from_input()
            somatotype_data = {'Somatotype': get_somatotype()}
            return generate_fallback_recommendations(user_data, body_data, somatotype_data)
        except Exception as fallback_error:
            print(f"[ERROR] Fallback generation also failed: {fallback_error}")
            return create_minimal_fallback()

def create_minimal_fallback():
    """Create a minimal fallback recommendation file"""
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
        print("[SUCCESS] Minimal fallback recommendations created")
        return True
    except Exception as e:
        print(f"[ERROR] Could not create minimal fallback: {e}")
        return False

def generate_fallback_recommendations(user_data, body_data, somatotype_data):
    """Generate recommendations using manual calculation as fallback"""
    try:
        somatotype = somatotype_data.get('Somatotype', 'mesomorph').lower()
        
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
        else:  # mesomorph or mixed types
            protein_ratio, carb_ratio, fat_ratio = 0.30, 0.40, 0.30
        
        # Calculate macros
        protein_g = round((target_calories * protein_ratio) / 4)
        carbs_g = round((target_calories * carb_ratio) / 4)
        fat_g = round((target_calories * fat_ratio) / 9)
        
        # Save fallback recommendations
        output_file = os.path.join(OUTPUT_FILES_DIR, "output_recommendation.csv")
        with open(output_file, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Macronutrient", "Value"])
            writer.writerow(["calories", int(target_calories)])
            writer.writerow(["protein", protein_g])
            writer.writerow(["carbs", carbs_g])
            writer.writerow(["fat", fat_g])
            writer.writerow([])
            
            writer.writerow(["Suggested Foods"])
            # Basic somatotype-based food recommendations
            
            # Somatotype-based food recommendations
            food_recommendations = {
                'ectomorph': [
                    'Oats', 'Peanut Butter', 'Grilled Chicken', 'Brown Rice', 
                    'Protein Shake', 'Salmon', 'Sweet Potatoes', 'Nuts'
                ],
                'mesomorph': [
                    'Greek Yogurt', 'Chicken Breast', 'Quinoa', 'Turkey', 
                    'Lean Beef', 'Brown Rice', 'Eggs', 'Vegetables'
                ],
                'endomorph': [
                    'Boiled Chicken', 'Steamed Vegetables', 'Protein Smoothie', 
                    'Grilled Fish', 'Salad', 'Egg Whites', 'Broccoli'
                ]
            }
            
            # Get appropriate foods for this somatotype
            foods = food_recommendations.get(somatotype, food_recommendations['mesomorph'])
            for food in foods:
                writer.writerow([food])
            
            writer.writerow([])
            writer.writerow(["Diet Principles"])
            
            if 'ecto' in somatotype:
                writer.writerow(["Focus on calorie-dense foods and strength training"])
                writer.writerow(["Don't skip meals - eat frequently"])
            elif 'endo' in somatotype:
                writer.writerow(["Emphasize protein and control carbohydrate portions"])
                writer.writerow(["Focus on whole foods and avoid processed foods"])
            else:
                writer.writerow(["Maintain balanced nutrition with variety"])
                writer.writerow(["Combine strength training with cardio"])
        
        print("[SUCCESS] Fallback recommendations generated successfully!")
        print(f"Somatotype: {somatotype.title()}")
        print(f"Target Calories: {int(target_calories)}")
        print(f"Macros - Protein: {protein_g}g, Carbs: {carbs_g}g, Fat: {fat_g}g")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error generating fallback recommendations: {e}")
        import traceback
        traceback.print_exc()
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
