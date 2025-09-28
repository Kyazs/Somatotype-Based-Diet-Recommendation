"""
Database Module for Diet Recommendation System
Handles SQLite database operations for storing user data, analysis results,
and recommendations with proper error handling and connection management.
"""

import sqlite3
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import sys

# Add project root to path
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(PROJECT_DIR)

from src.utils.utils import BASE_DIR


class DatabaseManager:
    """
    Comprehensive database manager for the Diet Recommendation System.
    Handles all database operations including user data, analysis results,
    and recommendation history.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database manager with connection path"""
        if db_path is None:
            # Store database in the database folder
            db_folder = os.path.join(BASE_DIR, "data", "database")
            os.makedirs(db_folder, exist_ok=True)
            db_path = os.path.join(db_folder, "app_data.db")
        
        self.db_path = db_path
        self.connection = None
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize database on first run
        self.init_db()
    
    def connect_db(self) -> sqlite3.Connection:
        """Create database connection with optimized settings"""
        try:
            conn = sqlite3.connect(
                self.db_path,
                timeout=30.0,
                isolation_level=None  # Autocommit mode
            )
            
            # Enable foreign keys and WAL mode for better performance
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            
            # Set row factory for easier data access
            conn.row_factory = sqlite3.Row
            
            return conn
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            raise
    
    def init_db(self):
        """Initialize database with all required tables"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                # Create Users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        age INTEGER NOT NULL,
                        gender TEXT NOT NULL CHECK (gender IN ('male', 'female')),
                        height_cm REAL NOT NULL,
                        weight_kg REAL NOT NULL,
                        activity_level TEXT NOT NULL,
                        fitness_goals TEXT,
                        exercise_type TEXT DEFAULT 'bodyweight',
                        exercise_complexity TEXT DEFAULT 'beginner',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create Analysis Sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS analysis_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        front_image_path TEXT,
                        side_image_path TEXT,
                        processed_front_path TEXT,
                        processed_side_path TEXT,
                        status TEXT DEFAULT 'pending',
                        somatotype_class TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """)
                
                # Create Body Measurements table (from CNN output)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS body_measurements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id INTEGER NOT NULL,
                        measurement_type TEXT NOT NULL,
                        basic_input REAL,
                        predicted_input REAL,
                        avatar_output REAL NOT NULL,
                        unit TEXT DEFAULT 'cm',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES analysis_sessions (id) ON DELETE CASCADE
                    )
                """)
                
                # Create Somatotype Classifications table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS somatotype_classifications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id INTEGER NOT NULL,
                        endomorphy REAL NOT NULL,
                        mesomorphy REAL NOT NULL,
                        ectomorphy REAL NOT NULL,
                        somatotype_class TEXT NOT NULL,
                        height_weight_ratio REAL DEFAULT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES analysis_sessions (id) ON DELETE CASCADE
                    )
                """)
                
                # Create Diet Recommendations table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS diet_recommendations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id INTEGER NOT NULL,
                        calories INTEGER NOT NULL,
                        protein_g INTEGER NOT NULL,
                        carbs_g INTEGER NOT NULL,
                        fat_g INTEGER NOT NULL,
                        bmr INTEGER,
                        tdee INTEGER,
                        protein_percentage REAL,
                        carbs_percentage REAL,
                        fat_percentage REAL,
                        nutrition_insights TEXT,
                        meal_recommendations TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        template_id TEXT DEFAULT NULL,
                        diet_principles TEXT DEFAULT NULL,
                        FOREIGN KEY (session_id) REFERENCES analysis_sessions (id) ON DELETE CASCADE
                    )
                """)
                
                # Create Fitness Recommendations table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS fitness_recommendations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id INTEGER NOT NULL,
                        exercises TEXT NOT NULL,
                        workout_plan TEXT,
                        fitness_insights TEXT,
                        template_id TEXT DEFAULT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES analysis_sessions (id) ON DELETE CASCADE
                    )
                """)
                
                conn.commit()
                print("✅ Database initialized successfully")
                
        except sqlite3.Error as e:
            print(f"Error initializing database: {e}")
            # Don't raise here as this might be expected for new databases
    
    def insert_user(self, user_data: Dict[str, Any]) -> int:
        """Insert new user and return user ID"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO users (name, age, gender, height_cm, weight_kg, activity_level, fitness_goals, exercise_type, exercise_complexity)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_data['name'],
                    user_data['age'], 
                    user_data['gender'],
                    user_data['height_cm'],
                    user_data['weight_kg'],
                    user_data['activity_level'],
                    user_data.get('fitness_goals'),
                    user_data.get('exercise_type', 'bodyweight'),
                    user_data.get('exercise_complexity', 'beginner')
                ))
                
                user_id = cursor.lastrowid
                conn.commit()
                print(f"✅ User inserted with ID: {user_id}")
                return user_id
                
        except sqlite3.Error as e:
            print(f"Error inserting user: {e}")
            raise
    
    def create_analysis_session(self, user_id: int, front_image: str = None, side_image: str = None) -> int:
        """Create new analysis session and return session ID"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO analysis_sessions (user_id, front_image_path, side_image_path, status)
                    VALUES (?, ?, ?, 'pending')
                """, (user_id, front_image, side_image))
                
                session_id = cursor.lastrowid
                conn.commit()
                print(f"✅ Analysis session created with ID: {session_id}")
                return session_id
                
        except sqlite3.Error as e:
            print(f"Error creating analysis session: {e}")
            raise
    
    def update_session_status(self, session_id: int, status: str, processed_paths: Dict[str, str] = None):
        """Update session status and processed image paths"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                if processed_paths:
                    cursor.execute("""
                        UPDATE analysis_sessions 
                        SET status = ?, processed_front_path = ?, processed_side_path = ?
                        WHERE id = ?
                    """, (status, 
                          processed_paths.get('front'), 
                          processed_paths.get('side'),
                          session_id))
                else:
                    cursor.execute("""
                        UPDATE analysis_sessions SET status = ? WHERE id = ?
                    """, (status, session_id))
                
                conn.commit()
                print(f"✅ Session {session_id} status updated to: {status}")
                
        except sqlite3.Error as e:
            print(f"Error updating session status: {e}")
            raise
    
    def insert_body_measurements(self, session_id: int, measurements: List[Dict[str, Any]]):
        """Insert body measurements from CNN processing"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                for measurement in measurements:
                    cursor.execute("""
                        INSERT INTO body_measurements 
                        (session_id, measurement_type, basic_input, predicted_input, avatar_output, unit)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        session_id,
                        measurement['type'],
                        measurement.get('basic_input'),
                        measurement.get('predicted_input'),
                        measurement['avatar_output'],
                        measurement.get('unit', 'cm')
                    ))
                
                conn.commit()
                print(f"✅ Body measurements inserted for session {session_id}")
                
        except sqlite3.Error as e:
            print(f"Error inserting body measurements: {e}")
            raise
    
    def insert_somatotype_classification(self, session_id: int, classification: Dict[str, Any]):
        """Insert somatotype classification results"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                # Calculate height_weight_ratio from user data
                cursor.execute("""
                    SELECT u.height_cm, u.weight_kg
                    FROM analysis_sessions s
                    JOIN users u ON s.user_id = u.id
                    WHERE s.id = ?
                """, (session_id,))
                
                user_data = cursor.fetchone()
                height_weight_ratio = None
                if user_data:
                    height_cm = user_data['height_cm']
                    weight_kg = user_data['weight_kg']
                    if height_cm and weight_kg and weight_kg > 0:
                        height_weight_ratio = height_cm / weight_kg
                
                cursor.execute("""
                    INSERT INTO somatotype_classifications 
                    (session_id, endomorphy, mesomorphy, ectomorphy, somatotype_class, height_weight_ratio)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    classification['endomorphy'],
                    classification['mesomorphy'],
                    classification['ectomorphy'],
                    classification['somatotype_class'],
                    height_weight_ratio
                ))
                
                conn.commit()
                print(f"✅ Somatotype classification inserted for session {session_id}")
                
        except sqlite3.Error as e:
            print(f"Error inserting somatotype classification: {e}")
            raise
    
    def insert_diet_recommendation(self, session_id: int, recommendation: Dict[str, Any]) -> int:
        """Insert diet recommendation and return recommendation ID"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO diet_recommendations 
                    (session_id, calories, protein_g, carbs_g, fat_g, bmr, tdee, 
                     protein_percentage, carbs_percentage, fat_percentage, nutrition_insights, 
                     meal_recommendations, template_id, diet_principles)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    recommendation['calories'],
                    recommendation.get('protein_g', recommendation.get('protein', 0)),
                    recommendation.get('carbs_g', recommendation.get('carbs', 0)),
                    recommendation.get('fat_g', recommendation.get('fat', 0)),
                    recommendation.get('bmr'),
                    recommendation.get('tdee'),
                    recommendation.get('protein_percentage'),
                    recommendation.get('carbs_percentage'),
                    recommendation.get('fat_percentage'),
                    recommendation.get('nutrition_insights'),
                    recommendation.get('meal_recommendations', '{}'),  # JSON string of meal data
                    recommendation.get('template_id'),  # Template ID for mapping
                    recommendation.get('diet_principles', '[]')  # JSON string of principles
                ))
                
                recommendation_id = cursor.lastrowid
                conn.commit()
                print(f"✅ Diet recommendation inserted with ID: {recommendation_id}")
                return recommendation_id
                
        except sqlite3.Error as e:
            print(f"Error inserting diet recommendation: {e}")
            raise
    
    def insert_fitness_recommendation(self, session_id: int, fitness_data: Dict[str, Any]) -> int:
        """Insert fitness recommendation and return recommendation ID"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO fitness_recommendations 
                    (session_id, fitness_strategy, strength_days, cardio_days, exercise_recommendations, template_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    fitness_data.get('fitness_strategy', ''),
                    fitness_data.get('strength_days', 0),
                    fitness_data.get('cardio_days', 0),
                    fitness_data.get('exercise_recommendations', fitness_data.get('exercises', '{}')),  # Support both field names
                    fitness_data.get('template_id', '')
                ))
                
                recommendation_id = cursor.lastrowid
                conn.commit()
                print(f"✅ Fitness recommendation inserted with ID: {recommendation_id}")
                return recommendation_id
                
        except sqlite3.Error as e:
            print(f"Error inserting fitness recommendation: {e}")
            raise
    
    def get_user_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent analysis history with complete information"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        s.id as session_id,
                        u.name,
                        u.age,
                        u.gender,
                        u.height_cm,
                        u.weight_kg,
                        u.fitness_goals as goal,
                        s.session_date,
                        s.status,
                        s.front_image_path,
                        s.side_image_path,
                        sc.somatotype_class,
                        sc.endomorphy,
                        sc.mesomorphy, 
                        sc.ectomorphy,
                        sc.height_weight_ratio,
                        dr.calories,
                        dr.protein_g,
                        dr.carbs_g,
                        dr.fat_g,
                        dr.template_id as diet_template_id,
                        dr.diet_principles,
                        fr.template_id as fitness_template_id
                    FROM analysis_sessions s
                    JOIN users u ON s.user_id = u.id
                    LEFT JOIN somatotype_classifications sc ON s.id = sc.session_id
                    LEFT JOIN diet_recommendations dr ON s.id = dr.session_id
                    LEFT JOIN fitness_recommendations fr ON s.id = fr.session_id
                    ORDER BY s.session_date DESC
                    LIMIT ?
                """, (limit,))
                
                results = cursor.fetchall()
                
                history = []
                for row in results:
                    history.append({
                        'session_id': row['session_id'],
                        'name': row['name'],
                        'age': row['age'],
                        'gender': row['gender'],
                        'height_cm': row['height_cm'],
                        'weight_kg': row['weight_kg'],
                        'goal': row['goal'],
                        'session_date': row['session_date'],
                        'status': row['status'],
                        'front_image_path': row['front_image_path'],
                        'side_image_path': row['side_image_path'],
                        'somatotype_class': row['somatotype_class'],
                        'endomorphy': row['endomorphy'],
                        'mesomorphy': row['mesomorphy'],
                        'ectomorphy': row['ectomorphy'],
                        'height_weight_ratio': row['height_weight_ratio'],
                        'calories': row['calories'],
                        'protein_g': row['protein_g'],
                        'carbs_g': row['carbs_g'],
                        'fat_g': row['fat_g'],
                        'diet_template_id': row['diet_template_id'],
                        'diet_principles': row['diet_principles'],
                        'fitness_template_id': row['fitness_template_id']
                    })
                
                print(f"✅ Retrieved {len(history)} history records")
                return history
                
        except sqlite3.Error as e:
            print(f"Error retrieving user history: {e}")
            return []
    
    def get_somatotype_classification(self, session_id: int) -> Dict[str, Any]:
        """Get somatotype classification for a session"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT endomorphy, mesomorphy, ectomorphy, somatotype_class, height_weight_ratio
                    FROM somatotype_classifications
                    WHERE session_id = ?
                """, (session_id,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        'endomorph_score': result['endomorphy'],
                        'mesomorph_score': result['mesomorphy'], 
                        'ectomorph_score': result['ectomorphy'],
                        'somatotype_class': result['somatotype_class'],
                        'height_weight_ratio': result['height_weight_ratio']
                    }
                return {}
                
        except sqlite3.Error as e:
            print(f"Error retrieving somatotype classification: {e}")
            return {}
    
    def get_diet_recommendations(self, session_id: int) -> Dict[str, Any]:
        """Get diet recommendations for a session"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT calories, protein_g, carbs_g, fat_g, bmr, tdee,
                           protein_percentage, carbs_percentage, fat_percentage,
                           nutrition_insights, meal_recommendations, template_id, diet_principles
                    FROM diet_recommendations
                    WHERE session_id = ?
                """, (session_id,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        'calories': result['calories'],
                        'protein_g': result['protein_g'],
                        'carbs_g': result['carbs_g'], 
                        'fat_g': result['fat_g'],
                        'bmr': result['bmr'],
                        'tdee': result['tdee'],
                        'protein_percentage': result['protein_percentage'],
                        'carbs_percentage': result['carbs_percentage'],
                        'fat_percentage': result['fat_percentage'],
                        'nutrition_insights': result['nutrition_insights'],
                        'meal_recommendations': result['meal_recommendations'],
                        'template_id': result['template_id'],
                        'diet_principles': result['diet_principles']
                    }
                return {}
                
        except sqlite3.Error as e:
            print(f"Error retrieving diet recommendations: {e}")
            return {}
    
    def get_fitness_recommendations(self, session_id: int) -> Dict[str, Any]:
        """Get fitness recommendations for a session"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT fitness_strategy, strength_days, cardio_days, exercise_recommendations, template_id
                    FROM fitness_recommendations
                    WHERE session_id = ?
                """, (session_id,))
                
                result = cursor.fetchone()
                if result:
                    return {
                        'fitness_strategy': result['fitness_strategy'],
                        'strength_days': result['strength_days'],
                        'cardio_days': result['cardio_days'],
                        'exercise_recommendations': result['exercise_recommendations'],
                        'template_id': result['template_id']
                    }
                return {}
                
        except sqlite3.Error as e:
            print(f"Error retrieving fitness recommendations: {e}")
            return {}
    
    def get_session_details(self, session_id: int) -> Dict[str, Any]:
        """Get complete session details including user info"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT s.*, u.name as user_name, u.age, u.gender, u.height_cm, u.weight_kg, 
                           u.activity_level, u.fitness_goals, u.exercise_type, u.exercise_complexity
                    FROM analysis_sessions s
                    JOIN users u ON s.user_id = u.id
                    WHERE s.id = ?
                """, (session_id,))
                
                result = cursor.fetchone()
                if result:
                    return dict(result)
                return {}
                
        except sqlite3.Error as e:
            print(f"Error retrieving session details: {e}")
            return {}
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Total analyses (sessions)
                cursor.execute("SELECT COUNT(*) as count FROM analysis_sessions")
                stats['total_analyses'] = cursor.fetchone()['count']
                
                # This week analyses (simplified - last 7 days)
                cursor.execute("""
                    SELECT COUNT(*) as count FROM analysis_sessions 
                    WHERE session_date >= datetime('now', '-7 days')
                """)
                stats['week_analyses'] = cursor.fetchone()['count']
                
                # Latest analysis date
                cursor.execute("""
                    SELECT MAX(session_date) as latest_date FROM analysis_sessions
                """)
                result = cursor.fetchone()
                stats['latest_analysis'] = result['latest_date'] if result['latest_date'] else 'Never'
                
                return stats
                
        except sqlite3.Error as e:
            print(f"Error retrieving database stats: {e}")
            return {
                'total_analyses': 0,
                'week_analyses': 0,
                'latest_analysis': 'Never'
            }