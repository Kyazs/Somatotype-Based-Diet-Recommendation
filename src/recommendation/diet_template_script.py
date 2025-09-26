#!/usr/bin/env python3
"""
Fixed Comprehensive Template Generator with Proper Exercise IDs
Generates 1080 diet templates with correct exercise categorization
"""

import pandas as pd
import json
import numpy as np
import itertools
import re
import hashlib
import random

print("🏗️ Starting Fixed Comprehensive Template Generation...")
print("📊 Loading exercise databases...")

# Load exercise databases
try:
    with open('data/datasets/fitness/data/exercises.json', 'r') as f:
        all_exercises = json.load(f)
    
    print(f"✅ Loaded {len(all_exercises)} total exercises")
    
    # Categorize exercises based on requirements
    push_exercises = {
        'chest': [],    # 4 exercises (chest bodypart/pectorals target)
        'triceps': [],  # 2 exercises (triceps target)
        'shoulders': [] # 2 exercises (shoulders target/delts)
    }
    
    pull_exercises = {
        'back': [],     # 4 exercises (back bodypart/lats target)
        'biceps': []    # 3 exercises (biceps target)
    }
    
    legs_exercises = {
        'legs': [],     # 5 exercises (upper legs bodypart)
        'traps': []     # 1 exercise (traps target)
    }
    
    bodyweight_exercises = []  # 8+ exercises with "body weight" equipment
    
    # Categorize all exercises
    for exercise in all_exercises:
        exercise_id = exercise['exerciseId']
        target_muscles = exercise.get('targetMuscles', [])
        body_parts = exercise.get('bodyParts', [])
        equipments = exercise.get('equipments', [])
        
        # Bodyweight exercises
        if 'body weight' in equipments:
            bodyweight_exercises.append(exercise_id)
        
        # Push exercises - Chest
        if ('chest' in body_parts or 'pectorals' in target_muscles) and 'body weight' not in equipments:
            push_exercises['chest'].append(exercise_id)
        
        # Push exercises - Triceps
        if 'triceps' in target_muscles and 'body weight' not in equipments:
            push_exercises['triceps'].append(exercise_id)
        
        # Push exercises - Shoulders
        if any(muscle in target_muscles for muscle in ['delts', 'shoulders', 'deltoids']) and 'body weight' not in equipments:
            push_exercises['shoulders'].append(exercise_id)
        # Also include shoulder-specific bodyparts
        if 'shoulders' in body_parts and 'body weight' not in equipments:
            push_exercises['shoulders'].append(exercise_id)
        
        # Pull exercises - Back
        if ('back' in body_parts or any(muscle in target_muscles for muscle in ['lats', 'rhomboids', 'middle traps', 'lower traps'])) and 'body weight' not in equipments:
            pull_exercises['back'].append(exercise_id)
        
        # Pull exercises - Biceps
        if 'biceps' in target_muscles and 'body weight' not in equipments:
            pull_exercises['biceps'].append(exercise_id)
        
        # Legs exercises - Legs
        if ('upper legs' in body_parts or any(muscle in target_muscles for muscle in ['quads', 'hamstrings', 'glutes', 'quadriceps'])) and 'body weight' not in equipments:
            legs_exercises['legs'].append(exercise_id)
        
        # Legs exercises - Traps (for shrugs)
        if 'traps' in target_muscles and 'body weight' not in equipments:
            legs_exercises['traps'].append(exercise_id)
    
    # Print categorization results
    print(f"📊 Exercise categorization:")
    print(f"   Push - Chest: {len(push_exercises['chest'])} exercises")
    print(f"   Push - Triceps: {len(push_exercises['triceps'])} exercises") 
    print(f"   Push - Shoulders: {len(push_exercises['shoulders'])} exercises")
    print(f"   Pull - Back: {len(pull_exercises['back'])} exercises")
    print(f"   Pull - Biceps: {len(pull_exercises['biceps'])} exercises")
    print(f"   Legs - Legs: {len(legs_exercises['legs'])} exercises")
    print(f"   Legs - Traps: {len(legs_exercises['traps'])} exercises")
    print(f"   Bodyweight: {len(bodyweight_exercises)} exercises")
    
