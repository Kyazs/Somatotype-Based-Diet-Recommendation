#!/usr/bin/env python3
"""
Evidence-Based Fitness Dataset Processor

This script processes fitness data based on scientifically-backed principles:
- Fitness goals (strength, endurance, weight maintenance, muscle building, fat loss)
- Activity levels and training experience
- Movement quality and exercise progression
- Individual preferences and accessibility

Based on: ACSM Guidelines, NSCA Position Statements, and Exercise Physiology Research

"""

import json
import pandas as pd
import numpy as np
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any

class EvidenceBasedFitnessProcessor:
    """
    Processes fitness datasets based on evidence-based exercise prescription
    """
    
    def __init__(self):
        self.base_path = r"c:\Users\LENOVO\Desktop\Kekious_Maximus\diet-recommendation-somatotype\data\datasets\fitness"
        self.data_path = os.path.join(self.base_path, "data")
        self.processed_path = os.path.join(self.base_path, "processed")
        
        # Ensure processed directory exists
        os.makedirs(self.processed_path, exist_ok=True)
        
        # Evidence-based exercise classification
        self.goal_priorities = {
            'maintain_weight': {
                'cardiovascular_health': 0.25,
                'strength_maintenance': 0.30,
                'functional_movement': 0.25,
                'flexibility_mobility': 0.20
            },
            'lose_weight': {
                'calorie_expenditure': 0.35,
                'cardiovascular_fitness': 0.30,
                'muscle_preservation': 0.25,
                'metabolic_conditioning': 0.10
            },
            'gain_muscle': {
                'progressive_overload': 0.40,
                'muscle_hypertrophy': 0.30,
                'strength_building': 0.20,
                'recovery_optimization': 0.10
            },
            'improve_fitness': {
                'cardiovascular_endurance': 0.30,
                'muscular_strength': 0.25,
                'functional_capacity': 0.25,
                'movement_quality': 0.20
            }
        }
        
        # Activity level modifiers based on ACSM guidelines
        self.activity_modifiers = {
            'sedentary': {
                'volume_multiplier': 0.6,
                'intensity_cap': 'low_moderate',
                'progression_rate': 'conservative',
                'emphasis': 'movement_introduction'
            },
            'lightly_active': {
                'volume_multiplier': 0.8,
                'intensity_cap': 'moderate',
                'progression_rate': 'gradual',
                'emphasis': 'consistency_building'
            },
            'moderately_active': {
                'volume_multiplier': 1.0,
                'intensity_cap': 'moderate_high',
                'progression_rate': 'standard',
                'emphasis': 'balanced_development'
            },
            'very_active': {
                'volume_multiplier': 1.3,
                'intensity_cap': 'high',
                'progression_rate': 'aggressive',
                'emphasis': 'performance_optimization'
            },
            'extremely_active': {
                'volume_multiplier': 1.5,
                'intensity_cap': 'very_high',
                'progression_rate': 'advanced',
                'emphasis': 'specialization'
            }
        }
    
    def load_json_data(self, filename: str) -> List[Dict]:
        """Load JSON data from file"""
        file_path = os.path.join(self.data_path, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def classify_exercise_by_adaptation(self, exercise: Dict) -> Dict[str, float]:
        """
        Classify exercises by physiological adaptations based on exercise science
        """
        name = exercise['name'].lower()
        equipment = exercise['equipments'][0].lower() if exercise['equipments'] else ''
        target_muscles = exercise['targetMuscles']
        secondary_muscles = exercise.get('secondaryMuscles', [])
        instructions = ' '.join(exercise.get('instructions', [])).lower()
        
        # Initialize adaptation scores
        adaptations = {
            'cardiovascular_endurance': 0.0,
            'muscular_strength': 0.0,
            'muscular_hypertrophy': 0.0,
            'power_development': 0.0,
            'functional_movement': 0.0,
            'calorie_expenditure': 0.0,
            'flexibility_mobility': 0.0,
            'balance_coordination': 0.0
        }
        
        # Cardiovascular adaptations
        cardio_indicators = ['run', 'bike', 'row', 'jump', 'burpee', 'mountain climber', 'cardio']
        if any(indicator in name or indicator in equipment for indicator in cardio_indicators):
            adaptations['cardiovascular_endurance'] = 8.5
            adaptations['calorie_expenditure'] = 9.0
        
        # High-intensity circuit indicators
        circuit_indicators = ['circuit', 'hiit', 'tabata', 'complex']
        if any(indicator in name or indicator in instructions for indicator in circuit_indicators):
            adaptations['calorie_expenditure'] += 2.0
            adaptations['cardiovascular_endurance'] += 1.5
        
        # Strength adaptations
        strength_indicators = ['press', 'squat', 'deadlift', 'pull', 'row', 'curl']
        heavy_equipment = ['barbell', 'dumbbell', 'kettlebell', 'machine']
        
        if any(indicator in name for indicator in strength_indicators) or equipment in heavy_equipment:
            total_muscles = len(target_muscles) + len(secondary_muscles)
            
            # Compound vs isolation classification
            if total_muscles >= 3:
                adaptations['muscular_strength'] = 8.0
                adaptations['muscular_hypertrophy'] = 7.5
                adaptations['functional_movement'] = 7.0
                adaptations['calorie_expenditure'] = 6.0
            else:
                adaptations['muscular_strength'] = 6.5
                adaptations['muscular_hypertrophy'] = 8.0
                adaptations['functional_movement'] = 4.0
                adaptations['calorie_expenditure'] = 4.5
        
        # Power development
        power_indicators = ['jump', 'throw', 'slam', 'clean', 'snatch', 'explosive', 'plyometric']
        if any(indicator in name for indicator in power_indicators):
            adaptations['power_development'] = 8.5
            adaptations['muscular_strength'] = 6.5
            adaptations['calorie_expenditure'] = 7.0
        
        # Bodyweight functional movement
        if equipment == 'body weight':
            adaptations['functional_movement'] += 3.0
            adaptations['balance_coordination'] += 2.0
            
            # Bodyweight cardio vs strength
            if any(indicator in name for indicator in ['push', 'pull', 'squat', 'lunge']):
                adaptations['muscular_strength'] += 4.0
                adaptations['muscular_hypertrophy'] += 3.5
            else:
                adaptations['cardiovascular_endurance'] += 3.0
                adaptations['calorie_expenditure'] += 3.5
        
        # Flexibility and mobility
        flexibility_indicators = ['stretch', 'yoga', 'mobility', 'roll', 'foam']
        if any(indicator in name or indicator in equipment for indicator in flexibility_indicators):
            adaptations['flexibility_mobility'] = 8.0
            adaptations['balance_coordination'] = 6.0
        
        # Balance and coordination
        balance_indicators = ['balance', 'stability', 'single leg', 'unilateral', 'bosu']
        if any(indicator in name or indicator in equipment for indicator in balance_indicators):
            adaptations['balance_coordination'] = 8.0
            adaptations['functional_movement'] += 2.0
        
        # Normalize scores to 0-10 scale
        for key in adaptations:
            adaptations[key] = min(10.0, adaptations[key])
        
        return adaptations
    
    def calculate_goal_compatibility(self, adaptations: Dict[str, float], goal: str) -> float:
        """
        Calculate exercise compatibility with specific fitness goals
        """
        goal_mapping = {
            'maintain weight': 'maintain_weight',
            'lose weight': 'lose_weight',
            'gain muscle': 'gain_muscle',
            'improve fitness': 'improve_fitness'
        }
        
        goal_key = goal_mapping.get(goal.lower(), 'maintain_weight')
        priorities = self.goal_priorities[goal_key]
        
        # Map adaptations to goal priorities
        adaptation_mapping = {
            'cardiovascular_health': 'cardiovascular_endurance',
            'strength_maintenance': 'muscular_strength',
            'functional_movement': 'functional_movement',
            'flexibility_mobility': 'flexibility_mobility',
            'calorie_expenditure': 'calorie_expenditure',
            'cardiovascular_fitness': 'cardiovascular_endurance',
            'muscle_preservation': 'muscular_strength',
            'metabolic_conditioning': 'calorie_expenditure',
            'progressive_overload': 'muscular_strength',
            'muscle_hypertrophy': 'muscular_hypertrophy',
            'strength_building': 'muscular_strength',
            'recovery_optimization': 'flexibility_mobility',
            'cardiovascular_endurance': 'cardiovascular_endurance',
            'muscular_strength': 'muscular_strength',
            'functional_capacity': 'functional_movement',
            'movement_quality': 'balance_coordination'
        }
        
        compatibility_score = 0.0
        for priority, weight in priorities.items():
            adaptation_key = adaptation_mapping.get(priority, priority)
            if adaptation_key in adaptations:
                compatibility_score += adaptations[adaptation_key] * weight
        
        return round(compatibility_score, 1)
    
    def calculate_activity_level_suitability(self, exercise: Dict, activity_level: str) -> float:
        """
        Calculate exercise suitability based on activity level
        """
        complexity = self.calculate_complexity_score(exercise)
        equipment = exercise['equipments'][0].lower() if exercise['equipments'] else 'body weight'
        
        activity_key = activity_level.lower().replace(' ', '_')
        if activity_key not in self.activity_modifiers:
            activity_key = 'moderately_active'
        
        modifiers = self.activity_modifiers[activity_key]
        
        # Base suitability score
        suitability = 5.0
        
        # Adjust for complexity vs activity level
        if activity_key == 'sedentary':
            if complexity <= 2:
                suitability += 3.0
            elif complexity >= 4:
                suitability -= 2.0
        elif activity_key in ['lightly_active', 'moderately_active']:
            if 2 <= complexity <= 3:
                suitability += 2.0
            elif complexity >= 5:
                suitability -= 1.0
        else:  # very_active, extremely_active
            if complexity >= 3:
                suitability += 2.0
            elif complexity <= 1:
                suitability -= 1.0
        
        # Equipment accessibility adjustment
        accessible_equipment = ['body weight', 'dumbbell', 'band', 'kettlebell']
        if equipment in accessible_equipment:
            suitability += 1.0
        elif equipment in ['machine', 'cable', 'barbell']:
            if activity_key in ['very_active', 'extremely_active']:
                suitability += 0.5
            else:
                suitability -= 0.5
        
        return round(min(10.0, max(0.0, suitability)), 1)
    
    def calculate_complexity_score(self, exercise: Dict) -> int:
        """Calculate exercise complexity (1-5 scale)"""
        instructions = exercise.get('instructions', [])
        num_steps = len(instructions)
        equipment = exercise['equipments'][0].lower() if exercise['equipments'] else ''
        name = exercise['name'].lower()
        
        # Base complexity on number of instructions
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
        complex_movements = ['snatch', 'clean', 'jerk', 'turkish', 'complex', 'alternating']
        if any(movement in name for movement in complex_movements):
            complexity = min(5, complexity + 1)
        
        simple_movements = ['curl', 'raise', 'shrug', 'extension']
        if any(movement in name for movement in simple_movements):
            complexity = max(1, complexity - 1)
        
        return complexity
    
    def determine_primary_training_category(self, adaptations: Dict[str, float]) -> str:
        """Determine primary training category based on adaptations"""
        max_adaptation = max(adaptations, key=adaptations.get)
        
        category_mapping = {
            'cardiovascular_endurance': 'Cardiovascular Training',
            'muscular_strength': 'Strength Training',
            'muscular_hypertrophy': 'Hypertrophy Training',
            'power_development': 'Power Training',
            'functional_movement': 'Functional Training',
            'calorie_expenditure': 'Metabolic Training',
            'flexibility_mobility': 'Flexibility & Mobility',
            'balance_coordination': 'Balance & Coordination'
        }
        
        return category_mapping.get(max_adaptation, 'General Fitness')
    
    def process_exercises_with_evidence_base(self) -> pd.DataFrame:
        """Process exercises using evidence-based classification"""
        print("Processing exercises with evidence-based approach...")
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
            adaptations = self.classify_exercise_by_adaptation(exercise)
            
            # Add adaptation scores
            for adaptation, score in adaptations.items():
                processed_exercise[f"{adaptation}_score"] = score
            
            # Determine primary training category
            processed_exercise['primary_training_category'] = self.determine_primary_training_category(adaptations)
            
            # Calculate goal compatibility scores
            goals = ['Maintain Weight', 'Lose Weight', 'Gain Muscle', 'Improve Fitness']
            for goal in goals:
                goal_key = f"{goal.lower().replace(' ', '_')}_compatibility"
                processed_exercise[goal_key] = self.calculate_goal_compatibility(adaptations, goal)
            
            # Calculate activity level suitability
            activity_levels = ['Sedentary', 'Lightly Active', 'Moderately Active', 'Very Active', 'Extremely Active']
            for activity in activity_levels:
                activity_key = f"{activity.lower().replace(' ', '_')}_suitability"
                processed_exercise[activity_key] = self.calculate_activity_level_suitability(exercise, activity)
            
            # Calculate overall exercise quality score
            adaptation_average = np.mean(list(adaptations.values()))
            goal_average = np.mean([processed_exercise[f"{goal.lower().replace(' ', '_')}_compatibility"] for goal in goals])
            processed_exercise['overall_quality_score'] = round((adaptation_average + goal_average) / 2, 1)
            
            processed_exercises.append(processed_exercise)
        
        return pd.DataFrame(processed_exercises)
    
    def generate_user_specific_recommendations(self, exercises_df: pd.DataFrame, user_profile: Dict) -> pd.DataFrame:
        """Generate recommendations specific to user profile"""
        print(f"Generating recommendations for {user_profile['name']}...")
        
        goal = user_profile['goal']
        activity_level = user_profile['activity_level']
        age = user_profile['age']
        
        # Calculate user-specific scores
        user_exercises = exercises_df.copy()
        
        # Goal compatibility weighting
        goal_key = f"{goal.lower().replace(' ', '_')}_compatibility"
        if goal_key in user_exercises.columns:
            user_exercises['goal_match_score'] = user_exercises[goal_key]
        else:
            user_exercises['goal_match_score'] = 5.0
        
        # Activity level suitability weighting
        activity_key = f"{activity_level.lower().replace(' ', '_')}_suitability"
        if activity_key in user_exercises.columns:
            user_exercises['activity_match_score'] = user_exercises[activity_key]
        else:
            user_exercises['activity_match_score'] = 5.0
        
        # Age-based adjustments (evidence-based)
        user_exercises['age_adjusted_score'] = user_exercises['overall_quality_score']
        
        if age < 25:
            # Young adults can handle higher complexity and intensity
            user_exercises.loc[user_exercises['complexity_level'] >= 3, 'age_adjusted_score'] += 0.5
        elif age > 40:
            # Older adults benefit from lower complexity and joint-friendly exercises
            user_exercises.loc[user_exercises['complexity_level'] <= 2, 'age_adjusted_score'] += 0.5
            user_exercises.loc[user_exercises['flexibility_mobility_score'] >= 6, 'age_adjusted_score'] += 0.5
        
        # Calculate final recommendation score
        user_exercises['user_recommendation_score'] = (
            user_exercises['goal_match_score'] * 0.4 +
            user_exercises['activity_match_score'] * 0.3 +
            user_exercises['age_adjusted_score'] * 0.3
        )
        
        return user_exercises.sort_values('user_recommendation_score', ascending=False)
    
    def create_goal_based_categories(self, exercises_df: pd.DataFrame) -> None:
        """Create exercise files based on training categories"""
        print("Creating goal-based exercise categories...")
        
        categories = exercises_df['primary_training_category'].unique()
        
        for category in categories:
            category_df = exercises_df[exercises_df['primary_training_category'] == category].copy()
            category_df = category_df.sort_values('overall_quality_score', ascending=False)
            
            filename = f"exercises_{category.lower().replace(' ', '_').replace('&', 'and')}.csv"
            filepath = os.path.join(self.processed_path, filename)
            
            category_df.to_csv(filepath, index=False)
            print(f"  ✅ Created {filename} with {len(category_df)} exercises")
    
    def generate_evidence_based_summary(self, exercises_df: pd.DataFrame, user_recommendations: pd.DataFrame) -> None:
        """Generate summary based on evidence-based classification"""
        print("\nGenerating evidence-based summary...")
        
        summary_stats = {
            'total_exercises': len(exercises_df),
            'training_categories': exercises_df['primary_training_category'].value_counts().to_dict(),
            'complexity_distribution': exercises_df['complexity_level'].value_counts().to_dict(),
            'equipment_accessibility': exercises_df['primary_equipment'].value_counts().head(10).to_dict(),
            'top_adaptations': {
                'cardiovascular': exercises_df['cardiovascular_endurance_score'].mean(),
                'strength': exercises_df['muscular_strength_score'].mean(),
                'hypertrophy': exercises_df['muscular_hypertrophy_score'].mean(),
                'functional': exercises_df['functional_movement_score'].mean()
            },
            'user_specific_recommendations': {
                'top_10_exercises': user_recommendations.head(10)[['name', 'primary_training_category', 'user_recommendation_score']].to_dict('records'),
                'recommended_focus': user_recommendations.iloc[0]['primary_training_category'],
                'average_recommendation_score': user_recommendations['user_recommendation_score'].mean()
            }
        }
        
        # Save summary
        summary_path = os.path.join(self.processed_path, 'evidence_based_summary.json')
        with open(summary_path, 'w') as f:
            json.dump(summary_stats, f, indent=2)
        
        print(f"✅ Evidence-based summary saved")
        print(f"\n📊 Analysis Summary:")
        print(f"  • Total Exercises: {summary_stats['total_exercises']:,}")
        print(f"  • Training Categories: {len(summary_stats['training_categories'])}")
        print(f"  • Recommended Focus: {summary_stats['user_specific_recommendations']['recommended_focus']}")
        print(f"  • User Match Score: {summary_stats['user_specific_recommendations']['average_recommendation_score']:.1f}/10")
    
    def run_evidence_based_processing(self, user_profile: Dict) -> None:
        """Run the complete evidence-based processing pipeline"""
        print("🔬 Starting Evidence-Based Fitness Dataset Processing")
        print("=" * 65)
        print(f"👤 User Profile: {user_profile['name']}, {user_profile['age']} years old")
        print(f"🎯 Goal: {user_profile['goal']}")
        print(f"🏃 Activity Level: {user_profile['activity_level']}")
        print("=" * 65)
        
        try:
            # Process exercises with evidence-based approach
            exercises_df = self.process_exercises_with_evidence_base()
            exercises_path = os.path.join(self.processed_path, 'evidence_based_exercises_database.csv')
            exercises_df.to_csv(exercises_path, index=False)
            print(f"✅ Evidence-based exercises database saved: {len(exercises_df):,} exercises")
            
            # Generate user-specific recommendations
            user_recommendations = self.generate_user_specific_recommendations(exercises_df, user_profile)
            user_path = os.path.join(self.processed_path, f'user_recommendations_{user_profile["name"].lower()}.csv')
            user_recommendations.to_csv(user_path, index=False)
            print(f"✅ User-specific recommendations saved: {user_profile['name']}")
            
            # Create goal-based categories
            self.create_goal_based_categories(exercises_df)
            
            # Generate summary
            self.generate_evidence_based_summary(exercises_df, user_recommendations)
            
            print(f"\n🎯 Evidence-Based Processing Complete!")
            print(f"📁 All files saved to: {self.processed_path}")
            
        except Exception as e:
            print(f"❌ Error during processing: {str(e)}")
            raise

def main():
    """Main execution function"""
    
    # Load user input
    user_input_path = r"c:\Users\LENOVO\Desktop\Kekious_Maximus\diet-recommendation-somatotype\data\input_files\input_info_recommendation.csv"
    
    try:
        user_df = pd.read_csv(user_input_path)
        user_profile = {
            'name': user_df.iloc[0]['Name'],
            'age': int(user_df.iloc[0]['Age']),
            'goal': user_df.iloc[0]['Goal'],
            'activity_level': user_df.iloc[0]['Activity_Level']
        }
        
        # Initialize processor and run
        processor = EvidenceBasedFitnessProcessor()
        processor.run_evidence_based_processing(user_profile)
        
    except Exception as e:
        print(f"❌ Error loading user input: {str(e)}")
        print("Using default profile for demonstration...")
        
        default_profile = {
            'name': 'casper',
            'age': 21,
            'goal': 'Maintain Weight',
            'activity_level': 'Moderately active'
        }
        
        processor = EvidenceBasedFitnessProcessor()
        processor.run_evidence_based_processing(default_profile)

if __name__ == "__main__":
    main()
