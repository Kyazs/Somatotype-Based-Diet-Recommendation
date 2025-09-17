"""
Extract ALL outdoor exercises from exercises.json
Get all body weight, band, and weighted exercises for outdoor workouts
"""

import json

def extract_all_outdoor_exercises():
    """Extract ALL exercises suitable for outdoor workouts."""
    
    # Load the main exercises database
    with open('data/datasets/fitness/data/exercises.json', 'r') as f:
        all_exercises = json.load(f)
    
    print(f"Loaded {len(all_exercises)} total exercises from exercises.json")
    
    # Define outdoor-suitable equipment
    outdoor_equipment = ['body weight', 'band', 'weighted']
    
    # Extract ALL outdoor exercises
    outdoor_exercises = []
    
    for exercise in all_exercises:
        equipments = exercise.get('equipments', [])
        
        # Check if the exercise uses any outdoor-suitable equipment
        if any(equipment in outdoor_equipment for equipment in equipments):
            outdoor_exercises.append(exercise)
    
    print(f"Found {len(outdoor_exercises)} outdoor exercises")
    
    # Group by equipment type for analysis
    by_equipment = {}
    for exercise in outdoor_exercises:
        for equipment in exercise.get('equipments', []):
            if equipment in outdoor_equipment:
                if equipment not in by_equipment:
                    by_equipment[equipment] = []
                by_equipment[equipment].append(exercise)
    
    # Print detailed summary
    print("\nDetailed breakdown by equipment type:")
    total_extracted = 0
    for equipment in ['body weight', 'band', 'weighted']:
        if equipment in by_equipment:
            count = len(by_equipment[equipment])
            print(f"  {equipment}: {count} exercises")
            total_extracted += count
        else:
            print(f"  {equipment}: 0 exercises")
    
    # Remove duplicates (exercise might appear in multiple equipment categories)
    unique_exercises = []
    seen_ids = set()
    
    for exercise in outdoor_exercises:
        if exercise['exerciseId'] not in seen_ids:
            unique_exercises.append(exercise)
            seen_ids.add(exercise['exerciseId'])
    
    print(f"\nTotal unique outdoor exercises: {len(unique_exercises)}")
    
    # Sort exercises by equipment type for better organization
    def get_sort_key(exercise):
        equipments = exercise.get('equipments', [''])
        primary_equipment = equipments[0] if equipments else 'unknown'
        
        # Sort order: body weight, band, weighted, others
        sort_order = {'body weight': '1', 'band': '2', 'weighted': '3'}
        sort_prefix = sort_order.get(primary_equipment, '9')
        
        return f"{sort_prefix}_{exercise['name']}"
    
    unique_exercises.sort(key=get_sort_key)
    
    # Save ALL outdoor exercises
    with open('data/datasets/fitness/data/outdoor_exercises.json', 'w') as f:
        json.dump(unique_exercises, f, indent=4)
    
    print(f"✓ Saved {len(unique_exercises)} outdoor exercises to outdoor_exercises.json")
    
    # Final equipment count verification
    final_equipment_count = {}
    for exercise in unique_exercises:
        for equipment in exercise.get('equipments', []):
            final_equipment_count[equipment] = final_equipment_count.get(equipment, 0) + 1
    
    print("\nFinal equipment distribution in saved file:")
    for equipment, count in sorted(final_equipment_count.items()):
        print(f"  {equipment}: {count} exercises")
    
    # Show sample of body weight exercises
    body_weight_exercises = [ex for ex in unique_exercises if 'body weight' in ex.get('equipments', [])]
    print(f"\nSample of {len(body_weight_exercises)} body weight exercises:")
    for i, exercise in enumerate(body_weight_exercises[:10]):
        target = ', '.join(exercise.get('targetMuscles', []))
        body_parts = ', '.join(exercise.get('bodyParts', []))
        print(f"  {i+1:2d}. {exercise['exerciseId']} | {exercise['name']}")
        print(f"       Target: {target} | Body Parts: {body_parts}")
    
    if len(body_weight_exercises) > 10:
        print(f"       ... and {len(body_weight_exercises) - 10} more body weight exercises")
    
    return unique_exercises

if __name__ == "__main__":
    extract_all_outdoor_exercises()