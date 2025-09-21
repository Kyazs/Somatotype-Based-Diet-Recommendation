"""
Diet Page for the Diet Recommendation System.
Shows detailed view of the most recent analysis with diet recommendations.
Based on the history_detail_page.py design but loads the latest data automatically.
"""
import customtkinter as ctk
import pandas as pd
import os
import sys
from PIL import Image, ImageTk
import json
import time
import traceback
from datetime import datetime

# Configuration
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(PROJECT_DIR)

from src.utils.theme_manager import ThemeManager
from src.utils.database import DatabaseManager


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


class FoodCard(ctk.CTkFrame):
    """Enhanced food card with proper styling and click interaction"""
    
    def __init__(self, parent, food_data, on_click_callback=None):
        super().__init__(parent, fg_color=ThemeManager.get_card_fg_color(), corner_radius=8, border_width=1, border_color=ThemeManager.GRAY_LIGHT)
        
        self.food_data = food_data
        self.on_click_callback = on_click_callback
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Food name
        self.grid_rowconfigure(1, weight=0)  # Quick info
        self.grid_rowconfigure(2, weight=1)  # Spacer
        
        # Extract food information
        if isinstance(food_data, dict):
            self.food_name = food_data.get('Food_Item', 'Unknown Food')
            self.calories = food_data.get('Calories_kcal', 0)
            self.protein = food_data.get('Protein_g', 0)
            self.portion = food_data.get('Portion_Recommendation', 'N/A')
        else:
            self.food_name = str(food_data)
            self.calories = 0
            self.protein = 0
            self.portion = 'N/A'
        
        # Food name (truncated if too long)
        display_name = self.food_name
        if len(display_name) > 25:
            display_name = display_name[:22] + "..."
            
        self.name_label = ctk.CTkLabel(
            self,
            text=display_name,
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.GRAY_DARK,
            wraplength=180,
            justify="center"
        )
        self.name_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        
        # Quick nutritional info
        if isinstance(food_data, dict) and self.calories > 0:
            info_text = f"{int(self.calories)} kcal • {self.protein:.1f}g protein"
            if self.portion and self.portion != 'N/A':
                info_text += f"\nServing: {self.portion}"
        else:
            info_text = "Click for details"
            
        self.info_label = ctk.CTkLabel(
            self,
            text=info_text,
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.GRAY_MEDIUM,
            justify="center"
        )
        self.info_label.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        # Make the entire card clickable
        self.bind("<Button-1>", self._on_click)
        self.name_label.bind("<Button-1>", self._on_click)
        self.info_label.bind("<Button-1>", self._on_click)
        
        # Hover effects
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.name_label.bind("<Enter>", self._on_enter)
        self.name_label.bind("<Leave>", self._on_leave)
        self.info_label.bind("<Enter>", self._on_enter)
        self.info_label.bind("<Leave>", self._on_leave)
        
    def _on_click(self, event):
        """Handle card click"""
        if self.on_click_callback:
            self.on_click_callback(self.food_data)
            
    def _on_enter(self, event):
        """Handle mouse enter - hover effect"""
        self.configure(border_color=ThemeManager.PRIMARY_COLOR, border_width=2)
        
    def _on_leave(self, event):
        """Handle mouse leave - remove hover effect"""
        self.configure(border_color=ThemeManager.GRAY_LIGHT, border_width=1)