except FileNotFoundError as e:
    print(f"❌ Error loading exercise files: {e}")
    exit(1)

# Load existing Filipino meals template
try:
    filipino_meals_df = pd.read_csv('enhanced_diet_templates_filipino_meals.csv')
    print(f"✅ Loaded {len(filipino_meals_df)} Filipino meal templates")
except FileNotFoundError as e:
    print(f"❌ Error loading Filipino meals file: {e}")
    exit(1)

def get_exercises_by_category_and_count(category, muscle_group, count):
    """Get specific number of exercises for a category and muscle group"""
    if category == 'push':
        available = push_exercises[muscle_group]
    elif category == 'pull':
        available = pull_exercises[muscle_group]
    elif category == 'legs':
        available = legs_exercises[muscle_group]
    else:
        return []
    
    if len(available) >= count:
        return random.sample(available, count)
    else:
        # If not enough exercises, repeat some
        result = available.copy()
        while len(result) < count:
            result.extend(random.sample(available, min(count - len(result), len(available))))
        return result[:count]

def get_bodyweight_exercises(count=8):
    """Get bodyweight exercises"""
    if len(bodyweight_exercises) >= count:
        return random.sample(bodyweight_exercises, count)
    else:
        # If not enough, repeat some
        result = bodyweight_exercises.copy()
        while len(result) < count:
            result.extend(random.sample(bodyweight_exercises, min(count - len(result), len(bodyweight_exercises))))
        return result[:count]

def generate_template_id(somatotype, gender, goal, activity_level, exercise_complexity, exercise_type):
    """Generate template ID in format: ENDO_M_WEIGHT_SEDE_BEG_GYM_D664"""
    
    # Somatotype mapping
    somatotype_map = {
        'ectomorph': 'ECTO',
        'mesomorph': 'MESO', 
        'endomorph': 'ENDO',
        'ecto_endo': 'ECEN',
        'meso_ecto': 'MEEC',
        'endo_meso': 'ENME'
    }
    
    # Gender mapping
    gender_map = {'male': 'M', 'female': 'F'}
    
    # Goal mapping  
    goal_map = {
        'weight_loss': 'LOSS',
        'maintenance': 'MAIN',
        'weight_gain': 'GAIN'
    }
    
    # Activity level mapping
    activity_map = {
        'sedentary': 'SEDE',
        'lightly_active': 'LITE', 
        'moderately_active': 'MODR',
        'very_active': 'VERY',
        'extra_active': 'EXTR'
    }
    
    # Exercise complexity mapping
    complexity_map = {
        'beginner': 'BEG',
        'intermediate': 'INT',
        'hard': 'ADV'
    }
    
    # Exercise type mapping
    type_map = {'gym': 'GYM', 'bodyweight': 'BWE'}
    
    # Create base ID
    base_id = f"{somatotype_map[somatotype]}_{gender_map[gender]}_{goal_map.get(goal, 'MAIN')}_{activity_map[activity_level]}_{complexity_map[exercise_complexity]}_{type_map[exercise_type]}"
    
    # Generate unique suffix using hash
    hash_input = f"{base_id}_{somatotype}_{gender}_{goal}_{activity_level}_{exercise_complexity}_{exercise_type}"
    hash_suffix = hashlib.md5(hash_input.encode()).hexdigest()[:4].upper()
    
    return f"{base_id}_{hash_suffix}"

