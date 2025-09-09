#!/usr/bin/env python3
"""
Universal Evidence-Based Fitness Dataset Processor

This script processes fitness data to create a universal system that can handle
ANY user input with different goals and activity levels, not just one specific user.

Goals Supported: Maintain Weight, Lose Weight, Gain Weight, Build Muscle, Improve Fitness
Activity Levels: Sedentary, Lightly Active, Moderately Active, Very Active, Extremely Active

Based on: ACSM Guidelines, NSCA Position Statements, and Exercise Physiology Research

"""

import json
import pandas as pd
import numpy as np
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any

class UniversalFitnessProcessor:
    """
    Processes fitness datasets for universal user recommendations
    """
    
    def __init__(self):
        self.base_path = r"c:\Users\LENOVO\Desktop\Kekious_Maximus\diet-recommendation-somatotype"
        self.data_path = os.path.join(self.base_path, "data", "datasets", "fitness", "data")
        self.processed_path = os.path.dirname(os.path.abspath(__file__))  # Current directory (processed folder)
        
        # Ensure processed directory exists (already exists since we're in it)
        os.makedirs(self.processed_path, exist_ok=True)
        
        # Universal goal-specific exercise priorities (evidence-based)
        self.goal_frameworks = {
            'maintain_weight': {
                'primary_adaptations': ['muscular_strength', 'cardiovascular_endurance', 'functional_movement'],
                'secondary_adaptations': ['flexibility_mobility', 'balance_coordination'],
                'training_split': {'strength': 0.4, 'cardio': 0.3, 'functional': 0.2, 'recovery': 0.1}
            },
            'lose_weight': {
                'primary_adaptations': ['calorie_expenditure', 'cardiovascular_endurance', 'metabolic_conditioning'],
                'secondary_adaptations': ['muscular_strength', 'functional_movement'],
                'training_split': {'cardio': 0.4, 'metabolic': 0.3, 'strength': 0.2, 'recovery': 0.1}
            },
            'gain_weight': {
                'primary_adaptations': ['muscular_hypertrophy', 'muscular_strength', 'progressive_overload'],
                'secondary_adaptations': ['functional_movement', 'power_development'],
                'training_split': {'strength': 0.5, 'hypertrophy': 0.3, 'functional': 0.1, 'recovery': 0.1}
            },
            'build_muscle': {
                'primary_adaptations': ['muscular_hypertrophy', 'progressive_overload', 'muscular_strength'],
                'secondary_adaptations': ['power_development', 'functional_movement'],
                'training_split': {'hypertrophy': 0.5, 'strength': 0.3, 'power': 0.1, 'recovery': 0.1}
            },
            'improve_fitness': {
                'primary_adaptations': ['cardiovascular_endurance', 'muscular_strength', 'functional_movement'],
                'secondary_adaptations': ['flexibility_mobility', 'balance_coordination', 'power_development'],
                'training_split': {'cardio': 0.3, 'strength': 0.3, 'functional': 0.2, 'recovery': 0.2}
            }
        }
        
        # Universal activity level parameters (ACSM-based)
        self.activity_parameters = {
            'sedentary': {
                'weekly_frequency': 3,
                'session_duration': 30,
                'intensity_level': 'low',
                'complexity_preference': 1,
                'equipment_accessibility': 'high',
                'progression_rate': 'conservative'
            },
            'lightly_active': {
                'weekly_frequency': 3,
                'session_duration': 40,
                'intensity_level': 'low_moderate',
                'complexity_preference': 2,
                'equipment_accessibility': 'moderate',
                'progression_rate': 'gradual'
            },
            'moderately_active': {
                'weekly_frequency': 4,
                'session_duration': 45,
                'intensity_level': 'moderate',
                'complexity_preference': 3,
                'equipment_accessibility': 'moderate',
                'progression_rate': 'standard'
            },
            'very_active': {
                'weekly_frequency': 5,
                'session_duration': 60,
                'intensity_level': 'moderate_high',
                'complexity_preference': 4,
                'equipment_accessibility': 'low',
                'progression_rate': 'aggressive'
            },
            'extremely_active': {
                'weekly_frequency': 6,
                'session_duration': 75,
                'intensity_level': 'high',
                'complexity_preference': 5,
                'equipment_accessibility': 'low',
                'progression_rate': 'advanced'
            }
        }
    
    def load_json_data(self, filename: str) -> List[Dict]:
        """Load JSON data from file"""
        file_path = os.path.join(self.data_path, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def calculate_exercise_adaptations(self, exercise: Dict) -> Dict[str, float]:
        """
        Calculate physiological adaptations for each exercise based on exercise science
        """
        name = exercise['name'].lower()
        equipment = exercise['equipments'][0].lower() if exercise['equipments'] else 'body weight'
        target_muscles = exercise['targetMuscles']
        secondary_muscles = exercise.get('secondaryMuscles', [])
        instructions = ' '.join(exercise.get('instructions', [])).lower()
        
        # Initialize adaptation scores (0-10 scale)
        adaptations = {
            'cardiovascular_endurance': 0.0,
            'muscular_strength': 0.0, 
            'muscular_hypertrophy': 0.0,
            'power_development': 0.0,
            'functional_movement': 0.0,
            'calorie_expenditure': 0.0,
            'flexibility_mobility': 0.0,
            'balance_coordination': 0.0,
            'metabolic_conditioning': 0.0,
            'progressive_overload': 0.0
        }
        
        total_muscles = len(target_muscles) + len(secondary_muscles)
        
        # Cardiovascular training identification
        cardio_keywords = ['run', 'bike', 'row', 'cardio', 'treadmill', 'elliptical', 'step']
        if any(keyword in name or keyword in equipment for keyword in cardio_keywords):
            adaptations['cardiovascular_endurance'] = 9.0
            adaptations['calorie_expenditure'] = 8.5
            adaptations['metabolic_conditioning'] = 8.0
            return adaptations
        
        # High-intensity/circuit training
        hiit_keywords = ['jump', 'burpee', 'mountain climber', 'sprint', 'tabata', 'circuit']
        if any(keyword in name for keyword in hiit_keywords):
            adaptations['cardiovascular_endurance'] = 7.5
            adaptations['calorie_expenditure'] = 9.0
            adaptations['metabolic_conditioning'] = 8.5
            adaptations['power_development'] = 6.0
        
        # Strength training identification
        strength_keywords = ['press', 'squat', 'deadlift', 'pull', 'row', 'curl', 'extension']
        strength_equipment = ['barbell', 'dumbbell', 'kettlebell', 'machine', 'cable']
        
        if any(keyword in name for keyword in strength_keywords) or equipment in strength_equipment:
            if total_muscles >= 3:  # Compound movements
                adaptations['muscular_strength'] = 8.5
                adaptations['muscular_hypertrophy'] = 7.5
                adaptations['functional_movement'] = 8.0
                adaptations['progressive_overload'] = 9.0
                adaptations['calorie_expenditure'] = 6.0
            else:  # Isolation movements
                adaptations['muscular_strength'] = 6.5
                adaptations['muscular_hypertrophy'] = 8.5
                adaptations['progressive_overload'] = 7.5
                adaptations['calorie_expenditure'] = 4.0
        
        # Power/explosive movements
        power_keywords = ['jump', 'throw', 'slam', 'clean', 'snatch', 'explosive', 'plyometric']
        if any(keyword in name for keyword in power_keywords):
            adaptations['power_development'] = 9.0
            adaptations['muscular_strength'] = 7.0
            adaptations['calorie_expenditure'] = 7.5
            adaptations['functional_movement'] = 7.5
        
        # Bodyweight exercises
        if equipment == 'body weight':
            adaptations['functional_movement'] += 2.5
            adaptations['balance_coordination'] += 2.0
            
            if total_muscles >= 3:
                adaptations['muscular_strength'] += 3.5
                adaptations['muscular_hypertrophy'] += 3.0
            else:
                adaptations['cardiovascular_endurance'] += 2.0
                adaptations['calorie_expenditure'] += 2.5
        
        # Flexibility and mobility
        flexibility_keywords = ['stretch', 'yoga', 'mobility', 'foam', 'roll']
        if any(keyword in name or keyword in equipment for keyword in flexibility_keywords):
            adaptations['flexibility_mobility'] = 9.0
            adaptations['balance_coordination'] = 6.5
            adaptations['functional_movement'] = 5.0
        
        # Balance and coordination
        balance_keywords = ['balance', 'stability', 'single leg', 'unilateral', 'bosu']
        if any(keyword in name or keyword in equipment for keyword in balance_keywords):
            adaptations['balance_coordination'] = 8.5
            adaptations['functional_movement'] += 2.0
        
        # Normalize all scores to 0-10 range
        for key in adaptations:
            adaptations[key] = min(10.0, max(0.0, adaptations[key]))
        
        return adaptations
    
    def calculate_goal_compatibility_scores(self, adaptations: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate compatibility scores for all possible goals
        """
        goal_scores = {}
        
        for goal_key, framework in self.goal_frameworks.items():
            score = 0.0
            
            # Primary adaptations (70% weight)
            primary_weight = 0.7 / len(framework['primary_adaptations'])
            for adaptation in framework['primary_adaptations']:
                if adaptation in adaptations:
                    score += adaptations[adaptation] * primary_weight
            
            # Secondary adaptations (30% weight)
            secondary_weight = 0.3 / len(framework['secondary_adaptations'])
            for adaptation in framework['secondary_adaptations']:
                if adaptation in adaptations:
                    score += adaptations[adaptation] * secondary_weight
            
            goal_scores[f"{goal_key}_compatibility"] = round(score, 1)
        
        return goal_scores
    
    def calculate_activity_level_suitability(self, exercise: Dict, adaptations: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate suitability scores for all activity levels
        """
        complexity = self.calculate_complexity_score(exercise)
        equipment = exercise['equipments'][0].lower() if exercise['equipments'] else 'body weight'
        
        suitability_scores = {}
        
        for activity_key, params in self.activity_parameters.items():
            base_score = 5.0
            
            # Complexity matching
            preferred_complexity = params['complexity_preference']
            complexity_diff = abs(complexity - preferred_complexity)
            
            if complexity_diff == 0:
                base_score += 2.0
            elif complexity_diff == 1:
                base_score += 1.0
            elif complexity_diff >= 3:
                base_score -= 2.0
            
            # Equipment accessibility
            accessible_equipment = ['body weight', 'dumbbell', 'band', 'kettlebell']
            gym_equipment = ['barbell', 'machine', 'cable', 'smith machine']
            
            if params['equipment_accessibility'] == 'high' and equipment in accessible_equipment:
                base_score += 1.5
            elif params['equipment_accessibility'] == 'low' and equipment in gym_equipment:
                base_score += 1.0
            elif params['equipment_accessibility'] == 'high' and equipment in gym_equipment:
                base_score -= 1.0
            
            # Intensity matching based on adaptations
            high_intensity_adaptations = ['power_development', 'calorie_expenditure', 'metabolic_conditioning']
            intensity_score = sum(adaptations[adapt] for adapt in high_intensity_adaptations) / 3
            
            if params['intensity_level'] in ['high', 'moderate_high'] and intensity_score >= 7:
                base_score += 1.0
            elif params['intensity_level'] in ['low', 'low_moderate'] and intensity_score <= 4:
                base_score += 1.0
            
            suitability_scores[f"{activity_key}_suitability"] = round(min(10.0, max(0.0, base_score)), 1)
        
        return suitability_scores
    
    def calculate_complexity_score(self, exercise: Dict) -> int:
        """Calculate exercise complexity (1-5 scale)"""
        instructions = exercise.get('instructions', [])
        num_steps = len(instructions)
        equipment = exercise['equipments'][0].lower() if exercise['equipments'] else 'body weight'
        name = exercise['name'].lower()
        
        # Base complexity from instruction count
        if num_steps <= 3:
            complexity = 1
        elif num_steps <= 5:
            complexity = 2
        elif num_steps <= 7:
            complexity = 3
        elif num_steps <= 9:
            complexity = 4
        else:
            complexity = 5
        
        # Adjust for movement complexity
        complex_movements = ['snatch', 'clean', 'jerk', 'turkish', 'complex', 'coordination']
        if any(movement in name for movement in complex_movements):
            complexity = min(5, complexity + 1)
        
        simple_movements = ['curl', 'raise', 'shrug', 'extension', 'crunch']
        if any(movement in name for movement in simple_movements):
            complexity = max(1, complexity - 1)
        
        return complexity
    
    def determine_primary_category(self, adaptations: Dict[str, float]) -> str:
        """Determine primary training category"""
        # Category mapping based on dominant adaptation
        category_mapping = {
            'cardiovascular_endurance': 'Cardiovascular Training',
            'muscular_strength': 'Strength Training', 
            'muscular_hypertrophy': 'Hypertrophy Training',
            'power_development': 'Power Training',
            'functional_movement': 'Functional Training',
            'calorie_expenditure': 'Metabolic Training',
            'flexibility_mobility': 'Flexibility & Mobility',
            'balance_coordination': 'Balance & Coordination',
            'metabolic_conditioning': 'Metabolic Training',
            'progressive_overload': 'Strength Training'
        }
        
        max_adaptation = max(adaptations, key=adaptations.get)
        return category_mapping.get(max_adaptation, 'General Fitness')
    
    def process_universal_exercise_database(self) -> pd.DataFrame:
        """Process exercises for universal compatibility"""
        print("Processing exercises for universal user compatibility...")
        exercises_data = self.load_json_data('exercises.json')
        
        processed_exercises = []
        
        for exercise in exercises_data:
            # Basic exercise information
            processed_exercise = {
                'exercise_id': exercise['exerciseId'],
                'name': exercise['name'].title(),
                'complexity_level': self.calculate_complexity_score(exercise),
                'primary_equipment': exercise['equipments'][0] if exercise['equipments'] else 'body weight',
                'target_muscles': ', '.join(exercise['targetMuscles']),
                'secondary_muscles': ', '.join(exercise.get('secondaryMuscles', [])),
                'body_parts': ', '.join(exercise['bodyParts']),
                'total_muscle_groups': len(exercise['targetMuscles']) + len(exercise.get('secondaryMuscles', [])),
                'gif_url': exercise['gifUrl'],
                'instructions': ' | '.join(exercise['instructions'])
            }
            
            # Calculate physiological adaptations
            adaptations = self.calculate_exercise_adaptations(exercise)
            
            # Add adaptation scores to exercise data
            for adaptation, score in adaptations.items():
                processed_exercise[f"{adaptation}_score"] = score
            
            # Determine primary training category
            processed_exercise['primary_training_category'] = self.determine_primary_category(adaptations)
            
            # Calculate goal compatibility for all goals
            goal_scores = self.calculate_goal_compatibility_scores(adaptations)
            processed_exercise.update(goal_scores)
            
            # Calculate activity level suitability for all levels
            activity_scores = self.calculate_activity_level_suitability(exercise, adaptations)
            processed_exercise.update(activity_scores)
            
            # Calculate overall quality score
            adaptation_avg = np.mean(list(adaptations.values()))
            goal_avg = np.mean([score for key, score in goal_scores.items()])
            processed_exercise['overall_quality_score'] = round((adaptation_avg + goal_avg) / 2, 1)
            
            processed_exercises.append(processed_exercise)
        
        return pd.DataFrame(processed_exercises)
    
    def create_universal_categories(self, exercises_df: pd.DataFrame) -> None:
        """Create category files for different training types"""
        print("Creating universal training category files...")
        
        categories = exercises_df['primary_training_category'].unique()
        
        for category in categories:
            category_df = exercises_df[exercises_df['primary_training_category'] == category].copy()
            category_df = category_df.sort_values('overall_quality_score', ascending=False)
            
            filename = f"universal_{category.lower().replace(' ', '_').replace('&', 'and')}.csv"
            filepath = os.path.join(self.processed_path, filename)
            
            category_df.to_csv(filepath, index=False)
            print(f"  ✅ Created {filename} with {len(category_df)} exercises")
    
    def create_goal_specific_files(self, exercises_df: pd.DataFrame) -> None:
        """Create goal-specific exercise recommendations"""
        print("Creating goal-specific exercise files...")
        
        goals = ['maintain_weight', 'lose_weight', 'gain_weight', 'build_muscle', 'improve_fitness']
        
        for goal in goals:
            goal_column = f"{goal}_compatibility"
            
            # Get top exercises for this goal
            goal_exercises = exercises_df.nlargest(300, goal_column).copy()
            
            filename = f"goal_{goal}_top_exercises.csv"
            filepath = os.path.join(self.processed_path, filename)
            
            goal_exercises.to_csv(filepath, index=False)
            print(f"  ✅ Created {filename} with {len(goal_exercises)} exercises")
    
    def create_activity_level_files(self, exercises_df: pd.DataFrame) -> None:
        """Create activity level specific exercise recommendations"""
        print("Creating activity level specific files...")
        
        activity_levels = ['sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extremely_active']
        
        for activity in activity_levels:
            activity_column = f"{activity}_suitability"
            
            # Get top exercises for this activity level
            activity_exercises = exercises_df.nlargest(250, activity_column).copy()
            
            filename = f"activity_{activity}_suitable_exercises.csv"
            filepath = os.path.join(self.processed_path, filename)
            
            activity_exercises.to_csv(filepath, index=False)
            print(f"  ✅ Created {filename} with {len(activity_exercises)} exercises")
    
    def generate_universal_summary(self, exercises_df: pd.DataFrame) -> None:
        """Generate comprehensive summary statistics"""
        print("\nGenerating universal system summary...")
        
        summary_stats = {
            'database_info': {
                'total_exercises': len(exercises_df),
                'processing_date': '2025-09-02',
                'scientific_basis': 'ACSM Guidelines, NSCA Position Statements'
            },
            'training_categories': exercises_df['primary_training_category'].value_counts().to_dict(),
            'complexity_distribution': exercises_df['complexity_level'].value_counts().to_dict(),
            'equipment_distribution': exercises_df['primary_equipment'].value_counts().head(15).to_dict(),
            'adaptation_averages': {
                'cardiovascular_endurance': round(exercises_df['cardiovascular_endurance_score'].mean(), 2),
                'muscular_strength': round(exercises_df['muscular_strength_score'].mean(), 2),
                'muscular_hypertrophy': round(exercises_df['muscular_hypertrophy_score'].mean(), 2),
                'functional_movement': round(exercises_df['functional_movement_score'].mean(), 2),
                'calorie_expenditure': round(exercises_df['calorie_expenditure_score'].mean(), 2)
            },
            'goal_compatibility_averages': {
                'maintain_weight': round(exercises_df['maintain_weight_compatibility'].mean(), 2),
                'lose_weight': round(exercises_df['lose_weight_compatibility'].mean(), 2), 
                'gain_weight': round(exercises_df['gain_weight_compatibility'].mean(), 2),
                'build_muscle': round(exercises_df['build_muscle_compatibility'].mean(), 2),
                'improve_fitness': round(exercises_df['improve_fitness_compatibility'].mean(), 2)
            },
            'quality_metrics': {
                'high_quality_exercises': len(exercises_df[exercises_df['overall_quality_score'] >= 7]),
                'medium_quality_exercises': len(exercises_df[(exercises_df['overall_quality_score'] >= 5) & (exercises_df['overall_quality_score'] < 7)]),
                'basic_exercises': len(exercises_df[exercises_df['overall_quality_score'] < 5])
            }
        }
        
        # Save summary
        summary_path = os.path.join(self.processed_path, 'universal_fitness_system_summary.json')
        with open(summary_path, 'w') as f:
            json.dump(summary_stats, f, indent=2)
        
        print(f"✅ Universal system summary saved")
        print(f"\n📊 Universal System Statistics:")
        print(f"  • Total Exercises: {summary_stats['database_info']['total_exercises']:,}")
        print(f"  • Training Categories: {len(summary_stats['training_categories'])}")
        print(f"  • High Quality Exercises: {summary_stats['quality_metrics']['high_quality_exercises']:,}")
        print(f"  • Goals Supported: {len(summary_stats['goal_compatibility_averages'])}")
        print(f"  • Activity Levels Supported: 5 (Sedentary to Extremely Active)")
    
    def run_universal_processing(self) -> None:
        """Run the complete universal processing pipeline"""
        print("🌍 Starting Universal Evidence-Based Fitness Processing")
        print("=" * 65)
        print("🎯 Building system to handle ANY user input:")
        print("   • Goals: Maintain/Lose/Gain Weight, Build Muscle, Improve Fitness")
        print("   • Activity: Sedentary → Extremely Active")
        print("   • Ages: All age groups with appropriate adjustments")
        print("=" * 65)
        
        try:
            # Process exercises for universal compatibility
            exercises_df = self.process_universal_exercise_database()
            
            # Save main database
            main_path = os.path.join(self.processed_path, 'universal_exercises_database.csv')
            exercises_df.to_csv(main_path, index=False)
            print(f"✅ Universal exercises database saved: {len(exercises_df):,} exercises")
            
            # Create category-specific files
            self.create_universal_categories(exercises_df)
            
            # Create goal-specific files
            self.create_goal_specific_files(exercises_df)
            
            # Create activity level files
            self.create_activity_level_files(exercises_df)
            
            # Generate comprehensive summary
            self.generate_universal_summary(exercises_df)
            
            print(f"\n🎯 Universal Processing Complete!")
            print(f"📁 System ready to handle any user input!")
            print(f"📂 Files saved to: {self.processed_path}")
            
        except Exception as e:
            print(f"❌ Error during processing: {str(e)}")
            raise

def main():
    """Main execution function"""
    processor = UniversalFitnessProcessor()
    processor.run_universal_processing()

if __name__ == "__main__":
    main()
