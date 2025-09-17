import json
import csv
import pandas as pd
import random
from difflib import get_close_matches

# Load exercise data
with open('data/datasets/fitness/data/exercises.json', 'r') as f:
    gym_exercises = json.load(f)

with open('data/datasets/fitness/data/outdoor_exercises.json', 'r') as f:
    bodyweight_exercises = json.load(f)

# Create exercise name to ID mapping for gym exercises
gym_exercise_map = {}
for exercise in gym_exercises:
    gym_exercise_map[exercise['name'].lower()] = exercise['exerciseId']

# Create exercise name to ID mapping for bodyweight exercises
bodyweight_exercise_map = {}
for exercise in bodyweight_exercises:
    bodyweight_exercise_map[exercise['name'].lower()] = exercise['exerciseId']

# Function to find exercise ID by name (with fuzzy matching)
def find_exercise_id(exercise_name, exercise_map):
    """Find exercise ID with fuzzy matching"""
    exercise_name_lower = exercise_name.lower()
    
    # Try exact match first
    if exercise_name_lower in exercise_map:
        return exercise_map[exercise_name_lower]
    
    # Try fuzzy matching
    matches = get_close_matches(exercise_name_lower, exercise_map.keys(), n=1, cutoff=0.6)
    if matches:
        return exercise_map[matches[0]]
    
    return None

# PPL Exercise mappings based on the comprehensive document
PPL_EXERCISES = {
    'beginner': {
        'push': [
            'barbell bench press',
            'incline dumbbell press', 
            'dumbbell bench press',
            'push-ups',
            'overhead shoulder press',
            'dumbbell lateral raises',
            'triceps pushdowns',
            'tricep dips'
        ],
        'pull': [
            'deadlift',
            'bent-over barbell row',
            'lat pulldown',
            'seated cable rows',
            'biceps curls',
            'hammer curls'
        ],
        'legs': [
            'barbell back squat',
            'leg press',
            'romanian deadlift',
            'leg curl',
            'standing calf raise'
        ]
    },
    'intermediate': {
        'push': [
            'flat barbell bench press',
            'incline dumbbell press',
            'standing overhead press',
            'triceps pushdowns',
            'incline bench press',
            'cable fly crossover',
            'seated dumbbell shoulder press',
            'triceps extensions'
        ],
        'pull': [
            'deadlift',
            'pull-ups',
            'barbell biceps curls',
            'face pulls',
            'bent-over barbell row',
            'seated cable rows',
            'hammer curls',
            'dumbbell shrugs'
        ],
        'legs': [
            'barbell back squat',
            'romanian deadlift',
            'leg extensions',
            'standing calf raise',
            'leg press',
            'bulgarian split squats',
            'leg curls',
            'seated leg curls'
        ]
    },
    'advanced': {
        'push': [
            'barbell bench press',
            'incline dumbbell press',
            'weighted dips',
            'overhead press',
            'dumbbell flyes',
            'lateral raises',
            'close-grip bench press',
            'dumbbell shoulder press'
        ],
        'pull': [
            'deadlift',
            'weighted pull-ups',
            'barbell rows',
            't-bar rows',
            'barbell curls',
            'preacher curls',
            'face pulls',
            'shrugs'
        ],
        'legs': [
            'back squat',
            'front squat',
            'romanian deadlift',
            'bulgarian split squats',
            'leg press',
            'leg curls',
            'calf raises',
            'walking lunges'
        ]
    }
}

def get_ppl_exercise_ids(complexity):
    """Get exercise IDs for PPL split based on complexity"""
    push_ids = []
    pull_ids = []
    legs_ids = []
    
    exercises = PPL_EXERCISES.get(complexity, PPL_EXERCISES['beginner'])
    
    for exercise_name in exercises['push']:
        exercise_id = find_exercise_id(exercise_name, gym_exercise_map)
        if exercise_id:
            push_ids.append(exercise_id)
    
    for exercise_name in exercises['pull']:
        exercise_id = find_exercise_id(exercise_name, gym_exercise_map)
        if exercise_id:
            pull_ids.append(exercise_id)
    
    for exercise_name in exercises['legs']:
        exercise_id = find_exercise_id(exercise_name, gym_exercise_map)
        if exercise_id:
            legs_ids.append(exercise_id)
    
    return push_ids, pull_ids, legs_ids