# Somatotype characteristics and meal adjustments
SOMATOTYPE_PROFILES = {
    'ectomorph': {
        'description': 'Naturally lean and struggles to gain weight, fast metabolism',
        'diet_principles': {
            'weight_loss': 'Focus on nutrient-dense foods | Maintain muscle mass during deficit | Don\'t cut calories too drastically | Include healthy fats and complex carbs',
            'maintenance': 'Eat frequently throughout the day | Include calorie-dense healthy foods | Focus on complex carbohydrates and healthy fats | Don\'t skip meals',
            'weight_gain': 'Eat in caloric surplus with frequent meals | Focus on calorie-dense foods | Include plenty of complex carbohydrates | Add healthy fats to every meal'
        },
        'macros': {
            'weight_loss': (30, 40, 30),  # P, C, F
            'maintenance': (25, 45, 30),
            'weight_gain': (25, 50, 25)
        }
    },
    'mesomorph': {
        'description': 'Naturally muscular and athletic build, efficient metabolism',
        'diet_principles': {
            'weight_loss': 'Balance macronutrients evenly | Focus on whole foods | Moderate caloric deficit | Maintain protein for muscle preservation',
            'maintenance': 'Maintain balanced macronutrient ratios | Focus on whole food sources | Eat around training sessions | Stay consistent with meal timing',
            'weight_gain': 'Increase calories gradually | Maintain balanced macronutrient approach | Focus on quality protein sources | Time carbs around workouts'
        },
        'macros': {
            'weight_loss': (35, 35, 30),
            'maintenance': (30, 40, 30),
            'weight_gain': (30, 45, 25)
        }
    },
    'endomorph': {
        'description': 'Naturally soft and round, gains weight easily, slower metabolism',
        'diet_principles': {
            'weight_loss': 'Prioritize lean protein and healthy fats | Strictly limit refined carbohydrates and sugars | Focus on high-fiber vegetables to stay full | Drink plenty of water to support metabolism',
            'maintenance': 'Monitor portions carefully | Choose low-glycemic carbohydrates | Include plenty of fiber and protein | Stay active throughout the day',
            'weight_gain': 'Focus on lean muscle gain | Increase protein significantly | Choose nutrient-dense foods | Limit processed foods and sugars'
        },
        'macros': {
            'weight_loss': (35, 25, 40),
            'maintenance': (30, 30, 40),
            'weight_gain': (35, 30, 35)
        }
    },
    'ecto_endo': {
        'description': 'Combination of ectomorph-endomorph traits, varies between fast and slow metabolism periods',
        'diet_principles': {
            'weight_loss': 'Moderate caloric deficit with higher protein | Focus on nutrient timing around workouts | Balance healthy fats and complex carbs | Monitor metabolism responses',
            'maintenance': 'Flexible approach based on activity levels | Higher carbs on training days | Maintain consistent protein intake | Adjust portions based on metabolic response',
            'weight_gain': 'Strategic surplus with quality foods | Higher protein for muscle building | Moderate healthy fats | Monitor body composition changes closely'
        },
        'macros': {
            'weight_loss': (35, 30, 35),
            'maintenance': (30, 35, 35),
            'weight_gain': (30, 40, 30)
        }
    },
    'meso_ecto': {
        'description': 'Athletic build with faster metabolism, builds muscle easily but stays lean',
        'diet_principles': {
            'weight_loss': 'Moderate deficit with balanced macros | Maintain high protein for muscle preservation | Include complex carbs for energy | Don\'t cut too aggressively',
            'maintenance': 'Balanced approach with consistent eating | Time carbs around training | Focus on whole food sources | Maintain steady meal schedule',
            'weight_gain': 'Gradual surplus with quality foods | Higher carbs for muscle building | Adequate protein for growth | Monitor lean mass gains'
        },
        'macros': {
            'weight_loss': (35, 35, 30),
            'maintenance': (28, 42, 30),
            'weight_gain': (28, 47, 25)
        }
    },
    'endo_meso': {
        'description': 'Muscular build but tends to store fat easily, moderate metabolism',
        'diet_principles': {
            'weight_loss': 'Higher protein with controlled carbs | Focus on post-workout carb timing | Emphasize healthy fats | Create moderate deficit consistently',
            'maintenance': 'Careful portion control | Strategic carb cycling | Consistent protein intake | Regular physical activity',
            'weight_gain': 'Clean bulk approach | High protein priority | Limit processed foods | Focus on muscle building over fat gain'
        },
        'macros': {
            'weight_loss': (38, 30, 32),
            'maintenance': (32, 35, 33),
            'weight_gain': (32, 38, 30)
        }
    }
}

# Activity multipliers for TDEE calculation
ACTIVITY_MULTIPLIERS = {
    'sedentary': 1.2,
    'lightly_active': 1.375,
    'moderately_active': 1.55,
    'very_active': 1.725,
    'extra_active': 1.9
}

