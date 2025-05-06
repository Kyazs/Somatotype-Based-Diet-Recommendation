"""
State manager for the application.
Manages data flow and state between pages.
"""
import os
import csv
import json
from datetime import datetime

from utils.utils import INPUT_FILES_DIR, OUTPUT_FILES_DIR

class StateManager:
    """Manages application state and data flow between pages"""
    
    def __init__(self):
        """Initialize the state manager with default values"""
        self.reset_state()
        
    def reset_state(self):
        """Reset the state to default values"""
        self.user_data = {
            "name": "",
            "gender": "male",
            "age": "",
            "weight": "",
            "height": "",
            "goal": "Maintain Weight",
            "activity_level": "Moderately active",
            "allergies": []
        }
        
        self.image_data = {
            "front_image_path": None,
            "side_image_path": None,
            "front_silhouette_path": None,
            "side_silhouette_path": None
        }
        
        self.analysis_data = {
            "measurements": {},
            "somatotype": {
                "ectomorph": 0.0,
                "mesomorph": 0.0,
                "endomorph": 0.0
            },
            "classification": "",
            "macros": {
                "protein": 0.0,
                "carbs": 0.0,
                "fats": 0.0
            },
            "calories": 0.0,
            "diet_recommendations": []
        }
        
    def update_user_data(self, **kwargs):
        """Update user data with new values"""
        self.user_data.update(kwargs)
        
    def update_image_data(self, **kwargs):
        """Update image data with new values"""
        self.image_data.update(kwargs)
        
    def update_analysis_data(self, **kwargs):
        """Update analysis data with new values"""
        # For nested updates, this implementation merges at the top level only
        # Extend this if needed for deeper nesting
        for key, value in kwargs.items():
            if key in self.analysis_data and isinstance(self.analysis_data[key], dict) and isinstance(value, dict):
                self.analysis_data[key].update(value)
            else:
                self.analysis_data[key] = value
                
    def save_user_input_files(self):
        """Save user data to the required CSV files for processing"""
        # Ensure directories exist
        os.makedirs(INPUT_FILES_DIR, exist_ok=True)
        
        # File paths
        extractor_file_path = os.path.join(INPUT_FILES_DIR, "input_info_extractor.csv")
        recommendation_file_path = os.path.join(INPUT_FILES_DIR, "input_info_recommendation.csv")
        
        # Write data to input_info_extractor.csv
        with open(extractor_file_path, mode="w", newline="") as extractor_file:
            extractor_writer = csv.writer(extractor_file)
            extractor_writer.writerow(["gender", "stature_cm", "weight_kg"])  # Write header
            extractor_writer.writerow([
                self.user_data["gender"], 
                self.user_data["height"], 
                self.user_data["weight"]
            ])
            
        # Write data to input_info_recommendation.csv
        with open(recommendation_file_path, mode="w", newline="") as recommendation_file:
            recommendation_writer = csv.writer(recommendation_file)
            recommendation_writer.writerow(["Name", "Age", "Goal", "Activity_Level"])  # Write header
            recommendation_writer.writerow([
                self.user_data["name"], 
                self.user_data["age"], 
                self.user_data["goal"],
                self.user_data["activity_level"]
            ])
            
        return True
        
    def load_analysis_results(self):
        """Load analysis results from output files"""
        # Ensure output directory exists
        if not os.path.exists(OUTPUT_FILES_DIR):
            print("Output directory doesn't exist yet.")
            return False
            
        # Try to load the classification result
        classification_path = os.path.join(OUTPUT_FILES_DIR, "output_classification.csv")
        if os.path.exists(classification_path):
            try:
                with open(classification_path, mode="r") as classification_file:
                    reader = csv.reader(classification_file)
                    next(reader)  # Skip header
                    row = next(reader)  # Get first data row
                    
                    # Update somatotype values based on file content
                    # Adjust this based on your actual file structure
                    self.analysis_data["somatotype"]["ectomorph"] = float(row[1])
                    self.analysis_data["somatotype"]["mesomorph"] = float(row[2])
                    self.analysis_data["somatotype"]["endomorph"] = float(row[3])
                    self.analysis_data["classification"] = row[4]
            except Exception as e:
                print(f"Error loading classification data: {str(e)}")
                
        # Try to load recommendation data
        recommendation_path = os.path.join(OUTPUT_FILES_DIR, "output_recommendation.csv")
        if os.path.exists(recommendation_path):
            try:
                with open(recommendation_path, mode="r") as recommendation_file:
                    reader = csv.reader(recommendation_file)
                    headers = next(reader)  # Get headers
                    row = next(reader)  # Get first data row
                    
                    # Update diet recommendations based on file content
                    # This will depend on your specific file structure
                    macros = {
                        "protein": float(row[headers.index("Protein(%)")]) if "Protein(%)" in headers else 0.0,
                        "carbs": float(row[headers.index("Carbohydrates(%)")]) if "Carbohydrates(%)" in headers else 0.0,
                        "fats": float(row[headers.index("Fats(%)")]) if "Fats(%)" in headers else 0.0
                    }
                    
                    self.analysis_data["macros"] = macros
                    
                    # Try to parse calories if available
                    if "Calories" in headers:
                        self.analysis_data["calories"] = float(row[headers.index("Calories")])
                    
                    # Load diet recommendations
                    # This is just a placeholder - modify according to your actual data structure
                    self.analysis_data["diet_recommendations"] = self._parse_diet_recommendations()
            except Exception as e:
                print(f"Error loading recommendation data: {str(e)}")
                
        return True
        
    def _parse_diet_recommendations(self):
        """Parse diet recommendations from templates based on classification"""
        recommendations = []
        
        # Load diet templates
        template_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "diet_templates.csv")
        
        if not os.path.exists(template_path):
            print(f"Diet templates file not found at {template_path}")
            return recommendations
            
        try:
            with open(template_path, mode="r") as template_file:
                reader = csv.DictReader(template_file)
                
                # Find recommendations matching the classification
                somatotype = self.analysis_data["classification"]
                
                for row in reader:
                    if row.get("Somatotype", "").lower() == somatotype.lower():
                        # Process this recommendation
                        # Modify this based on your actual template structure
                        category = row.get("Category", "")
                        if category:
                            # Find all foods in this category
                            food = {
                                "name": row.get("Food", ""),
                                "category": category,
                                "frequency": row.get("Frequency", ""),
                                "portion_size": row.get("Portion_Size", ""),
                                "protein": row.get("Protein(g)", ""),
                                "carbs": row.get("Carbs(g)", ""),
                                "fats": row.get("Fats(g)", "")
                            }
                            
                            # Add to recommendations list
                            recommendations.append(food)
        except Exception as e:
            print(f"Error parsing diet recommendations: {str(e)}")
            
        return recommendations
        
    def export_data(self):
        """Export all data to a JSON file for reference"""
        export_data = {
            "user_data": self.user_data,
            "image_data": self.image_data,
            "analysis_data": self.analysis_data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Ensure output directory exists
        os.makedirs(OUTPUT_FILES_DIR, exist_ok=True)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = os.path.join(OUTPUT_FILES_DIR, f"analysis_results_{timestamp}.json")
        
        try:
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=4)
            return export_path
        except Exception as e:
            print(f"Error exporting data: {str(e)}")
            return None