class MealCategoryCard(ctk.CTkFrame):
    """Card container for a specific meal category (breakfast, lunch, etc.)"""
    
    def __init__(self, parent, meal_type, foods, on_food_click=None):
        super().__init__(parent, fg_color="transparent")
        
        self.meal_type = meal_type
        self.foods = foods
        self.on_food_click = on_food_click
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Food cards
        
        # Meal category header
        meal_icons = {
            'breakfast': '🌅',
            'lunch': '🌞', 
            'dinner': '🌙',
            'snack': '🍎'
        }
        icon = meal_icons.get(meal_type.lower(), '🍽️')
        
        self.header = ctk.CTkLabel(
            self,
            text=f"{icon} {meal_type.title()}",
            font=ThemeManager.get_subtitle_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        self.header.grid(row=0, column=0, padx=10, pady=(0, 10), sticky="w")
        
        # Food cards container with scrolling
        self.cards_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            height=280,
            corner_radius=0,
            scrollbar_button_color=ThemeManager.GRAY_LIGHT,
            scrollbar_button_hover_color=ThemeManager.GRAY_MEDIUM
        )
        self.cards_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        
        # Configure cards grid
        for i in range(3):  # 3 columns of cards
            self.cards_frame.grid_columnconfigure(i, weight=1)
            
        # Create food cards
        self._create_food_cards()
        
    def _create_food_cards(self):
        """Create individual food cards"""
        if not self.foods:
            # No foods message
            no_foods_label = ctk.CTkLabel(
                self.cards_frame,
                text="No recommendations available",
                font=ThemeManager.get_small_font(),
                text_color=ThemeManager.GRAY_MEDIUM
            )
            no_foods_label.grid(row=0, column=0, columnspan=3, pady=20)
            return
            
        # Create cards in a grid (3 columns)
        foods_to_show = self.foods[:9] if isinstance(self.foods, list) else [self.foods]  # Show up to 9 foods
        
        for i, food_data in enumerate(foods_to_show):
            row = i // 3
            col = i % 3
            
            food_card = FoodCard(
                self.cards_frame,
                food_data,
                on_click_callback=self.on_food_click
            )
            food_card.grid(row=row, column=col, padx=5, pady=5, sticky="ew")