# Base metabolic rates (BMR) - approximate values
BMR_VALUES = {
    ('male', 'ectomorph'): 1800,
    ('male', 'mesomorph'): 1900,
    ('male', 'endomorph'): 1800,
    ('male', 'ecto_endo'): 1825,
    ('male', 'meso_ecto'): 1850,
    ('male', 'endo_meso'): 1850,
    ('female', 'ectomorph'): 1400,
    ('female', 'mesomorph'): 1500,
    ('female', 'endomorph'): 1400,
    ('female', 'ecto_endo'): 1425,
    ('female', 'meso_ecto'): 1450,
    ('female', 'endo_meso'): 1450,
}

def calculate_calories_and_macros(somatotype, gender, goal, activity_level):
    """Calculate calories and macronutrient distribution"""
    base_bmr = BMR_VALUES.get((gender, somatotype), 1600)
    tdee = base_bmr * ACTIVITY_MULTIPLIERS[activity_level]
    
    # Adjust calories based on goal
    if goal == 'weight_loss':
        total_calories = int(tdee * 0.8)  # 20% deficit
    elif goal == 'weight_gain':
        total_calories = int(tdee * 1.15)  # 15% surplus
    else:  # maintenance
        total_calories = int(tdee)
    
    # Get macro ratios
    protein_pct, carbs_pct, fats_pct = SOMATOTYPE_PROFILES[somatotype]['macros'][goal]
    
    # Calculate grams
    protein_g = round((total_calories * protein_pct / 100) / 4, 1)  # 4 cal/g
    carbs_g = round((total_calories * carbs_pct / 100) / 4, 1)    # 4 cal/g
    fats_g = round((total_calories * fats_pct / 100) / 9, 1)     # 9 cal/g
    
    return total_calories, protein_g, carbs_g, fats_g, protein_pct, carbs_pct, fats_pct

def get_fitness_strategy_and_split(somatotype, goal):
    """Get fitness strategy and split based on somatotype and goal"""
    strategies = {
        'ectomorph': {
            'weight_loss': 'Focus on resistance training to maintain muscle mass during cut with minimal cardio.',
            'maintenance': 'Balanced approach with resistance training emphasis and moderate cardio for general health.',
            'weight_gain': 'Heavy focus on progressive overload strength training with minimal cardio to maximize muscle gain.'
        },
        'mesomorph': {
            'weight_loss': 'Combine strength training with cardio intervals for efficient fat loss while maintaining muscle.',
            'maintenance': 'Balanced mix of strength training and cardio with variety in training styles.',
            'weight_gain': 'Focus on progressive strength training with moderate cardio for athletic development.'
        },
        'endomorph': {
            'weight_loss': 'Combine consistent cardiovascular exercise to manage fat with strength training to build metabolic-boosting muscle.',
            'maintenance': 'Emphasize strength training with regular cardio to maintain body composition and metabolic health.',
            'weight_gain': 'Prioritize lean muscle building through strength training with moderate cardio to minimize fat gain.'
        },
        'ecto_endo': {
            'weight_loss': 'Strategic combination of strength and cardio with careful monitoring of recovery and energy levels.',
            'maintenance': 'Flexible training approach adapting to energy levels with emphasis on consistency.',
            'weight_gain': 'Focus on strength training with strategic cardio timing to support both muscle gain and metabolic health.'
        },
        'meso_ecto': {
            'weight_loss': 'Efficient combination of strength and cardio with emphasis on maintaining athletic performance.',
            'maintenance': 'Performance-focused training with balanced strength and conditioning elements.',
            'weight_gain': 'Progressive overload strength training with athletic conditioning for lean muscle development.'
        },
        'endo_meso': {
            'weight_loss': 'Strength-focused program with strategic cardio placement to optimize fat loss while maintaining muscle.',
            'maintenance': 'Balanced strength and cardio approach with attention to body composition management.',
            'weight_gain': 'Clean bulk approach with strength priority and careful cardio integration.'
        }
    }
    
    # Strength and cardio frequency
    splits = {
        'weight_loss': (3, 4),    # 3 strength, 4 cardio
        'maintenance': (4, 3),    # 4 strength, 3 cardio  
        'weight_gain': (5, 2)     # 5 strength, 2 cardio
    }
    
    return strategies[somatotype][goal], splits[goal][0], splits[goal][1]

