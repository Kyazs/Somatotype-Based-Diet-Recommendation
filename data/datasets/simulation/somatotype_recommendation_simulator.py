#!/usr/bin/env python3
"""
Somatotype-Based Diet & Exercise Recommendation Simulation

This script simulates the complete recommendation workflow:
1. User Input Processing
2. Somatotype Classification (Heath-Carter Method)
3. Exercise Recommendations (from fitness processed folder)
4. Diet Recommendations (from FNDDS processed folder)
5. Complete Output Report

Input: input_info_simulation.csv
Output: simulation_results.txt


"""

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

class SomatotypeRecommendationSimulator:
    """
    Complete simulation of somatotype-based recommendations
    """
    
    def __init__(self):
        self.simulation_path = r"c:\Users\LENOVO\Desktop\Kekious_Maximus\diet-recommendation-somatotype\data\datasets\simulation"
        self.fitness_path = r"c:\Users\LENOVO\Desktop\Kekious_Maximus\diet-recommendation-somatotype\data\datasets\fitness\processed"
        self.diet_path = r"c:\Users\LENOVO\Desktop\Kekious_Maximus\diet-recommendation-somatotype\data\datasets\diet\fndds_processed"
        
        # Load datasets
        self.load_datasets()
        
        # Heath-Carter Somatotype Classification
        self.somatotype_profiles = {
            'ectomorph': {
                'description': 'Lean, low body fat, difficulty gaining weight',
                'characteristics': ['Fast metabolism', 'Linear build', 'Low muscle mass', 'Low fat storage'],
                'exercise_focus': ['Strength training', 'Compound movements', 'Progressive overload'],
                'diet_focus': ['High calorie', 'Complex carbohydrates', 'Healthy fats']
            },
            'mesomorph': {
                'description': 'Muscular, athletic build, gains muscle easily',
                'characteristics': ['Moderate metabolism', 'Athletic build', 'Good muscle development', 'Moderate fat storage'],
                'exercise_focus': ['Balanced training', 'Strength and cardio', 'Varied workouts'],
                'diet_focus': ['Balanced macros', 'Moderate calories', 'Lean proteins']
            },
            'endomorph': {
                'description': 'Higher body fat, gains weight easily, slower metabolism',
                'characteristics': ['Slower metabolism', 'Rounder build', 'Easy weight gain', 'Higher fat storage'],
                'exercise_focus': ['Cardiovascular training', 'High-intensity workouts', 'Fat burning'],
                'diet_focus': ['Lower calories', 'High protein', 'Complex carbs']
            }
        }
    
    def load_datasets(self):
        """Load all necessary datasets"""
        try:
            # Load fitness datasets
            self.fitness_exercises = pd.read_csv(os.path.join(self.fitness_path, 'universal_exercises_database.csv'))
            self.strength_exercises = pd.read_csv(os.path.join(self.fitness_path, 'universal_strength_training.csv'))
            self.cardio_exercises = pd.read_csv(os.path.join(self.fitness_path, 'universal_cardiovascular_training.csv'))
            self.power_exercises = pd.read_csv(os.path.join(self.fitness_path, 'universal_power_training.csv'))
            self.hypertrophy_exercises = pd.read_csv(os.path.join(self.fitness_path, 'universal_hypertrophy_training.csv'))
            self.functional_exercises = pd.read_csv(os.path.join(self.fitness_path, 'universal_functional_training.csv'))
            
            # Load goal-specific datasets
            self.goal_datasets = {}
            goal_files = {
                'Gain Weight': 'goal_gain_weight_top_exercises.csv',
                'Lose Weight': 'goal_lose_weight_top_exercises.csv',
                'Maintain Weight': 'goal_maintain_weight_top_exercises.csv',
                'Build Muscle': 'goal_build_muscle_top_exercises.csv',
                'Improve Fitness': 'goal_improve_fitness_top_exercises.csv'
            }
            
            for goal, filename in goal_files.items():
                file_path = os.path.join(self.fitness_path, filename)
                if os.path.exists(file_path):
                    self.goal_datasets[goal] = pd.read_csv(file_path)
            
            # Load activity-specific datasets
            self.activity_datasets = {}
            activity_files = {
                'Sedentary': 'activity_sedentary_suitable_exercises.csv',
                'Lightly active': 'activity_lightly_active_suitable_exercises.csv',
                'Moderately active': 'activity_moderately_active_suitable_exercises.csv',
                'Very active': 'activity_very_active_suitable_exercises.csv',
                'Extremely active': 'activity_extremely_active_suitable_exercises.csv'
            }
            
            for activity, filename in activity_files.items():
                file_path = os.path.join(self.fitness_path, filename)
                if os.path.exists(file_path):
                    self.activity_datasets[activity] = pd.read_csv(file_path)
            
            # Load diet datasets
            self.diet_database = pd.read_csv(os.path.join(self.diet_path, 'optimized_diet_recommendation_database.csv'))
            self.lean_proteins = pd.read_csv(os.path.join(self.diet_path, 'foods_lean_proteins.csv'))
            self.complex_carbs = pd.read_csv(os.path.join(self.diet_path, 'foods_complex_carbs.csv'))
            self.healthy_fats = pd.read_csv(os.path.join(self.diet_path, 'foods_healthy_fats.csv'))
            
            print("✅ All datasets loaded successfully")
            
        except Exception as e:
            print(f"❌ Error loading datasets: {e}")
            # Create mock data if files don't exist
            self.create_mock_datasets()
    
    def create_mock_datasets(self):
        """Create mock datasets if actual files are not available"""
        print("📝 Creating mock datasets for simulation...")
        
        # Mock fitness data
        self.fitness_exercises = pd.DataFrame({
            'name': ['Push-up', 'Squat', 'Deadlift', 'Running', 'Cycling'],
            'primary_training_category': ['Strength Training', 'Strength Training', 'Strength Training', 'Cardiovascular Training', 'Cardiovascular Training'],
            'muscular_strength_score': [7.0, 8.5, 9.0, 3.0, 2.5],
            'cardiovascular_endurance_score': [3.0, 2.0, 2.0, 9.0, 8.5],
            'target_muscles': ['Chest, Triceps', 'Legs, Glutes', 'Back, Legs', 'Full Body', 'Legs, Cardio']
        })
        
        # Mock diet data
        self.diet_database = pd.DataFrame({
            'food_name': ['Chicken Breast', 'Brown Rice', 'Salmon', 'Oats', 'Broccoli'],
            'calories_per_100g': [165, 123, 208, 389, 25],
            'protein_g': [25.0, 2.6, 25.4, 16.9, 2.6],
            'carbs_g': [0.0, 25.0, 0.0, 66.3, 5.1],
            'fat_g': [3.6, 0.9, 12.4, 6.9, 0.3],
            'category': ['Lean Protein', 'Complex Carbs', 'Healthy Fats', 'Complex Carbs', 'Vegetables']
        })
    
    def parse_somatotype_rating(self, somatotype_str):
        """Parse Heath-Carter somatotype rating (e.g., '3-6-5')"""
        try:
            components = somatotype_str.split('-')
            endomorphy = float(components[0])
            mesomorphy = float(components[1])
            ectomorphy = float(components[2])
            
            return {
                'endomorphy': endomorphy,
                'mesomorphy': mesomorphy,
                'ectomorphy': ectomorphy,
                'raw_rating': somatotype_str
            }
        except:
            # Default balanced somatotype
            return {
                'endomorphy': 4.0,
                'mesomorphy': 4.0,
                'ectomorphy': 4.0,
                'raw_rating': '4-4-4'
            }
    
    def classify_dominant_somatotype(self, somatotype_components):
        """Classify the dominant somatotype based on Heath-Carter ratings"""
        endo = somatotype_components['endomorphy']
        meso = somatotype_components['mesomorphy']
        ecto = somatotype_components['ectomorphy']
        
        # Determine dominant component
        max_component = max(endo, meso, ecto)
        
        if max_component == meso:
            if meso >= 6.0:
                return 'mesomorph', 'Strongly Mesomorphic'
            elif meso >= 5.0:
                return 'mesomorph', 'Moderately Mesomorphic'
            else:
                return 'mesomorph', 'Balanced Mesomorphic'
        elif max_component == ecto:
            if ecto >= 6.0:
                return 'ectomorph', 'Strongly Ectomorphic'
            elif ecto >= 5.0:
                return 'ectomorph', 'Moderately Ectomorphic'
            else:
                return 'ectomorph', 'Balanced Ectomorphic'
        else:  # endomorph dominant
            if endo >= 6.0:
                return 'endomorph', 'Strongly Endomorphic'
            elif endo >= 5.0:
                return 'endomorph', 'Moderately Endomorphic'
            else:
                return 'endomorph', 'Balanced Endomorphic'
    
    def calculate_bmi(self, weight_kg, height_cm):
        """Calculate BMI (Body Mass Index)"""
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        return round(bmi, 1)
    
    def classify_bmi(self, bmi):
        """Classify BMI into categories"""
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25.0:
            return "Normal weight"
        elif bmi < 30.0:
            return "Overweight"
        else:
            return "Obese"
    
    def calculate_bmr(self, weight_kg, height_cm, age, gender):
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation"""
        if gender.lower() == 'male':
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        else:  # female
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
        return round(bmr, 0)
    
    def calculate_tdee(self, bmr, activity_level):
        """Calculate Total Daily Energy Expenditure"""
        activity_multipliers = {
            'Sedentary': 1.2,
            'Lightly active': 1.375,
            'Moderately active': 1.55,
            'Very active': 1.725,
            'Extremely active': 1.9
        }
        multiplier = activity_multipliers.get(activity_level, 1.55)
        return round(bmr * multiplier, 0)
    
    def get_anthropometric_analysis(self, user_data):
        """Generate comprehensive anthropometric analysis"""
        weight = user_data['Weight']
        height = user_data['Height']
        age = user_data['Age']
        gender = user_data['Gender']
        
        bmi = self.calculate_bmi(weight, height)
        bmi_category = self.classify_bmi(bmi)
        bmr = self.calculate_bmr(weight, height, age, gender)
        tdee = self.calculate_tdee(bmr, user_data['Activity_Level'])
        
        return {
            'bmi': bmi,
            'bmi_category': bmi_category,
            'bmr': int(bmr),
            'tdee': int(tdee),
            'weight_kg': weight,
            'height_cm': height,
            'healthy_weight_range': self.get_healthy_weight_range(height)
        }
    
    def get_healthy_weight_range(self, height_cm):
        """Calculate healthy weight range based on BMI 18.5-24.9"""
        height_m = height_cm / 100
        min_weight = round(18.5 * (height_m ** 2), 1)
        max_weight = round(24.9 * (height_m ** 2), 1)
        return f"{min_weight}-{max_weight} kg"
    
    def generate_exercise_recommendations(self, user_data, somatotype_type):
        """Generate exercise recommendations based on somatotype, goal, and activity level"""
        
        # Get goal-specific exercises first
        goal_exercises = None
        if user_data['Goal'] in self.goal_datasets:
            goal_exercises = self.goal_datasets[user_data['Goal']].copy()
        
        # Get activity-level suitable exercises
        activity_exercises = None
        if user_data['Activity_Level'] in self.activity_datasets:
            activity_exercises = self.activity_datasets[user_data['Activity_Level']].copy()
        
        # Somatotype-specific exercise selection
        if somatotype_type == 'ectomorph':
            # Focus on strength training and compound movements
            exercise_focus = "Strength training for muscle building and weight gain"
            
            # Priority: Strength > Power > Hypertrophy
            primary_exercises = self.strength_exercises.head(6)  # Main strength exercises
            secondary_exercises = self.power_exercises.head(2)   # Power development
            
            # Combine and prioritize goal-specific exercises
            if goal_exercises is not None:
                # Filter goal exercises by strength and power training
                goal_strength = goal_exercises[
                    goal_exercises['primary_training_category'].isin(['Strength Training', 'Power Training'])
                ].head(5)
                if len(goal_strength) > 0:
                    primary_exercises = goal_strength
                    
        elif somatotype_type == 'mesomorph':
            # Balanced approach: strength + cardio
            exercise_focus = "Balanced strength and cardiovascular training"
            
            # Priority: Balanced strength and cardio
            primary_exercises = self.strength_exercises.head(4)  # Strength component
            secondary_exercises = self.cardio_exercises.head(4)  # Cardio component
            
            # Use goal-specific exercises if available
            if goal_exercises is not None:
                goal_balanced = goal_exercises.head(6)
                if len(goal_balanced) > 0:
                    primary_exercises = goal_balanced.head(4)
                    secondary_exercises = goal_exercises[
                        goal_exercises['primary_training_category'] == 'Cardiovascular Training'
                    ].head(2)
                    
        else:  # endomorph
            # Focus on cardiovascular training and metabolic conditioning
            exercise_focus = "Cardiovascular training for fat loss and weight management"
            
            # Priority: Cardio > Metabolic > Functional
            primary_exercises = self.cardio_exercises.head(5)    # Main cardio
            secondary_exercises = self.functional_exercises.head(3)  # Functional training
            
            # Use goal-specific exercises
            if goal_exercises is not None:
                goal_cardio = goal_exercises[
                    goal_exercises['primary_training_category'].isin(['Cardiovascular Training', 'Metabolic Training'])
                ].head(6)
                if len(goal_cardio) > 0:
                    primary_exercises = goal_cardio
        
        # Combine exercises
        try:
            if 'secondary_exercises' in locals():
                recommended_exercises = pd.concat([primary_exercises, secondary_exercises], ignore_index=True)
            else:
                recommended_exercises = primary_exercises
        except:
            # Fallback to basic exercises if concat fails
            recommended_exercises = self.fitness_exercises.head(8)
        
        # Filter by activity level if available
        if activity_exercises is not None and len(activity_exercises) > 0:
            # Prioritize exercises that match activity level
            activity_suitable_ids = set(activity_exercises['exercise_id'].values)
            if 'exercise_id' in recommended_exercises.columns:
                activity_matched = recommended_exercises[
                    recommended_exercises['exercise_id'].isin(activity_suitable_ids)
                ]
                if len(activity_matched) >= 4:  # If we have enough activity-matched exercises
                    recommended_exercises = activity_matched.head(8)
        
        return {
            'focus': exercise_focus,
            'exercises': recommended_exercises.head(8),  # Limit to 8 exercises
            'weekly_frequency': self.get_weekly_frequency(user_data['Activity_Level']),
            'session_duration': self.get_session_duration(user_data['Activity_Level']),
            'somatotype_rationale': self.get_exercise_rationale(somatotype_type),
            'goal_alignment': f"Optimized for {user_data['Goal'].lower()}"
        }
    
    def get_weekly_frequency(self, activity_level):
        """Get recommended weekly frequency based on activity level"""
        frequency_map = {
            'Sedentary': '3 sessions per week',
            'Lightly active': '3-4 sessions per week',
            'Moderately active': '4-5 sessions per week',
            'Very active': '5-6 sessions per week',
            'Extremely active': '6-7 sessions per week'
        }
        return frequency_map.get(activity_level, '4 sessions per week')
    
    def get_session_duration(self, activity_level):
        """Get recommended session duration based on activity level"""
        duration_map = {
            'Sedentary': '30-40 minutes',
            'Lightly active': '40-50 minutes',
            'Moderately active': '45-60 minutes',
            'Very active': '60-75 minutes',
            'Extremely active': '75-90 minutes'
        }
        return duration_map.get(activity_level, '45-60 minutes')
    
    def get_exercise_rationale(self, somatotype_type):
        """Get exercise rationale for somatotype"""
        rationales = {
            'ectomorph': 'Compound movements and progressive overload for muscle building',
            'mesomorph': 'Balanced approach utilizing natural athletic ability',
            'endomorph': 'High-intensity training for metabolic enhancement'
        }
        return rationales.get(somatotype_type, 'Functional training approach')
    
    def generate_diet_recommendations(self, user_data, somatotype_type):
        """Generate diet recommendations based on somatotype, anthropometrics, and goals"""
        
        # Get anthropometric analysis for accurate calorie calculation
        anthro_data = self.get_anthropometric_analysis(user_data)
        base_calories = anthro_data['tdee']
        
        # Somatotype-specific macro ratios
        if somatotype_type == 'ectomorph':
            protein_ratio = 0.25
            carb_ratio = 0.50
            fat_ratio = 0.25
        elif somatotype_type == 'mesomorph':
            protein_ratio = 0.30
            carb_ratio = 0.40
            fat_ratio = 0.30
        else:  # endomorph
            protein_ratio = 0.35
            carb_ratio = 0.30
            fat_ratio = 0.35
        
        # Adjust calories based on goal
        if user_data['Goal'] == 'Gain Weight':
            total_calories = int(base_calories + 300)
        elif user_data['Goal'] == 'Lose Weight':
            total_calories = int(base_calories - 500)
        else:  # Maintain Weight
            total_calories = int(base_calories)
        
        # Calculate macros
        protein_calories = total_calories * protein_ratio
        carb_calories = total_calories * carb_ratio
        fat_calories = total_calories * fat_ratio
        
        protein_grams = int(protein_calories / 4)
        carb_grams = int(carb_calories / 4)
        fat_grams = int(fat_calories / 9)
        
        # Generate food recommendations
        food_recommendations = self.get_food_recommendations(somatotype_type, user_data['Goal'])
        
        return {
            'anthropometric_data': anthro_data,
            'total_calories': total_calories,
            'base_tdee': int(base_calories),
            'protein_grams': protein_grams,
            'carb_grams': carb_grams,
            'fat_grams': fat_grams,
            'meal_distribution': self.get_meal_distribution(somatotype_type),
            'food_recommendations': food_recommendations,
            'hydration': self.get_hydration_recommendation(user_data['Activity_Level']),
            'timing': self.get_meal_timing(somatotype_type)
        }
    
    def get_food_recommendations(self, somatotype_type, goal):
        """Get specific food recommendations"""
        if somatotype_type == 'ectomorph':
            return {
                'proteins': ['Chicken breast', 'Salmon', 'Eggs', 'Greek yogurt', 'Protein powder'],
                'carbohydrates': ['Oats', 'Brown rice', 'Sweet potatoes', 'Quinoa', 'Whole grain bread'],
                'fats': ['Nuts', 'Avocado', 'Olive oil', 'Peanut butter', 'Seeds'],
                'focus': 'Calorie-dense, nutrient-rich foods for weight gain'
            }
        elif somatotype_type == 'mesomorph':
            return {
                'proteins': ['Lean chicken', 'Fish', 'Turkey', 'Tofu', 'Legumes'],
                'carbohydrates': ['Brown rice', 'Quinoa', 'Vegetables', 'Fruits', 'Whole grains'],
                'fats': ['Olive oil', 'Nuts', 'Avocado', 'Fish oil', 'Seeds'],
                'focus': 'Balanced nutrition for optimal performance'
            }
        else:  # endomorph
            return {
                'proteins': ['Lean fish', 'Chicken breast', 'Egg whites', 'Plant proteins', 'Low-fat dairy'],
                'carbohydrates': ['Vegetables', 'Leafy greens', 'Berries', 'Limited whole grains'],
                'fats': ['Limited healthy fats', 'Fish oil', 'Small amounts of nuts'],
                'focus': 'Low-calorie, high-satiety foods for weight management'
            }
    
    def get_meal_distribution(self, somatotype_type):
        """Get meal distribution recommendations"""
        if somatotype_type == 'ectomorph':
            return "5-6 smaller meals throughout the day to maintain energy"
        elif somatotype_type == 'mesomorph':
            return "4-5 balanced meals with pre/post workout nutrition"
        else:  # endomorph
            return "3-4 meals with focus on satiety and blood sugar control"
    
    def get_hydration_recommendation(self, activity_level):
        """Get hydration recommendations"""
        base_water = 2.5  # liters
        activity_multipliers = {
            'Sedentary': 1.0,
            'Lightly active': 1.2,
            'Moderately active': 1.4,
            'Very active': 1.6,
            'Extremely active': 1.8
        }
        
        total_water = base_water * activity_multipliers.get(activity_level, 1.4)
        return f"{total_water:.1f} liters per day"
    
    def get_meal_timing(self, somatotype_type):
        """Get meal timing recommendations"""
        if somatotype_type == 'ectomorph':
            return "Frequent meals every 2-3 hours, including pre-bed snack"
        elif somatotype_type == 'mesomorph':
            return "Regular meals every 3-4 hours with pre/post workout nutrition"
        else:  # endomorph
            return "Larger gaps between meals (4-5 hours) to improve insulin sensitivity"
    
    def get_training_benefits(self, somatotype_type):
        """Get training benefits for specific somatotype"""
        if somatotype_type == 'ectomorph':
            return [
                "Responds well to strength training for muscle building",
                "Benefits from compound movements",
                "Requires adequate recovery between sessions",
                "Progressive overload essential for growth"
            ]
        elif somatotype_type == 'mesomorph':
            return [
                "Excellent response to resistance training",
                "Can handle higher training volumes",
                "Benefits from periodization",
                "Good recovery between sessions"
            ]
        else:  # endomorph
            return [
                "Responds well to high-intensity cardio",
                "Benefits from circuit training",
                "Requires consistent training for fat loss",
                "Good endurance capacity"
            ]
    
    def get_exercise_description(self, exercise_name):
        """Get descriptive text for exercises"""
        descriptions = {
            'Semi Squat Jump': 'Explosive power development',
            'Bodyweight Drop Jump Squat': 'Plyometric strength',
            'Jump Squat': 'Lower body power',
            'Jump Squat V. 2': 'Variation for progression',
            'Medicine Ball Supine Chest Throw': 'Upper body cardio power',
            'Dumbbell Burpee': 'Full body conditioning'
        }
        return descriptions.get(exercise_name, 'Functional movement pattern')
    
    def get_goal_adjustment_text(self, goal, total_calories, base_tdee):
        """Get goal adjustment explanation"""
        diff = total_calories - base_tdee
        if diff > 0:
            return f"+{diff} kcal for {goal.lower()}"
        elif diff < 0:
            return f"{diff} kcal for {goal.lower()}"
        else:
            return "Maintenance calories (no adjustment)"
    
    def get_protein_rationale(self, somatotype_type):
        """Get protein rationale for somatotype"""
        rationales = {
            'ectomorph': 'Adequate protein for muscle building',
            'mesomorph': 'Higher protein for muscle maintenance',
            'endomorph': 'High protein for satiety and metabolism'
        }
        return rationales.get(somatotype_type, 'Balanced protein intake')
    
    def get_carb_rationale(self, somatotype_type):
        """Get carbohydrate rationale for somatotype"""
        rationales = {
            'ectomorph': 'High carbs for energy and recovery',
            'mesomorph': 'Moderate carbs for energy and recovery',
            'endomorph': 'Lower carbs for improved insulin sensitivity'
        }
        return rationales.get(somatotype_type, 'Balanced carb intake')
    
    def get_fat_rationale(self, somatotype_type):
        """Get fat rationale for somatotype"""
        rationales = {
            'ectomorph': 'Healthy fats for calorie density',
            'mesomorph': 'Adequate fats for hormone production',
            'endomorph': 'Higher fats for satiety and hormones'
        }
        return rationales.get(somatotype_type, 'Balanced fat intake')
    
    def get_preworkout_nutrition(self, somatotype_type):
        """Get pre-workout nutrition advice"""
        if somatotype_type == 'ectomorph':
            return "Complex carbs + protein (1-2 hours before)"
        elif somatotype_type == 'mesomorph':
            return "Complex carbs + protein (1-2 hours before)"
        else:  # endomorph
            return "Light protein + minimal carbs (30-60 minutes before)"
    
    def get_postworkout_nutrition(self, somatotype_type):
        """Get post-workout nutrition advice"""
        if somatotype_type == 'ectomorph':
            return "Protein + fast carbs (within 30 minutes)"
        elif somatotype_type == 'mesomorph':
            return "Protein + simple carbs (within 30 minutes)"
        else:  # endomorph
            return "Protein + minimal carbs (within 45 minutes)"
    
    def get_food_category_analysis(self, food_type, somatotype_type):
        """Get detailed food category analysis"""
        if food_type == 'proteins':
            if somatotype_type == 'ectomorph':
                return [
                    "     Chicken breast - High biological value protein",
                    "     Salmon - Omega-3 fatty acids + protein",
                    "     Eggs - Complete amino acid profile",
                    "     Greek yogurt - Casein protein for sustained release",
                    "     Protein powder - Convenient post-workout option"
                ]
            elif somatotype_type == 'mesomorph':
                return [
                    "     Lean chicken - High biological value",
                    "     Fish - Omega-3 fatty acids",
                    "     Turkey - Low fat, high protein",
                    "     Tofu - Plant-based option",
                    "     Legumes - Fiber + protein"
                ]
            else:  # endomorph
                return [
                    "     Lean fish - High protein, low fat",
                    "     Chicken breast - Lean protein source",
                    "     Egg whites - Pure protein",
                    "     Cottage cheese - Casein protein",
                    "     Lean beef - Iron + protein"
                ]
        elif food_type == 'carbohydrates':
            if somatotype_type == 'ectomorph':
                return [
                    "     Oats - Sustained energy release",
                    "     Brown rice - Complex carbohydrates",
                    "     Sweet potatoes - Nutrient-dense carbs",
                    "     Quinoa - Complete protein + carbs",
                    "     Whole grain bread - B vitamins + fiber"
                ]
            elif somatotype_type == 'mesomorph':
                return [
                    "     Brown rice - Sustained energy",
                    "     Quinoa - Complete amino acids",
                    "     Vegetables - Micronutrients",
                    "     Fruits - Natural sugars + vitamins",
                    "     Whole grains - Fiber + B vitamins"
                ]
            else:  # endomorph
                return [
                    "     Vegetables - Low calorie, high fiber",
                    "     Berries - Antioxidants, lower sugar",
                    "     Quinoa - Protein + complex carbs",
                    "     Sweet potato - Nutrient-dense",
                    "     Leafy greens - Micronutrients, minimal calories"
                ]
        else:  # fats
            if somatotype_type == 'ectomorph':
                return [
                    "     Nuts - Calorie-dense healthy fats",
                    "     Avocado - Monounsaturated fats",
                    "     Olive oil - Anti-inflammatory fats",
                    "     Peanut butter - Convenient calorie source",
                    "     Seeds - Essential fatty acids"
                ]
            elif somatotype_type == 'mesomorph':
                return [
                    "     Olive oil - Monounsaturated fats",
                    "     Nuts - Vitamin E + healthy fats",
                    "     Avocado - Potassium + fiber",
                    "     Fish oil - EPA/DHA omega-3s",
                    "     Seeds - Minerals + essential fats"
                ]
            else:  # endomorph
                return [
                    "     Olive oil - Anti-inflammatory",
                    "     Nuts (portion controlled) - Healthy fats",
                    "     Avocado - Fiber + monounsaturated fats",
                    "     Fish oil - Omega-3 fatty acids",
                    "     Coconut oil - MCT fats for energy"
                ]
    
    def run_simulation(self):
        """Run the complete simulation"""
        
        # Load user input
        input_file = os.path.join(self.simulation_path, 'input_info_simulation.csv')
        users_df = pd.read_csv(input_file)
        
        simulation_results = []
        
        print(f"🎯 Starting Somatotype-Based Recommendation Simulation")
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"👥 Processing {len(users_df)} user(s)")
        print("=" * 70)
        
        for idx, user_row in users_df.iterrows():
            user_data = {
                'Name': user_row['Name'],
                'Weight': float(user_row['Weight']),
                'Gender': user_row['Gender'],
                'Height': float(user_row['Height']),
                'Age': int(user_row['Age']),
                'Goal': user_row['Goal'],
                'Activity_Level': user_row['Activity_Level'],
                'Somatotype': user_row['Somatotype']
            }
            
            print(f"\n👤 Processing: {user_data['Name'].title()}")
            
            # Step 1: Parse somatotype
            somatotype_components = self.parse_somatotype_rating(user_data['Somatotype'])
            somatotype_type, classification = self.classify_dominant_somatotype(somatotype_components)
            
            print(f"   📊 Somatotype Analysis: {classification}")
            
            # Step 2: Generate exercise recommendations
            exercise_recs = self.generate_exercise_recommendations(user_data, somatotype_type)
            print(f"   🏋️ Exercise Focus: {exercise_recs['focus']}")
            
            # Step 3: Generate diet recommendations
            diet_recs = self.generate_diet_recommendations(user_data, somatotype_type)
            print(f"   🍽️ Daily Calories: {diet_recs['total_calories']} kcal")
            print(f"   📏 BMI: {diet_recs['anthropometric_data']['bmi']} ({diet_recs['anthropometric_data']['bmi_category']})")
            
            # Compile results
            user_results = {
                'user_info': user_data,
                'anthropometric_analysis': diet_recs['anthropometric_data'],
                'somatotype_analysis': {
                    'components': somatotype_components,
                    'dominant_type': somatotype_type,
                    'classification': classification,
                    'profile': self.somatotype_profiles[somatotype_type]
                },
                'exercise_recommendations': exercise_recs,
                'diet_recommendations': diet_recs,
                'simulation_metadata': {
                    'processed_date': datetime.now().isoformat(),
                    'datasets_used': ['universal_exercises_database', 'optimized_diet_recommendation_database'],
                    'method': 'Heath-Carter Somatotype Classification + Mifflin-St Jeor BMR'
                }
            }
            
            simulation_results.append(user_results)
        
        # Generate output report
        self.generate_simulation_report(simulation_results)
        
        print(f"\n✅ Simulation Complete!")
        print(f"📁 Results saved to: {os.path.join(self.simulation_path, 'simulation_results.txt')}")
        
        return simulation_results
    
    def generate_simulation_report(self, results):
        """Generate comprehensive simulation report"""
        
        report_lines = []
        
        # Header
        report_lines.extend([
            "="*80,
            "SOMATOTYPE-BASED DIET & EXERCISE RECOMMENDATION SIMULATION",
            "="*80,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Method: Heath-Carter Somatotype Classification",
            f"Users Processed: {len(results)}",
            "",
            "SIMULATION OVERVIEW:",
            "This simulation demonstrates the complete workflow from user input",
            "through somatotype classification to personalized recommendations.",
            "",
            "="*80,
            ""
        ])
        
        # Process each user
        for i, result in enumerate(results, 1):
            user = result['user_info']
            anthro = result['anthropometric_analysis']
            somatotype = result['somatotype_analysis']
            exercise = result['exercise_recommendations']
            diet = result['diet_recommendations']
            
            report_lines.extend([
                f"USER {i}: {user['Name'].upper()}",
                "-"*50,
                "",
                "📋 USER INPUT:",
                f"   Name: {user['Name']}",
                f"   Weight: {user['Weight']} kg",
                f"   Gender: {user['Gender']}",
                f"   Height: {user['Height']} cm",
                f"   Age: {user['Age']} years",
                f"   Goal: {user['Goal']}",
                f"   Activity Level: {user['Activity_Level']}",
                f"   Somatotype Rating: {user['Somatotype']} (Heath-Carter)",
                "",
                "📏 ANTHROPOMETRIC ANALYSIS:",
                f"   BMI: {anthro['bmi']} ({anthro['bmi_category']})",
                f"   Healthy Weight Range: {anthro['healthy_weight_range']}",
                f"   Basal Metabolic Rate (BMR): {anthro['bmr']} kcal/day",
                f"   Total Daily Energy Expenditure (TDEE): {anthro['tdee']} kcal/day",
                "",
                "📊 SOMATOTYPE ANALYSIS:",
                f"   Raw Components: Endomorphy={somatotype['components']['endomorphy']}, "
                f"Mesomorphy={somatotype['components']['mesomorphy']}, "
                f"Ectomorphy={somatotype['components']['ectomorphy']}",
                f"   Dominant Type: {somatotype['dominant_type'].title()}",
                f"   Classification: {somatotype['classification']}",
                f"   Description: {somatotype['profile']['description']}",
                "",
                "   Key Characteristics:",
                *[f"     • {char}" for char in somatotype['profile']['characteristics']],
                "",
                "🏋️ EXERCISE RECOMMENDATION ANALYSIS:",
                f"   Primary Training Focus: {exercise['focus']}",
                f"   Goal Alignment: {exercise.get('goal_alignment', 'General fitness')}",
                f"   Somatotype Rationale: {exercise.get('somatotype_rationale', 'Balanced approach')}",
                "",
                "   Training Parameters:",
                f"     • Weekly Frequency: {exercise['weekly_frequency']}",
                f"     • Session Duration: {exercise['session_duration']}",
                f"     • Intensity: Moderate to high",
                f"     • Progression: Linear progression suitable for {somatotype['dominant_type']}s",
                "",
                f"   {somatotype['dominant_type'].title()}-Specific Training Benefits:",
                *[f"     • {benefit}" for benefit in self.get_training_benefits(somatotype['dominant_type'])],
                "",
                "   Somatotype-Specific Exercise Selection:",
                "   Based on Universal Exercise Database + Goal/Activity Optimization:",
                "",
            ])
            
            # Add detailed exercise analysis with better categorization
            if len(exercise['exercises']) > 0:
                strength_exercises = []
                cardio_exercises = []
                power_exercises = []
                functional_exercises = []
                
                for idx, (_, ex) in enumerate(exercise['exercises'].head(8).iterrows(), 1):
                    if 'name' in ex:
                        category = ex.get('primary_training_category', 'General Training')
                        target = ex.get('target_muscles', 'Various muscle groups')
                        
                        exercise_line = f"     {idx}. {ex['name']} - {self.get_exercise_description(ex['name'])}"
                        exercise_line += f" (Target: {target})"
                        
                        if 'Strength' in category:
                            strength_exercises.append(exercise_line)
                        elif 'Cardiovascular' in category or 'Cardio' in category:
                            cardio_exercises.append(exercise_line)
                        elif 'Power' in category:
                            power_exercises.append(exercise_line)
                        elif 'Functional' in category:
                            functional_exercises.append(exercise_line)
                        else:
                            # Default to strength for unknown categories
                            strength_exercises.append(exercise_line)
                
                # Display exercises by category
                if strength_exercises:
                    percentage = int(len(strength_exercises)/len(exercise['exercises'])*100)
                    report_lines.extend([
                        f"   **Strength Training ({percentage}% of routine):**"
                    ])
                    report_lines.extend(strength_exercises[:5])  # Limit to 5 per category
                    report_lines.append("")
                
                if power_exercises:
                    percentage = int(len(power_exercises)/len(exercise['exercises'])*100)
                    report_lines.extend([
                        f"   **Power Training ({percentage}% of routine):**"
                    ])
                    report_lines.extend(power_exercises[:3])
                    report_lines.append("")
                
                if cardio_exercises:
                    percentage = int(len(cardio_exercises)/len(exercise['exercises'])*100)
                    report_lines.extend([
                        f"   **Cardiovascular Training ({percentage}% of routine):**"
                    ])
                    report_lines.extend(cardio_exercises[:4])
                    report_lines.append("")
                
                if functional_exercises:
                    percentage = int(len(functional_exercises)/len(exercise['exercises'])*100)
                    report_lines.extend([
                        f"   **Functional Training ({percentage}% of routine):**"
                    ])
                    report_lines.extend(functional_exercises[:3])
                    report_lines.append("")
            else:
                report_lines.extend([
                    "     1. Bodyweight squats (Strength) - Target: Legs, glutes",
                    "     2. Push-ups (Strength) - Target: Chest, arms",
                    "     3. Walking/Jogging (Cardio) - Target: Cardiovascular system"
                ])
            
            report_lines.extend([
                "",
                "🍽️ NUTRITION RECOMMENDATION ANALYSIS:",
                "",
                "   Caloric Distribution:",
                f"     • Total Daily Calories: {diet['total_calories']} kcal",
                f"     • Base TDEE: {diet['base_tdee']} kcal (activity-adjusted)",
                f"     • Goal Adjustment: {self.get_goal_adjustment_text(user['Goal'], diet['total_calories'], diet['base_tdee'])}",
                "",
                "   Macronutrient Breakdown:",
                f"   | Macro         | Grams | Calories | Percentage | {somatotype['dominant_type'].title()} Rationale |",
                f"   |---------------|-------|----------|------------|---------------------|",
                f"   | Protein       | {diet['protein_grams']}g  | {diet['protein_grams']*4} kcal  | {round(diet['protein_grams']*4/diet['total_calories']*100)}%        | {self.get_protein_rationale(somatotype['dominant_type'])} |",
                f"   | Carbohydrates | {diet['carb_grams']}g  | {diet['carb_grams']*4} kcal  | {round(diet['carb_grams']*4/diet['total_calories']*100)}%        | {self.get_carb_rationale(somatotype['dominant_type'])} |",
                f"   | Fats          | {diet['fat_grams']}g  | {diet['fat_grams']*9} kcal  | {round(diet['fat_grams']*9/diet['total_calories']*100)}%        | {self.get_fat_rationale(somatotype['dominant_type'])} |",
                "",
                f"   {somatotype['dominant_type'].title()}-Specific Nutrition Strategy:",
                f"     • Meal Timing: {diet['timing']}",
                f"     • Pre-Workout: {self.get_preworkout_nutrition(somatotype['dominant_type'])}",
                f"     • Post-Workout: {self.get_postworkout_nutrition(somatotype['dominant_type'])}",
                f"     • Hydration: {diet['hydration']}",
                "",
                "   Food Category Analysis:",
                "",
                f"   **Proteins (Lean sources for {somatotype['dominant_type']}s):**",
                *self.get_food_category_analysis('proteins', somatotype['dominant_type']),
                "",
                f"   **Carbohydrates (Optimized for {somatotype['dominant_type']} metabolism):**",
                *self.get_food_category_analysis('carbohydrates', somatotype['dominant_type']),
                "",
                f"   **Fats (Strategic selection for {somatotype['dominant_type']}s):**",
                *self.get_food_category_analysis('fats', somatotype['dominant_type']),
                "",
                "💡 PERSONALIZATION FACTORS:",
                f"   • BMI analysis: {anthro['bmi']} ({anthro['bmi_category']})",
                f"   • Gender-specific BMR calculation: {anthro['bmr']} kcal/day",
                f"   • Activity-adjusted TDEE: {anthro['tdee']} kcal/day",
                f"   • Somatotype-specific metabolism considerations",
                f"   • Goal-oriented calorie and macro adjustments",
                f"   • Activity level modifications for energy needs",
                f"   • Age-appropriate nutritional requirements",
                "",
                "📈 EXPECTED OUTCOMES:",
            ])
            
            # Add expected outcomes based on somatotype and goal
            if somatotype['dominant_type'] == 'ectomorph':
                if user['Goal'] in ['Gain Weight', 'Build Muscle']:
                    report_lines.extend([
                        "   • Gradual weight gain (0.5-1 lb/week)",
                        "   • Increased muscle mass with consistent training",
                        "   • Improved strength and body composition"
                    ])
                else:
                    report_lines.extend([
                        "   • Maintained lean body mass",
                        "   • Stable energy levels throughout the day",
                        "   • Improved overall fitness and strength"
                    ])
            elif somatotype['dominant_type'] == 'mesomorph':
                report_lines.extend([
                    "   • Balanced body composition improvements",
                    "   • Good response to both strength and cardio training",
                    "   • Efficient progress toward fitness goals"
                ])
            else:  # endomorph
                if user['Goal'] == 'Lose Weight':
                    report_lines.extend([
                        "   • Steady fat loss (1-2 lbs/week)",
                        "   • Improved metabolic health",
                        "   • Better insulin sensitivity"
                    ])
                else:
                    report_lines.extend([
                        "   • Weight maintenance with improved body composition",
                        "   • Enhanced cardiovascular fitness",
                        "   • Better energy regulation"
                    ])
            
            report_lines.extend([
                "",
                "="*80,
                ""
            ])
        
        # Add summary
        report_lines.extend([
            "SIMULATION SUMMARY:",
            "-"*30,
            "",
            "This simulation demonstrates how somatotype classification",
            "can be used to personalize both exercise and nutrition",
            "recommendations. The Heath-Carter method provides a",
            "scientific foundation for understanding body composition",
            "and metabolic tendencies.",
            "",
            "Key Benefits of Somatotype-Based Recommendations:",
            "• Personalized approach based on genetic predisposition",
            "• Optimized training methods for body type",
            "• Customized nutrition for metabolic characteristics",
            "• Realistic goal setting and expectations",
            "",
            "Data Sources:",
            "• Universal Exercise Database (1,500+ exercises)",
            "• FNDDS Optimized Nutrition Database (5,000+ foods)",
            "• Evidence-based somatotype research",
            "• Activity level and goal-specific modifications",
            "",
            f"Simulation completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "="*80
        ])
        
        # Save report
        output_file = os.path.join(self.simulation_path, 'simulation_results.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

def main():
    """Main execution function"""
    simulator = SomatotypeRecommendationSimulator()
    results = simulator.run_simulation()
    
    print(f"\n🎉 Simulation complete! Check simulation_results.txt for detailed output.")

if __name__ == "__main__":
    main()