class MacronutrientDetailModal(ctk.CTkToplevel):
    """Enhanced modal to show detailed food information with better error handling"""
    
    def __init__(self, parent, food_data):
        super().__init__(parent)
        
        self.food_data = food_data
        
        # Setup window safely
        self.setup_window_safely()
        
        # Create content
        self.create_content()
        
        # Center the window and show it
        self.after(100, self.finalize_window)
        
    def setup_window_safely(self):
        """Setup window with comprehensive error handling"""
        try:
            # Basic window configuration
            food_name = "Food Details"
            if isinstance(self.food_data, dict):
                food_name = self.food_data.get('Food_Item', 'Food Details')
                if len(food_name) > 40:
                    food_name = food_name[:37] + "..."
                    
            self.title(f"📊 {food_name}")
            self.geometry("500x700")
            self.resizable(False, False)
            
            # Set window properties safely
            self.transient(self.master)
            
        except Exception as e:
            print(f"Error setting up modal window: {e}")
            
    def create_content(self):
        """Create the modal content"""
        try:
            # Configure main grid
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0, weight=1)
            self.grid_rowconfigure(1, weight=0)
            
            # Main content with scrolling
            self.content_frame = ctk.CTkScrollableFrame(
                self,
                fg_color="transparent",
                corner_radius=0
            )
            self.content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
            self.content_frame.grid_columnconfigure(0, weight=1)
            
            # Extract food data safely
            if isinstance(self.food_data, dict):
                self._create_detailed_view()
            else:
                self._create_simple_view()
                
            # Close button
            self.close_button = ctk.CTkButton(
                self,
                text="Close",
                font=ThemeManager.get_label_font(),
                command=self.destroy_safely,
                width=100,
                height=35
            )
            self.close_button.grid(row=1, column=0, pady=(0, 20))
            
        except Exception as e:
            print(f"Error creating modal content: {e}")
            self._create_error_view(str(e))
            
    def _create_detailed_view(self):
        """Create detailed food information view"""
        # Food name header
        food_name = self.food_data.get('Food_Item', 'Unknown Food')
        self.name_header = ctk.CTkLabel(
            self.content_frame,
            text=food_name,
            font=ThemeManager.get_title_font(),
            text_color=ThemeManager.PRIMARY_COLOR,
            wraplength=450,
            justify="center"
        )
        self.name_header.grid(row=0, column=0, pady=(0, 20))
        
        # Main nutritional info card
        nutrition_card = ctk.CTkFrame(self.content_frame, fg_color=ThemeManager.get_card_fg_color(), corner_radius=10)
        nutrition_card.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        nutrition_card.grid_columnconfigure((0, 1), weight=1)
        
        # Calories
        calories = self.food_data.get('Calories_kcal', 0)
        self._add_info_item(nutrition_card, "🔥 Calories", f"{calories:.0f} kcal", 0, 0)
        
        # Portion
        portion = self.food_data.get('Portion_Recommendation', 'N/A')
        self._add_info_item(nutrition_card, "🍽️ Serving Size", portion, 0, 1)
        
        # Macronutrients card
        macro_card = ctk.CTkFrame(self.content_frame, fg_color=ThemeManager.get_card_fg_color(), corner_radius=10)
        macro_card.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        macro_card.grid_columnconfigure((0, 1), weight=1)
        
        # Protein
        protein = self.food_data.get('Protein_g', 0)
        self._add_info_item(macro_card, "🥩 Protein", f"{protein:.1f}g", 0, 0)
        
        # Carbohydrates
        carbs = self.food_data.get('Carbohydrates_g', 0)
        self._add_info_item(macro_card, "🌾 Carbs", f"{carbs:.1f}g", 0, 1)
        
        # Fat
        fat = self.food_data.get('Fat_g', 0)
        self._add_info_item(macro_card, "🥑 Fat", f"{fat:.1f}g", 1, 0)
        
        # Fiber
        fiber = self.food_data.get('Fiber_g', 0)
        self._add_info_item(macro_card, "🌿 Fiber", f"{fiber:.1f}g", 1, 1)
        
        # Additional info card
        if any(self.food_data.get(key, 0) for key in ['Sugars_g', 'Sodium_mg', 'Cholesterol_mg']):
            additional_card = ctk.CTkFrame(self.content_frame, fg_color=ThemeManager.get_card_fg_color(), corner_radius=10)
            additional_card.grid(row=3, column=0, sticky="ew", pady=(0, 15))
            additional_card.grid_columnconfigure((0, 1), weight=1)
            
            # Sugar
            sugars = self.food_data.get('Sugars_g', 0)
            if sugars > 0:
                self._add_info_item(additional_card, "🍯 Sugars", f"{sugars:.1f}g", 0, 0)
                
            # Sodium
            sodium = self.food_data.get('Sodium_mg', 0)
            if sodium > 0:
                self._add_info_item(additional_card, "🧂 Sodium", f"{sodium:.0f}mg", 0, 1)
                
            # Cholesterol
            cholesterol = self.food_data.get('Cholesterol_mg', 0)
            if cholesterol > 0:
                self._add_info_item(additional_card, "💊 Cholesterol", f"{cholesterol:.0f}mg", 1, 0)
        
        # Somatotype scores card
        if any(self.food_data.get(f'{soma}_Score', 0) for soma in ['Ectomorph', 'Mesomorph', 'Endomorph']):
            soma_card = ctk.CTkFrame(self.content_frame, fg_color=ThemeManager.get_card_fg_color(), corner_radius=10)
            soma_card.grid(row=4, column=0, sticky="ew", pady=(0, 15))
            soma_card.grid_columnconfigure(0, weight=1)
            
            soma_header = ctk.CTkLabel(
                soma_card,
                text="🎯 Body Type Compatibility",
                font=ThemeManager.get_subtitle_font(),
                text_color=ThemeManager.PRIMARY_COLOR
            )
            soma_header.grid(row=0, column=0, padx=15, pady=(15, 10))
            
            # Scores grid
            scores_frame = ctk.CTkFrame(soma_card, fg_color="transparent")
            scores_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
            scores_frame.grid_columnconfigure((0, 1, 2), weight=1)
            
            soma_types = ['Ectomorph', 'Mesomorph', 'Endomorph']
            soma_icons = ['🏃', '💪', '🏋️']
            
            for i, (soma_type, icon) in enumerate(zip(soma_types, soma_icons)):
                score = self.food_data.get(f'{soma_type}_Score', 0)
                score_text = f"{icon} {soma_type}\n{score}/10"
                
                score_label = ctk.CTkLabel(
                    scores_frame,
                    text=score_text,
                    font=ThemeManager.get_small_font(),
                    text_color=ThemeManager.GRAY_DARK,
                    justify="center"
                )
                score_label.grid(row=0, column=i, padx=5, pady=5)
                
    def _create_simple_view(self):
        """Create simple view for string-based food data"""
        food_name = str(self.food_data)
        
        self.name_header = ctk.CTkLabel(
            self.content_frame,
            text=food_name,
            font=ThemeManager.get_title_font(),
            text_color=ThemeManager.PRIMARY_COLOR,
            wraplength=450,
            justify="center"
        )
        self.name_header.grid(row=0, column=0, pady=(0, 20))
        
        info_label = ctk.CTkLabel(
            self.content_frame,
            text="Detailed nutritional information is not available for this food item.",
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.GRAY_MEDIUM,
            wraplength=400,
            justify="center"
        )
        info_label.grid(row=1, column=0, pady=20)
        
    def _create_error_view(self, error_message):
        """Create error view when content creation fails"""
        error_label = ctk.CTkLabel(
            self,
            text=f"Error loading food details:\n{error_message}",
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.WARNING_COLOR,
            wraplength=400,
            justify="center"
        )
        error_label.grid(row=0, column=0, padx=20, pady=20)
        
    def _add_info_item(self, parent, label, value, row, column):
        """Add an information item to the parent frame"""
        info_frame = ctk.CTkFrame(parent, fg_color="transparent")
        info_frame.grid(row=row, column=column, padx=10, pady=8, sticky="ew")
        
        label_widget = ctk.CTkLabel(
            info_frame,
            text=label,
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.GRAY_MEDIUM
        )
        label_widget.pack()
        
        value_widget = ctk.CTkLabel(
            info_frame,
            text=value,
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.GRAY_DARK
        )
        value_widget.pack()
        
    def finalize_window(self):
        """Final window setup with error handling"""
        try:
            # Center the window
            self.update_idletasks()
            x = (self.winfo_screenwidth() // 2) - (500 // 2)
            y = (self.winfo_screenheight() // 2) - (700 // 2)
            self.geometry(f"500x700+{x}+{y}")
            
            # Set focus and grab
            self.lift()
            self.focus_set()
            
            # Delayed grab to prevent handle issues
            self.after(200, self.safe_grab_set)
            
        except Exception as e:
            print(f"Error finalizing modal window: {e}")
            
    def safe_grab_set(self):
        """Safely set modal grab"""
        try:
            if self.winfo_exists():
                self.grab_set()
        except Exception as e:
            print(f"Error setting grab: {e}")
            
    def destroy_safely(self):
        """Safely destroy the modal"""
        try:
            if self.winfo_exists():
                self.grab_release()
                self.destroy()
        except Exception as e:
            print(f"Error destroying modal: {e}")


class MealBasedFoodRecommendations(ctk.CTkFrame):
    """Enhanced component showing food recommendations as interactive cards organized by meal type"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="🍽️ Personalized Food Recommendations",
            font=ThemeManager.get_title_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        self.title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Content frame for meal categories
        self.content_frame = ctk.CTkFrame(self, fg_color=ThemeManager.get_card_fg_color(), corner_radius=10)
        self.content_frame.grid(row=1, column=0, sticky="ew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Placeholder text
        self.placeholder_label = ctk.CTkLabel(
            self.content_frame,
            text="Loading meal recommendations...",
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.GRAY_MEDIUM
        )
        self.placeholder_label.grid(row=0, column=0, padx=20, pady=20)
    
    def update_recommendations(self, meal_recommendations):
        """Update all meal recommendations with enhanced card layout"""
        try:
            # Clear existing content
            for widget in self.content_frame.winfo_children():
                widget.destroy()
            
            if not meal_recommendations:
                # No recommendations message
                no_recs_label = ctk.CTkLabel(
                    self.content_frame,
                    text="No meal recommendations available",
                    font=ThemeManager.get_label_font(),
                    text_color=ThemeManager.GRAY_MEDIUM
                )
                no_recs_label.grid(row=0, column=0, padx=20, pady=20)
                return
            
            # Create meal category cards
            row = 0
            for meal_type, foods in meal_recommendations.items():
                if not foods or (isinstance(foods, list) and len(foods) == 0):
                    continue
                    
                # Create meal category card
                meal_card = MealCategoryCard(
                    self.content_frame,
                    meal_type,
                    foods,
                    on_food_click=self._show_food_details
                )
                meal_card.grid(row=row, column=0, sticky="ew", padx=15, pady=(0, 20))
                self.content_frame.grid_rowconfigure(row, weight=0)
                row += 1
                
        except Exception as e:
            print(f"Error updating meal recommendations: {e}")
            error_label = ctk.CTkLabel(
                self.content_frame,
                text="Error loading meal recommendations",
                font=ThemeManager.get_label_font(),
                text_color=ThemeManager.GRAY_MEDIUM
            )
            error_label.grid(row=0, column=0, padx=20, pady=20)
            
    def _show_food_details(self, food_data):
        """Show detailed food information in a modal"""
        try:
            modal = MacronutrientDetailModal(self, food_data)
        except Exception as e:
            print(f"Error showing food details: {e}")
            # Show a simple error message instead
            error_window = ctk.CTkToplevel(self)
            error_window.title("Error")
            error_window.geometry("300x150")
            error_window.transient(self)
            
            error_label = ctk.CTkLabel(
                error_window,
                text="Could not load food details",
                font=ThemeManager.get_label_font()
            )
            error_label.pack(expand=True)
            
            close_btn = ctk.CTkButton(
                error_window,
                text="Close",
                command=error_window.destroy
            )
            close_btn.pack(pady=10)


class DietPage(ctk.CTkFrame):
    """Page showing detailed view of the most recent analysis results"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=ThemeManager.BG_COLOR)
        self.controller = controller
        self.current_record = None
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        
        # Performance optimization flags
        self._content_loaded = False
        
        # Initialize basic layout immediately for fast load
        self._init_basic_layout()
        
    def _init_basic_layout(self):
        """Initialize basic layout structure quickly"""
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
    def load_content(self):
        """Load the actual content when page is shown"""
        if self._content_loaded:
            return
            
        # Load actual content immediately - no loading indicator
        self._init_content_layout()
        self._content_loaded = True
        
    def _init_content_layout(self):
        """Initialize the full content layout"""
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Content
        self.grid_rowconfigure(2, weight=0)  # Footer
        
        # Header with title and navigation
        self._create_header()
        
        # Main content area with scrollable container
        self._create_content_area()
        
        # Footer with action buttons
        self._create_footer()
        
    def _create_header(self):
        """Create page header with navigation and title"""
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(20, 0), padx=20)
        self.header_frame.grid_columnconfigure(1, weight=1)
        
        # Back button
        self.back_button = ctk.CTkButton(
            self.header_frame,
            text="← Back to Processing",
            font=ctk.CTkFont(size=14),
            width=140,
            height=32,
            corner_radius=16,
            fg_color="transparent",
            text_color=ThemeManager.GRAY_DARK,
            hover_color=ThemeManager.GRAY_LIGHT,
            command=self._go_back
        )
        self.back_button.grid(row=0, column=0, sticky="w")
        
        # Title section
        self.title_section = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.title_section.grid(row=0, column=1, sticky="")
        
        self.title_label = ctk.CTkLabel(
            self.title_section,
            text="Your Personalized Diet Plan",
            font=ThemeManager.get_title_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        self.title_label.grid(row=0, column=0)
        
        # Subtitle label (updated when record is loaded)
        self.subtitle_label = ctk.CTkLabel(
            self.title_section,
            text="Based on your body measurements and somatotype analysis",
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.GRAY_DARK
        )
        self.subtitle_label.grid(row=1, column=0, pady=(5, 0))
        
        # History button
        self.history_button = ctk.CTkButton(
            self.header_frame,
            text="📋 View History",
            font=ctk.CTkFont(size=14),
            width=120,
            height=32,
            corner_radius=16,
            fg_color=ThemeManager.PRIMARY_COLOR,
            hover_color=ThemeManager.PRIMARY_HOVER,
            command=self._go_to_history
        )
        self.history_button.grid(row=0, column=2, sticky="e")
        
    def _create_content_area(self):
        """Create main content area with scrollable container"""
        self.content_scroll = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            scrollbar_button_color=ThemeManager.PRIMARY_COLOR,
            scrollbar_button_hover_color=ThemeManager.PRIMARY_HOVER,
            corner_radius=0,  # Reduces rendering overhead
            border_width=0   # Reduces border redraw issues
        )
        self.content_scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.content_scroll.grid_columnconfigure(0, weight=1)  # Left column
        self.content_scroll.grid_columnconfigure(1, weight=1)  # Right column
        
        # Add scroll throttling to prevent UI distortion
        self.content_scroll.bind("<MouseWheel>", self._on_mousewheel)
        self.content_scroll.bind("<Button-4>", self._on_mousewheel)  # Linux
        self.content_scroll.bind("<Button-5>", self._on_mousewheel)  # Linux
        
        # Scroll throttling variables
        self._scroll_job = None
        self._last_scroll_time = 0
        
        # Row 0: User Summary
        self._create_user_summary()
        
        # Row 1: Calories & Macronutrients
        self._create_nutrition_section()
        
        # Row 2: Somatotype Visualization
        self._create_somatotype_section()
        
        # Row 3: Diet Recommendations
        self._create_diet_section()
        
    def _create_user_summary(self):
        """Create user summary section"""
        self.user_summary_frame = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        self.user_summary_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        self.user_summary_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # User info (filled when record is loaded)
        self.user_info = ctk.CTkLabel(
            self.user_summary_frame,
            text="Loading user data...",
            font=ThemeManager.get_subtitle_font(),
            text_color=ThemeManager.GRAY_DARK
        )
        self.user_info.grid(row=0, column=0, sticky="w", columnspan=2)
        
        # Body info (filled when record is loaded)
        self.body_info = ctk.CTkLabel(
            self.user_summary_frame,
            text="",
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.GRAY_MEDIUM
        )
        self.body_info.grid(row=1, column=0, sticky="w", columnspan=2, pady=(5, 0))
        
    def _create_nutrition_section(self):
        """Create calories and macronutrients section"""
        # Calories card
        self.calories_card = CalorieInfoCard(self.content_scroll)
        self.calories_card.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(0, 15))
        
        # Macronutrient chart container
        self.macro_frame = ctk.CTkFrame(
            self.content_scroll, 
            fg_color=ThemeManager.get_card_fg_color(), 
            corner_radius=10
        )
        self.macro_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 0), pady=(0, 15))
        self.macro_frame.grid_columnconfigure(0, weight=1)
        self.macro_frame.grid_rowconfigure(0, weight=1)
        
        # Macronutrient chart (initialized when data is loaded)
        self.macro_chart = None
        
    def _create_somatotype_section(self):
        """Create somatotype visualization section"""
        self.soma_frame = ctk.CTkFrame(
            self.content_scroll, 
            fg_color=ThemeManager.get_card_fg_color(), 
            corner_radius=10
        )
        self.soma_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(0, 15))
        self.soma_frame.grid_columnconfigure(0, weight=1)
        
        # Somatotype visualization (initialized when data is loaded)
        self.soma_visual = None
        
    def _create_diet_section(self):
        """Create diet recommendations section"""
        self.meal_recommendations = MealBasedFoodRecommendations(self.content_scroll)
        self.meal_recommendations.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(0, 15))
        
    def _create_footer(self):
        """Create footer with action buttons"""
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.footer_frame.grid_columnconfigure(1, weight=1)
        
        # New Analysis button
        self.new_analysis_button = ctk.CTkButton(
            self.footer_frame,
            text="🔄 New Analysis",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=140,
            height=44,
            corner_radius=22,
            fg_color=ThemeManager.PRIMARY_COLOR,
            hover_color=ThemeManager.PRIMARY_HOVER,
            command=self._start_new_analysis
        )
        self.new_analysis_button.grid(row=0, column=2, sticky="e")
        
    def on_show(self):
        """Called when the page is shown - implements lazy loading for performance"""
        try:
            # Check if the widget still exists (prevents handle errors)
            if not self.winfo_exists():
                return
                
            # Load content lazily when page is first shown
            self.load_content()
            
            # Load the most recent data
            self.load_latest_data()
                
        except Exception as e:
            print(f"Error in diet page on_show: {e}")
            traceback.print_exc()
            # Try to display error safely
            try:
                self._show_error(f"Failed to initialize diet page: {str(e)}")
            except Exception:
                print(f"Could not display error: {e}")
    
    def load_latest_data(self):
        """Load and display data from the most recent analysis session"""
        try:
            print(f"📊 Loading latest diet data from database...")
            
            # Get the most recent session
            history = self.db_manager.get_user_history(limit=1)
            
            if not history:
                error_msg = "No analysis data found. Please complete the analysis process first."
                print(f"❌ {error_msg}")
                self._show_error(error_msg)
                return
            
            print(f"✅ Found {len(history)} recent session(s) in database")
            
            # Get the most recent record
            most_recent_record = history[0]
            session_id = most_recent_record.get('session_id')
            
            if not session_id:
                error_msg = "Invalid session data. Please try running the analysis again."
                print(f"❌ {error_msg}")
                self._show_error(error_msg)
                return
                
            print(f"📋 Loading data for session ID: {session_id}")
            
            # Check session status
            session_status = most_recent_record.get('status', 'unknown')
            print(f"📊 Session status: {session_status}")
            
            if session_status != 'completed':
                error_msg = f"Session is not completed (status: {session_status}). Please wait for processing to finish."
                print(f"⚠️ {error_msg}")
                self._show_error(error_msg)
                return
            
            # Load and display the record data
            self.load_record_data(most_recent_record)
            
        except Exception as e:
            print(f"Error loading latest data from database: {str(e)}")
            traceback.print_exc()
            self._show_error(f"Error loading data: {str(e)}")
    
    def load_record_data(self, record_data):
        """Load and display data from a history record"""
        try:
            self.current_record = record_data
            
            # Update user summary
            name = record_data.get('name', 'Unknown User')
            gender = record_data.get('gender', 'Unknown')
            age = record_data.get('age', 'N/A')
            goal = record_data.get('goal', 'Not specified')
            
            self.user_info.configure(text=f"Diet Plan for {name}")
            self.body_info.configure(text=f"{gender.title()}, {age} years old | Goal: {goal}")
            
            # Load nutrition data
            self._load_nutrition_data(record_data)
            
            # Load somatotype data
            self._load_somatotype_data(record_data)
            
            # Load diet recommendations
            self._load_diet_recommendations(record_data)
            
        except Exception as e:
            print(f"Error loading record data: {e}")
            traceback.print_exc()
            
    def _load_nutrition_data(self, record_data):
        """Load and display nutrition data"""
        try:
            # Update calories card
            calories = record_data.get('calories', 2000)
            goal = record_data.get('goal', 'Maintain Weight')
            self.calories_card.update_values(calories, goal)
            
            # Load macronutrient data from database
            session_id = record_data.get('session_id')
            if session_id:
                # Get diet recommendations for macronutrient breakdown
                diet_data = self.db_manager.get_diet_recommendations(session_id)
                
                if diet_data:
                    # Parse nutrition data (assuming it's stored as JSON or structured data)
                    nutrition_data = diet_data.get('nutrition_data', {})
                    
                    # Extract macronutrient percentages
                    protein_pct = int(nutrition_data.get('protein_percentage', 30))
                    carbs_pct = int(nutrition_data.get('carbs_percentage', 45))
                    fat_pct = int(nutrition_data.get('fat_percentage', 25))
                    
                    # Create or update macronutrient chart
                    if self.macro_chart:
                        self.macro_chart.destroy()
                        
                    self.macro_chart = MacronutrientChart(
                        self.macro_frame,
                        protein=protein_pct,
                        carbs=carbs_pct,
                        fat=fat_pct
                    )
                    self.macro_chart.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
                    
        except Exception as e:
            print(f"Error loading nutrition data: {e}")
            # Create default macronutrient chart
            if self.macro_chart:
                self.macro_chart.destroy()
                
            self.macro_chart = MacronutrientChart(self.macro_frame)
            self.macro_chart.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
            
    def _load_somatotype_data(self, record_data):
        """Load and display somatotype data"""
        try:
            session_id = record_data.get('session_id')
            if session_id:
                # Get somatotype classification from database
                soma_data = self.db_manager.get_somatotype_classification(session_id)
                
                if soma_data:
                    ectomorph = float(soma_data.get('ectomorph_score', 33.3))
                    mesomorph = float(soma_data.get('mesomorph_score', 33.3))
                    endomorph = float(soma_data.get('endomorph_score', 33.3))
                    
                    # Create or update somatotype visualization
                    if self.soma_visual:
                        self.soma_visual.destroy()
                        
                    self.soma_visual = SomatotypeVisual(
                        self.soma_frame,
                        ectomorph=ectomorph,
                        mesomorph=mesomorph,
                        endomorph=endomorph
                    )
                    self.soma_visual.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
                    
        except Exception as e:
            print(f"Error loading somatotype data: {e}")
            # Create default somatotype visualization
            if self.soma_visual:
                self.soma_visual.destroy()
                
            self.soma_visual = SomatotypeVisual(self.soma_frame)
            self.soma_visual.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
            
    def _load_diet_recommendations(self, record_data):
        """Load and display diet recommendations"""
        try:
            session_id = record_data.get('session_id')
            if session_id:
                # Get diet recommendations from database
                diet_data = self.db_manager.get_diet_recommendations(session_id)
                
                if diet_data and 'meal_recommendations' in diet_data:
                    meal_data = diet_data['meal_recommendations']
                    
                    # If meal_data is a JSON string, parse it
                    if isinstance(meal_data, str):
                        try:
                            meal_data = json.loads(meal_data)
                        except json.JSONDecodeError:
                            meal_data = {}
                    
                    # Update meal recommendations
                    self.meal_recommendations.update_recommendations(meal_data)
                else:
                    # Show default/empty recommendations
                    print("No meal recommendations found in diet data")
                    # The meal recommendations component will show empty state
                    
        except Exception as e:
            print(f"Error loading diet recommendations: {e}")
            # Just print error, don't try to call non-existent method
            
    def _on_mousewheel(self, event):
        """Throttled scroll handler to prevent UI distortion"""
        import time
        
        current_time = time.time()
        
        # Cancel previous scroll job if it exists
        if self._scroll_job:
            self.after_cancel(self._scroll_job)
        
        # Only process scroll if enough time has passed (throttling)
        if current_time - self._last_scroll_time > 0.016:  # ~60fps limit
            self._last_scroll_time = current_time
            
            # Let the default scroll behavior handle it immediately
            return
        else:
            # Defer the scroll to prevent rapid updates
            self._scroll_job = self.after(16, lambda: self._deferred_scroll(event))
            return "break"  # Prevent default handling
            
    def _deferred_scroll(self, event):
        """Handle deferred scroll events"""
        try:
            # Manually scroll the content
            if event.delta:
                delta = -int(event.delta/120)  # Windows
            else:
                delta = -1 if event.num == 4 else 1  # Linux
                
            # Get current scroll position and update it smoothly
            try:
                current_pos = self.content_scroll._parent_canvas.canvasy(0)
                scroll_unit = 3  # Smaller scroll units for smoothness
                new_pos = current_pos + (delta * scroll_unit)
                
                # Apply the scroll
                bbox = self.content_scroll._parent_canvas.bbox("all")
                if bbox and bbox[3] > 0:
                    self.content_scroll._parent_canvas.yview_moveto(new_pos / bbox[3])
            except AttributeError:
                # Fallback to simple yview_scroll if _parent_canvas is not accessible
                self.content_scroll._parent_canvas.yview_scroll(delta * 3, "units")
                
        except Exception as e:
            print(f"Scroll error: {e}")
        finally:
            self._scroll_job = None
            
    def _show_error(self, message):
        """Show error message to user"""
        try:
            # Clear existing content if any
            for widget in self.content_scroll.winfo_children():
                widget.destroy()
                
            error_frame = ctk.CTkFrame(
                self.content_scroll,
                fg_color=ThemeManager.get_card_fg_color(),
                corner_radius=10,
                border_width=1,
                border_color="#EF4444"  # Red border
            )
            error_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=20, padx=20)
            error_frame.grid_columnconfigure(0, weight=1)
            
            # Error icon and message
            error_label = ctk.CTkLabel(
                error_frame,
                text=f"⚠️ {message}",
                font=ThemeManager.get_label_font(),
                text_color="#EF4444",
                justify="center",
                wraplength=400
            )
            error_label.grid(row=0, column=0, padx=20, pady=20)
            
            # Add suggestion
            suggestion_label = ctk.CTkLabel(
                error_frame,
                text="Return to the capture page and try again.",
                font=ThemeManager.get_small_font(),
                text_color=ThemeManager.GRAY_DARK
            )
            suggestion_label.grid(row=1, column=0, pady=(0, 10))
            
            # Add "Go to Capture" button
            capture_button = ctk.CTkButton(
                error_frame,
                text="Return to Capture",
                font=ThemeManager.get_label_font(),
                fg_color=ThemeManager.PRIMARY_COLOR,
                hover_color=ThemeManager.PRIMARY_HOVER,
                command=self._go_to_capture
            )
            capture_button.grid(row=2, column=0, pady=(0, 20))
            
        except Exception as e:
            print(f"Error showing error dialog: {e}")
            
    def _go_back(self):
        """Go back to processing page"""
        try:
            self.controller.show_frame("ProcessingPage")
        except Exception as e:
            print(f"Error going back: {e}")
            
    def _go_to_history(self):
        """Go to history page"""
        try:
            self.controller.show_frame("HistoryPage")
        except Exception as e:
            print(f"Error going to history: {e}")
            
    def _go_to_capture(self):
        """Go to capture page"""
        try:
            self.controller.show_frame("CapturePage")
        except Exception as e:
            print(f"Error going to capture: {e}")
            
    def _start_new_analysis(self):
        """Start a new analysis"""
        try:
            self.controller.show_frame("CapturePage")
        except Exception as e:
            print(f"Error starting new analysis: {e}")


# Test the page if run directly
if __name__ == "__main__":
    class DummyController:
        def show_frame(self, frame_name):
            print(f"Navigate to: {frame_name}")
        
        class StateManager:
            def __init__(self):
                self.user_data = {}

    controller = DummyController()
    controller.state_manager = controller.StateManager()
    
    root = ctk.CTk()
    root.title("Diet Page - Clean Design")
    root.geometry("1200x800")
    ThemeManager.setup_theme()
    
    app = DietPage(root, controller)
    app.pack(fill="both", expand=True)
    app.on_show()
    
    root.mainloop()