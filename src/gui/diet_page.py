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
from src.utils.modal_manager import ModalManager
from src.utils.database import DatabaseManager
from src.utils.food_data_loader import get_food_loader
from src.utils.exercise_data_loader import get_exercise_loader


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
    
    def __init__(self, parent, ectomorph=33, mesomorph=33, endomorph=34, somatotype_class="Balanced"):
        super().__init__(parent, fg_color="transparent")
        
        # Save the values
        self.ectomorph = ectomorph
        self.mesomorph = mesomorph
        self.endomorph = endomorph
        self.somatotype_class = somatotype_class
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Title
        self.grid_rowconfigure(1, weight=0)  # Classification
        self.grid_rowconfigure(2, weight=1)  # Content
        
        # Chart title
        self.chart_title = ctk.CTkLabel(
            self,
            text="Your Body Type Composition",
            font=ThemeManager.get_subtitle_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        self.chart_title.grid(row=0, column=0, pady=(0, 10))
        
        # Somatotype classification display
        self.classification_frame = ctk.CTkFrame(self, fg_color=ThemeManager.BG_COLOR, corner_radius=8)
        self.classification_frame.grid(row=1, column=0, pady=(0, 15), sticky="ew")
        
        self.classification_label = ctk.CTkLabel(
            self.classification_frame,
            text=f"Classification: {self.somatotype_class}",
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        self.classification_label.pack(pady=8)
        
        # Somatotype visualization
        self.soma_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.soma_frame.grid(row=2, column=0)
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
        
        # Percentage label inside circle (without % sign since these are scores, not percentages)
        score_label = ctk.CTkLabel(
            circle_frame,
            text=f"{percentage:.1f}",
            font=ThemeManager.get_title_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        score_label.place(relx=0.5, rely=0.5, anchor="center")
        
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
            # If we have food name but missing other data, try to load from database
            food_name = food_data.get('Food_Item', food_data.get('name', 'Unknown Food'))
            if food_name and food_name != 'Unknown Food':
                # Try to get complete food data from database
                food_loader = get_food_loader()
                complete_food_data = food_loader.get_food_info(food_name)
                if complete_food_data:
                    # Use complete data from database
                    self.food_name = complete_food_data['Food_Item']
                    self.calories = float(complete_food_data.get('Calories_kcal', 0))
                    self.protein = float(complete_food_data.get('Protein_g', 0))
                    self.portion = complete_food_data.get('Portion_Recommendation', 'N/A')
                    # Store complete data for details dialog
                    self.food_data = complete_food_data
                else:
                    # Use whatever data we have
                    self.food_name = food_name
                    self.calories = food_data.get('Calories_kcal', 0)
                    self.protein = food_data.get('Protein_g', 0)
                    self.portion = food_data.get('Portion_Recommendation', 'N/A')
            else:
                self.food_name = food_data.get('Food_Item', 'Unknown Food')
                self.calories = food_data.get('Calories_kcal', 0)
                self.protein = food_data.get('Protein_g', 0)
                self.portion = food_data.get('Portion_Recommendation', 'N/A')
        else:
            # Handle string input by trying to find in database
            if isinstance(food_data, str) and food_data.strip():
                food_loader = get_food_loader()
                complete_food_data = food_loader.get_food_info(food_data.strip())
                if complete_food_data:
                    self.food_name = complete_food_data['Food_Item']
                    self.calories = float(complete_food_data.get('Calories_kcal', 0))
                    self.protein = float(complete_food_data.get('Protein_g', 0))
                    self.portion = complete_food_data.get('Portion_Recommendation', 'N/A')
                    self.food_data = complete_food_data
                else:
                    self.food_name = str(food_data).strip()
                    self.calories = 0
                    self.protein = 0
                    self.portion = 'N/A'
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


class MacronutrientDetailModal:
    """Enhanced modal to show detailed food information with improved UI and centering"""
    
    def __init__(self, parent, food_data):
        self.parent = parent
        self.food_data = food_data
        
        try:
            # Create modal using standard CTkToplevel
            food_name = "Food Details"
            if isinstance(food_data, dict):
                food_name = food_data.get('Food_Item', 'Food Details')
                if len(food_name) > 40:
                    food_name = food_name[:37] + "..."
            
            self.modal = ctk.CTkToplevel(parent)
            self.modal.title(f"🍽️ {food_name}")
            self.modal.geometry("550x700")
            self.modal.resizable(False, False)
            
            # Set modal properties
            self.modal.transient(parent)
            self.modal.lift()
            self.modal.focus_set()
            
            # Center the modal
            self.modal.update_idletasks()
            x = (self.modal.winfo_screenwidth() // 2) - (550 // 2)
            y = (self.modal.winfo_screenheight() // 2) - (700 // 2)
            self.modal.geometry(f"550x700+{x}+{y}")
            
            # Configure background
            try:
                self.modal.configure(fg_color=ThemeManager.get_bg_color())
            except AttributeError:
                self.modal.configure(fg_color=ThemeManager.BG_COLOR)
            
            # Create content
            self._create_content()
            
            # Close button
            close_button = ctk.CTkButton(
                self.modal,
                text="Close",
                command=self.modal.destroy,
                font=ThemeManager.get_button_font(),
                fg_color=ThemeManager.PRIMARY_COLOR,
                hover_color=ThemeManager.PRIMARY_HOVER,
                corner_radius=12,
                width=120,
                height=40
            )
            close_button.pack(side="bottom", pady=10)
            
            # Set focus after modal is ready
            self.modal.after(100, lambda: self.modal.grab_set() if self.modal.winfo_exists() else None)
            
        except Exception as e:
            print(f"Error creating food modal: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_content(self):
        """Create the modal content with improved styling"""
        # Main content frame
        main_frame = ctk.CTkFrame(self.modal, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Create scrollable content frame
        try:
            bg_color = ThemeManager.get_card_fg_color()
        except AttributeError:
            bg_color = ThemeManager.SECONDARY_COLOR
            
        self.content_frame = ctk.CTkScrollableFrame(
            main_frame,
            height=580,
            fg_color=bg_color,
            corner_radius=15
        )
        self.content_frame.pack(fill="both", expand=True)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Extract and display food data
        if isinstance(self.food_data, dict):
            self._create_detailed_view()
        else:
            self._create_simple_view()
    
    def _create_detailed_view(self):
        """Create detailed food information view"""
        row = 0
        
        # Food name title
        food_name = self.food_data.get('Food_Item', 'Unknown Food')
        ModalManager.create_modal_title(
            self.content_frame, 
            food_name, 
            icon="🥗", 
            row=row
        )
        row += 1
        
        # Nutritional highlights section
        self._create_nutrition_highlights(self.content_frame, row)
        row += 1
        
        # Main macronutrients
        self._create_macronutrients_section(self.content_frame, row)
        row += 1
        
        # Vitamins and minerals
        self._create_micronutrients_section(self.content_frame, row)
        row += 1
        
        # Additional information
        self._create_additional_info(self.content_frame, row)
    
    def _create_nutrition_highlights(self, parent, row):
        """Create nutrition highlights with visual cards"""
        highlights_frame = ctk.CTkFrame(
            parent,
            fg_color=ThemeManager.get_card_fg_color(),
            corner_radius=15,
            border_width=2,
            border_color=ThemeManager.PRIMARY_COLOR + "40"
        )
        highlights_frame.grid(row=row, column=0, pady=(10, 20), padx=20, sticky="ew")
        highlights_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Title
        highlights_title = ctk.CTkLabel(
            highlights_frame,
            text="🌟 Nutritional Highlights",
            font=ThemeManager.get_subtitle_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        highlights_title.grid(row=0, column=0, columnspan=3, pady=(15, 10))
        
        # Get key nutritional values
        calories = self.food_data.get('Calories', 0)
        protein = self.food_data.get('Protein', 0)
        carbs = self.food_data.get('Carbohydrates', 0)
        
        # Calories card
        self._create_highlight_card(highlights_frame, "🔥", "Calories", f"{calories:.1f} kcal", 0, 1)
        
        # Protein card
        self._create_highlight_card(highlights_frame, "💪", "Protein", f"{protein:.1f}g", 1, 1)
        
        # Carbs card
        self._create_highlight_card(highlights_frame, "⚡", "Carbs", f"{carbs:.1f}g", 2, 1)
    
    def _create_highlight_card(self, parent, icon, title, value, column, row):
        """Create a small highlight card for key nutrients"""
        card = ctk.CTkFrame(
            parent,
            fg_color=ThemeManager.get_bg_color(),
            corner_radius=10,
            width=120,
            height=80
        )
        card.grid(row=row, column=column, padx=10, pady=(0, 15), sticky="ew")
        card.grid_propagate(False)
        
        # Icon and title
        icon_label = ctk.CTkLabel(
            card,
            text=f"{icon}\n{title}",
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        icon_label.grid(row=0, column=0, pady=(5, 0))
        
        # Value
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.GRAY_DARK
        )
        value_label.grid(row=1, column=0, pady=(0, 5))
    
    def _create_macronutrients_section(self, parent, row):
        """Create macronutrients section with improved layout"""
        # Section title
        ModalManager.create_info_section(
            parent, 
            "Macronutrients (per 100g)", 
            "", 
            row, 
            icon="🍽️",
            wraplength=500
        )
        
        # Macronutrients frame
        macro_frame = ctk.CTkFrame(
            parent,
            fg_color=ThemeManager.get_card_fg_color() + "30",
            corner_radius=10,
            border_width=1,
            border_color=ThemeManager.PRIMARY_COLOR + "20"
        )
        macro_frame.grid(row=row, column=0, pady=(30, 0), padx=20, sticky="ew")
        macro_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Macronutrient items
        macro_items = [
            ("🔥 Calories", self.food_data.get('Calories', 0), "kcal"),
            ("💪 Protein", self.food_data.get('Protein', 0), "g"),
            ("⚡ Carbohydrates", self.food_data.get('Carbohydrates', 0), "g"),
            ("🧈 Fat", self.food_data.get('Fat', 0), "g"),
            ("🌾 Fiber", self.food_data.get('Fiber', 0), "g"),
            ("🍯 Sugar", self.food_data.get('Sugar', 0), "g"),
        ]
        
        for i, (name, value, unit) in enumerate(macro_items):
            row_pos = i // 2
            col_pos = i % 2
            
            item_frame = ctk.CTkFrame(
                macro_frame,
                fg_color="transparent"
            )
            item_frame.grid(row=row_pos, column=col_pos, padx=10, pady=5, sticky="ew")
            item_frame.grid_columnconfigure(1, weight=1)
            
            # Name
            name_label = ctk.CTkLabel(
                item_frame,
                text=name,
                font=ThemeManager.get_small_font(),
                text_color=ThemeManager.GRAY_DARK,
                anchor="w"
            )
            name_label.grid(row=0, column=0, sticky="w")
            
            # Value
            value_text = f"{value:.1f} {unit}" if isinstance(value, (int, float)) else f"{value} {unit}"
            value_label = ctk.CTkLabel(
                item_frame,
                text=value_text,
                font=ThemeManager.get_label_font(),
                text_color=ThemeManager.PRIMARY_COLOR,
                anchor="e"
            )
            value_label.grid(row=0, column=1, sticky="e", padx=(10, 0))
    
    def _create_micronutrients_section(self, parent, row):
        """Create vitamins and minerals section"""
        # Get micronutrients data
        micronutrients = []
        
        # Common micronutrients to display
        micro_keys = [
            ('Vitamin_A', '🥕 Vitamin A', 'IU'),
            ('Vitamin_C', '🍊 Vitamin C', 'mg'),
            ('Vitamin_D', '☀️ Vitamin D', 'IU'),
            ('Vitamin_E', '🌰 Vitamin E', 'mg'),
            ('Vitamin_K', '🥬 Vitamin K', 'μg'),
            ('Calcium', '🦴 Calcium', 'mg'),
            ('Iron', '⚡ Iron', 'mg'),
            ('Magnesium', '🌿 Magnesium', 'mg'),
            ('Potassium', '🍌 Potassium', 'mg'),
            ('Sodium', '🧂 Sodium', 'mg'),
            ('Zinc', '⚗️ Zinc', 'mg'),
        ]
        
        # Filter available micronutrients
        for key, display_name, unit in micro_keys:
            if key in self.food_data and self.food_data[key]:
                value = self.food_data[key]
                if isinstance(value, (int, float)) and value > 0:
                    micronutrients.append((display_name, value, unit))
        
        if micronutrients:
            # Section title
            ModalManager.create_info_section(
                parent, 
                "Vitamins & Minerals", 
                "", 
                row, 
                icon="💎",
                wraplength=500
            )
            
            # Micronutrients frame
            micro_frame = ctk.CTkFrame(
                parent,
                fg_color=ThemeManager.get_card_fg_color() + "30",
                corner_radius=10,
                border_width=1,
                border_color=ThemeManager.PRIMARY_COLOR + "20"
            )
            micro_frame.grid(row=row, column=0, pady=(30, 0), padx=20, sticky="ew")
            micro_frame.grid_columnconfigure((0, 1), weight=1)
            
            # Display micronutrients
            for i, (name, value, unit) in enumerate(micronutrients[:10]):  # Limit to 10 items
                row_pos = i // 2
                col_pos = i % 2
                
                item_frame = ctk.CTkFrame(
                    micro_frame,
                    fg_color="transparent"
                )
                item_frame.grid(row=row_pos, column=col_pos, padx=10, pady=5, sticky="ew")
                item_frame.grid_columnconfigure(1, weight=1)
                
                # Name
                name_label = ctk.CTkLabel(
                    item_frame,
                    text=name,
                    font=ThemeManager.get_small_font(),
                    text_color=ThemeManager.GRAY_DARK,
                    anchor="w"
                )
                name_label.grid(row=0, column=0, sticky="w")
                
                # Value
                value_text = f"{value:.1f} {unit}" if isinstance(value, (int, float)) else f"{value} {unit}"
                value_label = ctk.CTkLabel(
                    item_frame,
                    text=value_text,
                    font=ThemeManager.get_label_font(),
                    text_color=ThemeManager.PRIMARY_COLOR,
                    anchor="e"
                )
                value_label.grid(row=0, column=1, sticky="e", padx=(10, 0))
    
    def _create_additional_info(self, parent, row):
        """Create additional information section"""
        # Additional info that might be available
        additional_items = []
        
        if 'Food_Group' in self.food_data:
            additional_items.append(("🏷️ Food Group", self.food_data['Food_Group']))
        
        if 'Serving_Size' in self.food_data:
            additional_items.append(("📏 Serving Size", self.food_data['Serving_Size']))
            
        if additional_items:
            # Section title
            ModalManager.create_info_section(
                parent, 
                "Additional Information", 
                "", 
                row, 
                icon="ℹ️",
                wraplength=500
            )
            
            # Additional info frame
            info_frame = ctk.CTkFrame(
                parent,
                fg_color=ThemeManager.get_card_fg_color() + "30",
                corner_radius=10,
                border_width=1,
                border_color=ThemeManager.PRIMARY_COLOR + "20"
            )
            info_frame.grid(row=row, column=0, pady=(30, 20), padx=20, sticky="ew")
            info_frame.grid_columnconfigure(0, weight=1)
            
            for i, (name, value) in enumerate(additional_items):
                item_label = ctk.CTkLabel(
                    info_frame,
                    text=f"{name}: {value}",
                    font=ThemeManager.get_small_font(),
                    text_color=ThemeManager.GRAY_DARK,
                    anchor="w"
                )
                item_label.grid(row=i, column=0, padx=15, pady=8, sticky="w")
    
    def _create_simple_view(self):
        """Create simple view for non-dict food data"""
        ModalManager.create_modal_title(
            self.content_frame, 
            "Food Information", 
            icon="🍽️", 
            row=0
        )
        
        # Simple content
        content_text = str(self.food_data) if self.food_data else "No food information available"
        content_label = ctk.CTkLabel(
            self.content_frame,
            text=content_text,
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.GRAY_DARK,
            wraplength=500,
            anchor="w",
            justify="left"
        )
        content_label.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
            
    def _create_detailed_view(self):
        """Create detailed food information view"""
        # Food name header - try to get complete data if needed
        food_name = self.food_data.get('Food_Item', 'Unknown Food')
        
        # If we still have Unknown Food, try to load from database
        if food_name == 'Unknown Food' and isinstance(self.food_data, dict):
            if 'name' in self.food_data:
                food_loader = get_food_loader()
                complete_data = food_loader.get_food_info(self.food_data['name'])
                if complete_data:
                    self.food_data = complete_data
                    food_name = complete_data['Food_Item']
        
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


class ExerciseRecommendations(ctk.CTkFrame):
    """Component showing exercise recommendations based on user preference"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color=ThemeManager.get_card_fg_color(), corner_radius=10)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="💪 Your Exercise Plan",
            font=ThemeManager.get_title_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        self.title_label.grid(row=0, column=0, pady=(20, 15), padx=20)
        
        # Content frame
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Default placeholder
        self.placeholder_label = ctk.CTkLabel(
            self.content_frame,
            text="Loading exercise recommendations...",
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.GRAY_MEDIUM
        )
        self.placeholder_label.grid(row=0, column=0, pady=20)
    
    def update_exercise_recommendations(self, exercise_data):
        """Update exercise recommendations based on data"""
        try:
            # Clear existing content
            for widget in self.content_frame.winfo_children():
                widget.destroy()
            
            if not exercise_data:
                self.placeholder_label = ctk.CTkLabel(
                    self.content_frame,
                    text="No exercise recommendations available",
                    font=ThemeManager.get_label_font(),
                    text_color=ThemeManager.GRAY_MEDIUM
                )
                self.placeholder_label.grid(row=0, column=0, pady=20)
                return
            
            # Exercise type and complexity info
            exercise_type = exercise_data.get('exercise_type', 'bodyweight')
            exercise_complexity = exercise_data.get('exercise_complexity', 'beginner')
            workout_description = exercise_data.get('workout_description', f'{exercise_type} {exercise_complexity} workout')
            
            # Header section
            header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
            header_frame.grid_columnconfigure(1, weight=1)
            
            # Exercise type badge
            type_badge = ctk.CTkLabel(
                header_frame,
                text=f"🏋️ {exercise_type.title()}",
                font=ThemeManager.get_label_font(),
                fg_color=ThemeManager.PRIMARY_COLOR,
                corner_radius=15,
                width=100,
                height=30
            )
            type_badge.grid(row=0, column=0, padx=(0, 10))
            
            # Complexity badge
            complexity_colors = {
                'beginner': ThemeManager.SUCCESS_COLOR,
                'intermediate': ThemeManager.WARNING_COLOR,
                'advanced': '#ff6b35'
            }
            complexity_badge = ctk.CTkLabel(
                header_frame,
                text=f"📊 {exercise_complexity.title()}",
                font=ThemeManager.get_label_font(),
                fg_color=complexity_colors.get(exercise_complexity, ThemeManager.GRAY_MEDIUM),
                corner_radius=15,
                width=120,
                height=30
            )
            complexity_badge.grid(row=0, column=1, sticky="w")
            
            # Workout description
            desc_label = ctk.CTkLabel(
                self.content_frame,
                text=workout_description,
                font=ThemeManager.get_small_font(),
                text_color=ThemeManager.GRAY_DARK,
                wraplength=400
            )
            desc_label.grid(row=1, column=0, pady=(0, 15))
            
            # Schedule info
            schedule_frame = ctk.CTkFrame(self.content_frame, fg_color=ThemeManager.GRAY_LIGHT, corner_radius=8)
            schedule_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15))
            schedule_frame.grid_columnconfigure((0, 1), weight=1)
            
            strength_days = exercise_data.get('strength_days', 0)
            cardio_days = exercise_data.get('cardio_days', 0)
            
            strength_label = ctk.CTkLabel(
                schedule_frame,
                text=f"💪 Strength: {strength_days} days/week",
                font=ThemeManager.get_small_font(),
                text_color=ThemeManager.GRAY_DARK
            )
            strength_label.grid(row=0, column=0, padx=10, pady=8)
            
            cardio_label = ctk.CTkLabel(
                schedule_frame,
                text=f"❤️ Cardio: {cardio_days} days/week",
                font=ThemeManager.get_small_font(),
                text_color=ThemeManager.GRAY_DARK
            )
            cardio_label.grid(row=0, column=1, padx=10, pady=8)
            
            # Exercise lists
            if exercise_type == 'gym':
                self._create_gym_exercises(exercise_data)
            else:
                self._create_bodyweight_exercises(exercise_data)
                
        except Exception as e:
            print(f"Error updating exercise recommendations: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_gym_exercises(self, exercise_data):
        """Create gym exercise display with push/pull/legs split"""
        exercises_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        exercises_frame.grid(row=3, column=0, sticky="ew")
        exercises_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Push exercises
        push_exercises = exercise_data.get('push_exercises', [])
        if push_exercises:
            self._create_exercise_category(exercises_frame, "🔥 Push", push_exercises[:4], 0)
        
        # Pull exercises  
        pull_exercises = exercise_data.get('pull_exercises', [])
        if pull_exercises:
            self._create_exercise_category(exercises_frame, "⬇️ Pull", pull_exercises[:4], 1)
        
        # Leg exercises
        legs_exercises = exercise_data.get('legs_exercises', [])
        if legs_exercises:
            self._create_exercise_category(exercises_frame, "🦵 Legs", legs_exercises[:4], 2)
    
    def _create_bodyweight_exercises(self, exercise_data):
        """Create bodyweight exercise display"""
        exercises_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        exercises_frame.grid(row=3, column=0, sticky="ew")
        
        bodyweight_exercises = exercise_data.get('bodyweight_exercises', [])
        if bodyweight_exercises:
            self._create_exercise_category(exercises_frame, "🏃 Bodyweight", bodyweight_exercises[:8], 0, single_column=True)
    
    def _create_exercise_category(self, parent, title, exercises, column, single_column=False):
        """Create an exercise category section"""
        category_frame = ctk.CTkFrame(parent, fg_color=ThemeManager.BG_COLOR, corner_radius=8)
        if single_column:
            category_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        else:
            category_frame.grid(row=0, column=column, sticky="nsew", padx=5, pady=5)
        category_frame.grid_columnconfigure(0, weight=1)
        
        # Category title
        title_label = ctk.CTkLabel(
            category_frame,
            text=title,
            font=ThemeManager.get_subtitle_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        title_label.grid(row=0, column=0, pady=(10, 5))
        
        # Exercise list
        for i, exercise in enumerate(exercises[:6]):  # Max 6 exercises per category
            if exercise and str(exercise).strip():  # Only show non-empty exercises
                exercise_str = str(exercise).strip()
                
                # Try to get exercise name from database if this looks like an ID
                exercise_loader = get_exercise_loader()
                exercise_info = exercise_loader.get_exercise_info(exercise_str)
                
                if exercise_info:
                    # Found exercise in database, use proper name
                    exercise_name = exercise_info['name'].title()
                    exercise_data = exercise_info
                else:
                    # Not found in database or already a name, use as is
                    exercise_name = exercise_str.title()
                    exercise_data = {'name': exercise_str, 'exerciseId': exercise_str}
                
                # Create clickable exercise button
                exercise_button = ctk.CTkButton(
                    category_frame,
                    text=f"• {exercise_name}",
                    font=ThemeManager.get_small_font(),
                    text_color=ThemeManager.GRAY_DARK,
                    fg_color="transparent",
                    hover_color=ThemeManager.PRIMARY_COLOR,
                    anchor="w",
                    height=25,
                    command=lambda ex=exercise_data: self._show_exercise_details(ex)
                )
                exercise_button.grid(row=i+1, column=0, sticky="ew", padx=10, pady=2)
        
        # Padding at bottom
        ctk.CTkLabel(category_frame, text="").grid(row=10, column=0, pady=(0, 5))
    
    def _show_exercise_details(self, exercise_data):
        """Show detailed exercise information in a modal window"""
        try:
            ExerciseDetailModal(self, exercise_data)
        except Exception as e:
            print(f"Error showing exercise details: {e}")


class ExerciseDetailModal:
    """Enhanced modal dialog showing detailed exercise information with GIF demonstration"""
    
    def __init__(self, parent, exercise_data):
        self.parent = parent
        self.exercise_data = exercise_data
        self.gif_frames = []
        self.current_frame = 0
        self.gif_label = None
        self.animation_job = None
        
        try:
            # Create modal using standard CTkToplevel to avoid issues
            exercise_name = self.exercise_data.get('name', 'Exercise Details').title()
            self.modal = ctk.CTkToplevel(parent)
            self.modal.title(f"💪 {exercise_name}")
            self.modal.geometry("650x750")
            self.modal.resizable(False, False)
            
            # Set modal properties
            self.modal.transient(parent)
            self.modal.lift()
            self.modal.focus_set()
            
            # Center the modal
            self.modal.update_idletasks()
            x = (self.modal.winfo_screenwidth() // 2) - (650 // 2)
            y = (self.modal.winfo_screenheight() // 2) - (750 // 2)
            self.modal.geometry(f"650x750+{x}+{y}")
            
            # Configure background with fallback
            try:
                self.modal.configure(fg_color=ThemeManager.get_bg_color())
            except AttributeError:
                self.modal.configure(fg_color=ThemeManager.BG_COLOR)
            
            # Handle window close event
            self.modal.protocol("WM_DELETE_WINDOW", self._close_modal)
            
            # Create content
            self._create_content()
            
            # Set focus after modal is ready
            self.modal.after(100, lambda: self.modal.grab_set() if self.modal.winfo_exists() else None)
            
        except Exception as e:
            print(f"Error creating exercise modal: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_content(self):
        """Create the modal content with improved styling"""
        # Main content frame
        main_frame = ctk.CTkFrame(self.modal, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Create scrollable content frame
        try:
            bg_color = ThemeManager.get_card_fg_color()
        except AttributeError:
            bg_color = ThemeManager.SECONDARY_COLOR
            
        self.content_frame = ctk.CTkScrollableFrame(
            main_frame,
            height=650,
            fg_color=bg_color,
            corner_radius=15
        )
        self.content_frame.pack(fill="both", expand=True)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        row = 0
        
        # Exercise title
        exercise_name = self.exercise_data.get('name', 'Unknown Exercise').title()
        title_label = ctk.CTkLabel(
            self.content_frame,
            text=f"🏋️ {exercise_name}",
            font=ThemeManager.get_title_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        title_label.grid(row=row, column=0, pady=(20, 15))
        row += 1
        
        # Exercise GIF section
        self._create_gif_section(self.content_frame, row)
        row += 1
        
        # Exercise information sections
        self._create_info_sections(self.content_frame, row)
        
        # Close button frame for proper positioning
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 0))
        
        close_button = ctk.CTkButton(
            button_frame,
            text="Close",
            command=self._close_modal,
            font=ThemeManager.get_button_font(),
            fg_color=ThemeManager.PRIMARY_COLOR,
            hover_color=ThemeManager.PRIMARY_HOVER,
            corner_radius=12,
            width=120,
            height=40
        )
        close_button.pack(anchor="center")
    
    def _create_info_sections(self, parent, row):
        """Create exercise information sections"""
        # Target muscles info
        target_muscles = self.exercise_data.get('targetMuscles', [])
        if target_muscles:
            muscles_text = ", ".join([muscle.title() for muscle in target_muscles])
            self._create_info_card(parent, "🎯 Target Muscles", muscles_text, row)
            row += 1
        
        # Body parts info
        body_parts = self.exercise_data.get('bodyParts', [])
        if body_parts:
            body_parts_text = ", ".join([part.title() for part in body_parts])
            self._create_info_card(parent, "💪 Body Parts", body_parts_text, row)
            row += 1
        
        # Equipment info
        equipments = self.exercise_data.get('equipments', [])
        if equipments:
            equipment_text = ", ".join([eq.title() for eq in equipments])
            self._create_info_card(parent, "🛠️ Equipment", equipment_text, row)
            row += 1
        
        # Secondary muscles
        secondary_muscles = self.exercise_data.get('secondaryMuscles', [])
        if secondary_muscles:
            secondary_text = ", ".join([muscle.title() for muscle in secondary_muscles])
            self._create_info_card(parent, "🔄 Secondary Muscles", secondary_text, row)
            row += 1
        
        # Instructions
        instructions = self.exercise_data.get('instructions', [])
        if instructions:
            self._create_instructions_card(parent, instructions, row)
    
    def _create_info_card(self, parent, title, content, row):
        """Create an information card"""
        try:
            card_color = ThemeManager.get_card_fg_color()
        except AttributeError:
            card_color = "white"
            
        card_frame = ctk.CTkFrame(
            parent,
            fg_color=card_color,
            corner_radius=15,
            border_width=2,
            border_color=ThemeManager.GRAY_LIGHT
        )
        card_frame.grid(row=row, column=0, pady=(0, 15), padx=20, sticky="ew")
        card_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            card_frame,
            text=title,
            font=ThemeManager.get_subtitle_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        title_label.grid(row=0, column=0, pady=(15, 10))
        
        # Content
        content_label = ctk.CTkLabel(
            card_frame,
            text=content,
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.GRAY_DARK,
            wraplength=500,  # Reduced from 550 to prevent overflow
            justify="left"
        )
        content_label.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="ew")
    
    def _create_instructions_card(self, parent, instructions, row):
        """Create a special card for step-by-step instructions with improved formatting"""
        try:
            card_color = ThemeManager.get_card_fg_color()
        except AttributeError:
            card_color = "white"
            
        # Main instructions card
        instructions_frame = ctk.CTkFrame(
            parent,
            fg_color=card_color,
            corner_radius=15,
            border_width=2,
            border_color=ThemeManager.GRAY_LIGHT
        )
        instructions_frame.grid(row=row, column=0, pady=(0, 15), padx=20, sticky="ew")
        instructions_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            instructions_frame,
            text="📋 Step-by-Step Instructions",
            font=ThemeManager.get_subtitle_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        title_label.grid(row=0, column=0, pady=(15, 10))
        
        # Instructions container with scrollable area if needed
        instructions_container = ctk.CTkFrame(
            instructions_frame,
            fg_color="transparent"
        )
        instructions_container.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="ew")
        instructions_container.grid_columnconfigure(0, weight=1)
        
        # Add each instruction as a separate step
        for i, instruction in enumerate(instructions, 1):
            # Clean up instruction text
            clean_instruction = instruction.replace(f"Step:{i}", "").strip()
            if not clean_instruction:
                continue
                
            # Step frame for each instruction
            step_frame = ctk.CTkFrame(
                instructions_container,
                fg_color=ThemeManager.SECONDARY_COLOR,
                corner_radius=8,
                border_width=1,
                border_color=ThemeManager.GRAY_LIGHT
            )
            step_frame.grid(row=i-1, column=0, pady=(0, 8), sticky="ew")
            step_frame.grid_columnconfigure(1, weight=1)
            
            # Step number
            step_number = ctk.CTkLabel(
                step_frame,
                text=str(i),
                font=ThemeManager.get_label_font(),
                text_color="white",
                fg_color=ThemeManager.PRIMARY_COLOR,
                corner_radius=15,
                width=30,
                height=30
            )
            step_number.grid(row=0, column=0, padx=(15, 10), pady=15, sticky="n")
            
            # Step text with proper wrapping
            step_text = ctk.CTkLabel(
                step_frame,
                text=clean_instruction,
                font=ThemeManager.get_small_font(),
                text_color=ThemeManager.GRAY_DARK,
                wraplength=480,  # Adjust for step number space
                justify="left",
                anchor="w"
            )
            step_text.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="ew")
    
    def _create_gif_section(self, parent, row):
        """Create the GIF display section with improved styling"""
        # GIF container frame
        gif_frame = ctk.CTkFrame(
            parent,
            fg_color=ThemeManager.get_card_fg_color(),
            corner_radius=15,
            border_width=3,
            border_color=ThemeManager.PRIMARY_COLOR,
            height=300
        )
        gif_frame.grid(row=row, column=0, pady=(10, 20), padx=20, sticky="ew")
        gif_frame.grid_columnconfigure(0, weight=1)
        gif_frame.grid_propagate(False)
        
        # GIF title
        gif_title = ctk.CTkLabel(
            gif_frame,
            text="🎬 Exercise Demonstration",
            font=ThemeManager.get_subtitle_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        gif_title.grid(row=0, column=0, pady=(15, 10))
        
        # GIF display label with improved styling
        self.gif_label = ctk.CTkLabel(
            gif_frame,
            text="Loading animation...",
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.GRAY_DARK,
            width=400,
            height=220,
            corner_radius=10
        )
        self.gif_label.grid(row=1, column=0, pady=(5, 15), padx=15)
        
        # Load and start GIF animation
        self._load_gif()
    
    def _create_instructions_section(self, parent, row):
        """Create the instructions section with improved formatting"""
        instructions = self.exercise_data.get('instructions', [])
        if not instructions:
            return
            
        # Instructions title
        instructions_title = ctk.CTkLabel(
            parent,
            text="📝 Instructions",
            font=ThemeManager.get_subtitle_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        instructions_title.grid(row=row, column=0, pady=(20, 10), sticky="w", padx=20)
        
        # Instructions container frame
        instructions_frame = ctk.CTkFrame(
            parent,
            fg_color="transparent",  # Use transparent instead of invalid color
            corner_radius=10,
            border_width=1,
            border_color=ThemeManager.GRAY_LIGHT
        )
        instructions_frame.grid(row=row, column=0, pady=(30, 0), padx=20, sticky="ew")
        instructions_frame.grid_columnconfigure(0, weight=1)
        
        # Add each instruction with improved styling
        for i, instruction in enumerate(instructions, 1):
            # Clean up instruction text
            instruction_text = instruction.replace(f"Step:{i} ", "").strip()
            
            # Create instruction frame for better visual separation
            step_frame = ctk.CTkFrame(
                instructions_frame,
                fg_color="transparent",
                corner_radius=5
            )
            step_frame.grid(row=i-1, column=0, pady=5, padx=15, sticky="ew")
            step_frame.grid_columnconfigure(1, weight=1)
            
            # Step number
            step_number = ctk.CTkLabel(
                step_frame,
                text=f"{i}.",
                font=ThemeManager.get_label_font(),
                text_color=ThemeManager.PRIMARY_COLOR,
                width=30
            )
            step_number.grid(row=0, column=0, sticky="nw", padx=(5, 10))
            
            # Step text
            step_text = ctk.CTkLabel(
                step_frame,
                text=instruction_text,
                font=ThemeManager.get_small_font(),
                text_color=ThemeManager.GRAY_DARK,
                wraplength=500,
                anchor="w",
                justify="left"
            )
            step_text.grid(row=0, column=1, sticky="ew", pady=5)
    
    def _load_gif(self):
        """Load and start GIF animation with improved error handling"""
        try:
            exercise_id = self.exercise_data.get('exerciseId', '')
            if not exercise_id:
                self._show_gif_placeholder("No exercise ID available")
                return
            
            # Construct GIF path
            gif_path = os.path.join(
                PROJECT_DIR,
                "data", "datasets", "fitness", "media", 
                f"{exercise_id}.gif"
            )
            
            if not os.path.exists(gif_path):
                self._show_gif_placeholder(f"Animation not available")
                return
            
            # Load GIF frames
            gif_image = Image.open(gif_path)
            self.gif_frames = []
            
            try:
                while True:
                    # Resize frame to fit display area (max 400x220)
                    frame = gif_image.copy()
                    frame.thumbnail((400, 220), Image.Resampling.LANCZOS)
                    
                    # Convert to PhotoImage
                    photo = ImageTk.PhotoImage(frame)
                    self.gif_frames.append(photo)
                    
                    gif_image.seek(gif_image.tell() + 1)
            except EOFError:
                pass  # End of frames
            
            if self.gif_frames:
                self.current_frame = 0
                self._animate_gif()
            else:
                self._show_gif_placeholder("Failed to load animation")
                
        except Exception as e:
            self._show_gif_placeholder(f"Animation unavailable")
            print(f"GIF loading error: {e}")
    
    def _animate_gif(self):
        """Animate the GIF by cycling through frames"""
        if self.gif_frames and self.gif_label and self.gif_label.winfo_exists():
            try:
                # Update the image
                self.gif_label.configure(image=self.gif_frames[self.current_frame], text="")
                
                # Move to next frame
                self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
                
                # Schedule next frame (120ms delay for smooth animation)
                self.animation_job = self.modal.after(120, self._animate_gif)
                
            except Exception as e:
                self._show_gif_placeholder(f"Animation error")
                print(f"Animation error: {e}")
    
    def _show_gif_placeholder(self, message):
        """Show placeholder when GIF cannot be loaded"""
        if self.gif_label and self.gif_label.winfo_exists():
            self.gif_label.configure(
                text=f"🎬\n\n{message}\n\nExercise demonstration\nnot available",
                image="",
                font=ThemeManager.get_small_font(),
                text_color=ThemeManager.GRAY_DARK
            )
    
    def _close_modal(self):
        """Clean up and close the modal"""
        # Stop animation
        if self.animation_job:
            self.modal.after_cancel(self.animation_job)
            self.animation_job = None
        
        # Clear references to prevent memory leaks
        self.gif_frames = []
        self.gif_label = None
        
        # Destroy window
        self.modal.destroy()


class DietPrinciples(ctk.CTkFrame):
    """Component showing diet principles and nutritional guidelines"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color=ThemeManager.get_card_fg_color(), corner_radius=10)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="📋 Diet Principles",
            font=ThemeManager.get_title_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        self.title_label.grid(row=0, column=0, pady=(20, 15), padx=20)
        
        # Content frame
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Default placeholder
        self.placeholder_label = ctk.CTkLabel(
            self.content_frame,
            text="Loading diet principles...",
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.GRAY_MEDIUM
        )
        self.placeholder_label.grid(row=0, column=0, pady=20)
    
    def update_principles(self, principles_data):
        """Update diet principles display"""
        try:
            # Clear existing content
            for widget in self.content_frame.winfo_children():
                widget.destroy()
            
            if not principles_data:
                self.placeholder_label = ctk.CTkLabel(
                    self.content_frame,
                    text="No diet principles available",
                    font=ThemeManager.get_label_font(),
                    text_color=ThemeManager.GRAY_MEDIUM
                )
                self.placeholder_label.grid(row=0, column=0, pady=20)
                return
            
            # Display principles as numbered list
            for i, principle in enumerate(principles_data, 1):
                principle_frame = ctk.CTkFrame(
                    self.content_frame, 
                    fg_color=ThemeManager.BG_COLOR, 
                    corner_radius=8
                )
                principle_frame.grid(row=i-1, column=0, sticky="ew", pady=5, padx=5)
                principle_frame.grid_columnconfigure(1, weight=1)
                
                # Number badge
                number_label = ctk.CTkLabel(
                    principle_frame,
                    text=str(i),
                    font=ThemeManager.get_label_font(),
                    fg_color=ThemeManager.PRIMARY_COLOR,
                    corner_radius=15,
                    width=30,
                    height=30
                )
                number_label.grid(row=0, column=0, padx=10, pady=10)
                
                # Principle text
                principle_label = ctk.CTkLabel(
                    principle_frame,
                    text=principle,
                    font=ThemeManager.get_label_font(),
                    text_color=ThemeManager.GRAY_DARK,
                    wraplength=500,
                    justify="left",
                    anchor="w"
                )
                principle_label.grid(row=0, column=1, sticky="ew", padx=(0, 15), pady=10)
                
        except Exception as e:
            print(f"Error updating diet principles: {e}")


class FitnessStrategy(ctk.CTkFrame):
    """Component showing fitness strategy and training split with graph visualization"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color=ThemeManager.get_card_fg_color(), corner_radius=10)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="💪 Fitness Strategy",
            font=ThemeManager.get_title_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        self.title_label.grid(row=0, column=0, pady=(20, 15), padx=20)
        
        # Content frame
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Default placeholder
        self.placeholder_label = ctk.CTkLabel(
            self.content_frame,
            text="Loading fitness strategy...",
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.GRAY_MEDIUM
        )
        self.placeholder_label.grid(row=0, column=0, pady=20)
    
    def update_strategy(self, strategy_data):
        """Update fitness strategy display"""
        try:
            # Clear existing content
            for widget in self.content_frame.winfo_children():
                widget.destroy()
            
            if not strategy_data:
                self.placeholder_label = ctk.CTkLabel(
                    self.content_frame,
                    text="No fitness strategy available",
                    font=ThemeManager.get_label_font(),
                    text_color=ThemeManager.GRAY_MEDIUM
                )
                self.placeholder_label.grid(row=0, column=0, pady=20)
                return
            
            # Strategy description
            strategy_text = strategy_data.get('fitness_strategy', 'No strategy description available')
            strategy_label = ctk.CTkLabel(
                self.content_frame,
                text=strategy_text,
                font=ThemeManager.get_label_font(),
                text_color=ThemeManager.GRAY_DARK,
                wraplength=500,
                justify="center"
            )
            strategy_label.grid(row=0, column=0, pady=(0, 20), sticky="ew")
            
            # Training split graph
            strength_days = strategy_data.get('strength_days', 0)
            cardio_days = strategy_data.get('cardio_days', 0)
            
            if strength_days > 0 or cardio_days > 0:
                self._create_training_split_graph(strength_days, cardio_days)
                
        except Exception as e:
            print(f"Error updating fitness strategy: {e}")
    
    def _create_training_split_graph(self, strength_days, cardio_days):
        """Create a visual graph showing training split"""
        # Graph frame
        graph_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        graph_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        graph_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Graph title
        graph_title = ctk.CTkLabel(
            graph_frame,
            text="Weekly Training Split",
            font=ThemeManager.get_subtitle_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        graph_title.grid(row=0, column=0, columnspan=2, pady=(0, 15))
        
        # Calculate total days and percentages
        total_days = strength_days + cardio_days
        rest_days = 7 - total_days
        
        # Create visual bars
        bar_height = 30
        bar_width = 300
        
        # Strength training bar
        strength_frame = ctk.CTkFrame(graph_frame, fg_color="transparent")
        strength_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        strength_frame.grid_columnconfigure(1, weight=1)
        
        strength_label = ctk.CTkLabel(
            strength_frame,
            text="🏋️ Strength",
            font=ThemeManager.get_label_font(),
            width=80
        )
        strength_label.grid(row=0, column=0, padx=(0, 10))
        
        strength_bar_frame = ctk.CTkFrame(
            strength_frame, 
            height=bar_height, 
            fg_color=ThemeManager.BG_COLOR,
            corner_radius=15
        )
        strength_bar_frame.grid(row=0, column=1, sticky="ew")
        strength_bar_frame.grid_propagate(False)
        
        if total_days > 0:
            strength_width = int((strength_days / 7) * bar_width)
            strength_bar = ctk.CTkFrame(
                strength_bar_frame,
                width=strength_width,
                height=bar_height-4,
                fg_color=ThemeManager.PRIMARY_COLOR,
                corner_radius=15
            )
            strength_bar.place(x=2, y=2)
            strength_bar.grid_propagate(False)
        
        strength_days_label = ctk.CTkLabel(
            strength_frame,
            text=f"{strength_days} days",
            font=ThemeManager.get_small_font(),
            width=60
        )
        strength_days_label.grid(row=0, column=2, padx=(10, 0))
        
        # Cardio training bar
        cardio_frame = ctk.CTkFrame(graph_frame, fg_color="transparent")
        cardio_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)
        cardio_frame.grid_columnconfigure(1, weight=1)
        
        cardio_label = ctk.CTkLabel(
            cardio_frame,
            text="🏃 Cardio",
            font=ThemeManager.get_label_font(),
            width=80
        )
        cardio_label.grid(row=0, column=0, padx=(0, 10))
        
        cardio_bar_frame = ctk.CTkFrame(
            cardio_frame, 
            height=bar_height, 
            fg_color=ThemeManager.BG_COLOR,
            corner_radius=15
        )
        cardio_bar_frame.grid(row=0, column=1, sticky="ew")
        cardio_bar_frame.grid_propagate(False)
        
        if total_days > 0:
            cardio_width = int((cardio_days / 7) * bar_width)
            cardio_bar = ctk.CTkFrame(
                cardio_bar_frame,
                width=cardio_width,
                height=bar_height-4,
                fg_color=ThemeManager.SUCCESS_COLOR,
                corner_radius=15
            )
            cardio_bar.place(x=2, y=2)
            cardio_bar.grid_propagate(False)
        
        cardio_days_label = ctk.CTkLabel(
            cardio_frame,
            text=f"{cardio_days} days",
            font=ThemeManager.get_small_font(),
            width=60
        )
        cardio_days_label.grid(row=0, column=2, padx=(10, 0))
        
        # Rest days
        if rest_days > 0:
            rest_frame = ctk.CTkFrame(graph_frame, fg_color="transparent")
            rest_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=5)
            rest_frame.grid_columnconfigure(1, weight=1)
            
            rest_label = ctk.CTkLabel(
                rest_frame,
                text="😴 Rest",
                font=ThemeManager.get_label_font(),
                width=80
            )
            rest_label.grid(row=0, column=0, padx=(0, 10))
            
            rest_bar_frame = ctk.CTkFrame(
                rest_frame, 
                height=bar_height, 
                fg_color=ThemeManager.BG_COLOR,
                corner_radius=15
            )
            rest_bar_frame.grid(row=0, column=1, sticky="ew")
            rest_bar_frame.grid_propagate(False)
            
            rest_width = int((rest_days / 7) * bar_width)
            rest_bar = ctk.CTkFrame(
                rest_bar_frame,
                width=rest_width,
                height=bar_height-4,
                fg_color=ThemeManager.GRAY_MEDIUM,
                corner_radius=15
            )
            rest_bar.place(x=2, y=2)
            rest_bar.grid_propagate(False)
            
            rest_days_label = ctk.CTkLabel(
                rest_frame,
                text=f"{rest_days} days",
                font=ThemeManager.get_small_font(),
                width=60
            )
            rest_days_label.grid(row=0, column=2, padx=(10, 0))


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
            for meal_type, meal_data in meal_recommendations.items():
                # Handle different data structures
                foods = []
                if isinstance(meal_data, list):
                    # Direct list of foods
                    foods = meal_data
                elif isinstance(meal_data, dict):
                    # Dictionary with 'foods' key
                    foods = meal_data.get('foods', [])
                elif isinstance(meal_data, str):
                    # Single food as string
                    foods = [meal_data]
                
                if not foods:
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
            import traceback
            traceback.print_exc()
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
            
            # Center the error window
            error_window.update_idletasks()
            x = (error_window.winfo_screenwidth() // 2) - (300 // 2)
            y = (error_window.winfo_screenheight() // 2) - (150 // 2)
            error_window.geometry(f"300x150+{x}+{y}")
            
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
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=32, pady=(24, 0))
        self.header_frame.grid_columnconfigure(1, weight=1)
        self.header_frame.grid_columnconfigure((2, 3), weight=0)  # Make buttons fixed width
        
        # Back button with arrow
        self.back_button = ctk.CTkButton(
            self.header_frame,
            text="← Back to Processing",
            font=ctk.CTkFont(size=14),
            width=160,
            height=32,
            corner_radius=16,
            fg_color="transparent",
            text_color=ThemeManager.GRAY_DARK,
            hover_color=ThemeManager.GRAY_LIGHT,
            border_width=1,
            border_color=ThemeManager.GRAY_LIGHT,
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
        self.history_button.grid(row=0, column=2, sticky="e", padx=(0, 10))
        
        # Export button
        self.export_button = ctk.CTkButton(
            self.header_frame,
            text="📤 Export",
            font=ctk.CTkFont(size=14),
            width=100,
            height=32,
            corner_radius=16,
            fg_color=ThemeManager.SUCCESS_COLOR,
            hover_color="#0d9668",  # Darker green for hover
            command=self._export_diet_plan
        )
        self.export_button.grid(row=0, column=3, sticky="e")
        
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
        # Diet principles section
        self.diet_principles = DietPrinciples(self.content_scroll)
        self.diet_principles.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(0, 15))
        
        # Fitness strategy section
        self.fitness_strategy = FitnessStrategy(self.content_scroll)
        self.fitness_strategy.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=(0, 15))
        
        # Meal recommendations section
        self.meal_recommendations = MealBasedFoodRecommendations(self.content_scroll)
        self.meal_recommendations.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=(0, 15))
        
        # Exercise recommendations section
        self.exercise_recommendations = ExerciseRecommendations(self.content_scroll)
        self.exercise_recommendations.grid(row=6, column=0, columnspan=2, sticky="nsew", pady=(0, 15))
        
    def _create_footer(self):
        """Create footer with action buttons"""
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.footer_frame.grid_columnconfigure(1, weight=1)
        
        # Try Again button (left side)
        self.try_again_button = ctk.CTkButton(
            self.footer_frame,
            text="🔄 Try Again",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=140,
            height=44,
            corner_radius=22,
            fg_color=ThemeManager.WARNING_COLOR,
            hover_color="#d97706",  # Darker orange for hover
            command=self._try_again
        )
        self.try_again_button.grid(row=0, column=0, sticky="w")
        
        # New Analysis button (right side)
        self.new_analysis_button = ctk.CTkButton(
            self.footer_frame,
            text="� New Analysis",
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
                    somatotype_class = soma_data.get('somatotype_class', 'Balanced')
                    
                    # Create or update somatotype visualization
                    if self.soma_visual:
                        self.soma_visual.destroy()
                        
                    self.soma_visual = SomatotypeVisual(
                        self.soma_frame,
                        ectomorph=ectomorph,
                        mesomorph=mesomorph,
                        endomorph=endomorph,
                        somatotype_class=somatotype_class
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
                            print("ERROR - Failed to parse meal recommendations JSON")
                            meal_data = {}
                    
                    print(f"DEBUG - Meal data keys: {list(meal_data.keys()) if meal_data else 'None'}")
                    
                    # Extract and display diet principles
                    if 'diet_principles' in meal_data:
                        diet_principles = meal_data['diet_principles']
                        print(f"DEBUG - Found diet principles: {len(diet_principles) if diet_principles else 0} items")
                        self.diet_principles.update_principles(diet_principles)
                    else:
                        print("DEBUG - No diet principles found")
                        self.diet_principles.update_principles([])
                    
                    # Extract and display fitness strategy
                    fitness_strategy_text = meal_data.get('fitness_strategy', '')
                    
                    # Try to get additional fitness data from fitness recommendations table
                    fitness_data = self.db_manager.get_fitness_recommendations(session_id)
                    
                    strategy_data = {
                        'fitness_strategy': fitness_strategy_text or (fitness_data.get('fitness_strategy', '') if fitness_data else ''),
                        'strength_days': fitness_data.get('strength_days', 0) if fitness_data else 0,
                        'cardio_days': fitness_data.get('cardio_days', 0) if fitness_data else 0
                    }
                    
                    if strategy_data['fitness_strategy'] or strategy_data['strength_days'] or strategy_data['cardio_days']:
                        print(f"DEBUG - Found fitness strategy: {strategy_data['fitness_strategy'][:50]}...")
                        self.fitness_strategy.update_strategy(strategy_data)
                    else:
                        print("DEBUG - No fitness strategy found")
                        self.fitness_strategy.update_strategy({})
                    
                    # Extract meals from the meal data structure
                    if 'meals' in meal_data:
                        meals = meal_data['meals']
                        print(f"DEBUG - Found meals structure with keys: {list(meals.keys())}")
                        self.meal_recommendations.update_recommendations(meals)
                    elif any(key in meal_data for key in ['breakfast', 'lunch', 'dinner', 'snack']):
                        # Direct meal structure
                        print("DEBUG - Found direct meal structure")
                        self.meal_recommendations.update_recommendations(meal_data)
                    else:
                        print("DEBUG - No recognized meal structure found")
                        self.meal_recommendations.update_recommendations({})
                    
                    # Extract and display exercise data
                    if 'exercises' in meal_data:
                        exercise_data = meal_data['exercises']
                        print(f"DEBUG - Found exercise data with keys: {list(exercise_data.keys()) if exercise_data else 'None'}")
                        self.exercise_recommendations.update_exercise_recommendations(exercise_data)
                    else:
                        print("DEBUG - No exercise data found in meal data, trying fitness recommendations")
                        # Use fitness data we already loaded
                        if fitness_data and fitness_data.get('exercises'):
                            print(f"DEBUG - Found fitness data with keys: {list(fitness_data['exercises'].keys())}")
                            self.exercise_recommendations.update_exercise_recommendations(fitness_data['exercises'])
                        else:
                            print("DEBUG - No fitness data found either")
                            self.exercise_recommendations.update_exercise_recommendations({})
                else:
                    print("No meal recommendations found in diet data")
                    self.diet_principles.update_principles([])
                    self.fitness_strategy.update_strategy({})
                    self.meal_recommendations.update_recommendations({})
                    self.exercise_recommendations.update_exercise_recommendations({})
                    
        except Exception as e:
            print(f"Error loading diet recommendations: {e}")
            import traceback
            traceback.print_exc()
            self.diet_principles.update_principles([])
            self.fitness_strategy.update_strategy({})
            self.meal_recommendations.update_recommendations({})
            self.exercise_recommendations.update_exercise_recommendations({})
            
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
            
    def _try_again(self):
        """Try again with current data - goes to capture page"""
        try:
            self.controller.show_frame("CapturePage")
        except Exception as e:
            print(f"Error trying again: {e}")
            
    def _start_new_analysis(self):
        """Start a new analysis - clears all data and goes to input page"""
        try:
            # Clear user data from state manager
            if hasattr(self.controller, 'state_manager'):
                self.controller.state_manager.user_data = {
                    "name": "",
                    "gender": "male",
                    "age": "",
                    "weight": "",
                    "height": "",
                    "goal": "Maintain Weight",
                    "activity_level": "Sedentary (little or no exercise)",
                    "allergies": []
                }
                
                # Clear analysis data if it exists
                if hasattr(self.controller.state_manager, 'analysis_data'):
                    self.controller.state_manager.analysis_data = {}
                
                # Clear any captured images
                if hasattr(self.controller.state_manager, 'image_data'):
                    self.controller.state_manager.image_data = {}
            
            # Reset capture page state
            self._clear_capture_page()
                    
            # Navigate to input page
            self.controller.show_frame("InputPage")
            
            # Clear the input form after a short delay to ensure page is loaded
            self.after(100, self._clear_input_form)
            
        except Exception as e:
            print(f"Error starting new analysis: {e}")
    
    def _clear_capture_page(self):
        """Clear the capture page state"""
        try:
            # Try to access the capture page and reset its state
            if hasattr(self.controller, 'frames') and 'CapturePage' in self.controller.frames:
                capture_page = self.controller.frames['CapturePage']
                if hasattr(capture_page, 'reset_capture_state'):
                    capture_page.reset_capture_state()
                    print("Capture page cleared successfully")
                    
            # Also clear any image data from state manager more thoroughly
            if hasattr(self.controller, 'state_manager'):
                # Clear various possible image storage locations
                attrs_to_clear = ['image_data', 'front_image', 'side_image', 'captured_images', 'analysis_images']
                for attr in attrs_to_clear:
                    if hasattr(self.controller.state_manager, attr):
                        setattr(self.controller.state_manager, attr, {})
            
            # Additional safety: directly clear input image files
            self._clear_input_image_files()
                        
        except Exception as e:
            print(f"Error clearing capture page: {e}")
    
    def _clear_input_image_files(self):
        """Directly clear input image files as backup"""
        try:
            # Get the input files directory path
            PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
            input_files_dir = os.path.join(PROJECT_DIR, "data", "input_files")
            
            # Files to clear
            files_to_clear = [
                os.path.join(input_files_dir, "input_front.png"),
                os.path.join(input_files_dir, "input_side.png")
            ]
            
            for file_path in files_to_clear:
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        print(f"Cleared input file: {file_path}")
                    except Exception as e:
                        print(f"Could not remove {file_path}: {e}")
                        
        except Exception as e:
            print(f"Error clearing input image files: {e}")
    
    def _clear_input_form(self):
        """Helper method to clear the input form"""
        try:
            # Try to access the input page and clear its form
            if hasattr(self.controller, 'frames') and 'InputPage' in self.controller.frames:
                input_page = self.controller.frames['InputPage']
                if hasattr(input_page, 'clear_form'):
                    input_page.clear_form()
        except Exception as e:
            print(f"Error clearing input form: {e}")
    
    def _export_diet_plan(self):
        """Export the current diet plan to CSV"""
        try:
            from tkinter import filedialog
            import csv
            from datetime import datetime
            
            # Ask user where to save the file
            filename = filedialog.asksaveasfilename(
                title="Export Diet Plan",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialname=f"diet_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if not filename:
                return  # User cancelled
                
            # Get current diet data
            if not hasattr(self, 'current_record') or not self.current_record:
                from tkinter import messagebox
                messagebox.showwarning("No Data", "No diet plan data available to export.")
                return
            
            # Prepare data for export
            export_data = []
            
            # Add header information
            export_data.append(["Diet Plan Export"])
            export_data.append(["Generated on:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            export_data.append([])  # Empty row
            
            # Add user information
            user_data = self.current_record.get('user_data', {})
            export_data.append(["User Information"])
            export_data.append(["Name:", user_data.get('name', 'N/A')])
            export_data.append(["Age:", user_data.get('age', 'N/A')])
            export_data.append(["Gender:", user_data.get('gender', 'N/A')])
            export_data.append(["Weight:", f"{user_data.get('weight', 'N/A')} kg"])
            export_data.append(["Height:", f"{user_data.get('height', 'N/A')} cm"])
            export_data.append(["Goal:", user_data.get('goal', 'N/A')])
            export_data.append(["Activity Level:", user_data.get('activity_level', 'N/A')])
            export_data.append([])  # Empty row
            
            # Add somatotype information
            somatotype_data = self.current_record.get('somatotype_data', {})
            export_data.append(["Somatotype Analysis"])
            export_data.append(["Classification:", somatotype_data.get('class', 'N/A')])
            export_data.append(["Ectomorph %:", somatotype_data.get('ectomorph', 'N/A')])
            export_data.append(["Mesomorph %:", somatotype_data.get('mesomorph', 'N/A')])
            export_data.append(["Endomorph %:", somatotype_data.get('endomorph', 'N/A')])
            export_data.append([])  # Empty row
            
            # Add diet recommendations
            diet_data = self.current_record.get('diet_data', {})
            if diet_data:
                export_data.append(["Daily Calorie Target"])
                export_data.append(["Total Calories:", f"{diet_data.get('daily_calories', 'N/A')} kcal"])
                export_data.append([])  # Empty row
                
                # Macronutrients
                export_data.append(["Macronutrient Distribution"])
                macros = diet_data.get('macronutrients', {})
                export_data.append(["Protein:", f"{macros.get('protein', 'N/A')}%"])
                export_data.append(["Carbohydrates:", f"{macros.get('carbs', 'N/A')}%"])
                export_data.append(["Fat:", f"{macros.get('fat', 'N/A')}%"])
                export_data.append([])  # Empty row
                
                # Meal recommendations
                meals = diet_data.get('meals', {})
                if meals:
                    export_data.append(["Recommended Meals"])
                    for meal_type, meal_data in meals.items():
                        export_data.append([f"{meal_type.title()}:"])
                        if isinstance(meal_data, list):
                            for food_item in meal_data:
                                if isinstance(food_item, dict):
                                    name = food_item.get('name', 'Unknown')
                                    calories = food_item.get('calories', 'N/A')
                                    export_data.append([f"  - {name}", f"{calories} kcal"])
                                else:
                                    export_data.append([f"  - {food_item}"])
                        export_data.append([])  # Empty row after each meal
            
            # Add fitness recommendations
            fitness_data = self.current_record.get('fitness_data', {})
            if fitness_data and fitness_data.get('exercises'):
                export_data.append(["Fitness Recommendations"])
                exercises = fitness_data.get('exercises', [])
                for exercise in exercises:
                    if isinstance(exercise, dict):
                        name = exercise.get('name', 'Unknown Exercise')
                        duration = exercise.get('duration', 'N/A')
                        export_data.append([f"- {name}", f"Duration: {duration}"])
                    else:
                        export_data.append([f"- {exercise}"])
                export_data.append([])  # Empty row
            
            # Write to CSV file
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(export_data)
            
            # Show success message
            from tkinter import messagebox
            messagebox.showinfo("Export Successful", f"Diet plan exported successfully to:\n{filename}")
            
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Export Error", f"Failed to export diet plan:\n{str(e)}")
            print(f"Error exporting diet plan: {e}")
            traceback.print_exc()


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