def select_meal_template(somatotype, gender, goal, activity_level):
    """Select appropriate meal template from Filipino meals dataset"""
    
    # Try to find exact match first
    exact_matches = filipino_meals_df[
        (filipino_meals_df['somatotype'] == somatotype) & 
        (filipino_meals_df['gender'] == gender) &
        (filipino_meals_df['goal'] == goal) &
        (filipino_meals_df['activity_level'] == activity_level)
    ]
    
    if not exact_matches.empty:
        return exact_matches.iloc[0]
    
    # Fall back to closest match by somatotype and gender
    fallback_matches = filipino_meals_df[
        (filipino_meals_df['somatotype'] == somatotype) & 
        (filipino_meals_df['gender'] == gender)
    ]
    
    if not fallback_matches.empty:
        return fallback_matches.iloc[0]
    
    # Final fallback to any match
    return filipino_meals_df.iloc[0]

def generate_template(somatotype, gender, goal, activity_level, exercise_complexity, exercise_type):
    """Generate a single comprehensive template"""
    
    # Generate unique template ID
    template_id = generate_template_id(somatotype, gender, goal, activity_level, exercise_complexity, exercise_type)
    
    # Calculate calories and macros
    total_calories, protein_g, carbs_g, fats_g, protein_pct, carbs_pct, fats_pct = \
        calculate_calories_and_macros(somatotype, gender, goal, activity_level)
    
    # Get meal template
    meal_template = select_meal_template(somatotype, gender, goal, activity_level)
    
    # Get fitness info
    fitness_strategy, strength_split, cardio_split = get_fitness_strategy_and_split(somatotype, goal)
    
    # Generate exercises based on type and requirements
    if exercise_type == 'gym':
        # Get specific exercises as required:
        # Push: 4 chest + 2 triceps + 2 shoulders = 8 total
        chest_exercises = get_exercises_by_category_and_count('push', 'chest', 4)
        triceps_exercises = get_exercises_by_category_and_count('push', 'triceps', 2)
        shoulders_exercises = get_exercises_by_category_and_count('push', 'shoulders', 2)
        
        # Pull: 4 back + 3 biceps = 7 total
        back_exercises = get_exercises_by_category_and_count('pull', 'back', 4)
        biceps_exercises = get_exercises_by_category_and_count('pull', 'biceps', 3)
        
        # Legs: 5 legs + 1 traps = 6 total
        legs_main_exercises = get_exercises_by_category_and_count('legs', 'legs', 5)
        traps_exercises = get_exercises_by_category_and_count('legs', 'traps', 1)
        
        # Combine into PPL format
        push_exercise_ids = chest_exercises + triceps_exercises + shoulders_exercises
        pull_exercise_ids = back_exercises + biceps_exercises
        legs_exercise_ids = legs_main_exercises + traps_exercises
        bodyweight_exercise_ids = []
        
    else:  # bodyweight
        # Get 8 bodyweight exercises
        bodyweight_exercise_ids = get_bodyweight_exercises(8)
        push_exercise_ids = []
        pull_exercise_ids = []
        legs_exercise_ids = []
    
    template = {
        'template_id': template_id,
        'somatotype': somatotype,
        'gender': gender,
        'goal': goal,
        'activity_level': activity_level,
        'exercise_complexity': exercise_complexity,
        'exercise_type': exercise_type,
        'total_calories': total_calories,
        'protein_g': protein_g,
        'carbs_g': carbs_g,
        'fats_g': fats_g,
        'protein_pct': protein_pct,
        'carbs_pct': carbs_pct,
        'fats_pct': fats_pct,
        'breakfast_foods': meal_template['breakfast_foods'],
        'lunch_foods': meal_template['lunch_foods'],
        'dinner_foods': meal_template['dinner_foods'],
        'snack_foods': meal_template['snack_foods'],
        'diet_principles': SOMATOTYPE_PROFILES[somatotype]['diet_principles'][goal],
        'fitness_strategy': fitness_strategy,
        'fitness_split_strength': strength_split,
        'fitness_split_cardio': cardio_split,
        'push_exercises': ','.join(push_exercise_ids) if push_exercise_ids else '',
        'pull_exercises': ','.join(pull_exercise_ids) if pull_exercise_ids else '',
        'legs_exercises': ','.join(legs_exercise_ids) if legs_exercise_ids else '',
        'bodyweight_exercises': ','.join(bodyweight_exercise_ids) if bodyweight_exercise_ids else '',
        'description': SOMATOTYPE_PROFILES[somatotype]['description']
    }
    
    return template

