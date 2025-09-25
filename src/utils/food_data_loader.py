"""
Food Data Loader Module
Handles loading and looking up food information from the optimized diet database
"""

import os
import pandas as pd
import sys
from typing import Dict, Optional

# Add project root to path
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(PROJECT_DIR)

class FoodDataLoader:
    """Handles loading and looking up food information"""
    
    def __init__(self):
        """Initialize food data loader"""
        self.food_database = None
        self.food_lookup = {}
        self._load_food_database()
    
    def _load_food_database(self):
        """Load the food database from CSV"""
        try:
            food_db_path = os.path.join(
                PROJECT_DIR, 
                "data", "datasets", "diet", "fndds_processed", 
                "optimized_diet_recommendation_database.csv"
            )
            
            if os.path.exists(food_db_path):
                self.food_database = pd.read_csv(food_db_path)
                
                # Create lookup dictionary for faster access
                for idx, row in self.food_database.iterrows():
                    food_name = row['Food_Item']
                    self.food_lookup[food_name.lower()] = {
                        'Food_Item': food_name,
                        'Enhanced_Category': row.get('Enhanced_Category', 'N/A'),
                        'Calories_kcal': row.get('Calories_kcal', 0),
                        'Protein_g': row.get('Protein_g', 0),
                        'Carbohydrates_g': row.get('Carbohydrates_g', 0),
                        'Fat_g': row.get('Fat_g', 0),
                        'Fiber_g': row.get('Fiber_g', 0),
                        'Sugars_g': row.get('Sugars_g', 0),
                        'Sodium_mg': row.get('Sodium_mg', 0),
                        'Portion_Recommendation': row.get('Portion_Recommendation', 'As needed'),
                        'Meal_Timing': row.get('Meal_Timing', 'any time'),
                        'Overall_Quality': row.get('Overall_Quality', 'N/A'),
                        'Nutrient_Density_Score': row.get('Nutrient_Density_Score', 0)
                    }
                
                print(f"✅ Food database loaded: {len(self.food_database)} items")
            else:
                print(f"❌ Food database not found at: {food_db_path}")
                
        except Exception as e:
            print(f"❌ Error loading food database: {e}")
    
    def get_food_info(self, food_name: str) -> Optional[Dict]:
        """Get food information by name"""
        if not food_name or not isinstance(food_name, str):
            return None
            
        # Try exact match first
        food_key = food_name.lower().strip()
        if food_key in self.food_lookup:
            return self.food_lookup[food_key]
        
        # Try partial match
        for key, food_data in self.food_lookup.items():
            if food_key in key or key in food_key:
                return food_data
        
        return None
    
    def search_foods(self, query: str, limit: int = 10) -> list:
        """Search for foods matching query"""
        if not query or not isinstance(query, str):
            return []
            
        query_lower = query.lower().strip()
        matches = []
        
        for key, food_data in self.food_lookup.items():
            if query_lower in key:
                matches.append(food_data)
                if len(matches) >= limit:
                    break
        
        return matches
    
    def get_random_foods(self, category: str = None, limit: int = 10) -> list:
        """Get random foods, optionally filtered by category"""
        if not self.food_database is not None:
            return []
        
        df = self.food_database
        if category:
            df = df[df['Enhanced_Category'].str.lower() == category.lower()]
        
        if len(df) > limit:
            df = df.sample(n=limit)
        
        foods = []
        for _, row in df.iterrows():
            foods.append({
                'Food_Item': row['Food_Item'],
                'Enhanced_Category': row.get('Enhanced_Category', 'N/A'),
                'Calories_kcal': row.get('Calories_kcal', 0),
                'Protein_g': row.get('Protein_g', 0),
                'Carbohydrates_g': row.get('Carbohydrates_g', 0),
                'Fat_g': row.get('Fat_g', 0),
                'Fiber_g': row.get('Fiber_g', 0),
                'Portion_Recommendation': row.get('Portion_Recommendation', 'As needed')
            })
        
        return foods

# Global instance
_food_loader = None

def get_food_loader():
    """Get global food loader instance"""
    global _food_loader
    if _food_loader is None:
        _food_loader = FoodDataLoader()
    return _food_loader