def get_bodyweight_exercise_ids(somatotype, goal, count=8):
    """Get bodyweight exercise IDs based on user preferences"""
    # Define muscle group preferences based on somatotype and goal
    muscle_preferences = {
        'endomorph': {
            'weight_loss': ['abs', 'cardiovascular system', 'cardio', 'glutes', 'quadriceps'],
            'muscle_gain': ['chest', 'shoulders', 'triceps', 'quadriceps', 'glutes'],
            'maintenance': ['abs', 'back', 'chest', 'shoulders', 'quadriceps']
        },
        'ectomorph': {
            'weight_loss': ['chest', 'shoulders', 'triceps', 'quadriceps', 'glutes'],
            'muscle_gain': ['chest', 'shoulders', 'triceps', 'quadriceps', 'glutes', 'back'],
            'maintenance': ['chest', 'back', 'shoulders', 'abs', 'quadriceps']
        },
        'mesomorph': {
            'weight_loss': ['abs', 'back', 'chest', 'shoulders', 'quadriceps'],
            'muscle_gain': ['chest', 'back', 'shoulders', 'triceps', 'quadriceps', 'glutes'],
            'maintenance': ['chest', 'back', 'shoulders', 'abs', 'quadriceps', 'glutes']
        }
    }
    
    preferred_muscles = muscle_preferences.get(somatotype, {}).get(goal, ['abs', 'chest', 'back'])
    
    # Filter bodyweight exercises by preferred muscle groups
    suitable_exercises = []
    for exercise in bodyweight_exercises:
        target_muscles = [muscle.lower() for muscle in exercise.get('targetMuscles', [])]
        if any(pref.lower() in target_muscles for pref in preferred_muscles):
            suitable_exercises.append(exercise['exerciseId'])
    
    # If not enough suitable exercises, add some general ones
    if len(suitable_exercises) < count:
        for exercise in bodyweight_exercises:
            if exercise['exerciseId'] not in suitable_exercises:
                suitable_exercises.append(exercise['exerciseId'])
    
    return random.sample(suitable_exercises, min(count, len(suitable_exercises)))

# Load existing enhanced template to get meal structure
try:
    existing_template = pd.read_csv('enhanced_diet_templates_filipino_meals.csv')
    print(f"Loaded existing template with {len(existing_template)} rows")
except FileNotFoundError:
    print("No existing template found, using basic structure")
    existing_template = None

def get_meals_from_existing_row(row_index=0):
    """Get meals from existing template"""
    if existing_template is not None and row_index < len(existing_template):
        row = existing_template.iloc[row_index]
        return {
            'breakfast': row.get('breakfast_foods', 'Scrambled Eggs | Rice | Coffee'),
            'lunch': row.get('lunch_foods', 'Chicken Adobo | Rice | Vegetables'),
            'dinner': row.get('dinner_foods', 'Fish | Rice | Salad'), 
            'snacks': row.get('snack_foods', 'Fruits | Nuts')
        }
    else:
        return {
            'breakfast': 'Scrambled Eggs | Rice | Coffee',
            'lunch': 'Chicken Adobo | Rice | Vegetables',
            'dinner': 'Fish | Rice | Salad',
            'snacks': 'Fruits | Nuts'
        }

def calculate_macros(calories, protein_pct, carbs_pct, fats_pct):
    """Calculate macro grams from percentages"""
    protein_g = round((calories * protein_pct / 100) / 4, 1)
    carbs_g = round((calories * carbs_pct / 100) / 4, 1)
    fats_g = round((calories * fats_pct / 100) / 9, 1)
    return protein_g, carbs_g, fats_g

