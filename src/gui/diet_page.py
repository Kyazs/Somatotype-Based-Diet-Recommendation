"""
Diet Page for the Diet Recommendation System.
Shows personalized diet recommendations and somatotype analysis results.
"""
import customtkinter as ctk
import pandas as pd
import os
import sys
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageTk

# Configuration
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(PROJECT_DIR)

from src.utils.utils import OUTPUT_FILES_DIR
from utils.theme_manager import ThemeManager, IMAGES_DIR

class MacronutrientChart(ctk.CTkFrame):
    """Custom macronutrient ratio chart with labels"""
    
    def __init__(self, parent, protein=30, carbs=45, fat=25):
        super().__init__(parent, fg_color="transparent")
        
        # Save the values
        self.protein = protein
        self.carbs = carbs
        self.fat = fat
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Title
        self.grid_rowconfigure(1, weight=0) # Bar
        self.grid_rowconfigure(2, weight=0) # Legend
        
        # Chart title
        self.chart_title = ctk.CTkLabel(
            self,
            text="Daily Macronutrient Distribution",
            font=ThemeManager.get_subtitle_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        self.chart_title.grid(row=0, column=0, pady=(0, 10))
        
        # Macro bar container
        self.bar_container = ctk.CTkFrame(self, corner_radius=8, fg_color=ThemeManager.GRAY_LIGHT)
        self.bar_container.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # Create the segments
        # Protein (left segment)
        self.protein_fill = ctk.CTkFrame(
            self.bar_container, 
            fg_color=ThemeManager.SUCCESS_COLOR,
            corner_radius=8,
            height=28
        )
        self.protein_fill.place(relx=0, rely=0, relwidth=self.protein/100, relheight=1)
        
        # Carbs (middle segment)
        self.carbs_fill = ctk.CTkFrame(
            self.bar_container, 
            fg_color=ThemeManager.WARNING_COLOR,
            corner_radius=0,
            height=28
        )
        self.carbs_fill.place(relx=self.protein/100, rely=0, relwidth=self.carbs/100, relheight=1)
        
        # Fat (right segment)
        self.fat_fill = ctk.CTkFrame(
            self.bar_container, 
            fg_color=ThemeManager.PRIMARY_COLOR,
            corner_radius=0,
            height=28
        )
        self.fat_fill.place(relx=(self.protein + self.carbs)/100, rely=0, 
                           relwidth=self.fat/100, relheight=1)
        
        # Add right rounded corner to fat segment if it's at the end
        if abs(self.protein + self.carbs + self.fat - 100) < 0.1:  # Roughly 100%
            self.fat_fill.configure(corner_radius=8)
        
        # Legend frame
        self.legend_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.legend_frame.grid(row=2, column=0, sticky="ew")
        self.legend_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Protein legend
        self.protein_legend = self._create_legend_item(
            self.legend_frame, 
            ThemeManager.SUCCESS_COLOR, 
            f"Protein: {self.protein}%",
            0
        )
        
        # Carbs legend
        self.carbs_legend = self._create_legend_item(
            self.legend_frame, 
            ThemeManager.WARNING_COLOR, 
            f"Carbs: {self.carbs}%",
            1
        )
        
        # Fat legend
        self.fat_legend = self._create_legend_item(
            self.legend_frame, 
            ThemeManager.PRIMARY_COLOR, 
            f"Fat: {self.fat}%",
            2
        )
    
    def _create_legend_item(self, parent, color, text, column):
        """Create a legend item with color indicator and text"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=column, padx=5, pady=5)
        
        indicator = ctk.CTkFrame(frame, width=12, height=12, fg_color=color, corner_radius=6)
        indicator.grid(row=0, column=0, padx=(0, 5))
        
        label = ctk.CTkLabel(
            frame, 
            text=text, 
            font=ThemeManager.get_small_font()
        )
        label.grid(row=0, column=1)
        
        return frame
    
    def update_values(self, protein, carbs, fat):
        """Update the chart with new values"""
        self.protein = protein
        self.carbs = carbs
        self.fat = fat
        
        # Update segments
        self.protein_fill.place(relwidth=self.protein/100)
        self.carbs_fill.place(relx=self.protein/100, relwidth=self.carbs/100)
        self.fat_fill.place(relx=(self.protein + self.carbs)/100, relwidth=self.fat/100)
        
        # Update legend
        self.protein_legend.winfo_children()[1].configure(text=f"Protein: {self.protein}%")
        self.carbs_legend.winfo_children()[1].configure(text=f"Carbs: {self.carbs}%")
        self.fat_legend.winfo_children()[1].configure(text=f"Fat: {self.fat}%")

class SomatotypeVisual(ctk.CTkFrame):
    """Custom visualization for the user's somatotype"""
    
    def __init__(self, parent, ectomorph=33, mesomorph=33, endomorph=34):
        super().__init__(parent, fg_color="transparent")
        
        # Save the values
        self.ectomorph = ectomorph
        self.mesomorph = mesomorph
        self.endomorph = endomorph
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Title
        self.grid_rowconfigure(1, weight=1)  # Content
        
        # Chart title
        self.chart_title = ctk.CTkLabel(
            self,
            text="Your Body Type Composition",
            font=ThemeManager.get_subtitle_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        self.chart_title.grid(row=0, column=0, pady=(0, 15))
        
        # Somatotype visualization
        self.soma_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.soma_frame.grid(row=1, column=0)
        self.soma_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Ectomorph
        self.ectomorph_frame = self._create_soma_item(
            self.soma_frame,
            "Ectomorph",
            self.ectomorph,
            "Lean & tall body type\nFast metabolism\nDifficult to gain weight",
            0
        )
        
        # Mesomorph
        self.mesomorph_frame = self._create_soma_item(
            self.soma_frame,
            "Mesomorph",
            self.mesomorph,
            "Athletic & muscular body\nResponds quickly to exercise\nGains/loses weight easily",
            1
        )
        
        # Endomorph
        self.endomorph_frame = self._create_soma_item(
            self.soma_frame,
            "Endomorph",
            self.endomorph,
            "Soft & round body type\nSlower metabolism\nGains weight more easily",
            2
        )
    
    def _create_soma_item(self, parent, title, percentage, description, column):
        """Create a somatotype visualization item"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=column, padx=10, pady=5)
        
        # Circle with percentage
        circle_size = 90
        circle_frame = ctk.CTkFrame(
            frame,
            width=circle_size,
            height=circle_size,
            corner_radius=circle_size//2,
            fg_color=ThemeManager.BG_COLOR,
            border_width=3,
            border_color=ThemeManager.PRIMARY_COLOR
        )
        circle_frame.pack(pady=5)
        circle_frame.grid_propagate(False)
        
        # Percentage label inside circle
        percentage_label = ctk.CTkLabel(
            circle_frame,
            text=f"{percentage}%",
            font=ThemeManager.get_title_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        percentage_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.GRAY_DARK
        )
        title_label.pack(pady=(5, 0))
        
        # Description
        desc_label = ctk.CTkLabel(
            frame,
            text=description,
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.GRAY_MEDIUM,
            justify="center",
            wraplength=150
        )
        desc_label.pack(pady=(5, 0))
        
        return frame
    
    def update_values(self, ectomorph, mesomorph, endomorph):
        """Update the visualization with new values"""
        self.ectomorph = ectomorph
        self.mesomorph = mesomorph
        self.endomorph = endomorph
        
        # Update labels
        self.ectomorph_frame.winfo_children()[0].winfo_children()[0].configure(text=f"{self.ectomorph}%")
        self.mesomorph_frame.winfo_children()[0].winfo_children()[0].configure(text=f"{self.mesomorph}%")
        self.endomorph_frame.winfo_children()[0].winfo_children()[0].configure(text=f"{self.endomorph}%")

class CalorieInfoCard(ctk.CTkFrame):
    """Card showing calorie information"""
    
    def __init__(self, parent, calorie_intake=2000, goal="Maintain Weight"):
        super().__init__(parent, corner_radius=10, fg_color=ThemeManager.get_card_fg_color())
        
        # Save values
        self.calorie_intake = calorie_intake
        self.goal = goal
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        self.header = ctk.CTkLabel(
            self,
            text="Daily Caloric Target",
            font=ThemeManager.get_subtitle_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        self.header.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        
        # Calorie display
        self.calorie_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.calorie_frame.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        
        self.calorie_value = ctk.CTkLabel(
            self.calorie_frame,
            text=f"{self.calorie_intake}",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        self.calorie_value.pack(side="left")
        
        self.calorie_unit = ctk.CTkLabel(
            self.calorie_frame,
            text="calories",
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.GRAY_DARK
        )
        self.calorie_unit.pack(side="left", padx=(5, 0), pady=(8, 0))
        
        # Goal
        self.goal_label = ctk.CTkLabel(
            self,
            text=f"Goal: {self.goal}",
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.GRAY_MEDIUM
        )
        self.goal_label.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="w")
    
    def update_values(self, calorie_intake, goal):
        """Update with new values"""
        self.calorie_intake = calorie_intake
        self.goal = goal
        
        self.calorie_value.configure(text=f"{self.calorie_intake}")
        self.goal_label.configure(text=f"Goal: {self.goal}")

class FoodRecommendationCard(ctk.CTkFrame):
    """Card showing recommended foods"""
    
    def __init__(self, parent, foods=None, category="Recommended"):
        super().__init__(parent, corner_radius=10, fg_color=ThemeManager.get_card_fg_color())
        
        if foods is None:
            foods = ["Loading..."]
            
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # Make the food list expandable
        
        # Header
        self.header = ctk.CTkLabel(
            self,
            text=f"{category} Foods",
            font=ThemeManager.get_subtitle_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        self.header.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")
        
        # Scrollable food list
        self.food_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=ThemeManager.BG_COLOR,
            corner_radius=5
        )
        self.food_scroll.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        self.food_scroll.grid_columnconfigure(0, weight=1)
        
        # Add foods
        self.foods = foods
        self.food_labels = []
        self.update_foods(foods)
    
    def update_foods(self, foods):
        """Update the list of foods"""
        # Clear existing food labels
        for label in self.food_labels:
            label.destroy()
        
        self.food_labels = []
        self.foods = foods
        
        # Add food items
        for i, food in enumerate(foods):
            food_item = ctk.CTkFrame(self.food_scroll, fg_color="transparent")
            food_item.grid(row=i, column=0, sticky="ew", pady=2)
            food_item.grid_columnconfigure(1, weight=1)
            
            bullet = ctk.CTkLabel(
                food_item,
                text="•",
                font=ThemeManager.get_label_font(),
                text_color=ThemeManager.PRIMARY_COLOR
            )
            bullet.grid(row=0, column=0, padx=(0, 5))
            
            food_label = ctk.CTkLabel(
                food_item,
                text=food.strip(),
                font=ThemeManager.get_small_font(),
                anchor="w",
                justify="left"
            )
            food_label.grid(row=0, column=1, sticky="w")
            
            self.food_labels.append(food_item)

class DietPage(ctk.CTkFrame):
    """Page showing personalized diet recommendations and somatotype analysis"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=ThemeManager.BG_COLOR)
        self.controller = controller
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Content
        self.grid_rowconfigure(2, weight=0)  # Footer
        
        # Header with title and subtitle
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(20, 0), padx=20)
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        # Title with emoji
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Your Personalized Diet Plan",
            font=ThemeManager.get_title_font()
        )
        self.title_label.grid(row=0, column=0)
        
        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Based on your body measurements and somatotype analysis",
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.GRAY_DARK
        )
        self.subtitle_label.grid(row=1, column=0, pady=(5, 0))
        
        # Main content area with scrollable container
        self.content_scroll = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            scrollbar_button_color=ThemeManager.PRIMARY_COLOR,
            scrollbar_button_hover_color=ThemeManager.PRIMARY_COLOR_HOVER
        )
        self.content_scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.content_scroll.grid_columnconfigure(0, weight=1)  # Left column
        self.content_scroll.grid_columnconfigure(1, weight=1)  # Right column
        
        # Top row: User summary and Calorie information
        self.user_summary_frame = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        self.user_summary_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        self.user_summary_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # User summary (filled later when data is loaded)
        self.user_info = ctk.CTkLabel(
            self.user_summary_frame,
            text="Loading user data...",
            font=ThemeManager.get_subtitle_font()
        )
        self.user_info.grid(row=0, column=0, sticky="w", columnspan=2)
        
        # Body info (filled later when data is loaded)
        self.body_info = ctk.CTkLabel(
            self.user_summary_frame,
            text="",
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.GRAY_DARK
        )
        self.body_info.grid(row=1, column=0, sticky="w", columnspan=2)
        
        # Second row: Calories & Macronutrients
        self.calories_card = CalorieInfoCard(self.content_scroll)
        self.calories_card.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(0, 15))
        
        # Empty macronutrient chart container
        self.macro_frame = ctk.CTkFrame(self.content_scroll, fg_color=ThemeManager.get_card_fg_color(), corner_radius=10)
        self.macro_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 0), pady=(0, 15))
        self.macro_frame.grid_columnconfigure(0, weight=1)
        self.macro_frame.grid_rowconfigure(0, weight=1)
        
        # Macronutrient chart (initialized later)
        self.macro_chart = None
        
        # Third row: Somatotype visualization
        self.soma_frame = ctk.CTkFrame(self.content_scroll, fg_color=ThemeManager.get_card_fg_color(), corner_radius=10)
        self.soma_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(0, 15))
        self.soma_frame.grid_columnconfigure(0, weight=1)
        
        # Somatotype visualization (initialized later)
        self.soma_visual = None
        
        # Fourth row: Recommended foods
        self.recommended_foods = FoodRecommendationCard(
            self.content_scroll,
            category="Recommended"
        )
        self.recommended_foods.grid(row=3, column=0, sticky="nsew", padx=(0, 10), pady=(0, 15))
        
        # self.avoid_foods = FoodRecommendationCard(
        #     self.content_scroll,
        #     category="Limit or Avoid"
        # )
        # self.avoid_foods.grid(row=3, column=1, sticky="nsew", padx=(10, 0), pady=(0, 15))
        
        # Footer with navigation buttons
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.footer_frame.grid_columnconfigure(0, weight=1)
        self.footer_frame.grid_columnconfigure(1, weight=1)
        
        # Button to start over
        self.start_over_button = ThemeManager.create_secondary_button(
            self.footer_frame,
            "Start Over",
            lambda: self.controller.show_frame("LandingPage")
        )
        self.start_over_button.grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        # Button to save results
        self.save_button = ThemeManager.create_primary_button(
            self.footer_frame,
            "Save Results",
            self.save_results
        )
        self.save_button.grid(row=0, column=1, padx=(10, 0), sticky="e")
        
        # Flag to track if data is loaded
        self.data_loaded = False
        
        # Reference to state manager
        self.state_manager = controller.state_manager if hasattr(controller, 'state_manager') else None
        
    def on_show(self):
        """Called when the page is shown"""
        # Try to load data if not already loaded
        if not self.data_loaded:
            self.load_data()
    
    def load_data(self):
        """Load diet recommendation and somatotype data"""
        try:
            # Get file paths
            recommendation_path = os.path.join(OUTPUT_FILES_DIR, "output_recommendation.csv")
            classification_path = os.path.join(OUTPUT_FILES_DIR, "output_classification.csv")
            
            # Check if files exist
            if not (os.path.exists(recommendation_path) and os.path.exists(classification_path)):
                self.display_error("Output files not found. Please complete the analysis process first.")
                return
            
            # Load recommendation data
            diet_data = pd.read_csv(recommendation_path)
            
            # Load classification data
            classification_data = pd.read_csv(classification_path)
            
            # Process and display the data
            self.process_recommendation_data(diet_data)
            self.process_classification_data(classification_data)
            
            # If we have a state manager, get the user data
            if self.state_manager and hasattr(self.state_manager, 'user_data'):
                user_data = self.state_manager.user_data
                
                # Update user summary
                name = user_data.get("name", "User")
                gender = user_data.get("gender", "")
                age = user_data.get("age", "")
                goal = user_data.get("goal", "")
                
                self.user_info.configure(text=f"Diet Plan for {name}")
                self.body_info.configure(text=f"{gender.capitalize()}, {age} years old | Goal: {goal}")
                
                # Update calories card
                self.calories_card.update_values(2000, goal)  # Sample value, should come from analysis
            
            self.data_loaded = True
            
        except Exception as e:
            self.display_error(f"Error loading data: {str(e)}")
    
    def process_recommendation_data(self, data):
        """Process and display diet recommendation data"""
        try:
            # Extract macronutrient data (typically first few rows)
            # Check if data has enough rows and expected columns
            if len(data) < 3 or 'Macronutrient' not in data.columns or 'Value' not in data.columns:
                print("Recommendation data doesn't have expected structure")
                # Set default macronutrient values
                protein_val = 30
                carbs_val = 45
                fat_val = 25
            else:
                # Try to find macronutrient values
                protein_val = 30
                carbs_val = 45
                fat_val = 25
                
                try:
                    if 'Protein' in data['Macronutrient'].values:
                        protein_row = data[data['Macronutrient'] == 'Protein']
                        if not protein_row.empty and pd.notna(protein_row['Value'].iloc[0]):
                            protein_val = int(float(protein_row['Value'].iloc[0]))
                except Exception as e:
                    print(f"Error extracting protein value: {str(e)}")
                
                try:
                    if 'Carbohydrates' in data['Macronutrient'].values:
                        carbs_row = data[data['Macronutrient'] == 'Carbohydrates']
                        if not carbs_row.empty and pd.notna(carbs_row['Value'].iloc[0]):
                            carbs_val = int(float(carbs_row['Value'].iloc[0]))
                except Exception as e:
                    print(f"Error extracting carbohydrates value: {str(e)}")
                
                try:
                    if 'Fat' in data['Macronutrient'].values:
                        fat_row = data[data['Macronutrient'] == 'Fat']
                        if not fat_row.empty and pd.notna(fat_row['Value'].iloc[0]):
                            fat_val = int(float(fat_row['Value'].iloc[0]))
                except Exception as e:
                    print(f"Error extracting fat value: {str(e)}")
            
            # Create and place the macronutrient chart 
            self.macro_chart = MacronutrientChart(
                self.macro_frame, 
                protein=protein_val, 
                carbs=carbs_val, 
                fat=fat_val
            )
            self.macro_chart.pack(fill="both", expand=True, padx=15, pady=15)
            
            # Extract food recommendations (subsequent rows)
            try:
                # Try to find recommended foods
                recommended_foods = []
                avoid_foods = []
                foods_section = "recommended"
                
                # Check if data has enough rows for food recommendations
                if len(data) > 4:
                    for i in range(4, len(data)):
                        if i < len(data) and len(data.iloc[i]) > 0:
                            food_item = str(data.iloc[i, 0]).strip() if pd.notna(data.iloc[i, 0]) else ""
                            
                            if food_item.lower() == "foods to avoid:" or "avoid" in food_item.lower():
                                foods_section = "avoid"
                                continue
                                
                            if food_item and not pd.isna(food_item) and food_item != "nan":
                                if foods_section == "recommended":
                                    recommended_foods.append(food_item)
                                else:
                                    avoid_foods.append(food_item)
                
                # Update food recommendation cards
                if recommended_foods:
                    self.recommended_foods.update_foods(recommended_foods)
                # if avoid_foods:
                #     self.avoid_foods.update_foods(avoid_foods)
                # else:
                #     self.avoid_foods.update_foods(["No specific foods to avoid"])
                
            except Exception as e:
                print(f"Error extracting food recommendations: {str(e)}")
                # Still show empty food cards if this part fails
                self.recommended_foods.update_foods(["Lean protein", "Whole grains", "Fresh fruits", "Vegetables", "Healthy fats"])
                self.avoid_foods.update_foods(["Processed foods", "Sugary drinks", "Excessive sodium", "Trans fats"])
            
        except Exception as e:
            print(f"Error processing recommendation data: {str(e)}")
            self.display_error(f"Error processing recommendation data")
    
    def process_classification_data(self, data):
        """Process and display somatotype classification data"""
        try:
            # Default values in case parsing fails
            endo_val = 33
            meso_val = 33
            ecto_val = 34
            
            if not data.empty:
                try:
                    # Try to find a row containing somatotype information
                    for i, row in data.iterrows():
                        for col in row.index:
                            cell_value = str(row[col]).lower()
                            if 'endomorph' in cell_value or 'ectomorph' in cell_value or 'mesomorph' in cell_value:
                                # Extract percentages using regex
                                import re
                                endo_match = re.search(r'endomorph:?\s*(\d+)%?', cell_value, re.IGNORECASE)
                                meso_match = re.search(r'mesomorph:?\s*(\d+)%?', cell_value, re.IGNORECASE)
                                ecto_match = re.search(r'ectomorph:?\s*(\d+)%?', cell_value, re.IGNORECASE)
                                
                                if endo_match:
                                    endo_val = int(endo_match.group(1))
                                if meso_match:
                                    meso_val = int(meso_match.group(1))
                                if ecto_match:
                                    ecto_val = int(ecto_match.group(1))
                                
                                break
                
                except Exception as e:
                    print(f"Error parsing somatotype percentages: {str(e)}")
                    
                    # Try alternative approach - direct column access if specific columns exist
                    try:
                        if 'Endomorph' in data.columns and 'Mesomorph' in data.columns and 'Ectomorph' in data.columns:
                            # Get the first row values
                            endo_val = int(float(data['Endomorph'].iloc[0]))
                            meso_val = int(float(data['Mesomorph'].iloc[0]))
                            ecto_val = int(float(data['Ectomorph'].iloc[0]))
                    except Exception as e2:
                        print(f"Error accessing somatotype columns: {str(e2)}")
            
            # Create and place the somatotype visualization
            self.soma_visual = SomatotypeVisual(
                self.soma_frame,
                ectomorph=ecto_val,
                mesomorph=meso_val,
                endomorph=endo_val
            )
            self.soma_visual.pack(fill="both", expand=True, padx=15, pady=15)
            
        except Exception as e:
            print(f"Error processing classification data: {str(e)}")
            
            # Create default somatotype visualization
            self.soma_visual = SomatotypeVisual(self.soma_frame)
            self.soma_visual.pack(fill="both", expand=True, padx=15, pady=15)
    
    def display_error(self, message):
        """Display an error message"""
        error_frame = ctk.CTkFrame(
            self.content_scroll,
            fg_color=ThemeManager.DANGER_COLOR,  # Light red with transparency
            corner_radius=10,
            border_width=1,
            border_color=ThemeManager.DANGER_COLOR
        )
        error_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=20)
        
        error_label = ctk.CTkLabel(
            error_frame,
            text=f"⚠️ {message}",
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.DANGER_COLOR
        )
        error_label.pack(padx=20, pady=20)
        
        # Add suggestion
        suggestion_label = ctk.CTkLabel(
            error_frame,
            text="Return to the capture page and try again.",
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.GRAY_DARK
        )
        suggestion_label.pack(pady=(0, 20))
        
        # Add "Go to Capture" button
        capture_button = ThemeManager.create_primary_button(
            error_frame,
            "Return to Capture",
            lambda: self.controller.show_frame("CapturePage")
        )
        capture_button.pack(pady=(0, 20))
    
    def save_results(self):
        """Save the results to PDF or similar format"""
        # This would be implemented with a PDF generation library in a complete implementation
        message_frame = ctk.CTkToplevel(self)
        message_frame.title("Save Results")
        message_frame.geometry("400x200")
        message_frame.resizable(False, False)
        
        message_label = ctk.CTkLabel(
            message_frame,
            text="This feature will allow you to save\nyour diet plan as a PDF file.\n\nCurrently, this feature is not implemented.",
            font=ThemeManager.get_label_font()
        )
        message_label.pack(expand=True)
        
        ok_button = ThemeManager.create_primary_button(
            message_frame,
            "OK",
            message_frame.destroy
        )
        ok_button.pack(pady=20)

if __name__ == "__main__":
    # For standalone testing
    class DummyController:
        def show_frame(self, frame_name):
            print(f"Switching to frame: {frame_name}")
            
        class StateManager:
            def __init__(self):
                self.user_data = {
                    "name": "John Doe",
                    "gender": "male",
                    "age": "32",
                    "weight": "75",
                    "height": "178",
                    "goal": "Maintain Weight"
                }
    
    controller = DummyController()
    controller.state_manager = controller.StateManager()
    
    # Create and run app
    root = ctk.CTk()
    root.title("Diet Page Test")
    root.geometry("1000x700")
    ThemeManager.setup_theme()
    
    app = DietPage(root, controller)
    app.pack(fill="both", expand=True)
    app.on_show()
    
    root.mainloop()