def main():
    """Generate all 1080 comprehensive templates"""
    
    print("\n🎯 Generating comprehensive templates with proper exercise IDs...")
    
    # Define all possible combinations
    somatotypes = ['ectomorph', 'mesomorph', 'endomorph', 'ecto_endo', 'meso_ecto', 'endo_meso']
    genders = ['male', 'female']
    goals = ['weight_loss', 'maintenance', 'weight_gain']
    activity_levels = ['sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extra_active']
    exercise_complexities = ['beginner', 'intermediate', 'hard']
    exercise_types = ['gym', 'bodyweight']
    
    templates = []
    total_combinations = len(somatotypes) * len(genders) * len(goals) * len(activity_levels) * len(exercise_complexities) * len(exercise_types)
    
    print(f"📊 Expected total templates: {total_combinations}")
    
    count = 0
    for somatotype, gender, goal, activity_level, exercise_complexity, exercise_type in itertools.product(
        somatotypes, genders, goals, activity_levels, exercise_complexities, exercise_types
    ):
        try:
            template = generate_template(somatotype, gender, goal, activity_level, exercise_complexity, exercise_type)
            templates.append(template)
            count += 1
            
            if count % 100 == 0:
                print(f"✅ Generated {count}/{total_combinations} templates...")
                
        except Exception as e:
            print(f"❌ Error generating template for {somatotype}/{gender}/{goal}: {e}")
    
    # Create DataFrame
    df = pd.DataFrame(templates)
    
    print(f"\n📊 Successfully generated {len(df)} templates")
    print(f"🎯 Somatotype distribution:")
    print(df['somatotype'].value_counts().sort_index())
    
    # Save to CSV
    output_filename = 'fixed_comprehensive_diet_templates_with_proper_exercise_ids.csv'
    df.to_csv(output_filename, index=False)
    print(f"\n💾 Saved to: {output_filename}")
    
    # Display sample
    print(f"\n📋 Sample of generated templates:")
    print(df[['template_id', 'somatotype', 'gender', 'goal', 'exercise_type', 'total_calories', 'push_exercises', 'bodyweight_exercises']].head(10))
    
    # Show exercise breakdown for gym example
    gym_sample = df[df['exercise_type'] == 'gym'].iloc[0]
    print(f"\n🏋️ Example gym template exercise breakdown:")
    print(f"   Template ID: {gym_sample['template_id']}")
    print(f"   Push exercises: {gym_sample['push_exercises']} (8 exercises: 4 chest + 2 triceps + 2 shoulders)")
    print(f"   Pull exercises: {gym_sample['pull_exercises']} (7 exercises: 4 back + 3 biceps)")
    print(f"   Legs exercises: {gym_sample['legs_exercises']} (6 exercises: 5 legs + 1 traps)")
    
    # Show bodyweight example
    bw_sample = df[df['exercise_type'] == 'bodyweight'].iloc[0]
    print(f"\n🤸 Example bodyweight template exercise breakdown:")
    print(f"   Template ID: {bw_sample['template_id']}")
    print(f"   Bodyweight exercises: {bw_sample['bodyweight_exercises']} (8 exercises with 'body weight' equipment)")
    
    print(f"\n🎉 Complete! Generated {len(df)} comprehensive Filipino meal templates with proper exercise IDs")
    return df

if __name__ == "__main__":
    main()