def get_diet_principles(somatotype, goal):
    """Get diet principles based on somatotype and goal"""
    principles = {
        'endomorph': {
            'weight_loss': "Prioritize lean protein and healthy fats | Strictly limit refined carbohydrates and sugars | Focus on high-fiber vegetables to stay full | Drink plenty of water to support metabolism",
            'muscle_gain': "Consume lean protein with every meal | Choose complex carbohydrates over simple sugars | Include healthy fats to support hormone production | Monitor portion sizes to avoid excessive fat gain",
            'maintenance': "Balance protein, carbs, and fats at each meal | Focus on whole, unprocessed foods | Practice portion control | Stay hydrated throughout the day"
        },
        'ectomorph': {
            'weight_loss': "Maintain adequate protein to preserve muscle mass | Include complex carbohydrates for energy | Don't restrict calories too severely | Focus on nutrient-dense foods",
            'muscle_gain': "Eat in a caloric surplus with quality foods | Consume protein every 3-4 hours | Include plenty of complex carbohydrates | Add healthy fats to increase caloric density",
            'maintenance': "Eat consistently throughout the day | Balance all macronutrients | Focus on whole foods | Don't skip meals"
        },
        'mesomorph': {
            'weight_loss': "Create a moderate caloric deficit | Maintain high protein intake | Reduce refined carbohydrates | Include regular cardiovascular exercise",
            'muscle_gain': "Eat in a slight caloric surplus | Consume adequate protein for muscle building | Time carbohydrates around workouts | Include healthy fats for hormone production",
            'maintenance': "Maintain balanced macronutrient ratios | Eat regularly throughout the day | Focus on whole, unprocessed foods | Adjust portions based on activity level"
        }
    }
    return principles.get(somatotype, {}).get(goal, "Follow a balanced diet with adequate protein, complex carbohydrates, and healthy fats")

def get_fitness_strategy(somatotype, goal):
    """Get fitness strategy based on somatotype and goal"""
    strategies = {
        'endomorph': {
            'weight_loss': "Combine consistent cardiovascular exercise to manage fat with strength training to build metabolic-boosting muscle.",
            'muscle_gain': "Focus primarily on progressive strength training with moderate cardiovascular exercise to support recovery.",
            'maintenance': "Balance strength training with moderate cardiovascular exercise to maintain body composition."
        },
        'ectomorph': {
            'weight_loss': "Prioritize strength training to preserve muscle mass with minimal cardiovascular exercise.",
            'muscle_gain': "Focus heavily on progressive strength training with minimal cardiovascular exercise to maximize muscle growth.",
            'maintenance': "Emphasize strength training with light cardiovascular exercise for overall health."
        },
        'mesomorph': {
            'weight_loss': "Combine intense strength training with regular cardiovascular exercise for optimal fat loss.",
            'muscle_gain': "Focus on progressive strength training with moderate cardiovascular exercise for balanced development.",
            'maintenance': "Maintain balanced strength training and cardiovascular exercise for overall fitness."
        }
    }
    return strategies.get(somatotype, {}).get(goal, "Follow a balanced exercise program combining strength training and cardiovascular exercise.")

def get_somatotype_description(somatotype):
    """Get description for each somatotype"""
    descriptions = {
        'endomorph': "Naturally soft and round, gains weight easily, slower metabolism",
        'ectomorph': "Naturally lean and thin, fast metabolism, difficulty gaining weight",
        'mesomorph': "Naturally muscular and athletic, balanced metabolism, gains muscle easily"
    }
    return descriptions.get(somatotype, "Balanced body type")

def get_calorie_target(gender, goal, activity_level, somatotype):
    """Calculate calorie targets based on parameters"""
    base_calories = {
        'male': {'sedentary': 1800, 'lightly_active': 2000, 'moderately_active': 2200, 
                'very_active': 2400, 'extremely_active': 2600},
        'female': {'sedentary': 1400, 'lightly_active': 1600, 'moderately_active': 1800,
                  'very_active': 2000, 'extremely_active': 2200}
    }
    
    base = base_calories[gender][activity_level]
    
    # Adjust for somatotype
    if somatotype == 'ectomorph':
        base += 200
    elif somatotype == 'endomorph':
        base -= 200
    
    # Adjust for goal
    if goal == 'weight_loss':
        return int(base * 0.8)
    elif goal == 'muscle_gain':
        return int(base * 1.15)
    else:  # maintenance
        return base

def get_macro_ratios(somatotype, goal):
    """Get macro ratios based on somatotype and goal"""
    ratios = {
        'endomorph': {
            'weight_loss': (35, 25, 40),    # Higher protein, lower carbs, moderate fat
            'muscle_gain': (30, 35, 35),    # Balanced with adequate carbs
            'maintenance': (25, 40, 35)     # Balanced macros
        },
        'ectomorph': {
            'weight_loss': (30, 40, 30),    # Moderate protein, higher carbs
            'muscle_gain': (25, 45, 30),    # High carbs for energy
            'maintenance': (25, 45, 30)     # High carbs maintained
        },
        'mesomorph': {
            'weight_loss': (30, 35, 35),    # Balanced with slight protein emphasis
            'muscle_gain': (25, 40, 35),    # Balanced for muscle growth
            'maintenance': (25, 40, 35)     # Balanced maintenance
        }
    }
    return ratios.get(somatotype, {}).get(goal, (25, 40, 35))

