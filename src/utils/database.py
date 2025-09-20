"""
Database Module for Diet Recommendation System
Handles SQLite database operations for storing user data, analysis results,
and recommendations with proper error handling and connection management.
"""
import sqlite3
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
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
        
        # Initialize database
        self.init_db()
    
    def connect_db(self) -> sqlite3.Connection:
        """Create and return database connection with proper configuration"""
        try:
            conn = sqlite3.connect(
                self.db_path,
                timeout=30.0,  # 30 second timeout
                check_same_thread=False  # Allow usage across threads
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
                        goal TEXT NOT NULL,
                        activity_level TEXT NOT NULL,
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
                        status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
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
                        confidence_score REAL DEFAULT 0.0,
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
                        FOREIGN KEY (session_id) REFERENCES analysis_sessions (id) ON DELETE CASCADE
                    )
                """)
                
                # Create Recommended Foods table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS recommended_foods (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        recommendation_id INTEGER NOT NULL,
                        food_name TEXT NOT NULL,
                        food_category TEXT,
                        priority_order INTEGER DEFAULT 0,
                        nutritional_benefits TEXT,
                        FOREIGN KEY (recommendation_id) REFERENCES diet_recommendations (id) ON DELETE CASCADE
                    )
                """)
                
                # Create Meal Plans table (optional for future expansion)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS meal_plans (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        recommendation_id INTEGER NOT NULL,
                        meal_type TEXT NOT NULL CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
                        meal_name TEXT NOT NULL,
                        ingredients TEXT,  -- JSON format
                        calories_per_serving INTEGER,
                        macros_json TEXT,  -- JSON format for detailed macros
                        preparation_notes TEXT,
                        FOREIGN KEY (recommendation_id) REFERENCES diet_recommendations (id) ON DELETE CASCADE
                    )
                """)
                
                # Create indexes for better query performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_name ON users(name)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_date ON analysis_sessions(user_id, session_date)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_measurements_session ON body_measurements(session_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_somatotype_session ON somatotype_classifications(session_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_recommendations_session ON diet_recommendations(session_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_foods_recommendation ON recommended_foods(recommendation_id)")
                
                conn.commit()
                print("✅ Database initialized successfully")
                
                # Run database migrations after initialization
                self._run_migrations()
                
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            raise
    
    def _run_migrations(self):
        """Run database migrations to update schema"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                # Check if meal_recommendations column exists
                cursor.execute("PRAGMA table_info(diet_recommendations)")
                columns = [row[1] for row in cursor.fetchall()]
                
                if 'meal_recommendations' not in columns:
                    print("🔄 Adding meal_recommendations column to diet_recommendations table...")
                    cursor.execute("""
                        ALTER TABLE diet_recommendations 
                        ADD COLUMN meal_recommendations TEXT DEFAULT '{}'
                    """)
                    print("✅ meal_recommendations column added successfully")
                
                conn.commit()
                
        except sqlite3.Error as e:
            print(f"Migration error: {e}")
            # Don't raise here as this might be expected for new databases
    
    def insert_user(self, user_data: Dict[str, Any]) -> int:
        """Insert new user and return user ID"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO users (name, age, gender, height_cm, weight_kg, goal, activity_level)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_data['name'],
                    user_data['age'], 
                    user_data['gender'],
                    user_data['height'],
                    user_data['weight'],
                    user_data['goal'],
                    user_data['activity_level']
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
        """Update analysis session status and processed image paths"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                if processed_paths:
                    cursor.execute("""
                        UPDATE analysis_sessions 
                        SET status = ?, processed_front_path = ?, processed_side_path = ?
                        WHERE id = ?
                    """, (
                        status,
                        processed_paths.get('front'),
                        processed_paths.get('side'),
                        session_id
                    ))
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
        """Insert body measurements from CNN analysis"""
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
                print(f"✅ Inserted {len(measurements)} body measurements for session {session_id}")
                
        except sqlite3.Error as e:
            print(f"Error inserting body measurements: {e}")
            raise
    
    def insert_somatotype_classification(self, session_id: int, classification: Dict[str, Any]):
        """Insert somatotype classification results"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO somatotype_classifications 
                    (session_id, endomorphy, mesomorphy, ectomorphy, somatotype_class, confidence_score)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    classification['endomorphy'],
                    classification['mesomorphy'],
                    classification['ectomorphy'],
                    classification['somatotype_class'],
                    classification.get('confidence_score', 0.0)
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
                     protein_percentage, carbs_percentage, fat_percentage, nutrition_insights, meal_recommendations)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    recommendation['calories'],
                    recommendation['protein'],
                    recommendation['carbs'],
                    recommendation['fat'],
                    recommendation.get('bmr'),
                    recommendation.get('tdee'),
                    recommendation.get('protein_percentage'),
                    recommendation.get('carbs_percentage'),
                    recommendation.get('fat_percentage'),
                    recommendation.get('nutrition_insights'),
                    recommendation.get('meal_recommendations', '{}')  # JSON string of meal data
                ))
                
                recommendation_id = cursor.lastrowid
                conn.commit()
                print(f"✅ Diet recommendation inserted with ID: {recommendation_id}")
                return recommendation_id
                
        except sqlite3.Error as e:
            print(f"Error inserting diet recommendation: {e}")
            raise
    
    def insert_recommended_foods(self, recommendation_id: int, foods: List[str]):
        """Insert recommended foods for a diet recommendation"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                for i, food in enumerate(foods):
                    cursor.execute("""
                        INSERT INTO recommended_foods (recommendation_id, food_name, priority_order)
                        VALUES (?, ?, ?)
                    """, (recommendation_id, food.strip(), i + 1))
                
                conn.commit()
                print(f"✅ Inserted {len(foods)} recommended foods")
                
        except sqlite3.Error as e:
            print(f"Error inserting recommended foods: {e}")
            raise
    
    def get_user_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent analysis history with complete information"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        u.name,
                        u.age,
                        u.gender,
                        u.goal,
                        s.session_date,
                        s.status,
                        s.front_image_path,
                        s.side_image_path,
                        st.somatotype_class,
                        st.endomorphy,
                        st.mesomorphy, 
                        st.ectomorphy,
                        dr.calories,
                        dr.protein_g,
                        dr.carbs_g,
                        dr.fat_g,
                        s.id as session_id
                    FROM analysis_sessions s
                    JOIN users u ON s.user_id = u.id
                    LEFT JOIN somatotype_classifications st ON s.id = st.session_id
                    LEFT JOIN diet_recommendations dr ON s.id = dr.session_id
                    ORDER BY s.session_date DESC
                    LIMIT ?
                """, (limit,))
                
                rows = cursor.fetchall()
                history = []
                
                for row in rows:
                    history.append({
                        'name': row['name'],
                        'age': row['age'],
                        'gender': row['gender'],
                        'goal': row['goal'],
                        'session_date': row['session_date'],
                        'status': row['status'],
                        'front_image_path': row['front_image_path'],
                        'side_image_path': row['side_image_path'],
                        'somatotype_class': row['somatotype_class'],
                        'endomorphy': row['endomorphy'],
                        'mesomorphy': row['mesomorphy'],
                        'ectomorphy': row['ectomorphy'],
                        'calories': row['calories'],
                        'protein_g': row['protein_g'],
                        'carbs_g': row['carbs_g'],
                        'fat_g': row['fat_g'],
                        'session_id': row['session_id']
                    })
                
                print(f"✅ Retrieved {len(history)} history records")
                return history
                
        except sqlite3.Error as e:
            print(f"Error retrieving user history: {e}")
            return []
    
    def get_somatotype_classification(self, session_id: int) -> Dict[str, Any]:
        """Get somatotype classification for a specific session"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM somatotype_classifications WHERE session_id = ?
                """, (session_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'ectomorph_score': row['ectomorphy'],
                        'mesomorph_score': row['mesomorphy'],
                        'endomorph_score': row['endomorphy'],
                        'somatotype_class': row['somatotype_class'],
                        'confidence_score': row['confidence_score']
                    }
                return {}
                
        except sqlite3.Error as e:
            print(f"Error retrieving somatotype classification: {e}")
            return {}
    
    def get_diet_recommendations(self, session_id: int) -> Dict[str, Any]:
        """Get diet recommendations for a specific session"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM diet_recommendations WHERE session_id = ? ORDER BY created_at DESC LIMIT 1
                """, (session_id,))
                
                row = cursor.fetchone()
                if row:
                    # Get recommended foods
                    cursor.execute("""
                        SELECT food_name, food_category, priority_order, nutritional_benefits
                        FROM recommended_foods rf
                        WHERE rf.recommendation_id = ?
                        ORDER BY rf.priority_order
                    """, (row['id'],))
                    
                    foods = cursor.fetchall()
                    
                    return {
                        'calories': row['calories'],
                        'protein_g': row['protein_g'],
                        'carbs_g': row['carbs_g'],
                        'fat_g': row['fat_g'],
                        'bmr': row['bmr'],
                        'tdee': row['tdee'],
                        'protein_percentage': row['protein_percentage'],
                        'carbs_percentage': row['carbs_percentage'],
                        'fat_percentage': row['fat_percentage'],
                        'nutrition_insights': row['nutrition_insights'],
                        'nutrition_data': {
                            'protein_percentage': row['protein_percentage'],
                            'carbs_percentage': row['carbs_percentage'],
                            'fat_percentage': row['fat_percentage']
                        },
                        'recommended_foods': [dict(food) for food in foods],
                        'meal_recommendations': row['meal_recommendations'] if row['meal_recommendations'] else '{}'
                    }
                return {}
                
        except sqlite3.Error as e:
            print(f"Error retrieving diet recommendations: {e}")
            return {}
    
    def get_session_details(self, session_id: int) -> Dict[str, Any]:
        """Get complete details for a specific session"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                # Get session and user info
                cursor.execute("""
                    SELECT 
                        s.*,
                        u.name, u.age, u.gender, u.height_cm, u.weight_kg, u.goal, u.activity_level
                    FROM analysis_sessions s
                    JOIN users u ON s.user_id = u.id
                    WHERE s.id = ?
                """, (session_id,))
                
                session_data = cursor.fetchone()
                if not session_data:
                    return {}
                
                # Convert to dictionary
                result = dict(session_data)
                
                # Get somatotype classification
                cursor.execute("""
                    SELECT * FROM somatotype_classifications WHERE session_id = ?
                """, (session_id,))
                somatotype = cursor.fetchone()
                if somatotype:
                    result['somatotype'] = dict(somatotype)
                
                # Get diet recommendation
                cursor.execute("""
                    SELECT * FROM diet_recommendations WHERE session_id = ?
                """, (session_id,))
                recommendation = cursor.fetchone()
                if recommendation:
                    result['diet_recommendation'] = dict(recommendation)
                
                # Get recommended foods
                cursor.execute("""
                    SELECT food_name FROM recommended_foods 
                    WHERE recommendation_id = (
                        SELECT id FROM diet_recommendations WHERE session_id = ?
                    )
                    ORDER BY priority_order
                """, (session_id,))
                foods = cursor.fetchall()
                result['recommended_foods'] = [food['food_name'] for food in foods]
                
                # Get body measurements
                cursor.execute("""
                    SELECT * FROM body_measurements WHERE session_id = ? ORDER BY measurement_type
                """, (session_id,))
                measurements = cursor.fetchall()
                result['body_measurements'] = [dict(measurement) for measurement in measurements]
                
                return result
                
        except sqlite3.Error as e:
            print(f"Error retrieving session details: {e}")
            return {}
    
    def delete_session(self, session_id: int) -> bool:
        """Delete a complete analysis session and all related data"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                # Delete session (CASCADE will handle related tables)
                cursor.execute("DELETE FROM analysis_sessions WHERE id = ?", (session_id,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    print(f"✅ Deleted session {session_id} and all related data")
                    return True
                else:
                    print(f"❌ Session {session_id} not found")
                    return False
                
        except sqlite3.Error as e:
            print(f"Error deleting session: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics for monitoring"""
        try:
            with self.connect_db() as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Count records in each table
                tables = [
                    'users', 'analysis_sessions', 'body_measurements',
                    'somatotype_classifications', 'diet_recommendations', 'recommended_foods'
                ]
                
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[table] = cursor.fetchone()[0]
                
                # Get recent activity
                cursor.execute("""
                    SELECT COUNT(*) FROM analysis_sessions 
                    WHERE session_date >= datetime('now', '-7 days')
                """)
                stats['sessions_last_7_days'] = cursor.fetchone()[0]
                
                return stats
                
        except sqlite3.Error as e:
            print(f"Error getting database stats: {e}")
            return {}
    
    def close_connection(self):
        """Close database connection if exists"""
        if self.connection:
            self.connection.close()
            self.connection = None
            print("🔒 Database connection closed")


