"""
Enhanced Somatotype Diet and Fitness Template Generator with Filipino Meal Structure
Updated with PPL methodology for gym exercises and bodyweight terminology
"""

import pandas as pd
import json
import numpy as np
from typing import Dict, List, Tuple
import random
import warnings
warnings.filterwarnings('ignore')

class FilipinoMealTemplateGenerator:
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.output_path = f"{base_path}/enhanced_diet_templates_filipino_meals.csv"
        
        # Load data files
        self.diet_db = self._load_diet_database()
        self.gym_exercises = self._load_gym_exercises()
        self.bodyweight_exercises = self._load_bodyweight_exercises()
        
        # PPL Exercise Categories from methodology
        self.ppl_categories = {
            'push': {
                'beginner': [
                    {'name': 'Barbell Bench Press', 'sets': 3, 'reps': '8-10'},
                    {'name': 'Incline Dumbbell Press', 'sets': 3, 'reps': '10-12'},
                    {'name': 'Dumbbell Bench Press', 'sets': 3, 'reps': '10-12'},
                    {'name': 'Push-Ups', 'sets': 3, 'reps': '10-12'},
                    {'name': 'Overhead Shoulder Press', 'sets': 3, 'reps': '8-10'},
                    {'name': 'Dumbbell Lateral Raises', 'sets': 3, 'reps': '12-15'},
                    {'name': 'Triceps Pushdowns', 'sets': 3, 'reps': '10-12'},
                    {'name': 'Tricep Dips', 'sets': 3, 'reps': '10-12'}
                ],
                'intermediate': [
                    {'name': 'Flat Barbell Bench Press', 'sets': 4, 'reps': '6-8'},
                    {'name': 'Incline Dumbbell Press', 'sets': 3, 'reps': '10-12'},
                    {'name': 'Standing Overhead Press', 'sets': 3, 'reps': '8-10'},
                    {'name': 'Triceps Pushdowns', 'sets': 3, 'reps': '10-12'},
                    {'name': 'Incline Bench Press', 'sets': 3, 'reps': '8-10'},
                    {'name': 'Cable Fly Crossover', 'sets': 3, 'reps': '12-15'},
                    {'name': 'Seated Dumbbell Shoulder Press', 'sets': 3, 'reps': '8-10'},
                    {'name': 'Triceps Extensions', 'sets': 3, 'reps': '10-12'}
                ],
                'hard': [
                    {'name': 'Dumbbell Chest Press', 'sets': 4, 'reps': '8-10'},
                    {'name': 'Incline Dumbbell Press', 'sets': 3, 'reps': '8-10'},
                    {'name': 'Dumbbell Shoulder Press', 'sets': 3, 'reps': '8-10'},
                    {'name': 'Barbell Lying Triceps Extension', 'sets': 3, 'reps': '10-12'},
                    {'name': 'Bench Press', 'sets': 4, 'reps': '8-10'},
                    {'name': 'Standing Cable Chest Fly', 'sets': 3, 'reps': '12-15'},
                    {'name': 'Barbell Upright Row', 'sets': 3, 'reps': '8-10'},
                    {'name': 'Close-Grip Bench Press', 'sets': 3, 'reps': '8-10'}
                ]
            },
            'pull': {
                'beginner': [
                    {'name': 'Deadlift', 'sets': 3, 'reps': '5-6'},
                    {'name': 'Bent-Over Barbell Row', 'sets': 3, 'reps': '8-10'},
                    {'name': 'Lat Pulldown or Pull-Ups', 'sets': 3, 'reps': '10-12'},
                    {'name': 'Seated Cable Rows', 'sets': 3, 'reps': '10-12'},
                    {'name': 'Biceps Curls', 'sets': 3, 'reps': '10-12'},
                    {'name': 'Hammer Curls', 'sets': 3, 'reps': '10-12'}
                ],
                'intermediate': [
                    {'name': 'Deadlift', 'sets': 3, 'reps': '6-8'},
                    {'name': 'Pull-Ups or Lat Pulldowns', 'sets': 3, 'reps': '8-12'},
                    {'name': 'Barbell Biceps Curls', 'sets': 3, 'reps': '10-12'},
                    {'name': 'Face Pulls', 'sets': 3, 'reps': '15-20'},
                    {'name': 'Bent-Over Barbell Row', 'sets': 3, 'reps': '8-10'},
                    {'name': 'Seated Cable Rows', 'sets': 3, 'reps': '10-12'},
                    {'name': 'Hammer Curls', 'sets': 3, 'reps': '10-12'},
                    {'name': 'Dumbbell Shrugs', 'sets': 3, 'reps': '10-12'}
                ],
                'hard': [
                    {'name': 'Deadlift', 'sets': 4, 'reps': '6-8'},
                    {'name': 'Lat Pulldown', 'sets': 3, 'reps': '8-12'},
                    {'name': 'Barbell Curls', 'sets': 3, 'reps': '10-12'},
                    {'name': 'Face Pulls', 'sets': 3, 'reps': '15-20'},
                    {'name': 'Barbell Rows', 'sets': 3, 'reps': '8-10'},
                    {'name': 'Seated Cable Row', 'sets': 3, 'reps': '10-12'},
                    {'name': 'Concentration Curl', 'sets': 3, 'reps': '12-15'},
                    {'name': 'Dumbbell Shrugs', 'sets': 3, 'reps': '10-12'}
                ]
            },
            'legs': {
                'beginner': [
                    {'name': 'Barbell Back Squat', 'sets': 3, 'reps': '6-8'},
                    {'name': 'Leg Press', 'sets': 3, 'reps': '10-12'},
                    {'name': 'Romanian Deadlift', 'sets': 3, 'reps': '10-12'},
                    {'name': 'Leg Curl', 'sets': 3, 'reps': '10-12'},
                    {'name': 'Standing Calf Raise', 'sets': 3, 'reps': '12-15'}
                ],
                'intermediate': [
                    {'name': 'Barbell Back Squat', 'sets': 4, 'reps': '6-8'},
                    {'name': 'Romanian Deadlift', 'sets': 3, 'reps': '8-10'},
                    {'name': 'Leg Extensions', 'sets': 3, 'reps': '12-15'},
                    {'name': 'Standing Calf Raise', 'sets': 4, 'reps': '15-20'},
                    {'name': 'Leg Press', 'sets': 3, 'reps': '10-12'},
                    {'name': 'Bulgarian Split Squats', 'sets': 3, 'reps': '10-12 (per leg)'},
                    {'name': 'Leg Curls', 'sets': 3, 'reps': '12-15'},
                    {'name': 'Seated Leg Curls', 'sets': 3, 'reps': '12-15'}
                ],
                'hard': [
                    {'name': 'Barbell Squat', 'sets': 5, 'reps': '6-8'},
                    {'name': 'Leg Press', 'sets': 3, 'reps': '10-12'},
                    {'name': 'Leg Extensions', 'sets': 3, 'reps': '12-15'},
                    {'name': 'Romanian Deadlift', 'sets': 4, 'reps': '8-10'},
                    {'name': 'Lunges (Dumbbell or Barbell)', 'sets': 3, 'reps': '10-12 (per leg)'},
                    {'name': 'Leg Curls', 'sets': 3, 'reps': '12-15'}
                ]
            }
        }
        
        # Somatotype specifications with scientific macronutrient ratios
        self.somatotype_specs = {
            'endomorph': {
                'description': 'Naturally soft and round, gains weight easily, slower metabolism',
                'macros': {
                    'weight_loss': [35, 25, 40],      # protein, carbs, fat
                    'maintenance': [30, 30, 40],
                    'weight_gain': [30, 40, 30]
                },
                'preferred_foods': ['protein', 'vegetables', 'healthy_fats'],
                'calorie_multiplier': {'weight_loss': 0.8, 'maintenance': 1.0, 'weight_gain': 1.15}
            },
            'mesomorph': {
                'description': 'Naturally muscular and athletic, balanced metabolism',
                'macros': {
                    'weight_loss': [35, 35, 30],
                    'maintenance': [30, 40, 30], 
                    'weight_gain': [30, 45, 25]
                },
                'preferred_foods': ['protein', 'complex_carbs', 'vegetables'],
                'calorie_multiplier': {'weight_loss': 0.85, 'maintenance': 1.0, 'weight_gain': 1.2}
            },
            'ectomorph': {
                'description': 'Naturally slender and lean, fast metabolism',
                'macros': {
                    'weight_loss': [25, 45, 30],
                    'maintenance': [25, 50, 25],
                    'weight_gain': [25, 55, 20]
                },
                'preferred_foods': ['complex_carbs', 'protein', 'healthy_fats'],
                'calorie_multiplier': {'weight_loss': 0.9, 'maintenance': 1.0, 'weight_gain': 1.3}
            },
            'endo_meso': {
                'description': 'Muscular but gains fat easily, hybrid metabolism',
                'macros': {
                    'weight_loss': [40, 25, 35],
                    'maintenance': [35, 35, 30],
                    'weight_gain': [35, 40, 25]
                },
                'preferred_foods': ['protein', 'vegetables', 'controlled_carbs'],
                'calorie_multiplier': {'weight_loss': 0.8, 'maintenance': 1.0, 'weight_gain': 1.15}
            },
            'meso_ecto': {
                'description': 'Lean and athletic, efficient metabolism',
                'macros': {
                    'weight_loss': [30, 40, 30],
                    'maintenance': [25, 45, 30],
                    'weight_gain': [25, 50, 25]
                },
                'preferred_foods': ['protein', 'complex_carbs', 'healthy_fats'],
                'calorie_multiplier': {'weight_loss': 0.85, 'maintenance': 1.0, 'weight_gain': 1.25}
            },
            'ecto_endo': {
                'description': 'Skinny-fat physique, inconsistent metabolism',
                'macros': {
                    'weight_loss': [35, 30, 35],
                    'maintenance': [30, 35, 35],
                    'weight_gain': [30, 45, 25]
                },
                'preferred_foods': ['protein', 'vegetables', 'moderate_carbs'],
                'calorie_multiplier': {'weight_loss': 0.8, 'maintenance': 1.0, 'weight_gain': 1.2}
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
        
        # Base calorie needs (BMR approximation)
        self.base_calories = {
            'male': 1800,
            'female': 1500
        }
        
        # Filipino food categories
        self.filipino_foods = {
            'breakfast': {
                'protein': ['Itlog (Eggs)', 'Tapa', 'Longganisa', 'Tuyo', 'Bangus (Milkfish)', 'Kesong Puti'],
                'carbs': ['Sinangag (Fried Rice)', 'Pandesal', 'Champorado', 'Lugaw', 'Tortang Talong Rice'],
                'vegetables': ['Kamote (Sweet Potato)', 'Ginisang Munggo', 'Fresh Tomatoes', 'Cucumber'],
                'fruits': ['Saging (Banana)', 'Mangga (Mango)', 'Papaya', 'Calamansi Juice']
            },
            'lunch': {
                'protein': ['Adobong Manok', 'Sinigang na Baboy', 'Grilled Bangus', 'Tinolang Manok', 'Lechon Kawali', 'Kare-Kare'],
                'carbs': ['Kanin (Steamed Rice)', 'Pancit Canton', 'Bihon', 'Fried Rice'],
                'vegetables': ['Pinakbet', 'Adobong Kangkong', 'Ginisang Sayote', 'Ensaladang Talong', 'Okra'],
                'soup': ['Sinigang', 'Tinola', 'Miso Soup', 'Bulalo']
            },
            'dinner': {
                'protein': ['Grilled Liempo', 'Fish Fillet', 'Beef Caldereta', 'Chicken Inasal', 'Pork Sisig', 'Bangus Belly'],
                'carbs': ['Brown Rice', 'Quinoa Rice', 'Sweet Potato', 'Pancit'],
                'vegetables': ['Laing', 'Gising-Gising', 'Chopsuey', 'Pinakbet', 'Ginataang Gulay'],
                'soup': ['Sinigang na Isda', 'Chicken Sopas', 'Munggo Soup']
            },
            'snacks': {
                'healthy': ['Nuts (Pili, Cashew)', 'Dried Mangoes', 'Banana Chips', 'Coconut Strips', 'Buko Juice'],
                'protein': ['Tokwat Baboy', 'Kwek-kwek', 'Fish Balls', 'Taho (Silken Tofu)'],
                'carbs': ['Bibingka', 'Turon', 'Mais con Hielo', 'Halo-halo (small)'],
                'fruits': ['Fresh Buko', 'Rambutan', 'Lanzones', 'Durian', 'Marang']
            }
        }
        
        # Diet principle templates
        self.diet_principles = {
            'endomorph': {
                'weight_loss': [
                    "Focus on high-protein, low-carbohydrate foods to boost metabolism",
                    "Prioritize fiber-rich vegetables to increase satiety",
                    "Choose lean proteins like fish and chicken breast",
                    "Limit processed foods and refined sugars",
                    "Eat smaller, frequent meals to maintain blood sugar stability"
                ],
                'maintenance': [
                    "Balance protein and healthy fats with moderate carbohydrates",
                    "Focus on complex carbohydrates from vegetables and whole grains",
                    "Include healthy fats from nuts, seeds, and fish",
                    "Monitor portion sizes to prevent weight gain",
                    "Stay hydrated and limit caloric beverages"
                ],
                'weight_gain': [
                    "Increase healthy calorie-dense foods like nuts and avocados",
                    "Add moderate amounts of complex carbohydrates",
                    "Focus on lean muscle-building proteins",
                    "Include strength training to gain lean mass",
                    "Monitor weight gain to ensure it's primarily muscle"
                ]
            },
            'mesomorph': {
                'weight_loss': [
                    "Maintain high protein intake to preserve muscle mass",
                    "Balance carbohydrates around workout times",
                    "Include moderate healthy fats for hormone production",
                    "Focus on whole, unprocessed foods",
                    "Adjust portions based on activity level"
                ],
                'maintenance': [
                    "Maintain balanced macronutrient ratios",
                    "Eat complex carbohydrates for sustained energy",
                    "Include variety in protein sources",
                    "Focus on nutrient timing around workouts",
                    "Listen to hunger and satiety cues"
                ],
                'weight_gain': [
                    "Increase overall caloric intake with quality foods",
                    "Emphasize complex carbohydrates for energy",
                    "Maintain high protein for muscle building",
                    "Include calorie-dense healthy snacks",
                    "Time carbohydrate intake around training"
                ]
            },
            'ectomorph': {
                'weight_loss': [
                    "Maintain adequate calories to preserve muscle mass",
                    "Focus on nutrient-dense, high-protein foods",
                    "Include healthy fats for essential nutrients",
                    "Avoid excessive cardio that may reduce muscle",
                    "Ensure adequate rest and recovery"
                ],
                'maintenance': [
                    "Eat frequently to maintain energy levels",
                    "Include calorie-dense healthy foods",
                    "Balance all three macronutrients",
                    "Don't skip meals or snacks",
                    "Focus on consistent eating patterns"
                ],
                'weight_gain': [
                    "Increase meal frequency and portion sizes",
                    "Focus on calorie-dense, nutrient-rich foods",
                    "Include healthy fats like nuts, oils, and avocados",
                    "Emphasize complex carbohydrates for energy",
                    "Add protein shakes or smoothies between meals"
                ]
            }
        }

    def _load_diet_database(self) -> pd.DataFrame:
        """Load the comprehensive Filipino diet database."""
        try:
            diet_path = f"{self.base_path}/data/datasets/diet/processed/filipino_foods_comprehensive.csv"
            df = pd.read_csv(diet_path)
            print(f"✓ Loaded {len(df)} Filipino foods from database")
            return df
        except Exception as e:
            print(f"✗ Error loading diet database: {e}")
            return pd.DataFrame()
    
    def _load_gym_exercises(self) -> List[Dict]:
        """Load gym exercises database."""
        try:
            gym_path = f"{self.base_path}/data/datasets/fitness/data/exercises.json"
            with open(gym_path, 'r') as f:
                exercises = json.load(f)
            print(f"✓ Loaded {len(exercises)} gym exercises")
            return exercises
        except Exception as e:
            print(f"✗ Error loading gym exercises: {e}")
            return []
    
    def _load_bodyweight_exercises(self) -> List[Dict]:
        """Load bodyweight exercises database (formerly outdoor)."""
        try:
            bodyweight_path = f"{self.base_path}/data/datasets/fitness/data/outdoor_exercises.json"
            with open(bodyweight_path, 'r') as f:
                exercises = json.load(f)
            print(f"✓ Loaded {len(exercises)} bodyweight exercises")
            return exercises
        except Exception as e:
            print(f"✗ Error loading bodyweight exercises: {e}")
            return []

    def get_ppl_gym_recommendations(self, somatotype: str, goal: str, complexity: str, gender: str) -> str:
        """Get PPL-based gym exercise recommendations with sets and reps."""
        
        # Select appropriate workout plan based on complexity
        if complexity == 'beginner':
            # 3-day PPL split
            push_exercises = self.ppl_categories['push']['beginner']
            pull_exercises = self.ppl_categories['pull']['beginner']  
            leg_exercises = self.ppl_categories['legs']['beginner']
            
            routine = []
            routine.append("**3-Day PPL Split (Beginner)**")
            routine.append("")
            routine.append("**Push Day (Chest, Shoulders, Triceps):**")
            for ex in push_exercises:
                routine.append(f"• {ex['name']}: {ex['sets']} sets x {ex['reps']} reps")
            
            routine.append("")
            routine.append("**Pull Day (Back, Biceps):**") 
            for ex in pull_exercises:
                routine.append(f"• {ex['name']}: {ex['sets']} sets x {ex['reps']} reps")
                
            routine.append("")
            routine.append("**Legs Day (Quads, Hamstrings, Glutes, Calves):**")
            for ex in leg_exercises:
                routine.append(f"• {ex['name']}: {ex['sets']} sets x {ex['reps']} reps")
                
        elif complexity == 'intermediate':
            # 6-day PPL split with 2 variations each
            push1_exercises = self.ppl_categories['push']['intermediate'][:4]
            push2_exercises = self.ppl_categories['push']['intermediate'][4:]
            pull1_exercises = self.ppl_categories['pull']['intermediate'][:4]
            pull2_exercises = self.ppl_categories['pull']['intermediate'][4:]
            leg1_exercises = self.ppl_categories['legs']['intermediate'][:4]
            leg2_exercises = self.ppl_categories['legs']['intermediate'][4:]
            
            routine = []
            routine.append("**6-Day PPL Split (Intermediate)**")
            routine.append("")
            routine.append("**Day 1: Push 1**")
            for ex in push1_exercises:
                routine.append(f"• {ex['name']}: {ex['sets']} sets x {ex['reps']} reps")
            
            routine.append("")
            routine.append("**Day 2: Pull 1**")
            for ex in pull1_exercises:
                routine.append(f"• {ex['name']}: {ex['sets']} sets x {ex['reps']} reps")
                
            routine.append("")
            routine.append("**Day 3: Legs 1**")
            for ex in leg1_exercises:
                routine.append(f"• {ex['name']}: {ex['sets']} sets x {ex['reps']} reps")
                
            routine.append("")
            routine.append("**Day 4: Push 2**")
            for ex in push2_exercises:
                routine.append(f"• {ex['name']}: {ex['sets']} sets x {ex['reps']} reps")
                
            routine.append("")
            routine.append("**Day 5: Pull 2**") 
            for ex in pull2_exercises:
                routine.append(f"• {ex['name']}: {ex['sets']} sets x {ex['reps']} reps")
                
            routine.append("")
            routine.append("**Day 6: Legs 2**")
            for ex in leg2_exercises:
                routine.append(f"• {ex['name']}: {ex['sets']} sets x {ex['reps']} reps")
                
        else:  # hard/advanced
            # 6-day specialized PPL split
            push1_exercises = self.ppl_categories['push']['hard'][:4]
            push2_exercises = self.ppl_categories['push']['hard'][4:]
            pull1_exercises = self.ppl_categories['pull']['hard'][:4]
            pull2_exercises = self.ppl_categories['pull']['hard'][4:]
            leg1_exercises = self.ppl_categories['legs']['hard'][:3]
            leg2_exercises = self.ppl_categories['legs']['hard'][3:]
            
            routine = []
            routine.append("**6-Day Specialized PPL Split (Advanced)**")
            routine.append("")
            routine.append("**Day 1: Push 1 (Heavy Pressing & Strength)**")
            for ex in push1_exercises:
                routine.append(f"• {ex['name']}: {ex['sets']} sets x {ex['reps']} reps")
            
            routine.append("")
            routine.append("**Day 2: Pull 1 (Deadlift & Vertical Pull)**")
            for ex in pull1_exercises:
                routine.append(f"• {ex['name']}: {ex['sets']} sets x {ex['reps']} reps")
                
            routine.append("")
            routine.append("**Day 3: Legs 1 (Squat & Quad Focus)**")
            for ex in leg1_exercises:
                routine.append(f"• {ex['name']}: {ex['sets']} sets x {ex['reps']} reps")
                
            routine.append("")
            routine.append("**Day 4: Push 2 (Accessory & Incline Focus)**")
            for ex in push2_exercises:
                routine.append(f"• {ex['name']}: {ex['sets']} sets x {ex['reps']} reps")
                
            routine.append("")
            routine.append("**Day 5: Pull 2 (Row & Horizontal Pull)**")
            for ex in pull2_exercises:
                routine.append(f"• {ex['name']}: {ex['sets']} sets x {ex['reps']} reps")
                
            routine.append("")
            routine.append("**Day 6: Legs 2 (Hamstring & Posterior Chain)**")
            for ex in leg2_exercises:
                routine.append(f"• {ex['name']}: {ex['sets']} sets x {ex['reps']} reps")
        
        return " | ".join(routine)

    def get_bodyweight_recommendations(self, somatotype: str, goal: str, complexity: str, gender: str) -> str:
        """Get bodyweight exercise recommendations using | separator format."""
        if not self.bodyweight_exercises:
            return "No bodyweight exercises available"
        
        # Determine number of exercises based on complexity and user preference
        num_exercises = {'beginner': 8, 'intermediate': 12, 'hard': 16}[complexity]
        
        # Preference mapping based on somatotype and goal
        muscle_preferences = {
            'endomorph': {
                'weight_loss': ['abs', 'cardiovascular system', 'glutes', 'quads'],
                'maintenance': ['abs', 'glutes', 'pectorals', 'lats'],
                'weight_gain': ['pectorals', 'lats', 'glutes', 'quads']
            },
            'mesomorph': {
                'weight_loss': ['abs', 'cardiovascular system', 'pectorals', 'lats'],
                'maintenance': ['pectorals', 'lats', 'glutes', 'abs'],
                'weight_gain': ['pectorals', 'lats', 'triceps', 'biceps']
            },
            'ectomorph': {
                'weight_loss': ['abs', 'pectorals', 'lats', 'glutes'],
                'maintenance': ['pectorals', 'lats', 'triceps', 'biceps'],
                'weight_gain': ['pectorals', 'lats', 'triceps', 'biceps']
            },
            'endo_meso': {
                'weight_loss': ['abs', 'cardiovascular system', 'glutes', 'quads'],
                'maintenance': ['abs', 'pectorals', 'lats', 'glutes'],
                'weight_gain': ['pectorals', 'lats', 'triceps', 'glutes']
            },
            'meso_ecto': {
                'weight_loss': ['abs', 'cardiovascular system', 'pectorals', 'lats'],
                'maintenance': ['pectorals', 'lats', 'triceps', 'biceps'],
                'weight_gain': ['pectorals', 'lats', 'triceps', 'biceps']
            },
            'ecto_endo': {
                'weight_loss': ['abs', 'cardiovascular system', 'glutes', 'pectorals'],
                'maintenance': ['abs', 'pectorals', 'lats', 'glutes'],
                'weight_gain': ['pectorals', 'lats', 'triceps', 'glutes']
            }
        }
        
        # Get preferred muscle groups
        preferred_muscles = muscle_preferences.get(somatotype, {}).get(goal, ['abs', 'pectorals', 'lats', 'glutes'])
        
        # Filter exercises by preferred muscle groups
        preferred_exercises = []
        other_exercises = []
        
        for exercise in self.bodyweight_exercises:
            target_muscles = exercise.get('targetMuscles', [])
            if any(muscle in preferred_muscles for muscle in target_muscles):
                preferred_exercises.append(exercise['name'])
            else:
                other_exercises.append(exercise['name'])
        
        # Build exercise list prioritizing preferred exercises
        selected_exercises = []
        
        # Add preferred exercises first (up to 70% of total)
        preferred_count = min(len(preferred_exercises), int(num_exercises * 0.7))
        selected_exercises.extend(random.sample(preferred_exercises, preferred_count))
        
        # Fill remaining slots with other exercises
        remaining_slots = num_exercises - len(selected_exercises)
        if remaining_slots > 0 and other_exercises:
            additional_count = min(len(other_exercises), remaining_slots)
            selected_exercises.extend(random.sample(other_exercises, additional_count))
        
        # If still need more exercises, add more from preferred
        if len(selected_exercises) < num_exercises and preferred_exercises:
            needed = num_exercises - len(selected_exercises)
            available_preferred = [ex for ex in preferred_exercises if ex not in selected_exercises]
            if available_preferred:
                additional_count = min(len(available_preferred), needed)
                selected_exercises.extend(random.sample(available_preferred, additional_count))
        
        return " | ".join(selected_exercises[:num_exercises])

    def calculate_calories_and_macros(self, somatotype: str, goal: str, gender: str, activity_level: str) -> Dict:
        """Calculate personalized calories and macronutrients."""
        base_calories = self.base_calories[gender]
        activity_multiplier = self.activity_multipliers[activity_level]
        calorie_multiplier = self.somatotype_specs[somatotype]['calorie_multiplier'][goal]
        
        total_calories = int(base_calories * activity_multiplier * calorie_multiplier)
        
        # Get macro ratios
        protein_ratio, carb_ratio, fat_ratio = self.somatotype_specs[somatotype]['macros'][goal]
        
        # Calculate macro grams
        protein_grams = int((total_calories * protein_ratio / 100) / 4)
        carb_grams = int((total_calories * carb_ratio / 100) / 4)  
        fat_grams = int((total_calories * fat_ratio / 100) / 9)
        
        return {
            'calories': total_calories,
            'protein': protein_grams,
            'carbs': carb_grams,
            'fat': fat_grams,
            'protein_ratio': protein_ratio,
            'carb_ratio': carb_ratio,
            'fat_ratio': fat_ratio
        }
    
    def get_filipino_meal_recommendations(self, somatotype: str, goal: str) -> Dict[str, str]:
        """Get structured Filipino meal recommendations."""
        preferred_foods = self.somatotype_specs[somatotype]['preferred_foods']
        
        meals = {}
        
        # Breakfast
        breakfast_items = []
        if 'protein' in preferred_foods:
            breakfast_items.extend(random.sample(self.filipino_foods['breakfast']['protein'], 2))
        if 'complex_carbs' in preferred_foods:
            breakfast_items.extend(random.sample(self.filipino_foods['breakfast']['carbs'], 1))
        else:
            breakfast_items.extend(random.sample(self.filipino_foods['breakfast']['carbs'], 1))
        breakfast_items.extend(random.sample(self.filipino_foods['breakfast']['fruits'], 1))
        meals['breakfast'] = " | ".join(breakfast_items)
        
        # Lunch  
        lunch_items = []
        lunch_items.extend(random.sample(self.filipino_foods['lunch']['protein'], 1))
        lunch_items.extend(random.sample(self.filipino_foods['lunch']['carbs'], 1))
        lunch_items.extend(random.sample(self.filipino_foods['lunch']['vegetables'], 2))
        lunch_items.extend(random.sample(self.filipino_foods['lunch']['soup'], 1))
        meals['lunch'] = " | ".join(lunch_items)
        
        # Dinner
        dinner_items = []
        dinner_items.extend(random.sample(self.filipino_foods['dinner']['protein'], 1))
        if goal != 'weight_loss':
            dinner_items.extend(random.sample(self.filipino_foods['dinner']['carbs'], 1))
        dinner_items.extend(random.sample(self.filipino_foods['dinner']['vegetables'], 2))
        meals['dinner'] = " | ".join(dinner_items)
        
        # Snacks
        snack_items = []
        if 'healthy_fats' in preferred_foods:
            snack_items.extend(random.sample(self.filipino_foods['snacks']['healthy'], 2))
        snack_items.extend(random.sample(self.filipino_foods['snacks']['fruits'], 1))
        if goal == 'weight_gain':
            snack_items.extend(random.sample(self.filipino_foods['snacks']['protein'], 1))
        meals['snacks'] = " | ".join(snack_items)
        
        return meals
    
    def get_diet_principles(self, somatotype: str, goal: str) -> str:
        """Get diet principles based on somatotype and goal."""
        base_somatotype = somatotype.split('_')[0]  # Handle hybrid types
        if base_somatotype in self.diet_principles and goal in self.diet_principles[base_somatotype]:
            principles = self.diet_principles[base_somatotype][goal]
            return " | ".join(principles)
        return "Follow a balanced, nutrient-dense diet appropriate for your goals"
    
    def get_fitness_strategy(self, somatotype: str) -> str:
        """Get fitness strategy based on somatotype."""
        strategies = {
            'endomorph': [
                "Focus on high-intensity interval training (HIIT) for fat burning",
                "Include strength training to build lean muscle mass", 
                "Incorporate steady-state cardio for cardiovascular health",
                "Prioritize compound movements for maximum calorie burn",
                "Allow adequate rest between intense sessions"
            ],
            'mesomorph': [
                "Balance strength training with moderate cardio",
                "Focus on progressive overload for muscle growth",
                "Include variety in training to prevent adaptation", 
                "Maintain consistent workout schedule",
                "Monitor body composition changes over weight alone"
            ],
            'ectomorph': [
                "Prioritize strength training over excessive cardio",
                "Focus on compound movements for maximum muscle activation",
                "Allow longer rest periods between intense sessions",
                "Include moderate cardio for cardiovascular health only",
                "Emphasize progressive overload and muscle building"
            ],
            'endo_meso': [
                "Combine strength training with moderate cardio",
                "Focus on muscle building while managing body fat",
                "Include HIIT sessions 2-3 times per week",
                "Prioritize compound movements",
                "Monitor body composition regularly"
            ],
            'meso_ecto': [
                "Focus primarily on strength training",
                "Include minimal cardio to maintain cardiovascular health",
                "Emphasize progressive overload",
                "Allow adequate recovery between sessions",
                "Focus on muscle building and strength gains"
            ],
            'ecto_endo': [
                "Balance muscle building with fat management",
                "Include both strength training and moderate cardio",
                "Focus on body recomposition goals",
                "Monitor progress through body composition not just weight",
                "Adjust training based on body fat percentage changes"
            ]
        }
        
        base_somatotype = somatotype.split('_')[0]
        if somatotype in strategies:
            return " | ".join(strategies[somatotype])
        elif base_somatotype in strategies:
            return " | ".join(strategies[base_somatotype])
        return "Follow a balanced exercise program appropriate for your body type"
    
    def get_fitness_split(self, somatotype: str) -> str:
        """Get recommended training split based on somatotype."""
        splits = {
            'endomorph': "Upper/Lower split with cardio days or Push/Pull/Legs with HIIT",
            'mesomorph': "Push/Pull/Legs split or Upper/Lower split",
            'ectomorph': "Push/Pull/Legs split or Full body workouts 3x/week",
            'endo_meso': "Push/Pull/Legs split with cardio days",
            'meso_ecto': "Push/Pull/Legs split or Upper/Lower split",
            'ecto_endo': "Push/Pull/Legs split with body recomposition focus"
        }
        return splits.get(somatotype, "Push/Pull/Legs split")

    def generate_comprehensive_template(self) -> pd.DataFrame:
        """Generate comprehensive Filipino meal templates for all combinations."""
        templates = []
        
        somatotypes = ['endomorph', 'mesomorph', 'ectomorph', 'endo_meso', 'meso_ecto', 'ecto_endo']
        genders = ['male', 'female']
        goals = ['weight_loss', 'weight_gain', 'maintenance']
        activity_levels = ['sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extra_active']
        complexities = ['beginner', 'intermediate', 'hard']
        exercise_types = ['gym', 'bodyweight']
        
        print("🏗️  Generating comprehensive Filipino meal templates...")
        
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
                                meals = self.get_filipino_meal_recommendations(somatotype, goal)
                                
                                # Get exercise recommendations
                                if exercise_type == 'gym':
                                    exercises = self.get_ppl_gym_recommendations(
                                        somatotype, goal, complexity, gender
                                    )
                                else:
                                    exercises = self.get_bodyweight_recommendations(
                                        somatotype, goal, complexity, gender
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
                                    'complexity': complexity,
                                    'exercise_type': exercise_type,
                                    'calories': nutrition['calories'],
                                    'protein_g': nutrition['protein'],
                                    'carbs_g': nutrition['carbs'],
                                    'fat_g': nutrition['fat'],
                                    'protein_ratio': nutrition['protein_ratio'],
                                    'carb_ratio': nutrition['carb_ratio'],
                                    'fat_ratio': nutrition['fat_ratio'],
                                    'breakfast': meals['breakfast'],
                                    'lunch': meals['lunch'],
                                    'dinner': meals['dinner'],
                                    'snacks': meals['snacks'],
                                    'diet_principles': diet_principles,
                                    'fitness_strategy': fitness_strategy,
                                    'fitness_split': fitness_split,
                                    'exercises': exercises,
                                    'description': self.somatotype_specs[somatotype]['description']
                                }
                                
                                templates.append(template)
                                
                                if current % 50 == 0:
                                    progress = (current / total_combinations) * 100
                                    print(f"   Progress: {current}/{total_combinations} ({progress:.1f}%)")
        
        df = pd.DataFrame(templates)
        print(f"✅ Generated {len(df)} comprehensive templates")
        return df
    
    def save_templates(self, df: pd.DataFrame):
        """Save templates to CSV file."""
        df.to_csv(self.output_path, index=False)
        print(f"📁 Templates saved to: {self.output_path}")
        
        # Print summary statistics
        print(f"\n📊 TEMPLATE SUMMARY:")
        print(f"   Total templates: {len(df)}")
        print(f"   Somatotypes: {df['somatotype'].nunique()}")
        print(f"   Goals: {df['goal'].nunique()}")
        print(f"   Exercise types: {df['exercise_type'].nunique()}")
        print(f"   Complexity levels: {df['complexity'].nunique()}")

if __name__ == "__main__":
    # Initialize generator
    base_path = "."
    generator = FilipinoMealTemplateGenerator(base_path)
    
    # Generate templates
    templates_df = generator.generate_comprehensive_template()
    
    # Save to file
    generator.save_templates(templates_df)
    
    print("\n🎉 Enhanced Filipino meal templates with PPL methodology generated successfully!")