def get_training_splits(somatotype, goal, complexity):
    """Get training split recommendations"""
    if complexity == 'beginner':
        return 3, 2  # 3 strength, 2 cardio
    elif complexity == 'intermediate':
        if goal == 'weight_loss':
            return 4, 3
        else:
            return 4, 2
    else:  # advanced
        if goal == 'weight_loss':
            return 5, 4
        else:
            return 5, 2

# Generate the diet templates
print("Generating comprehensive Filipino meal templates with exercise IDs...")

templates = []
somatotypes = ['endomorph', 'ectomorph', 'mesomorph']
genders = ['male', 'female']
goals = ['weight_loss', 'muscle_gain', 'maintenance']
activity_levels = ['sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extremely_active']
complexities = ['beginner', 'intermediate', 'advanced']
exercise_types = ['gym', 'bodyweight']

for somatotype in somatotypes:
    for gender in genders:
        for goal in goals:
            for activity_level in activity_levels:
                for complexity in complexities:
                    for exercise_type in exercise_types:
                        # Calculate nutritional values
                        total_calories = get_calorie_target(gender, goal, activity_level, somatotype)
                        protein_pct, carbs_pct, fats_pct = get_macro_ratios(somatotype, goal)
                        protein_g, carbs_g, fats_g = calculate_macros(total_calories, protein_pct, carbs_pct, fats_pct)
                        
                        # Get meals from existing template or defaults
                        meal_data = get_meals_from_existing_row(len(templates) % 10 if existing_template is not None else 0)
                        breakfast_foods = meal_data['breakfast']
                        lunch_foods = meal_data['lunch']
                        dinner_foods = meal_data['dinner']
                        snack_foods = meal_data['snacks']
                        
                        # Get training splits
                        strength_split, cardio_split = get_training_splits(somatotype, goal, complexity)
                        
                        # Get exercise IDs based on type
                        if exercise_type == 'gym':
                            push_exercises, pull_exercises, legs_exercises = get_ppl_exercise_ids(complexity)
                            push_ids = ','.join(push_exercises) if push_exercises else ''
                            pull_ids = ','.join(pull_exercises) if pull_exercises else ''
                            legs_ids = ','.join(legs_exercises) if legs_exercises else ''
                            bodyweight_ids = ''
                        else:  # bodyweight
                            bodyweight_exercise_ids = get_bodyweight_exercise_ids(somatotype, goal, 8)
                            push_ids = ''
                            pull_ids = ''
                            legs_ids = ''
                            bodyweight_ids = ','.join(bodyweight_exercise_ids)
                        
                        template = {
                            'somatotype': somatotype,
                            'gender': gender,
                            'goal': goal,
                            'activity_level': activity_level,
                            'exercise_complexity': complexity,
                            'exercise_type': exercise_type,
                            'total_calories': total_calories,
                            'protein_g': protein_g,
                            'carbs_g': carbs_g,
                            'fats_g': fats_g,
                            'protein_pct': protein_pct,
                            'carbs_pct': carbs_pct,
                            'fats_pct': fats_pct,
                            'breakfast_foods': breakfast_foods,
                            'lunch_foods': lunch_foods,
                            'dinner_foods': dinner_foods,
                            'snack_foods': snack_foods,
                            'diet_principles': get_diet_principles(somatotype, goal),
                            'fitness_strategy': get_fitness_strategy(somatotype, goal),
                            'fitness_split_strength': strength_split,
                            'fitness_split_cardio': cardio_split,
                            'push_exercises': push_ids,
                            'pull_exercises': pull_ids,
                            'legs_exercises': legs_ids,
                            'bodyweight_exercises': bodyweight_ids,
                            'description': get_somatotype_description(somatotype)
                        }
                        
                        templates.append(template)

# Save to CSV
df = pd.DataFrame(templates)
output_file = 'enhanced_diet_templates_with_exercise_ids.csv'
df.to_csv(output_file, index=False)

print(f"Generated {len(templates)} comprehensive templates saved to {output_file}")
print(f"Loaded {len(gym_exercises)} gym exercises")
print(f"Loaded {len(bodyweight_exercises)} bodyweight exercises")

# Display sample rows
print("\nSample templates generated:")
print(df[['somatotype', 'exercise_type', 'exercise_complexity', 'push_exercises', 'pull_exercises', 'legs_exercises', 'bodyweight_exercises']].head(4))