# Convenience function for external usage
def get_database_manager() -> DatabaseManager:
    """Get a configured database manager instance"""
    return DatabaseManager()


# Test function to verify database functionality
def test_database():
    """Test database functionality with sample data"""
    print("🧪 Testing database functionality...")
    
    try:
        # Initialize database
        db = DatabaseManager()
        
        # Test user insertion
        user_data = {
            'name': 'Test User',
            'age': 25,
            'gender': 'male',
            'height': 175.0,
            'weight': 70.0,
            'goal': 'Weight Loss',
            'activity_level': 'Moderately active'
        }
        user_id = db.insert_user(user_data)
        
        # Test session creation
        session_id = db.create_analysis_session(user_id, "test_front.png", "test_side.png")
        
        # Test somatotype insertion
        somatotype_data = {
            'endomorphy': 4.5,
            'mesomorphy': 3.6,
            'ectomorphy': 2.4,
            'somatotype_class': 'Endo-Mesomorph',
            'confidence_score': 0.85
        }
        db.insert_somatotype_classification(session_id, somatotype_data)
        
        # Test recommendation insertion
        recommendation_data = {
            'calories': 2200,
            'protein': 150,
            'carbs': 220,
            'fat': 80,
            'bmr': 1650,
            'tdee': 2200,
            'nutrition_insights': 'Sample insights'
        }
        rec_id = db.insert_diet_recommendation(session_id, recommendation_data)
        
        # Test food insertion
        foods = ['Chicken Breast', 'Brown Rice', 'Broccoli', 'Greek Yogurt']
        db.insert_recommended_foods(rec_id, foods)
        
        # Test data retrieval
        history = db.get_user_history(10)
        print(f"✅ Retrieved {len(history)} history records")
        
        # Test detailed session retrieval
        details = db.get_session_details(session_id)
        print(f"✅ Session details retrieved: {details.get('name', 'Unknown')}")
        
        # Test database stats
        stats = db.get_database_stats()
        print(f"✅ Database stats: {stats}")
        
        print("🎉 All database tests passed!")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        raise


if __name__ == "__main__":
    test_database()