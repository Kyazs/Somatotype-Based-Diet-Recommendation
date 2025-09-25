"""
Exercise Data Loader Module
Handles loading and looking up exercise information from the exercises database
"""

import os
import json
import sys
from typing import Dict, Optional

# Add project root to path
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(PROJECT_DIR)

class ExerciseDataLoader:
    """Handles loading and looking up exercise information"""
    
    def __init__(self):
        """Initialize exercise data loader"""
        self.exercise_database = None
        self.exercise_lookup = {}
        self._load_exercise_database()
    
    def _load_exercise_database(self):
        """Load the exercise database from JSON"""
        try:
            exercise_db_path = os.path.join(
                PROJECT_DIR, 
                "data", "datasets", "fitness", "data", 
                "exercises.json"
            )
            
            if os.path.exists(exercise_db_path):
                with open(exercise_db_path, 'r', encoding='utf-8') as f:
                    self.exercise_database = json.load(f)
                
                # Create lookup dictionary for faster access
                for exercise in self.exercise_database:
                    exercise_id = exercise.get('exerciseId', '')
                    if exercise_id:
                        self.exercise_lookup[exercise_id] = {
                            'exerciseId': exercise_id,
                            'name': exercise.get('name', 'Unknown Exercise'),
                            'gifUrl': exercise.get('gifUrl', ''),
                            'targetMuscles': exercise.get('targetMuscles', []),
                            'bodyParts': exercise.get('bodyParts', []),
                            'equipments': exercise.get('equipments', []),
                            'secondaryMuscles': exercise.get('secondaryMuscles', []),
                            'instructions': exercise.get('instructions', [])
                        }
                
                print(f"✅ Exercise database loaded: {len(self.exercise_database)} exercises")
            else:
                print(f"❌ Exercise database not found at: {exercise_db_path}")
                
        except Exception as e:
            print(f"❌ Error loading exercise database: {e}")
    
    def get_exercise_info(self, exercise_id: str) -> Optional[Dict]:
        """Get exercise information by ID"""
        if not exercise_id or not isinstance(exercise_id, str):
            return None
            
        return self.exercise_lookup.get(exercise_id.strip())
    
    def get_exercise_name(self, exercise_id: str) -> str:
        """Get exercise name by ID, with fallback"""
        exercise_info = self.get_exercise_info(exercise_id)
        if exercise_info:
            return exercise_info['name']
        return f"Exercise {exercise_id}" if exercise_id else "Unknown Exercise"
    
    def search_exercises(self, query: str, limit: int = 10) -> list:
        """Search for exercises by name or target muscle"""
        if not query or not isinstance(query, str):
            return []
            
        query_lower = query.lower().strip()
        matches = []
        
        for exercise_id, exercise_data in self.exercise_lookup.items():
            name = exercise_data['name'].lower()
            target_muscles = [m.lower() for m in exercise_data['targetMuscles']]
            body_parts = [b.lower() for b in exercise_data['bodyParts']]
            
            if (query_lower in name or 
                any(query_lower in muscle for muscle in target_muscles) or
                any(query_lower in part for part in body_parts)):
                matches.append(exercise_data)
                if len(matches) >= limit:
                    break
        
        return matches
    
    def get_exercises_by_equipment(self, equipment: str, limit: int = 20) -> list:
        """Get exercises by equipment type"""
        if not equipment:
            return []
            
        equipment_lower = equipment.lower()
        matches = []
        
        for exercise_id, exercise_data in self.exercise_lookup.items():
            equipments = [e.lower() for e in exercise_data['equipments']]
            if equipment_lower in equipments:
                matches.append(exercise_data)
                if len(matches) >= limit:
                    break
        
        return matches
    
    def get_exercises_by_muscle(self, muscle: str, limit: int = 20) -> list:
        """Get exercises by target muscle"""
        if not muscle:
            return []
            
        muscle_lower = muscle.lower()
        matches = []
        
        for exercise_id, exercise_data in self.exercise_lookup.items():
            target_muscles = [m.lower() for m in exercise_data['targetMuscles']]
            secondary_muscles = [m.lower() for m in exercise_data['secondaryMuscles']]
            
            if (muscle_lower in target_muscles or 
                muscle_lower in secondary_muscles):
                matches.append(exercise_data)
                if len(matches) >= limit:
                    break
        
        return matches

# Global instance
_exercise_loader = None

def get_exercise_loader():
    """Get global exercise loader instance"""
    global _exercise_loader
    if _exercise_loader is None:
        _exercise_loader = ExerciseDataLoader()
    return _exercise_loader