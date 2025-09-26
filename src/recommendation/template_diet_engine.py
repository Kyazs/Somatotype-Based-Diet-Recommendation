#!/usr/bin/env python3
"""
Template-based Diet Recommendation Engine

This module provides diet recommendations based on the provisional diet template CSV.
It matches user characteristics (somatotype, goal, activity level, exercise preferences)
to pre-defined diet templates and generates meal recommendations.
"""

import pandas as pd
import json
import os
import sys
from typing import Dict, List, Optional
import numpy as np

# Add project root to path
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(PROJECT_DIR)

from src.utils.utils import OUTPUT_FILES_DIR, INPUT_FILES_DIR

class TemplateDietEngine:
    """
    Template-based diet recommendation system using provisional diet template
    """
    
    def __init__(self):
        """Initialize the template diet engine"""
        self.diet_template_path = os.path.join(os.path.dirname(__file__), "provisional_diet_template.csv")
        self.diet_templates = None
        self._load_templates()
    
    def _load_templates(self):
        """Load diet templates from CSV file"""
        try:
            self.diet_templates = pd.read_csv(self.diet_template_path)
            print(f"OK - Loaded {len(self.diet_templates)} diet templates")
        except Exception as e:
            print(f"ERROR - Error loading diet templates: {e}")
            self.diet_templates = pd.DataFrame()
    
    def _normalize_somatotype(self, somatotype_class):
        """Normalize somatotype classification to match template format"""
        somatotype_map = {
            # Primary somatotypes
            'Ecto': 'ectomorph',
            'Meso': 'mesomorph', 
            'Endo': 'endomorph',
            'Ectomorph': 'ectomorph',
            'Mesomorph': 'mesomorph',
            'Endomorph': 'endomorph',
            # Mixed somatotypes - now map to specific mixed types
            'Ecto-Meso': 'meso_ecto',
            'Meso-Ecto': 'meso_ecto',
            'Endo-Meso': 'endo_meso',
            'Meso-Endo': 'endo_meso',
            'Ecto-Endo': 'ecto_endo',
            'Endo-Ecto': 'ecto_endo',
            # Alternative naming conventions
            'EctoMeso': 'meso_ecto',
            'MesoEcto': 'meso_ecto',
            'EndoMeso': 'endo_meso',
            'MesoEndo': 'endo_meso',
            'EctoEndo': 'ecto_endo',
            'EndoEcto': 'ecto_endo'
        }
        return somatotype_map.get(somatotype_class, 'mesomorph')
    
    def _normalize_goal(self, goal):
        """Normalize goal to match template format"""
        goal_map = {
            'Lose Weight': 'weight_loss',
            'Gain Weight': 'weight_gain', 
            'Maintain Weight': 'maintenance',
            'Build Muscle': 'weight_gain',
            'Muscle Gain': 'weight_gain',
            'Fat Loss': 'weight_loss',
            'Weight Loss': 'weight_loss',
            'Weight Gain': 'weight_gain',
            'Maintenance': 'maintenance'
        }
        return goal_map.get(goal, 'maintenance')
    
    def _normalize_activity_level(self, activity_level):
        """Normalize activity level to match template format"""
        if 'sedentary' in activity_level.lower() or 'little' in activity_level.lower():
            return 'sedentary'
        elif 'lightly' in activity_level.lower():
            return 'light'
        elif 'moderately' in activity_level.lower():
            return 'moderate'
        elif 'very active' in activity_level.lower():
            return 'very_active'
        elif 'extra active' in activity_level.lower():
            return 'extremely_active'
        else:
            return 'moderate'  # Default
    
    def _normalize_exercise_type(self, exercise_type):
        """Normalize exercise type to match template format"""
        return exercise_type.lower() if exercise_type else 'bodyweight'
    
    def _normalize_exercise_complexity(self, exercise_complexity):
        """Normalize exercise complexity to match template format"""
        complexity_map = {
            'Beginner': 'beginner',
            'Intermediate': 'intermediate',
            'Advanced': 'advanced'
        }
        return complexity_map.get(exercise_complexity, 'beginner')
    
    def find_best_template(self, user_data, somatotype_data):
        """Find the best matching diet template based on user characteristics"""
        if self.diet_templates.empty:
            return None
        
        # Extract and normalize user characteristics
        gender = user_data.get('gender', 'male').lower()
        somatotype = self._normalize_somatotype(somatotype_data.get('Somatotype', 'Mesomorph'))
        goal = self._normalize_goal(user_data.get('Goal', 'Maintain Weight'))
        activity = self._normalize_activity_level(user_data.get('Activity_Level', 'Moderately active'))
        exercise_type = self._normalize_exercise_type(user_data.get('Exercise_Type', 'bodyweight'))
        exercise_complexity = self._normalize_exercise_complexity(user_data.get('Exercise_Complexity', 'beginner'))
        
        print(f"INFO - Searching for template with:")
        print(f"   Gender: {gender}")
        print(f"   Somatotype: {somatotype}")  
        print(f"   Goal: {goal}")
        print(f"   Activity: {activity}")
        print(f"   Exercise Type: {exercise_type}")
        print(f"   Exercise Complexity: {exercise_complexity}")
        
        # Try exact match first
        exact_matches = self.diet_templates[
            (self.diet_templates['gender'] == gender) &
            (self.diet_templates['somatotype'] == somatotype) &
            (self.diet_templates['goal'] == goal) &
            (self.diet_templates['activity_level'] == activity) &
            (self.diet_templates['exercise_type'] == exercise_type) &
            (self.diet_templates['exercise_complexity'] == exercise_complexity)
        ]
        
        if not exact_matches.empty:
            print(f"OK - Found {len(exact_matches)} exact matches")
            return exact_matches.iloc[0].to_dict()
        
        # If no exact match, use progressive filtering with scoring
        print("INFO - No exact match found, using progressive matching...")
        
        # Start with mandatory filters
        filtered_templates = self.diet_templates[
            (self.diet_templates['gender'] == gender) &
            (self.diet_templates['somatotype'] == somatotype)
        ]
        
        if filtered_templates.empty:
            # Try mixed somatotype matching for compatibility
            if somatotype in ['ecto_endo', 'meso_ecto', 'endo_meso']:
                primary_types = somatotype.split('_')
                for primary_type in primary_types:
                    fallback_templates = self.diet_templates[
                        (self.diet_templates['gender'] == gender) &
                        (self.diet_templates['somatotype'] == primary_type)
                    ]
                    if not fallback_templates.empty:
                        filtered_templates = fallback_templates
                        print(f"INFO - Using fallback somatotype: {primary_type}")
                        break
            
            if filtered_templates.empty:
                print(f"ERROR - No templates found for {gender} {somatotype}")
                return None
        
        # Score remaining templates for best match
        templates_with_scores = []
        for idx, template in filtered_templates.iterrows():
            score = 0
            
            # Goal match (most important - 40 points)
            if template['goal'] == goal:
                score += 40
            elif (goal in ['weight_loss', 'cutting'] and template['goal'] in ['weight_loss', 'cutting']) or \
                 (goal in ['weight_gain', 'bulking', 'muscle_gain'] and template['goal'] in ['weight_gain', 'bulking', 'muscle_gain']):
                score += 20  # Related goals get partial credit
                
            # Activity level match (25 points)
            if template['activity_level'] == activity:
                score += 25
                
            # Exercise type match (20 points)
            if template['exercise_type'] == exercise_type:
                score += 20
                
            # Exercise complexity match (15 points)
            if template['exercise_complexity'] == exercise_complexity:
                score += 15
            
            templates_with_scores.append((score, template))
        
        if templates_with_scores:
            # Sort by score and return the best match
            templates_with_scores.sort(key=lambda x: x[0], reverse=True)
            best_score, best_template = templates_with_scores[0]
            print(f"OK - Found best partial match with score: {best_score}/100")
            print(f"   Template: {best_template['description']}")
            return best_template.to_dict()
        
        print("ERROR - No matching templates found")
        return None
    
    def _safe_split(self, value, separator):
        """Safely split a value, handling NaN and empty values"""
        if pd.isna(value) or not value or (isinstance(value, float) and np.isnan(value)):
            return []
        return str(value).split(separator)
    
    def _safe_int(self, value):
        """Safely convert to int, handling NaN values"""
        if pd.isna(value):
            return 0
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return 0
    
    def _safe_str(self, value):
        """Safely convert to string, handling NaN values"""
        if pd.isna(value):
            return ""
        return str(value)
    
    def _generate_exercise_recommendations(self, template):
        """Generate exercise recommendations based on exercise type preference"""
        exercise_type = template.get('exercise_type', 'gym')
        exercise_complexity = template.get('exercise_complexity', 'beginner')
        
        exercise_data = {
            "exercise_type": exercise_type,
            "exercise_complexity": exercise_complexity,
            "strength_days": self._safe_int(template['fitness_split_strength']),
            "cardio_days": self._safe_int(template['fitness_split_cardio'])
        }
        
        if exercise_type == 'gym':
            # For gym workouts, include push/pull/legs split
            exercise_data.update({
                "workout_split": "push_pull_legs",
                "push_exercises": self._safe_split(template['push_exercises'], ','),
                "pull_exercises": self._safe_split(template['pull_exercises'], ','),
                "legs_exercises": self._safe_split(template['legs_exercises'], ','),
                "workout_description": f"Gym-based {exercise_complexity} program with push/pull/legs split"
            })
        else:
            # For bodyweight workouts, include bodyweight exercises
            exercise_data.update({
                "workout_split": "bodyweight_full_body",
                "bodyweight_exercises": self._safe_split(template['bodyweight_exercises'], ','),
                "workout_description": f"Bodyweight {exercise_complexity} program for full-body training"
            })
        
        return exercise_data
    
    def generate_meal_recommendations(self, template):
        """Generate meal recommendations from the template"""
        if not template:
            return {}
        
        meal_recommendations = {
            "template_id": template.get('template_id', 'unknown'),
            "description": self._safe_str(template['description']),
            "total_calories": int(template['total_calories']),
            "macronutrients": {
                "protein_g": float(template['protein_g']),
                "carbs_g": float(template['carbs_g']),
                "fats_g": float(template['fats_g']),
                "protein_pct": float(template['protein_pct']),
                "carbs_pct": float(template['carbs_pct']),
                "fats_pct": float(template['fats_pct'])
            },
            "meals": {
                "breakfast": {
                    "foods": self._safe_split(template['breakfast_foods'], ' | '),
                    "description": "Start your day with these nutritious foods"
                },
                "lunch": {
                    "foods": self._safe_split(template['lunch_foods'], ' | '),
                    "description": "Maintain energy with this balanced midday meal"
                },
                "dinner": {
                    "foods": self._safe_split(template['dinner_foods'], ' | '),
                    "description": "End your day with these satisfying foods"
                },
                "snacks": {
                    "foods": self._safe_split(template['snack_foods'], ' | '),
                    "description": "Healthy snacks to keep you fueled between meals"
                }
            },
            "diet_principles": self._safe_split(template['diet_principles'], ' | '),
            "fitness_strategy": self._safe_str(template['fitness_strategy']),
            "exercises": self._generate_exercise_recommendations(template)
        }
        
        return meal_recommendations
    
    def create_recommendations(self):
        """Main function to create diet recommendations"""
        try:
            # Load user data
            user_input_file = os.path.join(INPUT_FILES_DIR, "input_info_recommendation.csv")
            if not os.path.exists(user_input_file):
                print(f"ERROR - User input file not found: {user_input_file}")
                return None
            
            user_df = pd.read_csv(user_input_file)
            user_data = user_df.iloc[0].to_dict() if not user_df.empty else {}
            
            # Load somatotype classification
            classification_file = os.path.join(OUTPUT_FILES_DIR, "output_classification.csv")
            if not os.path.exists(classification_file):
                print(f"ERROR - Classification file not found: {classification_file}")
                return None
            
            somatotype_df = pd.read_csv(classification_file)
            somatotype_data = somatotype_df.iloc[0].to_dict() if not somatotype_df.empty else {}
            
            # Find best template
            best_template = self.find_best_template(user_data, somatotype_data)
            if not best_template:
                return None
            
            # Generate meal recommendations
            meal_recommendations = self.generate_meal_recommendations(best_template)
            
            # Save to JSON file
            output_file = os.path.join(OUTPUT_FILES_DIR, "meal_recommendations.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(meal_recommendations, f, indent=2, ensure_ascii=False)
            
            print(f"OK - Meal recommendations saved to: {output_file}")
            return meal_recommendations
            
        except Exception as e:
            print(f"ERROR - Error creating recommendations: {e}")
            import traceback
            traceback.print_exc()
            return None

def main():
    """Test the template diet engine"""
    engine = TemplateDietEngine()
    recommendations = engine.create_recommendations()
    
    if recommendations:
        print("\nSUCCESS - MEAL RECOMMENDATIONS GENERATED:")
        print(f"Total Calories: {recommendations['total_calories']}")
        print(f"Protein: {recommendations['macronutrients']['protein_g']}g ({recommendations['macronutrients']['protein_pct']}%)")
        print(f"Carbs: {recommendations['macronutrients']['carbs_g']}g ({recommendations['macronutrients']['carbs_pct']}%)")
        print(f"Fats: {recommendations['macronutrients']['fats_g']}g ({recommendations['macronutrients']['fats_pct']}%)")
        print(f"\nBreakfast foods: {', '.join(recommendations['meals']['breakfast']['foods'][:3])}...")
    else:
        print("ERROR - Failed to generate recommendations")

if __name__ == "__main__":
    main()