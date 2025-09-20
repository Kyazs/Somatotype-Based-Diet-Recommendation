#!/usr/bin/env python3
"""
Advanced Diet Recommendation Engine

This module provides comprehensive diet recommendations based on:
1. Somatotype classification (from output_classification.csv)
2. User goals and preferences (from input_info_recommendation.csv)
3. Body measurements and anthropometric data (from output_data_avatar_male_fromImg.csv)
4. FNDDS processed food database (optimized_diet_recommendation_database.csv)

The engine calculates personalized macronutrient targets and selects optimal foods
based on somatotype-specific nutrition science and user goals.
"""

import pandas as pd
import numpy as np
import random
import os
import sys
from typing import Dict, List, Tuple, Optional

# Add project root to path
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(PROJECT_DIR)

from src.utils.utils import OUTPUT_FILES_DIR

class DietRecommendationEngine:
    """
    Advanced diet recommendation system using real user data and comprehensive food database
    """
    
    def __init__(self):
        """Initialize the diet recommendation engine"""
        self.user_data = None
        self.body_measurements = None
        self.somatotype_data = None
        self.food_database = None
        
        # Load all necessary data
        self._load_data()
        
        # Somatotype-specific nutrition parameters
        self.somatotype_nutrition_profiles = {
            'ectomorph': {
                'calorie_surplus': 300,      # Higher calorie needs
                'protein_ratio': 0.25,       # 25% of calories from protein
                'carbs_ratio': 0.50,         # 50% of calories from carbs  
                'fat_ratio': 0.25,           # 25% of calories from fat
                'meal_frequency': 5,         # More frequent meals
                'preferred_categories': ['complex_carbs', 'healthy_fats', 'complete_proteins'],
                'avoid_categories': [],
                'portion_multiplier': 1.2    # Larger portions
            },
            'mesomorph': {
                'calorie_surplus': 200,      # Moderate calorie adjustment
                'protein_ratio': 0.30,       # 30% of calories from protein
                'carbs_ratio': 0.40,         # 40% of calories from carbs
                'fat_ratio': 0.30,           # 30% of calories from fat
                'meal_frequency': 4,         # Balanced meal frequency
                'preferred_categories': ['lean_proteins', 'complex_carbs', 'healthy_fats'],
                'avoid_categories': [],
                'portion_multiplier': 1.0    # Standard portions
            },
            'endomorph': {
                'calorie_surplus': -200,     # Calorie deficit tendency
                'protein_ratio': 0.35,       # 35% of calories from protein
                'carbs_ratio': 0.30,         # 30% of calories from carbs
                'fat_ratio': 0.35,           # 35% of calories from fat
                'meal_frequency': 4,         # Controlled meal frequency
                'preferred_categories': ['lean_proteins', 'vegetables', 'healthy_fats'],
                'avoid_categories': ['simple_carbs'],
                'portion_multiplier': 0.9    # Smaller portions for weight control
            }
        }
        
        # Goal-specific adjustments
        self.goal_adjustments = {
            'lose_weight': {'calorie_adjustment': -500, 'protein_boost': 0.05},
            'gain_weight': {'calorie_adjustment': 500, 'carbs_boost': 0.05},
            'maintain_weight': {'calorie_adjustment': 0, 'balanced': True},
            'build_muscle': {'calorie_adjustment': 300, 'protein_boost': 0.10}
        }
    
    def _load_data(self):
        """Load all necessary data files"""
        try:
            # Load user input data
            input_file = os.path.join(PROJECT_DIR, "data", "input_files", "input_info_recommendation.csv")
            if os.path.exists(input_file):
                self.user_data = pd.read_csv(input_file).iloc[0].to_dict()
            
            # Load body measurements
            measurements_file = os.path.join(OUTPUT_FILES_DIR, "output_data_avatar_male_fromImg.csv")
            if os.path.exists(measurements_file):
                # Parse the pipe-separated format
                with open(measurements_file, 'r') as f:
                    lines = f.readlines()
                
                measurements_dict = {}
                for line in lines[2:]:  # Skip header lines
                    if '|' in line:
                        parts = [p.strip() for p in line.split('|')]
                        if len(parts) >= 4:
                            measurement = parts[0]
                            avatar_output = parts[3]
                            try:
                                measurements_dict[measurement] = float(avatar_output)
                            except:
                                pass
                
                self.body_measurements = measurements_dict
            
            # Load somatotype classification
            classification_file = os.path.join(OUTPUT_FILES_DIR, "output_classification.csv")
            if os.path.exists(classification_file):
                self.somatotype_data = pd.read_csv(classification_file).iloc[0].to_dict()
            
            # Load comprehensive food database
            food_db_file = os.path.join(PROJECT_DIR, "data", "datasets", "diet", "fndds_processed", "optimized_diet_recommendation_database.csv")
            if os.path.exists(food_db_file):
                self.food_database = pd.read_csv(food_db_file)
            
            print("Data loading completed successfully")
            
        except Exception as e:
            print(f"Error loading data: {e}")
            # Set default values if loading fails
            self._set_default_data()
    
    def _set_default_data(self):
        """Set default data if files are not available"""
        self.user_data = {
            'Name': 'User',
            'Age': 25,
            'Goal': 'Maintain Weight',
            'Activity_Level': 'Moderately active'
        }
        
        self.body_measurements = {
            'weight_kg': 70.0,
            'stature_cm': 175.0
        }
        
        self.somatotype_data = {
            'Somatotype': 'Mesomorph'
        }
    
    def _get_primary_somatotype(self) -> str:
        """Get the primary somatotype from classification data"""
        if self.somatotype_data and 'Somatotype' in self.somatotype_data:
            somatotype = self.somatotype_data['Somatotype'].lower()
            
            # Map variations to standard types
            if 'ecto' in somatotype:
                return 'ectomorph'
            elif 'meso' in somatotype:
                return 'mesomorph' 
            elif 'endo' in somatotype:
                return 'endomorph'
            else:
                return 'mesomorph'  # Default fallback
        return 'mesomorph'  # Default fallback
    
    def calculate_bmr(self, weight_kg: float, height_cm: float, age: int, gender: str) -> float:
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation"""
        if gender.lower() == 'male':
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        return round(bmr, 0)
    
    def calculate_tdee(self, bmr: float, activity_level: str) -> float:
        """Calculate Total Daily Energy Expenditure"""
        activity_multipliers = {
            'sedentary': 1.2,
            'lightly active': 1.375,
            'moderately active': 1.55,
            'very active': 1.725,
            'extremely active': 1.9
        }
        
        # Normalize activity level string
        activity_key = activity_level.lower()
        multiplier = activity_multipliers.get(activity_key, 1.55)
        return round(bmr * multiplier, 0)
    
    def get_somatotype_classification(self) -> str:
        """Extract and normalize somatotype classification"""
        if self.somatotype_data and 'Somatotype' in self.somatotype_data:
            somatotype = self.somatotype_data['Somatotype'].lower()
            # Handle variations in naming
            if 'ecto' in somatotype:
                return 'ectomorph'
            elif 'meso' in somatotype:
                return 'mesomorph'
            elif 'endo' in somatotype:
                return 'endomorph'
        return 'mesomorph'  # Default
    
    def calculate_personalized_macros(self) -> Dict[str, float]:
        """Calculate personalized macronutrient targets"""
        try:
            # Get user data
            age = int(self.user_data.get('Age', 25))
            goal = self.user_data.get('Goal', 'Maintain Weight').lower().replace(' ', '_')
            activity_level = self.user_data.get('Activity_Level', 'Moderately active')
            
            # Get body measurements
            weight = self.body_measurements.get('weight_kg', 70.0)
            height = self.body_measurements.get('stature_cm', 175.0)
            
            # Assume male for now (can be enhanced with gender detection)
            gender = 'male'
            
            # Calculate base metabolic needs
            bmr = self.calculate_bmr(weight, height, age, gender)
            tdee = self.calculate_tdee(bmr, activity_level)
            
            # Get somatotype and its nutrition profile
            somatotype = self.get_somatotype_classification()
            nutrition_profile = self.somatotype_nutrition_profiles[somatotype]
            
            # Apply somatotype-specific calorie adjustment
            base_calories = tdee + nutrition_profile['calorie_surplus']
            
            # Apply goal-specific adjustments
            if goal in self.goal_adjustments:
                goal_adj = self.goal_adjustments[goal]
                final_calories = base_calories + goal_adj['calorie_adjustment']
                
                # Adjust macronutrient ratios based on goal
                protein_ratio = nutrition_profile['protein_ratio']
                carbs_ratio = nutrition_profile['carbs_ratio']
                fat_ratio = nutrition_profile['fat_ratio']
                
                if 'protein_boost' in goal_adj:
                    protein_ratio += goal_adj['protein_boost']
                    carbs_ratio -= goal_adj['protein_boost'] / 2
                    fat_ratio -= goal_adj['protein_boost'] / 2
                
                if 'carbs_boost' in goal_adj:
                    carbs_ratio += goal_adj['carbs_boost']
                    fat_ratio -= goal_adj['carbs_boost']
            else:
                final_calories = base_calories
                protein_ratio = nutrition_profile['protein_ratio']
                carbs_ratio = nutrition_profile['carbs_ratio'] 
                fat_ratio = nutrition_profile['fat_ratio']
            
            # Calculate grams of each macronutrient
            protein_grams = round((final_calories * protein_ratio) / 4)  # 4 cal/g
            carbs_grams = round((final_calories * carbs_ratio) / 4)      # 4 cal/g
            fat_grams = round((final_calories * fat_ratio) / 9)          # 9 cal/g
            
            return {
                'calories': int(final_calories),
                'protein_g': protein_grams,
                'carbs_g': carbs_grams,
                'fat_g': fat_grams,
                'bmr': int(bmr),
                'tdee': int(tdee),
                'somatotype': somatotype,
                'goal': goal,
                'activity_level': activity_level
            }
            
        except Exception as e:
            print(f"Error calculating macros: {e}")
            # Return reasonable defaults
            return {
                'calories': 2000,
                'protein_g': 150,
                'carbs_g': 200,
                'fat_g': 70,
                'bmr': 1700,
                'tdee': 2000,
                'somatotype': 'mesomorph',
                'goal': 'maintain_weight',
                'activity_level': 'moderately active'
            }
    
    def recommend_foods(self, somatotype: str, goal: str, target_macros: Dict) -> List[Dict]:
        """Recommend optimal foods based on somatotype and goals"""
        if self.food_database is None or self.food_database.empty:
            return self._get_fallback_foods(somatotype, goal)
        
        try:
            # Get somatotype preferences
            nutrition_profile = self.somatotype_nutrition_profiles[somatotype]
            preferred_categories = nutrition_profile['preferred_categories']
            avoid_categories = nutrition_profile.get('avoid_categories', [])
            
            # Filter foods based on somatotype preferences
            suitable_foods = self.food_database.copy()
            
            # Apply category filters
            if preferred_categories:
                suitable_foods = suitable_foods[
                    suitable_foods['Enhanced_Category'].isin(preferred_categories) |
                    suitable_foods['Somatotype_Category'].isin(preferred_categories)
                ]
            
            # Remove avoided categories
            if avoid_categories:
                suitable_foods = suitable_foods[
                    ~suitable_foods['Enhanced_Category'].isin(avoid_categories)
                ]
            
            # Score foods based on goal compatibility
            goal_column_map = {
                'lose_weight': 'Weight_Loss_Score',
                'gain_weight': 'Weight_Gain_Score', 
                'maintain_weight': 'Maintenance_Score',
                'build_muscle': 'Weight_Gain_Score'  # Use gain score for muscle building
            }
            
            score_column = goal_column_map.get(goal, 'Maintenance_Score')
            
            # Filter high-quality foods
            if score_column in suitable_foods.columns:
                suitable_foods = suitable_foods[suitable_foods[score_column] >= 6]
                suitable_foods = suitable_foods.sort_values(score_column, ascending=False)
            
            # Select diverse foods across different categories
            recommended_foods = []
            categories_selected = set()
            
            for _, food in suitable_foods.head(50).iterrows():
                category = food['Enhanced_Category']
                
                # Ensure diversity across categories
                if len(recommended_foods) < 3 or category not in categories_selected or len(recommended_foods) < 15:
                    food_info = {
                        'name': food['Food_Item'],
                        'category': category,
                        'calories_per_100g': food.get('Calories_kcal', 0),
                        'protein_g': food.get('Protein_g', 0),
                        'carbs_g': food.get('Carbohydrates_g', 0),
                        'fat_g': food.get('Fat_g', 0),
                        'fiber_g': food.get('Fiber_g', 0),
                        'score': food.get(score_column, 0),
                        'meal_timing': food.get('Meal_Timing', 'any time'),
                        'portion_rec': food.get('Portion_Recommendation', '100g')
                    }
                    
                    recommended_foods.append(food_info)
                    categories_selected.add(category)
                    
                    if len(recommended_foods) >= 15:  # Limit to top 15 foods
                        break
            
            return recommended_foods[:15]
            
        except Exception as e:
            print(f"Error recommending foods: {e}")
            return self._get_fallback_foods(somatotype, goal)
    
    def _get_fallback_foods(self, somatotype: str, goal: str) -> List[Dict]:
        """Provide fallback food recommendations if database is unavailable"""
        fallback_foods = {
            'ectomorph': [
                {'name': 'Oats', 'category': 'complex_carbs', 'calories_per_100g': 389, 'protein_g': 16.9, 'carbs_g': 66.3, 'fat_g': 6.9},
                {'name': 'Peanut Butter', 'category': 'healthy_fats', 'calories_per_100g': 588, 'protein_g': 25.1, 'carbs_g': 19.6, 'fat_g': 50.4},
                {'name': 'Grilled Chicken', 'category': 'lean_proteins', 'calories_per_100g': 165, 'protein_g': 31.0, 'carbs_g': 0.0, 'fat_g': 3.6},
                {'name': 'Brown Rice', 'category': 'complex_carbs', 'calories_per_100g': 123, 'protein_g': 2.6, 'carbs_g': 25.0, 'fat_g': 0.9},
                {'name': 'Salmon', 'category': 'healthy_fats', 'calories_per_100g': 208, 'protein_g': 25.4, 'carbs_g': 0.0, 'fat_g': 12.4}
            ],
            'mesomorph': [
                {'name': 'Greek Yogurt', 'category': 'dairy_proteins', 'calories_per_100g': 97, 'protein_g': 9.0, 'carbs_g': 3.6, 'fat_g': 5.0},
                {'name': 'Chicken Breast', 'category': 'lean_proteins', 'calories_per_100g': 165, 'protein_g': 31.0, 'carbs_g': 0.0, 'fat_g': 3.6},
                {'name': 'Quinoa', 'category': 'complex_carbs', 'calories_per_100g': 120, 'protein_g': 4.4, 'carbs_g': 21.3, 'fat_g': 1.9},
                {'name': 'Sweet Potato', 'category': 'complex_carbs', 'calories_per_100g': 86, 'protein_g': 1.6, 'carbs_g': 20.1, 'fat_g': 0.1},
                {'name': 'Avocado', 'category': 'healthy_fats', 'calories_per_100g': 160, 'protein_g': 2.0, 'carbs_g': 8.5, 'fat_g': 14.7}
            ],
            'endomorph': [
                {'name': 'Boiled Chicken', 'category': 'lean_proteins', 'calories_per_100g': 165, 'protein_g': 31.0, 'carbs_g': 0.0, 'fat_g': 3.6},
                {'name': 'Steamed Broccoli', 'category': 'vegetables', 'calories_per_100g': 25, 'protein_g': 2.6, 'carbs_g': 5.1, 'fat_g': 0.3},
                {'name': 'Egg Whites', 'category': 'lean_proteins', 'calories_per_100g': 52, 'protein_g': 10.9, 'carbs_g': 0.7, 'fat_g': 0.2},
                {'name': 'Spinach', 'category': 'vegetables', 'calories_per_100g': 23, 'protein_g': 2.9, 'carbs_g': 3.6, 'fat_g': 0.4},
                {'name': 'Grilled Fish', 'category': 'lean_proteins', 'calories_per_100g': 150, 'protein_g': 25.0, 'carbs_g': 0.0, 'fat_g': 5.0}
            ]
        }
        
        return fallback_foods.get(somatotype, fallback_foods['mesomorph'])[:10]
    
    def create_meal_plan(self, macros: Dict, foods: List[Dict]) -> Dict:
        """Create a structured meal plan"""
        somatotype = macros['somatotype']
        nutrition_profile = self.somatotype_nutrition_profiles[somatotype]
        meal_frequency = nutrition_profile['meal_frequency']
        
        # Distribute calories across meals
        if meal_frequency == 5:
            meal_distribution = {
                'breakfast': 0.25,
                'mid_morning': 0.15,
                'lunch': 0.25,
                'afternoon_snack': 0.15,
                'dinner': 0.20
            }
        else:  # 4 meals
            meal_distribution = {
                'breakfast': 0.30,
                'lunch': 0.30,
                'dinner': 0.25,
                'snack': 0.15
            }
        
        meal_plan = {}
        target_calories = macros['calories']
        
        # Group foods by category for meal assignment
        protein_foods = [f for f in foods if 'protein' in f['category']]
        carb_foods = [f for f in foods if 'carb' in f['category']]
        fat_foods = [f for f in foods if 'fat' in f['category']]
        vegetable_foods = [f for f in foods if 'vegetable' in f['category']]
        
        for meal, proportion in meal_distribution.items():
            meal_calories = int(target_calories * proportion)
            meal_foods = []
            
            # Select foods for this meal
            if protein_foods:
                meal_foods.append(protein_foods[len(meal_foods) % len(protein_foods)])
            if carb_foods and meal != 'dinner':  # Reduce carbs at dinner for some somatotypes
                meal_foods.append(carb_foods[len(meal_foods) % len(carb_foods)])
            if vegetable_foods:
                meal_foods.append(vegetable_foods[len(meal_foods) % len(vegetable_foods)])
            if fat_foods:
                meal_foods.append(fat_foods[len(meal_foods) % len(fat_foods)])
            
            meal_plan[meal] = {
                'target_calories': meal_calories,
                'foods': meal_foods[:3],  # Limit to 3 foods per meal
                'timing': meal.replace('_', ' ').title()
            }
        
        return meal_plan
    
    def generate_comprehensive_recommendations(self) -> Dict:
        """Generate complete diet recommendations"""
        # Calculate personalized macronutrient targets
        macros = self.calculate_personalized_macros()
        
        # Get somatotype and goal
        somatotype = macros['somatotype']
        goal = macros['goal']
        
        # Recommend optimal foods
        recommended_foods = self.recommend_foods(somatotype, goal, macros)
        
        # Create meal plan
        meal_plan = self.create_meal_plan(macros, recommended_foods)
        
        # Generate nutrition insights
        nutrition_profile = self.somatotype_nutrition_profiles[somatotype]
        
        insights = [
            f"Your {somatotype} body type responds well to {nutrition_profile['protein_ratio']*100:.0f}% protein, {nutrition_profile['carbs_ratio']*100:.0f}% carbohydrates, and {nutrition_profile['fat_ratio']*100:.0f}% fat.",
            f"Aim for {nutrition_profile['meal_frequency']} meals per day for optimal metabolism.",
            f"Focus on {', '.join(nutrition_profile['preferred_categories'])} for best results.",
        ]
        
        if goal == 'lose_weight':
            insights.append("Your calorie target includes a deficit for healthy weight loss of 1-2 lbs per week.")
        elif goal == 'gain_weight':
            insights.append("Your calorie target includes a surplus for healthy weight gain and muscle building.")
        
        return {
            'macros': macros,
            'recommended_foods': recommended_foods,
            'meal_plan': meal_plan,
            'nutrition_insights': insights,
            'somatotype_profile': nutrition_profile
        }
    
    def generate_meal_based_recommendations(self, num_foods_per_meal: int = 8) -> Dict:
        """
        Generate food recommendations categorized by meal timing
        
        Args:
            num_foods_per_meal: Number of food options to recommend per meal category
            
        Returns:
            Dictionary with meals as keys and food data as values
        """
        if self.food_database is None or self.food_database.empty:
            return self._get_fallback_meal_recommendations()
        
        # Get somatotype and calculate scores
        somatotype = self._get_primary_somatotype()
        nutrition_profile = self.somatotype_nutrition_profiles.get(somatotype, self.somatotype_nutrition_profiles['mesomorph'])
        
        # Calculate somatotype scores for each food
        somatotype_score_col = f"{somatotype.title()}_Score"
        if somatotype_score_col not in self.food_database.columns:
            somatotype_score_col = "Mesomorph_Score"  # Fallback
        
        meal_recommendations = {}
        meal_mappings = {
            'breakfast': ['breakfast', 'pre_workout'],
            'lunch': ['lunch', 'post_workout'],
            'dinner': ['dinner'],
            'snack': ['snack']
        }
        
        for meal_type, meal_timings in meal_mappings.items():
            # Filter foods that are appropriate for this meal timing
            meal_foods = self.food_database[
                self.food_database['Meal_Timing'].apply(
                    lambda x: any(timing in str(x).lower() for timing in meal_timings) if pd.notna(x) else False
                )
            ].copy()
            
            if meal_foods.empty:
                # Fallback: get foods from preferred categories
                preferred_categories = nutrition_profile['preferred_categories']
                meal_foods = self.food_database[
                    self.food_database['Enhanced_Category'].isin(preferred_categories)
                ].copy()
            
            if not meal_foods.empty:
                # Calculate composite score for ranking
                meal_foods = meal_foods.copy()
                meal_foods['composite_score'] = (
                    meal_foods[somatotype_score_col].fillna(5) * 0.4 +
                    meal_foods['Overall_Quality'].fillna(5) * 0.3 +
                    meal_foods['Nutrient_Density_Score'].fillna(5) * 0.2 +
                    meal_foods['Protein_Efficiency'].fillna(0.05) * 100 * 0.1
                )
                
                # Filter out very low quality foods (composite score < 5)
                quality_foods = meal_foods[meal_foods['composite_score'] >= 5.0]
                
                if quality_foods.empty:
                    # If no high-quality foods found, use original set
                    quality_foods = meal_foods
                
                # Sort by composite score to get high-quality foods
                sorted_foods = quality_foods.sort_values('composite_score', ascending=False)
                
                # Select from top candidates with randomization and category diversity
                candidate_pool_size = max(min(30, len(sorted_foods)), num_foods_per_meal * 2)
                candidate_pool = sorted_foods.head(candidate_pool_size)
                
                # Try to ensure category diversity by grouping candidates by category
                selected_foods = []
                remaining_selections = num_foods_per_meal
                categories_used = set()
                
                # First pass: Select one food from each unique category to ensure diversity
                categories_available = candidate_pool['Enhanced_Category'].unique()
                random.shuffle(list(categories_available))  # Randomize category order
                
                for category in categories_available:
                    if remaining_selections <= 0:
                        break
                    
                    category_foods = candidate_pool[candidate_pool['Enhanced_Category'] == category]
                    if not category_foods.empty:
                        # Randomly select one food from this category
                        selected_food = category_foods.sample(n=1, random_state=None)
                        selected_foods.append(selected_food.iloc[0])
                        categories_used.add(category)
                        remaining_selections -= 1
                
                # Second pass: Fill remaining slots with random selection from candidate pool
                if remaining_selections > 0:
                    # Remove already selected foods from candidate pool
                    remaining_candidates = candidate_pool[
                        ~candidate_pool.index.isin([food.name for food in selected_foods])
                    ]
                    
                    if len(remaining_candidates) >= remaining_selections:
                        additional_foods = remaining_candidates.sample(
                            n=remaining_selections, random_state=None
                        )
                        selected_foods.extend(additional_foods.to_dict('records'))
                    else:
                        # If not enough candidates remaining, take all available
                        selected_foods.extend(remaining_candidates.to_dict('records'))
                
                # Convert to list of dictionaries for UI consumption
                if isinstance(selected_foods, list) and selected_foods:
                    # Handle mixed data types (Series and dict)
                    final_foods = []
                    for food in selected_foods:
                        if hasattr(food, 'to_dict'):  # pandas Series
                            final_foods.append(food.to_dict())
                        else:  # already a dict
                            final_foods.append(food)
                    meal_recommendations[meal_type] = final_foods
                else:
                    # Fallback: simple random sampling
                    if len(candidate_pool) >= num_foods_per_meal:
                        selected_foods = candidate_pool.sample(n=num_foods_per_meal, random_state=None)
                    else:
                        selected_foods = candidate_pool
                    meal_recommendations[meal_type] = selected_foods.to_dict('records')
            else:
                meal_recommendations[meal_type] = []
        
        return meal_recommendations
    
    def _get_fallback_meal_recommendations(self) -> Dict:
        """Provide fallback meal recommendations when database is unavailable"""
        return {
            'breakfast': [
                {
                    'Food_Item': 'Greek Yogurt with Berries',
                    'Enhanced_Category': 'dairy_proteins',
                    'Calories_kcal': 150,
                    'Protein_g': 15,
                    'Carbohydrates_g': 20,
                    'Fat_g': 3,
                    'Fiber_g': 3,
                    'Sugars_g': 15,
                    'Sodium_mg': 50,
                    'Portion_Recommendation': '150-200g',
                    'Overall_Quality': 9,
                    'Ectomorph_Score': 8,
                    'Mesomorph_Score': 9,
                    'Endomorph_Score': 7,
                    'Cholesterol_mg': 10
                },
                {
                    'Food_Item': 'Whole Grain Oats',
                    'Enhanced_Category': 'complex_carbs',
                    'Calories_kcal': 389,
                    'Protein_g': 16.9,
                    'Carbohydrates_g': 66,
                    'Fat_g': 6.9,
                    'Fiber_g': 10.6,
                    'Sugars_g': 1,
                    'Sodium_mg': 2,
                    'Portion_Recommendation': '40-50g',
                    'Overall_Quality': 9,
                    'Ectomorph_Score': 9,
                    'Mesomorph_Score': 8,
                    'Endomorph_Score': 6,
                    'Cholesterol_mg': 0
                }
            ],
            'lunch': [
                {
                    'Food_Item': 'Grilled Chicken Breast',
                    'Enhanced_Category': 'lean_proteins',
                    'Calories_kcal': 165,
                    'Protein_g': 31,
                    'Carbohydrates_g': 0,
                    'Fat_g': 3.6,
                    'Fiber_g': 0,
                    'Sugars_g': 0,
                    'Sodium_mg': 74,
                    'Portion_Recommendation': '100-150g',
                    'Overall_Quality': 9,
                    'Ectomorph_Score': 7,
                    'Mesomorph_Score': 9,
                    'Endomorph_Score': 8,
                    'Cholesterol_mg': 85
                },
                {
                    'Food_Item': 'Quinoa',
                    'Enhanced_Category': 'complex_carbs',
                    'Calories_kcal': 368,
                    'Protein_g': 14.1,
                    'Carbohydrates_g': 64.2,
                    'Fat_g': 6.1,
                    'Fiber_g': 7,
                    'Sugars_g': 1.6,
                    'Sodium_mg': 5,
                    'Portion_Recommendation': '80-120g',
                    'Overall_Quality': 9,
                    'Ectomorph_Score': 8,
                    'Mesomorph_Score': 9,
                    'Endomorph_Score': 7,
                    'Cholesterol_mg': 0
                }
            ],
            'dinner': [
                {
                    'Food_Item': 'Baked Salmon',
                    'Enhanced_Category': 'healthy_fats',
                    'Calories_kcal': 208,
                    'Protein_g': 28.5,
                    'Carbohydrates_g': 0,
                    'Fat_g': 9.1,
                    'Fiber_g': 0,
                    'Sugars_g': 0,
                    'Sodium_mg': 69,
                    'Portion_Recommendation': '100-150g',
                    'Overall_Quality': 10,
                    'Ectomorph_Score': 8,
                    'Mesomorph_Score': 9,
                    'Endomorph_Score': 8,
                    'Cholesterol_mg': 70
                },
                {
                    'Food_Item': 'Steamed Broccoli',
                    'Enhanced_Category': 'vegetables',
                    'Calories_kcal': 34,
                    'Protein_g': 2.8,
                    'Carbohydrates_g': 6.6,
                    'Fat_g': 0.4,
                    'Fiber_g': 2.6,
                    'Sugars_g': 1.5,
                    'Sodium_mg': 33,
                    'Portion_Recommendation': '100-150g',
                    'Overall_Quality': 9,
                    'Ectomorph_Score': 7,
                    'Mesomorph_Score': 8,
                    'Endomorph_Score': 9,
                    'Cholesterol_mg': 0
                }
            ],
            'snack': [
                {
                    'Food_Item': 'Mixed Nuts',
                    'Enhanced_Category': 'healthy_fats',
                    'Calories_kcal': 607,
                    'Protein_g': 20,
                    'Carbohydrates_g': 21,
                    'Fat_g': 54,
                    'Fiber_g': 8,
                    'Sugars_g': 4,
                    'Sodium_mg': 16,
                    'Portion_Recommendation': '30-40g',
                    'Overall_Quality': 8,
                    'Ectomorph_Score': 9,
                    'Mesomorph_Score': 8,
                    'Endomorph_Score': 6,
                    'Cholesterol_mg': 0
                },
                {
                    'Food_Item': 'Apple with Almond Butter',
                    'Enhanced_Category': 'fruits',
                    'Calories_kcal': 195,
                    'Protein_g': 4,
                    'Carbohydrates_g': 30,
                    'Fat_g': 8,
                    'Fiber_g': 6,
                    'Sugars_g': 22,
                    'Sodium_mg': 2,
                    'Portion_Recommendation': '1 medium apple + 15g',
                    'Overall_Quality': 8,
                    'Ectomorph_Score': 8,
                    'Mesomorph_Score': 8,
                    'Endomorph_Score': 7,
                    'Cholesterol_mg': 0
                }
            ]
        }

    def save_recommendations_to_csv(self, output_path: str = None) -> str:
        """
        Save comprehensive recommendations to CSV file in the expected format
        
        Args:
            output_path: Path to save the CSV file. If None, uses default output location
            
        Returns:
            Path to the saved file
        """
        if output_path is None:
            output_path = os.path.join(OUTPUT_FILES_DIR, "output_recommendation.csv")
        
        try:
            # Generate comprehensive recommendations
            recommendations = self.generate_comprehensive_recommendations()
            meal_recommendations = self.generate_meal_based_recommendations()
            
            # Extract macronutrient data
            macros = recommendations.get('macros', {})
            
            # Create CSV content
            lines = []
            
            # Macronutrients section
            lines.append(f"calories,{macros.get('calories', 2000)}")
            lines.append(f"protein,{macros.get('protein_g', 150)}")
            lines.append(f"carbs,{macros.get('carbs_g', 200)}")
            lines.append(f"fat,{macros.get('fat_g', 80)}")
            lines.append(f"bmr,{macros.get('bmr', 1500)}")
            lines.append(f"tdee,{macros.get('tdee', 2000)}")
            lines.append(f"somatotype,{macros.get('somatotype', 'mesomorph')}")
            lines.append("")
            
            # Suggested Foods section
            lines.append("Suggested Foods")
            
            # Add foods from all meal categories
            food_count = 0
            max_foods = 20  # Limit to prevent too many foods
            
            for meal_type, foods in meal_recommendations.items():
                for food in foods[:5]:  # Max 5 foods per meal type
                    if food_count >= max_foods:
                        break
                    food_name = food.get('Food_Item', 'Unknown Food')
                    category = food.get('Enhanced_Category', 'general').replace('_', ' ').title()
                    lines.append(f"{food_name} ({category})")
                    food_count += 1
                if food_count >= max_foods:
                    break
            
            lines.append("")
            
            # Nutrition Insights section
            lines.append("Nutrition Insights")
            
            # Add personalized insights
            somatotype = macros.get('somatotype', 'mesomorph').title()
            goal = macros.get('goal', 'maintain_weight').replace('_', ' ').title()
            activity = macros.get('activity_level', 'moderate').title()
            
            lines.append(f"Optimized for {somatotype} body type")
            lines.append(f"Goal: {goal}")
            lines.append(f"Activity Level: {activity}")
            lines.append(f"Meal distribution supports your metabolic profile")
            
            # Add somatotype-specific insights
            somatotype_insights = {
                'ectomorph': [
                    "Higher calorie intake to support weight gain",
                    "Focus on complex carbohydrates for sustained energy",
                    "Frequent meals to maximize nutrient absorption"
                ],
                'mesomorph': [
                    "Balanced macronutrient distribution for optimal performance",
                    "Moderate calorie surplus/deficit based on goals",
                    "Emphasizes protein for muscle maintenance and growth"
                ],
                'endomorph': [
                    "Controlled calorie intake for effective weight management",
                    "Higher protein ratio to boost metabolism",
                    "Focus on nutrient-dense, lower glycemic foods"
                ]
            }
            
            soma_key = macros.get('somatotype', 'mesomorph').lower()
            if soma_key in somatotype_insights:
                for insight in somatotype_insights[soma_key]:
                    lines.append(insight)
            
            # Write to file
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w') as f:
                f.write('\n'.join(lines))
            
            print(f"✅ Saved diet recommendations to {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Error saving recommendations to CSV: {e}")
            raise
    
    def save_meal_recommendations_to_json(self, output_path: str = None) -> str:
        """
        Save meal-based recommendations to JSON file for database storage
        
        Args:
            output_path: Path to save the JSON file. If None, uses default output location
            
        Returns:
            Path to the saved file
        """
        if output_path is None:
            output_path = os.path.join(OUTPUT_FILES_DIR, "meal_recommendations.json")
        
        try:
            import json
            
            # Generate meal recommendations
            meal_recommendations = self.generate_meal_based_recommendations()
            
            # Convert to serializable format
            serializable_meals = {}
            for meal_type, foods in meal_recommendations.items():
                serializable_meals[meal_type] = []
                for food in foods:
                    food_dict = {}
                    for key, value in food.items():
                        # Convert numpy types and handle NaN values
                        if pd.isna(value):
                            food_dict[key] = None
                        elif hasattr(value, 'item'):  # numpy types
                            food_dict[key] = value.item()
                        else:
                            food_dict[key] = value
                    serializable_meals[meal_type].append(food_dict)
            
            # Write to file
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(serializable_meals, f, indent=2)
            
            print(f"✅ Saved meal recommendations to {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Error saving meal recommendations to JSON: {e}")
            raise

# Example usage and testing
if __name__ == "__main__":
    print("Initializing Diet Recommendation Engine...")
    engine = DietRecommendationEngine()
    
    print("Generating comprehensive recommendations...")
    recommendations = engine.generate_comprehensive_recommendations()
    
    print("\n=== PERSONALIZED DIET RECOMMENDATIONS ===")
    print(f"Somatotype: {recommendations['macros']['somatotype'].title()}")
    print(f"Goal: {recommendations['macros']['goal'].replace('_', ' ').title()}")
    print(f"Activity Level: {recommendations['macros']['activity_level'].title()}")
    
    print(f"\n=== DAILY MACRONUTRIENT TARGETS ===")
    macros = recommendations['macros']
    print(f"Calories: {macros['calories']} kcal")
    print(f"Protein: {macros['protein_g']}g ({macros['protein_g']*4/macros['calories']*100:.1f}%)")
    print(f"Carbohydrates: {macros['carbs_g']}g ({macros['carbs_g']*4/macros['calories']*100:.1f}%)")
    print(f"Fat: {macros['fat_g']}g ({macros['fat_g']*9/macros['calories']*100:.1f}%)")
    
    print(f"\n=== RECOMMENDED FOODS ===")
    for i, food in enumerate(recommendations['recommended_foods'][:10], 1):
        print(f"{i}. {food['name']} ({food['category']}) - {food['calories_per_100g']} cal/100g")
    
    print(f"\n=== NUTRITION INSIGHTS ===")
    for insight in recommendations['nutrition_insights']:
        print(f"• {insight}")
