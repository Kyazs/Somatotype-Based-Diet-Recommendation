#!/usr/bin/env python3
"""
Universal User Recommendation Engine

This script takes user input (Name, Age, Goal, Activity_Level) and generates 
personalized exercise and diet recommendations using the universal databases.

Example User Input:
Name,Age,Goal,Activity_Level
casper,21,Maintain Weight,Moderately active

Based on: ACSM Guidelines, NSCA Position Statements, and Nutrition Science

"""

import pandas as pd
import numpy as np
import os
import json
from typing import Dict, List, Tuple, Any

class UniversalRecommendationEngine:
    """
    Generates personalized recommendations for any user input
    """
    
    def __init__(self):
        self.base_path = r"c:\Users\LENOVO\Desktop\Kekious_Maximus\diet-recommendation-somatotype"
        self.fitness_processed = os.path.dirname(os.path.abspath(__file__))  # Current directory (processed folder)
        self.diet_path = os.path.join(self.base_path, "diet_templates.csv")
        self.output_path = self.fitness_processed  # All outputs go to processed folder
        
        # Load universal databases
        self.universal_exercises = self.load_universal_exercises()
        self.diet_templates = self.load_diet_database()
        
        # Goal normalization mapping
        self.goal_mapping = {
            'maintain weight': 'maintain_weight',
            'maintain': 'maintain_weight', 
            'lose weight': 'lose_weight',
            'lose': 'lose_weight',
            'weight loss': 'lose_weight',
            'gain weight': 'gain_weight',
            'gain': 'gain_weight',
            'weight gain': 'gain_weight',
            'build muscle': 'build_muscle',
            'muscle': 'build_muscle',
            'muscle building': 'build_muscle',
            'improve fitness': 'improve_fitness',
            'fitness': 'improve_fitness',
            'general fitness': 'improve_fitness'
        }
        
        # Activity level normalization
        self.activity_mapping = {
            'sedentary': 'sedentary',
            'lightly active': 'lightly_active',
            'light': 'lightly_active',
            'moderately active': 'moderately_active',
            'moderate': 'moderately_active',
            'very active': 'very_active',
            'active': 'very_active',
            'extremely active': 'extremely_active',
            'extreme': 'extremely_active',
            'athlete': 'extremely_active'
        }
        
        # Age-based adjustments (evidence-based)
        self.age_factors = {
            'young_adult': (18, 30),      # Peak performance years
            'adult': (31, 45),            # Maintenance focus
            'middle_aged': (46, 60),      # Injury prevention focus
            'older_adult': (61, 100)      # Functional movement focus
        }
    
    def load_universal_exercises(self) -> pd.DataFrame:
        """Load the universal exercises database"""
        filepath = os.path.join(self.fitness_processed, 'universal_exercises_database.csv')
        return pd.read_csv(filepath)
    
    def load_diet_database(self) -> pd.DataFrame:
        """Load the diet templates database"""
        return pd.read_csv(self.diet_path)
    
    def normalize_user_input(self, goal: str, activity_level: str) -> Tuple[str, str]:
        """Normalize user input to match database keys"""
        goal_clean = goal.lower().strip()
        activity_clean = activity_level.lower().strip()
        
        normalized_goal = self.goal_mapping.get(goal_clean, 'improve_fitness')
        normalized_activity = self.activity_mapping.get(activity_clean, 'moderately_active')
        
        return normalized_goal, normalized_activity
    
    def determine_age_category(self, age: int) -> str:
        """Determine age category for appropriate recommendations"""
        for category, (min_age, max_age) in self.age_factors.items():
            if min_age <= age <= max_age:
                return category
        return 'adult'  # Default
    
    def calculate_age_adjustments(self, age: int) -> Dict[str, float]:
        """Calculate age-specific adjustments for recommendations"""
        age_category = self.determine_age_category(age)
        
        adjustments = {
            'young_adult': {
                'intensity_boost': 1.1,
                'recovery_factor': 1.0,
                'complexity_tolerance': 1.2,
                'volume_capacity': 1.1
            },
            'adult': {
                'intensity_boost': 1.0,
                'recovery_factor': 1.0,
                'complexity_tolerance': 1.0,
                'volume_capacity': 1.0
            },
            'middle_aged': {
                'intensity_boost': 0.9,
                'recovery_factor': 1.2,
                'complexity_tolerance': 0.9,
                'volume_capacity': 0.9
            },
            'older_adult': {
                'intensity_boost': 0.8,
                'recovery_factor': 1.4,
                'complexity_tolerance': 0.7,
                'volume_capacity': 0.8
            }
        }
        
        return adjustments[age_category]
    
    def generate_exercise_recommendations(self, name: str, age: int, goal: str, activity_level: str, num_recommendations: int = 20) -> pd.DataFrame:
        """Generate personalized exercise recommendations"""
        normalized_goal, normalized_activity = self.normalize_user_input(goal, activity_level)
        age_adjustments = self.calculate_age_adjustments(age)
        
        # Get goal and activity compatibility columns
        goal_column = f"{normalized_goal}_compatibility"
        activity_column = f"{normalized_activity}_suitability"
        
        # Create copy for calculations
        exercises = self.universal_exercises.copy()
        
        # Calculate personalized compatibility score
        exercises['goal_score'] = exercises[goal_column]
        exercises['activity_score'] = exercises[activity_column]
        
        # Age-based adjustments
        exercises['complexity_adjusted'] = exercises['complexity_level'] * age_adjustments['complexity_tolerance']
        
        # Adjust for high-intensity exercises based on age
        high_intensity_cols = ['power_development_score', 'calorie_expenditure_score', 'metabolic_conditioning_score']
        exercises['intensity_avg'] = exercises[high_intensity_cols].mean(axis=1)
        exercises['intensity_adjusted'] = exercises['intensity_avg'] * age_adjustments['intensity_boost']
        
        # Calculate final personalized score
        exercises['personalized_score'] = (
            exercises['goal_score'] * 0.4 +           # 40% goal compatibility
            exercises['activity_score'] * 0.3 +       # 30% activity suitability  
            exercises['overall_quality_score'] * 0.2 + # 20% exercise quality
            exercises['intensity_adjusted'] * 0.1      # 10% age-adjusted intensity
        )
        
        # Age-specific filtering
        if age >= 60:
            # Prioritize functional movement and balance for older adults
            exercises['personalized_score'] += (
                exercises['functional_movement_score'] * 0.1 +
                exercises['balance_coordination_score'] * 0.1
            )
            # Reduce complex movements
            exercises.loc[exercises['complexity_level'] >= 4, 'personalized_score'] *= 0.8
        
        elif age <= 25:
            # Young adults can handle more complex/intense exercises
            exercises['personalized_score'] += exercises['power_development_score'] * 0.05
        
        # Get top recommendations
        top_exercises = exercises.nlargest(num_recommendations, 'personalized_score').copy()
        
        # Add user-specific information
        top_exercises['recommended_for'] = name
        top_exercises['user_age'] = age
        top_exercises['user_goal'] = goal
        top_exercises['user_activity_level'] = activity_level
        top_exercises['age_category'] = self.determine_age_category(age)
        
        # Select relevant columns for output
        output_columns = [
            'name', 'primary_training_category', 'complexity_level', 
            'primary_equipment', 'target_muscles', 'personalized_score',
            'goal_score', 'activity_score', 'overall_quality_score',
            'cardiovascular_endurance_score', 'muscular_strength_score',
            'muscular_hypertrophy_score', 'functional_movement_score',
            'recommended_for', 'user_age', 'user_goal', 'user_activity_level'
        ]
        
        return top_exercises[output_columns]
    
    def generate_diet_recommendations(self, name: str, age: int, goal: str, activity_level: str, num_recommendations: int = 15) -> pd.DataFrame:
        """Generate personalized diet recommendations"""
        normalized_goal, normalized_activity = self.normalize_user_input(goal, activity_level)
        age_adjustments = self.calculate_age_adjustments(age)
        
        # Create copy for calculations
        diets = self.diet_templates.copy()
        
        # Goal-based scoring
        goal_weights = {
            'maintain_weight': {'protein': 0.3, 'carbs': 0.3, 'fat': 0.2, 'fiber': 0.2},
            'lose_weight': {'protein': 0.4, 'carbs': 0.2, 'fat': 0.15, 'fiber': 0.25},
            'gain_weight': {'protein': 0.35, 'carbs': 0.4, 'fat': 0.25, 'fiber': 0.0},
            'build_muscle': {'protein': 0.5, 'carbs': 0.3, 'fat': 0.15, 'fiber': 0.05},
            'improve_fitness': {'protein': 0.35, 'carbs': 0.35, 'fat': 0.2, 'fiber': 0.1}
        }
        
        weights = goal_weights.get(normalized_goal, goal_weights['improve_fitness'])
        
        # Activity level calorie adjustments
        activity_multipliers = {
            'sedentary': 0.9,
            'lightly_active': 1.0,
            'moderately_active': 1.1,
            'very_active': 1.2,
            'extremely_active': 1.3
        }
        
        calorie_multiplier = activity_multipliers[normalized_activity]
        
        # Age-based calorie adjustments
        if age >= 60:
            calorie_multiplier *= 0.95  # Slightly lower calorie needs
        elif age <= 25:
            calorie_multiplier *= 1.05  # Higher calorie needs
        
        # Calculate personalized nutrition score  
        diets['personalized_nutrition_score'] = (
            diets['protein_g'] / diets['protein_g'].max() * weights['protein'] * 10 +
            diets['carbs_g'] / diets['carbs_g'].max() * weights['carbs'] * 10 +
            diets['fats_g'] / diets['fats_g'].max() * weights['fat'] * 10
        )
        
        # Add fiber score if fiber column exists
        if 'fiber_g' in diets.columns:
            diets['personalized_nutrition_score'] += diets['fiber_g'] / diets['fiber_g'].max() * weights['fiber'] * 10
        
        # Adjust calories based on activity and age
        if 'calories' in diets.columns:
            diets['adjusted_calories'] = diets['calories'] * calorie_multiplier
        else:
            # Estimate calories from macros if calories column doesn't exist
            diets['adjusted_calories'] = (diets['protein_g'] * 4 + diets['carbs_g'] * 4 + diets['fats_g'] * 9) * calorie_multiplier
        
        # Penalize extreme calorie values
        if normalized_goal == 'lose_weight':
            diets.loc[diets['adjusted_calories'] > 2000, 'personalized_nutrition_score'] *= 0.8
        elif normalized_goal == 'gain_weight':
            diets.loc[diets['adjusted_calories'] < 2200, 'personalized_nutrition_score'] *= 0.8
        
        # Get top recommendations
        top_diets = diets.nlargest(num_recommendations, 'personalized_nutrition_score').copy()
        
        # Add user-specific information
        top_diets['recommended_for'] = name
        top_diets['user_age'] = age
        top_diets['user_goal'] = goal
        top_diets['user_activity_level'] = activity_level
        top_diets['calorie_adjustment'] = round(calorie_multiplier, 2)
        
        return top_diets
    
    def generate_complete_user_profile(self, user_data: Dict) -> Dict[str, Any]:
        """Generate complete user profile with recommendations"""
        name = user_data['name']
        age = int(user_data['age'])
        goal = user_data['goal']
        activity_level = user_data['activity_level']
        
        # Generate recommendations
        exercise_recs = self.generate_exercise_recommendations(name, age, goal, activity_level, 20)
        diet_recs = self.generate_diet_recommendations(name, age, goal, activity_level, 15)
        
        # Calculate summary statistics
        age_category = self.determine_age_category(age)
        normalized_goal, normalized_activity = self.normalize_user_input(goal, activity_level)
        
        profile = {
            'user_info': {
                'name': name,
                'age': age,
                'age_category': age_category,
                'goal': goal,
                'normalized_goal': normalized_goal,
                'activity_level': activity_level,
                'normalized_activity': normalized_activity
            },
            'exercise_summary': {
                'total_recommendations': len(exercise_recs),
                'avg_personalized_score': round(exercise_recs['personalized_score'].mean(), 1),
                'top_training_category': exercise_recs['primary_training_category'].iloc[0],
                'avg_complexity': round(exercise_recs['complexity_level'].mean(), 1),
                'strength_focus_percentage': round((exercise_recs['primary_training_category'] == 'Strength Training').mean() * 100, 1)
            },
            'diet_summary': {
                'total_recommendations': len(diet_recs),
                'avg_nutrition_score': round(diet_recs['personalized_nutrition_score'].mean(), 1),
                'avg_calories': round(diet_recs['adjusted_calories'].mean(), 0),
                'avg_protein': round(diet_recs['protein_g'].mean(), 1),
                'avg_carbs': round(diet_recs['carbs_g'].mean(), 1),
                'avg_fat': round(diet_recs['fats_g'].mean(), 1)
            }
        }
        
        return profile, exercise_recs, diet_recs
    
    def process_user_input_file(self, input_file: str) -> None:
        """Process a CSV file with user inputs and generate all recommendations"""
        # Read user input file
        users_df = pd.read_csv(input_file)
        
        print(f"🎯 Processing {len(users_df)} user(s) from {input_file}")
        print("=" * 60)
        
        for idx, user_row in users_df.iterrows():
            user_data = {
                'name': user_row['Name'],
                'age': user_row['Age'],
                'goal': user_row['Goal'], 
                'activity_level': user_row['Activity_Level']
            }
            
            print(f"\n👤 Processing User {idx + 1}: {user_data['name'].title()}")
            print(f"   Age: {user_data['age']} | Goal: {user_data['goal']} | Activity: {user_data['activity_level']}")
            
            # Generate complete profile
            profile, exercise_recs, diet_recs = self.generate_complete_user_profile(user_data)
            
            # Save individual user files
            user_name = user_data['name'].lower().replace(' ', '_')
            
            # Exercise recommendations
            exercise_file = os.path.join(self.output_path, f"user_exercises_{user_name}.csv")
            exercise_recs.to_csv(exercise_file, index=False)
            
            # Diet recommendations
            diet_file = os.path.join(self.output_path, f"user_diet_{user_name}.csv")
            diet_recs.to_csv(diet_file, index=False)
            
            # User profile summary
            profile_file = os.path.join(self.output_path, f"user_profile_{user_name}.json")
            with open(profile_file, 'w') as f:
                json.dump(profile, f, indent=2)
            
            # Print summary
            print(f"   ✅ Exercise Recommendations: {profile['exercise_summary']['total_recommendations']} exercises")
            print(f"      Top Category: {profile['exercise_summary']['top_training_category']}")
            print(f"      Avg Score: {profile['exercise_summary']['avg_personalized_score']}/10")
            print(f"   ✅ Diet Recommendations: {profile['diet_summary']['total_recommendations']} meals")
            print(f"      Avg Calories: {profile['diet_summary']['avg_calories']} kcal")
            print(f"      Avg Protein: {profile['diet_summary']['avg_protein']}g")
            print(f"   📁 Files: {os.path.basename(exercise_file)}, {os.path.basename(diet_file)}, {os.path.basename(profile_file)}")
            print(f"   📂 Location: {self.output_path}")
        
        print(f"\n🎉 All {len(users_df)} user(s) processed successfully!")

def main():
    """Main execution function"""
    # Create example user input file in current directory (processed folder)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    example_users = pd.DataFrame([
        {'Name': 'casper', 'Age': 21, 'Goal': 'Maintain Weight', 'Activity_Level': 'Moderately active'},
        {'Name': 'alice', 'Age': 35, 'Goal': 'Lose Weight', 'Activity_Level': 'Lightly active'},
        {'Name': 'bob', 'Age': 28, 'Goal': 'Build Muscle', 'Activity_Level': 'Very active'},
        {'Name': 'carol', 'Age': 55, 'Goal': 'Improve Fitness', 'Activity_Level': 'Moderately active'},
        {'Name': 'david', 'Age': 19, 'Goal': 'Gain Weight', 'Activity_Level': 'Extremely active'}
    ])
    
    example_file = os.path.join(current_dir, 'example_user_inputs.csv')
    example_users.to_csv(example_file, index=False)
    print(f"📝 Created example user input file: {example_file}")
    
    # Process the users
    engine = UniversalRecommendationEngine()
    engine.process_user_input_file(example_file)

if __name__ == "__main__":
    main()
