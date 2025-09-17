#!/usr/bin/env python3
"""
Dynamic Somatotype-Based Diet Recommendation Demo
Shows how the optimized database enables personalized recommendations
"""

import pandas as pd
import numpy as np

class DynamicDietRecommender:
    def __init__(self, database_path):
        """Initialize with optimized diet database"""
        self.foods_db = pd.read_csv(database_path)
        print(f"🍽️ Loaded {len(self.foods_db):,} optimized foods for recommendations")
    
    def calculate_individual_macros(self, user_profile, somatotype_scores):
        """
        Calculate personalized macros based on individual somatotype scores
        """
        endomorphy, mesomorphy, ectomorphy = somatotype_scores
        
        # Calculate BMR using Mifflin-St Jeor equation
        if user_profile['gender'].lower() == 'male':
            bmr = 10 * user_profile['weight'] + 6.25 * user_profile['height'] - 5 * user_profile['age'] + 5
        else:
            bmr = 10 * user_profile['weight'] + 6.25 * user_profile['height'] - 5 * user_profile['age'] - 161
        
        # Activity multipliers
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        
        tdee = bmr * activity_multipliers.get(user_profile['activity_level'], 1.55)
        
        # Goal adjustments
        goal_adjustments = {
            'weight_loss': -500,
            'maintenance': 0,
            'weight_gain': +500
        }
        
        target_calories = tdee + goal_adjustments.get(user_profile['goal'], 0)
        
        # Dynamic macro calculation based on somatotype scores
        # Protein ratio: Higher mesomorphy = more protein
        base_protein_ratio = 0.25
        meso_protein_bonus = (mesomorphy / 10) * 0.10  # Up to +10%
        endo_protein_bonus = (endomorphy / 10) * 0.05  # Up to +5% for satiety
        protein_ratio = min(base_protein_ratio + meso_protein_bonus + endo_protein_bonus, 0.40)
        
        # Carb ratio: Higher ectomorphy = more carbs, lower endomorphy = fewer carbs
        base_carb_ratio = 0.35
        ecto_carb_bonus = (ectomorphy / 10) * 0.15  # Up to +15%
        endo_carb_penalty = (endomorphy / 10) * 0.10  # Up to -10%
        carb_ratio = max(base_carb_ratio + ecto_carb_bonus - endo_carb_penalty, 0.20)
        
        # Fat ratio: Remaining calories
        fat_ratio = max(1.0 - protein_ratio - carb_ratio, 0.20)
        
        return {
            'calories': round(target_calories),
            'protein_g': round((target_calories * protein_ratio) / 4),
            'carbs_g': round((target_calories * carb_ratio) / 4),
            'fat_g': round((target_calories * fat_ratio) / 9),
            'protein_ratio': protein_ratio,
            'carb_ratio': carb_ratio,
            'fat_ratio': fat_ratio
        }
    
    def get_somatotype_food_preferences(self, somatotype_scores, goal):
        """
        Determine food category preferences based on somatotype and goal
        """
        endomorphy, mesomorphy, ectomorphy = somatotype_scores
        
        preferences = {}
        
        # Base preferences by dominant somatotype
        if ectomorphy >= max(endomorphy, mesomorphy):
            # Ectomorph-dominant: Need calorie density
            preferences = {
                'energy_dense': 9,
                'healthy_fats': 8,
                'complex_carbs': 8,
                'complete_proteins': 7,
                'dairy_proteins': 7,
                'quick_carbs': 6,
                'balanced_foods': 5,
                'weight_loss_friendly': 2
            }
        elif mesomorphy >= max(endomorphy, ectomorphy):
            # Mesomorph-dominant: Balanced with high protein
            preferences = {
                'lean_proteins': 9,
                'complete_proteins': 8,
                'complex_carbs': 8,
                'dairy_proteins': 7,
                'healthy_fats': 6,
                'balanced_foods': 7,
                'energy_dense': 5,
                'weight_loss_friendly': 4
            }
        else:
            # Endomorph-dominant: Lower calorie, high satiety
            preferences = {
                'weight_loss_friendly': 9,
                'vegetables': 9,
                'lean_proteins': 8,
                'complex_carbs': 6,
                'fruits': 6,
                'complete_proteins': 5,
                'balanced_foods': 5,
                'energy_dense': 2
            }
        
        # Adjust for goal
        if goal == 'weight_loss':
            preferences['weight_loss_friendly'] = min(preferences.get('weight_loss_friendly', 0) + 2, 10)
            preferences['vegetables'] = min(preferences.get('vegetables', 0) + 2, 10)
            preferences['energy_dense'] = max(preferences.get('energy_dense', 0) - 2, 1)
        elif goal == 'weight_gain':
            preferences['energy_dense'] = min(preferences.get('energy_dense', 0) + 3, 10)
            preferences['healthy_fats'] = min(preferences.get('healthy_fats', 0) + 2, 10)
            preferences['weight_loss_friendly'] = max(preferences.get('weight_loss_friendly', 0) - 2, 1)
        
        return preferences
    
    def recommend_daily_meals(self, user_profile, somatotype_scores):
        """
        Generate complete daily meal recommendations
        """
        print(f"\n🎯 GENERATING PERSONALIZED RECOMMENDATIONS")
        print(f"👤 User: {user_profile['name']} ({user_profile['goal']})")
        print(f"🧬 Somatotype: {somatotype_scores[0]}-{somatotype_scores[1]}-{somatotype_scores[2]}")
        print("=" * 60)
        
        # Calculate personalized macros
        target_macros = self.calculate_individual_macros(user_profile, somatotype_scores)
        
        print(f"📊 PERSONALIZED DAILY TARGETS:")
        print(f"   Calories: {target_macros['calories']:,} kcal")
        print(f"   Protein: {target_macros['protein_g']}g ({target_macros['protein_ratio']:.1%})")
        print(f"   Carbs: {target_macros['carbs_g']}g ({target_macros['carb_ratio']:.1%})")
        print(f"   Fat: {target_macros['fat_g']}g ({target_macros['fat_ratio']:.1%})")
        
        # Get food preferences
        food_preferences = self.get_somatotype_food_preferences(somatotype_scores, user_profile['goal'])
        
        print(f"\n🎯 SOMATOTYPE-OPTIMIZED FOOD CATEGORIES:")
        for category, score in sorted(food_preferences.items(), key=lambda x: x[1], reverse=True)[:6]:
            print(f"   {category}: Priority {score}/10")
        
        # Generate meal recommendations
        meals = {
            'breakfast': self.select_meal_foods('breakfast', target_macros, food_preferences, 0.25),
            'lunch': self.select_meal_foods('lunch', target_macros, food_preferences, 0.35),
            'dinner': self.select_meal_foods('dinner', target_macros, food_preferences, 0.30),
            'snacks': self.select_meal_foods('snack', target_macros, food_preferences, 0.10)
        }
        
        return meals, target_macros
    
    def select_meal_foods(self, meal_timing, target_macros, preferences, meal_proportion):
        """
        Select optimal foods for a specific meal based on somatotype preferences
        """
        # Filter foods suitable for this meal timing
        suitable_foods = self.foods_db[
            self.foods_db['Meal_Timing'].str.contains(meal_timing, na=False, case=False)
        ].copy()
        
        # Calculate meal targets
        meal_calories = target_macros['calories'] * meal_proportion
        meal_protein = target_macros['protein_g'] * meal_proportion
        meal_carbs = target_macros['carbs_g'] * meal_proportion
        meal_fat = target_macros['fat_g'] * meal_proportion
        
        # Add preference scores
        suitable_foods['preference_score'] = suitable_foods['Enhanced_Category'].map(preferences).fillna(1)
        
        # Select foods from each preferred category
        selected_foods = []
        remaining_calories = meal_calories
        remaining_protein = meal_protein
        
        # Sort by preference and nutritional fit
        suitable_foods['suitability_score'] = (
            suitable_foods['preference_score'] * 0.4 +
            suitable_foods['Overall_Quality'] * 0.3 +
            (suitable_foods['Protein_g'] / suitable_foods['Calories_kcal'].where(suitable_foods['Calories_kcal'] > 0, 1)) * 20 * 0.3
        )
        
        # Select top foods from preferred categories
        for category in sorted(preferences.keys(), key=lambda x: preferences[x], reverse=True):
            category_foods = suitable_foods[suitable_foods['Enhanced_Category'] == category].head(3)
            if len(category_foods) > 0 and len(selected_foods) < 4:
                best_food = category_foods.iloc[0]
                
                # Calculate appropriate portion
                calories_per_100g = max(best_food['Calories_kcal'], 1)
                portion_multiplier = min(remaining_calories / calories_per_100g, 2.0)
                portion_calories = best_food['Calories_kcal'] * portion_multiplier
                portion_protein = best_food['Protein_g'] * portion_multiplier
                
                selected_foods.append({
                    'food': best_food['Food_Item'],
                    'category': best_food['Enhanced_Category'],
                    'portion': f"{portion_multiplier * 100:.0f}g",
                    'calories': round(portion_calories),
                    'protein': round(portion_protein, 1),
                    'carbs': round(best_food['Carbohydrates_g'] * portion_multiplier, 1),
                    'fat': round(best_food['Fat_g'] * portion_multiplier, 1),
                    'suitability': round(best_food['suitability_score'], 1)
                })
                
                remaining_calories -= portion_calories
                remaining_protein -= portion_protein
                
                if remaining_calories <= 50:
                    break
        
        return selected_foods

