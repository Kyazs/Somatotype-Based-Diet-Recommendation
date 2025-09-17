"""
Extract outdoor exercises from exercises.json based on equipment types:
- body weight
- band (resistance band)
- dumbbell 
- kettlebell
"""

import json

def extract_outdoor_exercises():
    """Extract exercises suitable for outdoor workouts."""
    
    # Load the main exercises database
    with open('data/datasets/fitness/data/exercises.json', 'r') as f:
        all_exercises = json.load(f)
    
    # Define outdoor-suitable equipment
    outdoor_equipment = ['body weight', 'band', 'dumbbell', 'kettlebell']
    
    # Extract outdoor exercises
    outdoor_exercises = []
    
    for exercise in all_exercises:
        # Check if the exercise uses outdoor-suitable equipment
        if any(equipment in outdoor_equipment for equipment in exercise.get('equipments', [])):
            outdoor_exercises.append(exercise)
    
    print(f"Found {len(outdoor_exercises)} outdoor exercises from {len(all_exercises)} total exercises")
    
    # Group by equipment type for analysis
    by_equipment = {}
    for exercise in outdoor_exercises:
        for equipment in exercise.get('equipments', []):
            if equipment in outdoor_equipment:
                if equipment not in by_equipment:
                    by_equipment[equipment] = []
                by_equipment[equipment].append(exercise)
    
    # Print summary
    print("\nOutdoor exercises by equipment type:")
    for equipment, exercises in by_equipment.items():
        print(f"  {equipment}: {len(exercises)} exercises")
    
    # Select a good variety for outdoor exercises (limit to reasonable number)
    selected_exercises = []
    
    # Get diverse exercises from each category
    selections_per_category = {
        'body weight': 15,  # Most versatile for outdoor
        'band': 8,          # Portable and effective
        'dumbbell': 10,     # Can be done outdoors with portable weights
        'kettlebell': 7     # Great for outdoor functional training
    }
    
    for equipment, max_count in selections_per_category.items():
        if equipment in by_equipment:
            # Get diverse exercises from this category
            category_exercises = by_equipment[equipment]
            
            # Try to get variety of body parts
            body_parts_covered = set()
            selected_from_category = []
            
            for exercise in category_exercises:
                if len(selected_from_category) >= max_count:
                    break
                    
                # Prefer exercises targeting different body parts
                exercise_body_parts = set(exercise.get('bodyParts', []))
                if not body_parts_covered.intersection(exercise_body_parts) or len(selected_from_category) < max_count // 2:
                    selected_from_category.append(exercise)
                    body_parts_covered.update(exercise_body_parts)
            
            # If we need more, add remaining exercises
            if len(selected_from_category) < max_count:
                remaining = [ex for ex in category_exercises if ex not in selected_from_category]
                needed = max_count - len(selected_from_category)
                selected_from_category.extend(remaining[:needed])
            
            selected_exercises.extend(selected_from_category)
            print(f"Selected {len(selected_from_category)} {equipment} exercises")
    
    # Remove duplicates (exercise might appear in multiple equipment categories)
    unique_exercises = []
    seen_ids = set()
    
    for exercise in selected_exercises:
        if exercise['exerciseId'] not in seen_ids:
            unique_exercises.append(exercise)
            seen_ids.add(exercise['exerciseId'])
    
    print(f"\nSelected {len(unique_exercises)} unique outdoor exercises")
    
    # Save the outdoor exercises
    with open('data/datasets/fitness/data/outdoor_exercises.json', 'w') as f:
        json.dump(unique_exercises, f, indent=2)
    
    print("✓ Saved outdoor exercises to outdoor_exercises.json")
    
    # Show sample of what was selected
    print("\nSample of selected exercises:")
    for i, exercise in enumerate(unique_exercises[:10]):
        equipment = ', '.join(exercise.get('equipments', []))
        target = ', '.join(exercise.get('targetMuscles', []))
        print(f"  {i+1}. {exercise['name']} ({equipment}) - targets: {target}")
    
    return unique_exercises

if __name__ == "__main__":
    extract_outdoor_exercises()