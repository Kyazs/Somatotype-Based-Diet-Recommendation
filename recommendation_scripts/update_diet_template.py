#!/usr/bin/env python3
"""
Somatotype-Based Diet and Fitness Template Generator (Filipino Foods Edition)

This script generates comprehensive diet and fitness recommendations based on:
- Somatotype classification (Endomorph, Mesomorph, Ectomorph, and mixed types)
- User preferences (Gender, Goal, Activity Level, Exercise Complexity, Exercise Type)
- Scientific guidelines from the Somatotype Diet and Fitness Manual
- Foods commonly available in the Philippines

The script creates detailed templates with:
- Macronutrient recommendations
- Food suggestions from Filipino-available foods only
- Exercise recommendations with specific exercise IDs
- Caloric calculations based on activity level and goals
"""

import pandas as pd
import json
import numpy as np
import os
from typing import Dict, List, Tuple, Any

class SomatotypeDietFitnessGenerator:
    def __init__(self, base_path: str):
        """Initialize the generator with data file paths."""
        self.base_path = base_path
        self.diet_db_path = os.path.join(base_path, "data/datasets/diet/fndds_processed/optimized_diet_recommendation_database.csv")
        self.exercises_path = os.path.join(base_path, "data/datasets/fitness/data/exercises.json")
        self.outdoor_exercises_path = os.path.join(base_path, "data/datasets/fitness/data/outdoor_exercises.json")
        self.output_path = os.path.join(base_path, "enhanced_diet_templates_filipino.csv")
        
        # Load data
        self.diet_db = self._load_diet_database()
        self.gym_exercises = self._load_exercises()
        self.outdoor_exercises = self._load_outdoor_exercises()
        
        # Define somatotype characteristics and recommendations
        self._define_somatotype_specs()
        
    def _load_diet_database(self) -> pd.DataFrame:
        """Load the optimized diet recommendation database and filter for Filipino-available foods."""
        try:
            df = pd.read_csv(self.diet_db_path)
            print(f"✓ Loaded diet database with {len(df)} food items")
            
            # Filter for Filipino-available foods
            filipino_foods = self._get_filipino_available_foods()
            df_filtered = df[df['Food_Item'].isin(filipino_foods)]
            print(f"✓ Filtered to {len(df_filtered)} Filipino-available foods ({len(df_filtered)/len(df)*100:.1f}%)")
            
            return df_filtered
        except Exception as e:
            print(f"✗ Error loading diet database: {e}")
            return pd.DataFrame()
    
    def _load_exercises(self) -> List[Dict]:
        """Load gym exercises from JSON file."""
        try:
            with open(self.exercises_path, 'r', encoding='utf-8') as f:
                exercises = json.load(f)
            print(f"✓ Loaded {len(exercises)} gym exercises")
            return exercises
        except Exception as e:
            print(f"✗ Error loading gym exercises: {e}")
            return []
    
    def _load_outdoor_exercises(self) -> List[Dict]:
        """Load outdoor exercises from JSON file."""
        try:
            with open(self.outdoor_exercises_path, 'r', encoding='utf-8') as f:
                exercises = json.load(f)
            print(f"✓ Loaded {len(exercises)} outdoor exercises")
            return exercises
        except Exception as e:
            print(f"✗ Error loading outdoor exercises: {e}")
            return []
    
    def _get_filipino_available_foods(self) -> List[str]:
        """Get list of foods available in the Philippines."""
        # Load full database first to filter
        try:
            full_df = pd.read_csv(self.diet_db_path)
            
            # Define Filipino-available food keywords
            filipino_keywords = [
                # Grains and Starches
                'Rice', 'Oats', 'Quinoa', 'Bread', 'Pasta', 'Noodles', 'Wheat', 'Barley',
                
                # Proteins - Meat
                'Chicken', 'Pork', 'Beef', 'Turkey', 'Duck', 'Goat', 
                
                # Proteins - Seafood  
                'Fish', 'Tuna', 'Salmon', 'Tilapia', 'Bangus', 'Mackerel', 'Sardines', 
                'Shrimp', 'Crab', 'Squid', 'Calamari', 'Shellfish', 'Oyster', 'Clams',
                
                # Proteins - Others
                'Egg', 'Tofu', 'Tempeh', 'Beans', 'Lentils', 'Chickpeas', 'Peanut',
                
                # Dairy
                'Milk', 'Cheese', 'Yogurt', 'Cottage Cheese',
                
                # Vegetables
                'Broccoli', 'Spinach', 'Kale', 'Cabbage', 'Carrots', 'Lettuce', 'Cucumber',
                'Tomato', 'Onion', 'Garlic', 'Ginger', 'Bell Pepper', 'Eggplant', 'Squash',
                'Sweet Potato', 'Potato', 'Cassava', 'Taro', 'Mushroom', 'Seaweed',
                
                # Fruits
                'Banana', 'Mango', 'Papaya', 'Pineapple', 'Coconut', 'Avocado', 'Apple',
                'Orange', 'Grapes', 'Watermelon', 'Melon', 'Guava', 'Lemon', 'Lime',
                
                # Nuts and Seeds
                'Almonds', 'Cashews', 'Walnuts', 'Chia', 'Flax', 'Sunflower', 'Sesame',
                
                # Oils and Fats
                'Olive Oil', 'Coconut Oil', 'Vegetable Oil', 'Canola Oil', 'Butter',
                
                # Others
                'Honey', 'Brown Sugar', 'Soy Sauce', 'Vinegar', 'Ginger', 'Turmeric'
            ]
            
            # Find all foods containing these keywords
            available_foods = []
            for keyword in filipino_keywords:
                matches = full_df[full_df['Food_Item'].str.contains(keyword, case=False, na=False)]
                available_foods.extend(matches['Food_Item'].tolist())
            
            # Remove duplicates
            available_foods = list(set(available_foods))
            return available_foods
            
        except Exception as e:
            print(f"✗ Error filtering Filipino foods: {e}")
            return []
    
    def _define_somatotype_specs(self):
        """Define macronutrient ratios and characteristics for each somatotype based on the manual."""
        self.somatotype_specs = {
            'endomorph': {
                'description': 'Naturally soft and round, gains weight easily, slower metabolism',
                'macros': {
                    'weight_loss': {'carbs': 25, 'protein': 35, 'fat': 40},
                    'weight_gain': {'carbs': 30, 'protein': 35, 'fat': 35},  # Not typically recommended
                    'maintenance': {'carbs': 30, 'protein': 35, 'fat': 35}
                },
                'calorie_multipliers': {
                    'weight_loss': {'male': 10, 'female': 9},
                    'weight_gain': {'male': 15, 'female': 14},
                    'maintenance': {'male': 13, 'female': 12}
                },
                'preferred_foods': ['lean_proteins', 'healthy_fats', 'complex_carbs'],
                'exercise_focus': ['HIIT', 'strength_training', 'cardio']
            },
            'mesomorph': {
                'description': 'Naturally muscular and athletic, balanced metabolism',
                'macros': {
                    'weight_loss': {'carbs': 35, 'protein': 35, 'fat': 30},
                    'weight_gain': {'carbs': 50, 'protein': 25, 'fat': 25},
                    'maintenance': {'carbs': 40, 'protein': 30, 'fat': 30}
                },
                'calorie_multipliers': {
                    'weight_loss': {'male': 12, 'female': 11},
                    'weight_gain': {'male': 18, 'female': 16},
                    'maintenance': {'male': 15, 'female': 14}
                },
                'preferred_foods': ['complete_proteins', 'complex_carbs', 'healthy_fats'],
                'exercise_focus': ['strength_training', 'HIIT', 'cardio']
            },
            'ectomorph': {
                'description': 'Naturally slender and lean, fast metabolism, difficulty gaining weight',
                'macros': {
                    'weight_loss': {'carbs': 40, 'protein': 30, 'fat': 30},  # Rarely needed
                    'weight_gain': {'carbs': 50, 'protein': 30, 'fat': 20},
                    'maintenance': {'carbs': 45, 'protein': 30, 'fat': 25}
                },
                'calorie_multipliers': {
                    'weight_loss': {'male': 14, 'female': 13},
                    'weight_gain': {'male': 20, 'female': 18},
                    'maintenance': {'male': 17, 'female': 16}
                },
                'preferred_foods': ['complete_proteins', 'complex_carbs', 'healthy_fats'],
                'exercise_focus': ['strength_training', 'minimal_cardio']
            },
            'endo_meso': {
                'description': 'Muscular and strong but tends to gain fat easily',
                'macros': {
                    'weight_loss': {'carbs': 25, 'protein': 40, 'fat': 35},
                    'weight_gain': {'carbs': 35, 'protein': 35, 'fat': 30},
                    'maintenance': {'carbs': 30, 'protein': 35, 'fat': 35}
                },
                'calorie_multipliers': {
                    'weight_loss': {'male': 11, 'female': 10},
                    'weight_gain': {'male': 16, 'female': 15},
                    'maintenance': {'male': 14, 'female': 13}
                },
                'preferred_foods': ['lean_proteins', 'complex_carbs', 'healthy_fats'],
                'exercise_focus': ['strength_training', 'HIIT', 'cardio']
            },
            'meso_ecto': {
                'description': 'Naturally lean and athletic with visible muscle definition',
                'macros': {
                    'weight_loss': {'carbs': 35, 'protein': 35, 'fat': 30},
                    'weight_gain': {'carbs': 45, 'protein': 30, 'fat': 25},
                    'maintenance': {'carbs': 40, 'protein': 30, 'fat': 30}
                },
                'calorie_multipliers': {
                    'weight_loss': {'male': 13, 'female': 12},
                    'weight_gain': {'male': 19, 'female': 17},
                    'maintenance': {'male': 16, 'female': 15}
                },
                'preferred_foods': ['complete_proteins', 'complex_carbs', 'healthy_fats'],
                'exercise_focus': ['strength_training', 'HIIT', 'moderate_cardio']
            },
            'ecto_endo': {
                'description': 'Slender frame but tends to store fat, often "skinny-fat"',
                'macros': {
                    'weight_loss': {'carbs': 20, 'protein': 40, 'fat': 40},  # Phase 1: Fat loss
                    'weight_gain': {'carbs': 45, 'protein': 35, 'fat': 20},  # Phase 2: Muscle gain
                    'maintenance': {'carbs': 35, 'protein': 35, 'fat': 30}
                },
                'calorie_multipliers': {
                    'weight_loss': {'male': 10, 'female': 9},
                    'weight_gain': {'male': 17, 'female': 15},
                    'maintenance': {'male': 14, 'female': 13}
                },
                'preferred_foods': ['lean_proteins', 'complex_carbs', 'healthy_fats'],
                'exercise_focus': ['strength_training', 'HIIT', 'moderate_cardio']
            }
        }
        
        # Activity level multipliers
        self.activity_multipliers = {
            'sedentary': 1.2,
            'lightly_active': 1.375,
            'moderately_active': 1.55,
            'very_active': 1.725,
            'extra_active': 1.9
        }
        
    def calculate_calories_and_macros(self, somatotype: str, goal: str, gender: str, 
                                    activity_level: str, weight_lbs: float = 154) -> Dict:
        """Calculate total calories and macro breakdown."""
        specs = self.somatotype_specs[somatotype]
        
        # Base calorie calculation
        base_multiplier = specs['calorie_multipliers'][goal][gender]
        activity_mult = self.activity_multipliers[activity_level]
        
        total_calories = weight_lbs * base_multiplier * activity_mult
        
        # Macro ratios
        macros = specs['macros'][goal]
        
        # Calculate grams
        protein_cals = total_calories * (macros['protein'] / 100)
        carb_cals = total_calories * (macros['carbs'] / 100)
        fat_cals = total_calories * (macros['fat'] / 100)
        
        protein_g = protein_cals / 4  # 4 cal/g
        carbs_g = carb_cals / 4       # 4 cal/g
        fats_g = fat_cals / 9         # 9 cal/g
        
        return {
            'total_calories': round(total_calories),
            'protein_g': round(protein_g, 1),
            'carbs_g': round(carbs_g, 1),
            'fats_g': round(fats_g, 1),
            'protein_pct': macros['protein'],
            'carbs_pct': macros['carbs'],
            'fats_pct': macros['fat']
        }
    
    def get_meal_recommendations(self, somatotype: str, goal: str) -> Dict[str, List[str]]:
        """Get structured meal recommendations (breakfast, lunch, dinner, snacks) with Filipino foods."""
        specs = self.somatotype_specs[somatotype]
        
        if self.diet_db.empty:
            return {
                "breakfast": ["No food database available"],
                "lunch": ["No food database available"], 
                "dinner": ["No food database available"],
                "snacks": ["No food database available"]
            }
        
        # Filter foods based on goal
        if goal == 'weight_loss':
            filtered_foods = self.diet_db[self.diet_db['Weight_Loss_Score'] >= 6]
        elif goal == 'weight_gain':
            filtered_foods = self.diet_db[self.diet_db['Weight_Gain_Score'] >= 6]
        else:  # maintenance
            filtered_foods = self.diet_db[self.diet_db['Maintenance_Score'] >= 7]
        
        # Further filter by somatotype score
        somatotype_col = f'{somatotype.title()}_Score'
        if somatotype_col in filtered_foods.columns:
            filtered_foods = filtered_foods[filtered_foods[somatotype_col] >= 5]
        
        # Define Filipino-common foods by meal type
        meal_foods = self._get_filipino_meal_foods(filtered_foods)
        
        return meal_foods
    
    def _get_filipino_meal_foods(self, filtered_foods: pd.DataFrame) -> Dict[str, List[str]]:
        """Get Filipino meal foods organized by meal type."""
        
        # Define Filipino breakfast foods
        breakfast_keywords = ['egg', 'rice', 'milk', 'bread', 'oats', 'banana', 'coffee', 'cheese', 'yogurt']
        breakfast_foods = []
        for keyword in breakfast_keywords:
            matches = filtered_foods[filtered_foods['Food_Item'].str.contains(keyword, case=False, na=False)]
            if len(matches) > 0:
                breakfast_foods.extend(matches.head(2)['Food_Item'].tolist())
        
        # Define Filipino lunch/dinner foods  
        main_meal_keywords = ['chicken', 'fish', 'pork', 'beef', 'rice', 'beans', 'vegetables', 'soup', 'broccoli', 'carrots']
        lunch_foods = []
        dinner_foods = []
        for keyword in main_meal_keywords:
            matches = filtered_foods[filtered_foods['Food_Item'].str.contains(keyword, case=False, na=False)]
            if len(matches) > 0:
                lunch_foods.extend(matches.head(2)['Food_Item'].tolist())
                dinner_foods.extend(matches.head(2)['Food_Item'].tolist())
        
        # Define Filipino snack foods
        snack_keywords = ['nuts', 'peanut', 'fruit', 'banana', 'mango', 'crackers', 'yogurt', 'milk']
        snack_foods = []
        for keyword in snack_keywords:
            matches = filtered_foods[filtered_foods['Food_Item'].str.contains(keyword, case=False, na=False)]
            if len(matches) > 0:
                snack_foods.extend(matches.head(1)['Food_Item'].tolist())
        
        # Remove duplicates and limit to reasonable numbers
        breakfast_foods = list(dict.fromkeys(breakfast_foods))[:4]
        lunch_foods = list(dict.fromkeys(lunch_foods))[:4] 
        dinner_foods = list(dict.fromkeys(dinner_foods))[:4]
        snack_foods = list(dict.fromkeys(snack_foods))[:3]
        
        # Fallback to top-rated foods if categories are empty
        if not breakfast_foods:
            breakfast_foods = filtered_foods.head(4)['Food_Item'].tolist()
        if not lunch_foods:
            lunch_foods = filtered_foods.head(4)['Food_Item'].tolist()
        if not dinner_foods:
            dinner_foods = filtered_foods.head(4)['Food_Item'].tolist()
        if not snack_foods:
            snack_foods = filtered_foods.head(3)['Food_Item'].tolist()
            
        return {
            "breakfast": breakfast_foods,
            "lunch": lunch_foods,
            "dinner": dinner_foods, 
            "snacks": snack_foods
        }
    def get_diet_principles(self, somatotype: str, goal: str) -> List[str]:
        """Get diet principles based on somatotype and goal."""
        principles_map = {
            "endomorph": {
                "weight_loss": [
                    "Prioritize lean protein and healthy fats",
                    "Strictly limit refined carbohydrates and sugars", 
                    "Focus on high-fiber vegetables to stay full",
                    "Drink plenty of water to support metabolism"
                ],
                "maintenance": [
                    "Balance protein, healthy fats, and complex carbs",
                    "Control portions to avoid surplus calories",
                    "Time carbohydrates around workouts", 
                    "Incorporate a variety of nutrient-dense foods"
                ],
                "weight_gain": [
                    "Focus on complex carbohydrates for energy",
                    "Increase lean protein intake for muscle synthesis",
                    "Ensure a slight, clean caloric surplus",
                    "Don't neglect healthy fats for hormone function"
                ]
            },
            "mesomorph": {
                "weight_loss": [
                    "Slightly reduce carbohydrate intake",
                    "Keep protein intake high to preserve muscle",
                    "Focus on whole, unprocessed foods",
                    "Create a moderate calorie deficit"
                ],
                "maintenance": [
                    "Eat a balanced mix of all three macronutrients",
                    "Adjust calories based on daily activity level",
                    "Prioritize quality food sources",
                    "Listen to your body's hunger cues"
                ],
                "weight_gain": [
                    "Increase complex carbohydrates for workout fuel",
                    "Maintain high protein intake for muscle repair", 
                    "Achieve a moderate, clean caloric surplus",
                    "Eat consistently throughout the day"
                ]
            },
            "ectomorph": {
                "weight_loss": [
                    "Focus on a very small deficit to preserve muscle",
                    "Keep carbohydrate intake relatively high",
                    "Never skip meals",
                    "Prioritize protein to prevent muscle loss"
                ],
                "maintenance": [
                    "Embrace carbohydrates as your primary energy source",
                    "Eat frequent, smaller meals if needed",
                    "Ensure adequate protein for muscle maintenance",
                    "Don't shy away from healthy fats"
                ],
                "weight_gain": [
                    "High intake of complex carbohydrates is essential",
                    "Eat in a significant caloric surplus",
                    "Consume protein with every meal",
                    "Consider liquid nutrition (shakes) to add calories"
                ]
            },
            "endo-meso": {
                "weight_loss": [
                    "Higher protein and moderate fat to feel full",
                    "Control carbohydrates, especially simple sugars",
                    "Cycle carbs: more on training days, less on rest days",
                    "Maintain a consistent calorie deficit"
                ],
                "maintenance": [
                    "Balanced approach with a focus on protein",
                    "Adjust carbs based on workout intensity",
                    "Prioritize whole foods to manage body composition",
                    "Monitor portions closely"
                ],
                "weight_gain": [
                    "Focus on a lean bulk with a small caloric surplus",
                    "Use complex carbs strategically for energy",
                    "Keep protein high to support muscle growth",
                    "Avoid excessive 'dirty' bulking"
                ]
            },
            "meso-ecto": {
                "weight_loss": [
                    "Maintain a small deficit to reveal definition",
                    "Keep carbs relatively high to fuel performance",
                    "Ensure high protein intake to protect muscle",
                    "Focus on nutrient timing around workouts"
                ],
                "maintenance": [
                    "Eat to fuel performance with balanced macros",
                    "Ample carbohydrates for energy",
                    "Sufficient protein for recovery and strength",
                    "Don't neglect fats for hormonal health"
                ],
                "weight_gain": [
                    "Needs a consistent caloric surplus to add size",
                    "Higher carbohydrate intake is crucial",
                    "Prioritize protein post-workout",
                    "Eat frequently throughout the day"
                ]
            },
            "ecto-endo": {
                "weight_loss": [
                    "Prioritize protein to build muscle",
                    "Moderate healthy fats for satiety",
                    "Control carbohydrate intake, focusing on complex sources",
                    "Crucial to avoid sugary and processed foods"
                ],
                "maintenance": [
                    "Focus on body recomposition: building muscle while slowly losing fat",
                    "Eat a balanced diet around maintenance calories",
                    "Carbohydrates should be timed around workouts",
                    "Nutrient-dense foods are key"
                ],
                "weight_gain": [
                    "Aim for a very lean, slow bulk",
                    "Small caloric surplus from clean sources",
                    "Ample protein and complex carbs to support training",
                    "Monitor body composition closely"
                ]
            }
        }
        
        return principles_map.get(somatotype, {}).get(goal, [
            "Follow balanced nutrition principles",
            "Focus on whole, unprocessed foods",
            "Stay hydrated throughout the day",
            "Listen to your body's hunger cues"
        ])
    
    def get_fitness_strategy(self, somatotype: str) -> str:
        """Get general fitness strategy based on somatotype."""
        strategies = {
            "endomorph": "Combine consistent cardiovascular exercise to manage fat with strength training to build metabolic-boosting muscle.",
            "mesomorph": "Leverage natural athletic ability with performance-focused strength training and moderate cardio for cardiovascular health.",
            "ectomorph": "Prioritize resistance training with compound movements to stimulate muscle growth. Keep cardio minimal to preserve calories for building mass.",
            "endo-meso": "A power-building approach works well. Lift heavy to build on your strength base, but include regular HIIT or metabolic conditioning to keep body fat in check.",
            "meso-ecto": "Focus on athletic training and hypertrophy. Use compound lifts for strength and add isolation work for aesthetics. Cardio can be used for performance and health without much risk of muscle loss.",
            "ecto-endo": "The primary goal is body recomposition. Focus on full-body resistance training to increase overall muscle mass and metabolic rate. Supplement with moderate cardio, especially HIIT, to target fat stores."
        }
        
        return strategies.get(somatotype, "Follow a balanced approach of strength training and cardiovascular exercise.")
    
    def get_fitness_split(self, somatotype: str) -> List[int]:
        """Get recommended fitness split (strength days, cardio days) based on somatotype.""" 
        splits = {
            "endomorph": [3, 4],
            "mesomorph": [4, 2], 
            "ectomorph": [5, 1],
            "endo-meso": [4, 3],
            "meso-ecto": [4, 2],
            "ecto-endo": [4, 2]
        }
        
        return splits.get(somatotype, [4, 2])
    
    def get_exercise_recommendations(self, somatotype: str, goal: str, exercise_type: str, 
                                   complexity: str, gender: str) -> List[str]:
        """Get exercise recommendations with specific exercise IDs."""
        specs = self.somatotype_specs[somatotype]
        exercise_focus = specs['exercise_focus']
        
        exercises = []
        
        if exercise_type.lower() == 'gym':
            exercise_pool = self.gym_exercises
        else:  # outdoor
            exercise_pool = self.outdoor_exercises
        
        if not exercise_pool:
            return []
        
        # Exercise selection based on somatotype and goal
        selected_exercises = []
        
        # Target muscles and exercise types based on somatotype
        if somatotype in ['endomorph', 'endo_meso', 'ecto_endo']:
            # Focus on fat burning and metabolic exercises
            target_types = ['cardio', 'HIIT', 'full-body']
            target_muscles = ['cardiovascular system', 'core', 'glutes', 'legs']
            num_exercises = 6 if complexity == 'beginner' else 8 if complexity == 'intermediate' else 10
            
        elif somatotype in ['ectomorph']:
            # Focus on muscle building
            target_types = ['strength', 'compound']
            target_muscles = ['chest', 'back', 'shoulders', 'legs', 'arms']
            num_exercises = 5 if complexity == 'beginner' else 6 if complexity == 'intermediate' else 8
            
        else:  # mesomorph, meso_ecto
            # Balanced approach
            target_types = ['strength', 'cardio', 'HIIT']
            target_muscles = ['chest', 'back', 'shoulders', 'legs', 'core', 'cardiovascular system']
            num_exercises = 6 if complexity == 'beginner' else 8 if complexity == 'intermediate' else 10
        
        # Select exercises based on criteria
        cardio_count = 0
        strength_count = 0
        
        for exercise in exercise_pool:
            if len(selected_exercises) >= num_exercises:
                break
                
            exercise_name = exercise.get('name', '').lower()
            target_muscles_list = exercise.get('targetMuscles', [])
            body_parts = exercise.get('bodyParts', [])
            
            # Check if exercise matches criteria
            is_cardio = any(muscle in ['cardiovascular system'] for muscle in target_muscles_list) or \
                       any(part in ['cardio'] for part in body_parts)
            
            is_strength = any(muscle in target_muscles for muscle in target_muscles_list)
            
            # Balance cardio and strength based on somatotype
            if somatotype in ['endomorph', 'endo_meso', 'ecto_endo']:
                if is_cardio and cardio_count < num_exercises // 2:
                    selected_exercises.append(exercise['exerciseId'])
                    cardio_count += 1
                elif is_strength and strength_count < num_exercises // 2:
                    selected_exercises.append(exercise['exerciseId'])
                    strength_count += 1
            elif somatotype == 'ectomorph':
                if is_strength and strength_count < num_exercises:
                    selected_exercises.append(exercise['exerciseId'])
                    strength_count += 1
                elif len(selected_exercises) < num_exercises:  # Fill remaining with any suitable exercise
                    selected_exercises.append(exercise['exerciseId'])
            else:  # mesomorph, meso_ecto
                if (is_cardio and cardio_count < num_exercises // 3) or \
                   (is_strength and strength_count < 2 * num_exercises // 3):
                    selected_exercises.append(exercise['exerciseId'])
                    if is_cardio:
                        cardio_count += 1
                    else:
                        strength_count += 1
        
        return selected_exercises
    
    def generate_comprehensive_template(self) -> pd.DataFrame:
        """Generate comprehensive diet and fitness templates for all combinations."""
        templates = []
        
        somatotypes = ['endomorph', 'mesomorph', 'ectomorph', 'endo_meso', 'meso_ecto', 'ecto_endo']
        genders = ['male', 'female']
        goals = ['weight_loss', 'weight_gain', 'maintenance']
        activity_levels = ['sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extra_active']
        complexities = ['beginner', 'intermediate', 'hard']
        exercise_types = ['gym', 'outdoor']
        
        print("🏗️  Generating comprehensive diet and fitness templates...")
        
        total_combinations = len(somatotypes) * len(genders) * len(goals) * len(activity_levels) * len(complexities) * len(exercise_types)
        current = 0
        
        for somatotype in somatotypes:
            for gender in genders:
                for goal in goals:
                    # Skip weight gain for endomorphs as it's not typically recommended
                    if somatotype == 'endomorph' and goal == 'weight_gain':
                        continue
                    # Skip weight loss for ectomorphs as it's rarely needed
                    if somatotype == 'ectomorph' and goal == 'weight_loss':
                        continue
                        
                    for activity_level in activity_levels:
                        for complexity in complexities:
                            for exercise_type in exercise_types:
                                current += 1
                                
                                # Calculate nutrition
                                nutrition = self.calculate_calories_and_macros(
                                    somatotype, goal, gender, activity_level
                                )
                                
                                # Get meal recommendations
                                meals = self.get_meal_recommendations(somatotype, goal)
                                
                                # Get exercise recommendations
                                exercises = self.get_exercise_recommendations(
                                    somatotype, goal, exercise_type, complexity, gender
                                )
                                
                                # Get diet principles and fitness strategy
                                diet_principles = self.get_diet_principles(somatotype, goal)
                                fitness_strategy = self.get_fitness_strategy(somatotype)
                                fitness_split = self.get_fitness_split(somatotype)
                                
                                # Create template entry
                                template = {
                                    'somatotype': somatotype,
                                    'gender': gender,
                                    'goal': goal,
                                    'activity_level': activity_level,
                                    'exercise_complexity': complexity,
                                    'exercise_type': exercise_type,
                                    'total_calories': nutrition['total_calories'],
                                    'protein_g': nutrition['protein_g'],
                                    'carbs_g': nutrition['carbs_g'],
                                    'fats_g': nutrition['fats_g'],
                                    'protein_pct': nutrition['protein_pct'],
                                    'carbs_pct': nutrition['carbs_pct'],
                                    'fats_pct': nutrition['fats_pct'],
                                    'breakfast_foods': '; '.join(meals['breakfast']),
                                    'lunch_foods': '; '.join(meals['lunch']),
                                    'dinner_foods': '; '.join(meals['dinner']),
                                    'snack_foods': '; '.join(meals['snacks']),
                                    'diet_principles': ' | '.join(diet_principles),
                                    'fitness_strategy': fitness_strategy,
                                    'fitness_split_strength': fitness_split[0],
                                    'fitness_split_cardio': fitness_split[1],
                                    'exercise_ids': '; '.join(exercises),
                                    'num_exercises': len(exercises),
                                    'description': self.somatotype_specs[somatotype]['description']
                                }
                                
                                templates.append(template)
                                
                                if current % 50 == 0:
                                    print(f"   Progress: {current}/{total_combinations} templates generated")
        
        df = pd.DataFrame(templates)
        print(f"✓ Generated {len(df)} comprehensive diet and fitness templates")
        return df
    
    def save_templates(self, df: pd.DataFrame):
        """Save the generated templates to CSV."""
        try:
            df.to_csv(self.output_path, index=False)
            print(f"✓ Templates saved to: {self.output_path}")
            
            # Print summary statistics
            print("\n📊 Template Summary:")
            print(f"   Total templates: {len(df)}")
            print(f"   Somatotypes: {df['somatotype'].nunique()}")
            print(f"   Gender combinations: {df['gender'].nunique()}")
            print(f"   Goal types: {df['goal'].nunique()}")
            print(f"   Activity levels: {df['activity_level'].nunique()}")
            print(f"   Exercise complexities: {df['exercise_complexity'].nunique()}")
            print(f"   Exercise types: {df['exercise_type'].nunique()}")
            
            # Show sample of data
            print("\n📋 Sample Templates:")
            sample_columns = ['somatotype', 'gender', 'goal', 'total_calories', 'protein_g', 'fitness_strategy']
            print(df[sample_columns].head(10).to_string(index=False))
            
        except Exception as e:
            print(f"✗ Error saving templates: {e}")

def main():
    """Main function to run the diet and fitness template generator with Filipino-available foods."""
    print("🏋️ Somatotype-Based Diet and Fitness Template Generator (Filipino Foods)")
    print("=" * 70)
    
    # Set base path (adjust as needed)
    base_path = r"c:\Users\Lesler John\Desktop\Projects\Thesis\Somatotype-Based-Diet-Recommendation"
    
    # Initialize generator
    generator = SomatotypeDietFitnessGenerator(base_path)
    
    # Generate comprehensive templates
    templates_df = generator.generate_comprehensive_template()
    
    # Save templates
    generator.save_templates(templates_df)
    
    print("\n✅ Diet and fitness template generation completed successfully!")
    print(f"📁 Output file: {generator.output_path}")

if __name__ == "__main__":
    main()