def demo_recommendations():
    """Demonstrate dynamic recommendations for different somatotypes and goals"""
    
    # Initialize recommender
    recommender = DynamicDietRecommender('optimized_diet_recommendation_database.csv')
    
    # Test cases representing different scenarios
    test_cases = [
        {
            'name': 'Alex (Ectomorph)',
            'user_profile': {
                'name': 'Alex',
                'gender': 'male',
                'age': 25,
                'weight': 65,  # kg
                'height': 175, # cm
                'activity_level': 'moderate',
                'goal': 'weight_gain'
            },
            'somatotype_scores': (2, 3, 6)  # Low endo, moderate meso, high ecto
        },
        {
            'name': 'Jamie (Mesomorph)',
            'user_profile': {
                'name': 'Jamie',
                'gender': 'female',
                'age': 28,
                'weight': 68,
                'height': 165,
                'activity_level': 'active',
                'goal': 'maintenance'
            },
            'somatotype_scores': (3, 6, 2)  # Moderate endo, high meso, low ecto
        },
        {
            'name': 'Taylor (Endomorph)',
            'user_profile': {
                'name': 'Taylor',
                'gender': 'male',
                'age': 35,
                'weight': 85,
                'height': 170,
                'activity_level': 'light',
                'goal': 'weight_loss'
            },
            'somatotype_scores': (6, 3, 2)  # High endo, moderate meso, low ecto
        }
    ]
    
    for test_case in test_cases:
        meals, macros = recommender.recommend_daily_meals(
            test_case['user_profile'],
            test_case['somatotype_scores']
        )
        
        print(f"\n🍽️ DAILY MEAL PLAN:")
        for meal_name, foods in meals.items():
            print(f"\n   {meal_name.upper()}:")
            total_calories = sum(food['calories'] for food in foods)
            total_protein = sum(food['protein'] for food in foods)
            print(f"   Target: ~{macros['calories'] * {'breakfast': 0.25, 'lunch': 0.35, 'dinner': 0.30, 'snacks': 0.10}[meal_name]:.0f} kcal")
            
            for food in foods:
                print(f"      • {food['food']} ({food['portion']})")
                print(f"        {food['calories']} kcal | {food['protein']}g protein | Category: {food['category']}")
            
            print(f"   Subtotal: {total_calories} kcal, {total_protein:.1f}g protein")
        
        print("\n" + "="*80)

if __name__ == "__main__":
    print("🍽️ DYNAMIC SOMATOTYPE-BASED DIET RECOMMENDATION DEMO")
    print("=" * 60)
    demo_recommendations()
