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
from src.utils.theme_manager import ThemeManager, IMAGES_DIR

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

class MacronutrientDetailModal(ctk.CTkToplevel):
    """Modal window showing detailed macronutrient information for a food item"""
    
    def __init__(self, parent, food_data):
        super().__init__(parent)
        self.food_data = food_data

        # Window setup - wrap window manager calls to avoid invalid handle errors
        try:
            self.title("Food Nutrition Details")
        except Exception:
            pass

        try:
            self.geometry("500x600")
            self.resizable(False, False)
        except Exception:
            # Some platforms may not support geometry calls on certain toplevels
            pass

        # Try to set transient and grab, but don't crash if OS-level handles are invalid
        try:
            if parent is not None:
                try:
                    self.transient(parent)
                except Exception:
                    # transient may fail if parent handle is invalid
                    pass

            try:
                self.grab_set()
            except Exception:
                # grab_set can raise TclError on some systems or if called from non-main thread
                pass
        except Exception:
            # Ignore any errors related to window manager operations
            pass

        # Configure
        try:
            self.configure(fg_color=ThemeManager.BG_COLOR)
        except Exception:
            pass
        try:
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(1, weight=1)
        except Exception:
            pass
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color=ThemeManager.get_card_fg_color(), corner_radius=10)
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Food name
        food_name = ctk.CTkLabel(
            header_frame,
            text=food_data.get('Food_Item', 'Unknown Food'),
            font=ThemeManager.get_title_font(),
            text_color=ThemeManager.PRIMARY_COLOR,
            wraplength=450
        )
        food_name.grid(row=0, column=0, padx=20, pady=15)
        
        # Category and portion
        category_text = f"Category: {food_data.get('Enhanced_Category', 'N/A').title().replace('_', ' ')}"
        portion_text = f"Recommended Portion: {food_data.get('Portion_Recommendation', 'N/A')}"
        
        category_label = ctk.CTkLabel(
            header_frame,
            text=f"{category_text} | {portion_text}",
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.GRAY_MEDIUM
        )
        category_label.grid(row=1, column=0, padx=20, pady=(0, 15))
        
        # Scrollable content
        content_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        content_scroll.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        content_scroll.grid_columnconfigure(0, weight=1)
        
        # Main macronutrients
        macro_frame = ctk.CTkFrame(content_scroll, fg_color=ThemeManager.get_card_fg_color(), corner_radius=10)
        macro_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        macro_frame.grid_columnconfigure((0, 1), weight=1)
        
        macro_title = ctk.CTkLabel(
            macro_frame,
            text="Macronutrients (per 100g)",
            font=ThemeManager.get_subtitle_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        macro_title.grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 10))
        
        # Main macros
        self._create_nutrient_row(macro_frame, "Calories", f"{food_data.get('Calories_kcal', 0):.0f} kcal", 1, 0)
        self._create_nutrient_row(macro_frame, "Protein", f"{food_data.get('Protein_g', 0):.1f} g", 2, 0)
        self._create_nutrient_row(macro_frame, "Carbohydrates", f"{food_data.get('Carbohydrates_g', 0):.1f} g", 1, 1)
        self._create_nutrient_row(macro_frame, "Fat", f"{food_data.get('Fat_g', 0):.1f} g", 2, 1)
        
        # Additional nutrients
        additional_frame = ctk.CTkFrame(content_scroll, fg_color=ThemeManager.get_card_fg_color(), corner_radius=10)
        additional_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        additional_frame.grid_columnconfigure((0, 1), weight=1)
        
        additional_title = ctk.CTkLabel(
            additional_frame,
            text="Additional Nutrients",
            font=ThemeManager.get_subtitle_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        additional_title.grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 10))
        
        self._create_nutrient_row(additional_frame, "Fiber", f"{food_data.get('Fiber_g', 0):.1f} g", 1, 0)
        self._create_nutrient_row(additional_frame, "Sugars", f"{food_data.get('Sugars_g', 0):.1f} g", 2, 0)
        self._create_nutrient_row(additional_frame, "Sodium", f"{food_data.get('Sodium_mg', 0):.0f} mg", 1, 1)
        self._create_nutrient_row(additional_frame, "Cholesterol", f"{food_data.get('Cholesterol_mg', 0):.0f} mg", 2, 1)
        
        # Somatotype scores
        scores_frame = ctk.CTkFrame(content_scroll, fg_color=ThemeManager.get_card_fg_color(), corner_radius=10)
        scores_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        scores_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        scores_title = ctk.CTkLabel(
            scores_frame,
            text="Body Type Suitability Scores",
            font=ThemeManager.get_subtitle_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        scores_title.grid(row=0, column=0, columnspan=3, padx=15, pady=(15, 10))
        
        self._create_score_item(scores_frame, "Ectomorph", food_data.get('Ectomorph_Score', 0), 1, 0)
        self._create_score_item(scores_frame, "Mesomorph", food_data.get('Mesomorph_Score', 0), 1, 1)
        self._create_score_item(scores_frame, "Endomorph", food_data.get('Endomorph_Score', 0), 1, 2)
        
        # Close button
        close_btn = ctk.CTkButton(
            self,
            text="Close",
            command=self.destroy,
            font=ThemeManager.get_label_font(),
            fg_color=ThemeManager.PRIMARY_COLOR,
            hover_color=ThemeManager.PRIMARY_HOVER
        )
        close_btn.grid(row=2, column=0, pady=20)
        
        # Ensure the window can be closed cleanly and shown properly
        try:
            self.protocol("WM_DELETE_WINDOW", self.destroy)
        except Exception:
            pass
            
        # Focus the modal window
        try:
            self.lift()
            self.focus_force()
        except Exception:
            # If focus fails, just continue - the modal is still created
            pass
    
    def _create_nutrient_row(self, parent, label, value, row, col):
        """Create a nutrient information row"""
        nutrient_frame = ctk.CTkFrame(parent, fg_color="transparent")
        nutrient_frame.grid(row=row, column=col, padx=15, pady=5, sticky="ew")
        
        label_widget = ctk.CTkLabel(
            nutrient_frame,
            text=f"{label}:",
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.GRAY_DARK,
            anchor="w"
        )
        label_widget.pack(anchor="w")
        
        value_widget = ctk.CTkLabel(
            nutrient_frame,
            text=value,
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.PRIMARY_COLOR,
            anchor="w"
        )
        value_widget.pack(anchor="w")
    
    def _create_score_item(self, parent, label, score, row, col):
        """Create a somatotype score item"""
        score_frame = ctk.CTkFrame(parent, fg_color="transparent")
        score_frame.grid(row=row, column=col, padx=10, pady=10)
        
        # Score circle
        score_color = ThemeManager.SUCCESS_COLOR if score >= 7 else ThemeManager.WARNING_COLOR if score >= 5 else ThemeManager.DANGER_COLOR
        
        circle = ctk.CTkFrame(
            score_frame,
            width=50,
            height=50,
            corner_radius=25,
            fg_color=score_color,
            border_width=2,
            border_color=ThemeManager.GRAY_LIGHT
        )
        circle.pack()
        circle.grid_propagate(False)
        
        score_label = ctk.CTkLabel(
            circle,
            text=str(int(score)),
            font=ThemeManager.get_label_font(),
            text_color="white"
        )
        score_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Label
        name_label = ctk.CTkLabel(
            score_frame,
            text=label,
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.GRAY_DARK
        )
        name_label.pack(pady=(5, 0))

class FoodCard(ctk.CTkFrame):
    """Individual food card with macronutrient preview"""
    
    def __init__(self, parent, food_data, on_click_callback=None):
        super().__init__(parent, 
                         corner_radius=12, 
                         fg_color=ThemeManager.get_card_fg_color(),
                         border_width=1,
                         border_color=ThemeManager.GRAY_LIGHT)
        
        self.food_data = food_data
        self.on_click_callback = on_click_callback
        
        # Fixed width for horizontal scrolling
        self.configure(width=280, height=140)
        self.grid_propagate(False)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Food name
        self.name_label = ctk.CTkLabel(
            self,
            text=food_data.get('Food_Item', 'Unknown Food'),
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.PRIMARY_COLOR,
            wraplength=260,
            anchor="w",
            justify="left"
        )
        self.name_label.grid(row=0, column=0, padx=12, pady=(12, 5), sticky="ew")
        
        # Macro preview
        calories = food_data.get('Calories_kcal', 0)
        protein = food_data.get('Protein_g', 0)
        carbs = food_data.get('Carbohydrates_g', 0)
        fat = food_data.get('Fat_g', 0)
        
        macro_text = f"{calories:.0f} kcal • {protein:.1f}g protein • {carbs:.1f}g carbs • {fat:.1f}g fat"
        
        self.macro_label = ctk.CTkLabel(
            self,
            text=macro_text,
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.GRAY_MEDIUM,
            wraplength=260,
            anchor="w",
            justify="left"
        )
        self.macro_label.grid(row=1, column=0, padx=12, pady=(0, 5), sticky="ew")
        
        # Portion and category info
        portion = food_data.get('Portion_Recommendation', 'N/A')
        category = food_data.get('Enhanced_Category', 'other').title().replace('_', ' ')
        
        info_text = f"Portion: {portion} | {category}"
        
        self.info_label = ctk.CTkLabel(
            self,
            text=info_text,
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.GRAY_MEDIUM,
            wraplength=260,
            anchor="w",
            justify="left"
        )
        self.info_label.grid(row=2, column=0, padx=12, pady=(0, 5), sticky="new")
        
        # Click to view more button
        self.more_btn = ctk.CTkButton(
            self,
            text="View Details",
            font=ThemeManager.get_small_font(),
            fg_color=ThemeManager.PRIMARY_COLOR,
            hover_color=ThemeManager.PRIMARY_HOVER,
            height=28,
            command=self._on_card_clicked
        )
        self.more_btn.grid(row=3, column=0, padx=12, pady=(0, 12), sticky="ew")
        
        # Make the entire card clickable
        self.bind("<Button-1>", lambda e: self._on_card_clicked())
        self.name_label.bind("<Button-1>", lambda e: self._on_card_clicked())
        self.macro_label.bind("<Button-1>", lambda e: self._on_card_clicked())
        self.info_label.bind("<Button-1>", lambda e: self._on_card_clicked())
    
    def _on_card_clicked(self):
        """Handle card click to show detailed nutrition info"""
        try:
            if self.on_click_callback:
                # If caller provided a callback, use it
                self.on_click_callback(self.food_data)
                return

            # Get the toplevel window safely
            try:
                parent = self.winfo_toplevel()
                # Use after() to schedule modal creation on main thread
                parent.after(0, lambda: self._create_modal_safely(parent, self.food_data))
            except Exception as inner_e:
                raise inner_e

        except Exception as e:
            # Log the error
            import traceback
            print(f"Error in _on_card_clicked: {e}")
            traceback.print_exc()

            # Show error message safely
            try:
                import tkinter as tk
                from tkinter import messagebox
                messagebox.showerror("Error", f"Could not open food details: {str(e)}")
            except:
                print(f"Could not show error dialog: {e}")
                
    def _create_modal_safely(self, parent, food_data):
        """Safely create the modal window"""
        try:
            MacronutrientDetailModal(parent, food_data)
        except Exception as e:
            print(f"Error creating modal: {e}")
            import traceback
            traceback.print_exc()
            
            try:
                import tkinter as tk
                from tkinter import messagebox
                messagebox.showerror("Error", f"Could not open food details: {str(e)}", parent=parent)
            except:
                print("Could not show error dialog")

class MealCategoryCard(ctk.CTkFrame):
    """Card showing foods for a specific meal category with horizontal scrolling"""
    
    def __init__(self, parent, meal_type, foods_data, on_food_click=None):
        super().__init__(parent, corner_radius=15, fg_color=ThemeManager.get_card_fg_color())
        
        self.meal_type = meal_type
        self.foods_data = foods_data or []
        self.on_food_click = on_food_click
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header with meal type and count
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        
        meal_icon = {"breakfast": "🌅", "lunch": "☀️", "dinner": "🌙", "snack": "🍎"}
        
        self.header_label = ctk.CTkLabel(
            header_frame,
            text=f"{meal_icon.get(meal_type.lower(), '🍽️')} {meal_type.title()} ({len(self.foods_data)} options)",
            font=ThemeManager.get_subtitle_font(),
            text_color=ThemeManager.PRIMARY_COLOR,
            anchor="w"
        )
        self.header_label.grid(row=0, column=0, sticky="w")
        
        # Horizontal scrollable food container
        if self.foods_data:
            self.food_container = ctk.CTkScrollableFrame(
                self,
                orientation="horizontal",
                fg_color=ThemeManager.BG_COLOR,
                corner_radius=10,
                height=160
            )
            self.food_container.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
            
            # Add food cards horizontally
            for i, food_data in enumerate(self.foods_data):
                food_card = FoodCard(
                    self.food_container, 
                    food_data, 
                    on_click_callback=self.on_food_click
                )
                food_card.grid(row=0, column=i, padx=(0, 12), sticky="ns")
        else:
            # No foods available message
            no_foods_frame = ctk.CTkFrame(self, fg_color=ThemeManager.GRAY_LIGHT, corner_radius=10, height=100)
            no_foods_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
            no_foods_frame.grid_propagate(False)
            
            no_foods_label = ctk.CTkLabel(
                no_foods_frame,
                text=f"No {meal_type.lower()} options available",
                font=ThemeManager.get_label_font(),
                text_color=ThemeManager.GRAY_MEDIUM
            )
            no_foods_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def update_foods(self, foods_data):
        """Update the foods in this meal category"""
        self.foods_data = foods_data or []
        
        # Update header count
        meal_icon = {"breakfast": "🌅", "lunch": "☀️", "dinner": "🌙", "snack": "🍎"}
        self.header_label.configure(
            text=f"{meal_icon.get(self.meal_type.lower(), '🍽️')} {self.meal_type.title()} ({len(self.foods_data)} options)"
        )
        
        # Clear and rebuild food container
        if hasattr(self, 'food_container'):
            self.food_container.destroy()
        
        if self.foods_data:
            self.food_container = ctk.CTkScrollableFrame(
                self,
                orientation="horizontal",
                fg_color=ThemeManager.BG_COLOR,
                corner_radius=10,
                height=160
            )
            self.food_container.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
            
            # Add food cards horizontally
            for i, food_data in enumerate(self.foods_data):
                food_card = FoodCard(
                    self.food_container, 
                    food_data, 
                    on_click_callback=self.on_food_click
                )
                food_card.grid(row=0, column=i, padx=(0, 12), sticky="ns")

class MealBasedFoodRecommendations(ctk.CTkFrame):
    """Component showing food recommendations categorized by meal type"""
    
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
        
        # Meal category containers
        self.meal_cards = {}
        self.current_row = 1
        
        # Initialize with empty meal categories
        self.init_meal_categories()
    
    def init_meal_categories(self):
        """Initialize empty meal category cards"""
        meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
        
        for i, meal_type in enumerate(meal_types):
            meal_card = MealCategoryCard(
                self, 
                meal_type, 
                [], 
                on_food_click=self._show_food_details
            )
            meal_card.grid(row=self.current_row + i, column=0, sticky="ew", pady=(0, 15))
            self.meal_cards[meal_type] = meal_card
    
    def update_recommendations(self, meal_recommendations):
        """Update all meal recommendations"""
        for meal_type, foods in meal_recommendations.items():
            if meal_type in self.meal_cards:
                self.meal_cards[meal_type].update_foods(foods)
    
    def _show_food_details(self, food_data):
        """Show detailed nutrition information for a food item"""
        try:
            # Get the actual root window to avoid handle issues
            root = self.winfo_toplevel()
            # Use after() to create modal on main thread
            root.after(0, lambda: self._create_modal_safely(root, food_data))
        except Exception as e:
            print(f"Error showing food details: {e}")
            import traceback
            traceback.print_exc()
            
    def _create_modal_safely(self, parent, food_data):
        """Safely create the modal window"""
        try:
            MacronutrientDetailModal(parent, food_data)
        except Exception as e:
            print(f"Error creating modal: {e}")
            # Show simple error message
            try:
                import tkinter as tk
                from tkinter import messagebox
                messagebox.showerror("Error", f"Could not open food details: {str(e)}", parent=parent)
            except:
                print("Could not show error dialog")

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
        
        # Fourth row: Meal-based food recommendations
        self.meal_recommendations = MealBasedFoodRecommendations(self.content_scroll)
        self.meal_recommendations.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(0, 15))
        
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
        """Process and display diet recommendation data using the new diet engine"""
        try:
            # Import diet engine
            from src.recommendation.diet_engine import DietRecommendationEngine
            
            # Initialize the diet engine
            engine = DietRecommendationEngine()
            
            # Generate meal-based recommendations
            meal_recommendations = engine.generate_meal_based_recommendations()
            
            # Store meal recommendations data for testing/debugging
            self.meal_recommendations_data = meal_recommendations
            
            # Also get comprehensive recommendations for macronutrient data
            comprehensive_recs = engine.generate_comprehensive_recommendations()
            macros = comprehensive_recs.get('macros', {})
            
            # Extract macronutrient percentages
            total_calories = macros.get('calories', 2000)
            protein_g = macros.get('protein_g', 150)
            carbs_g = macros.get('carbs_g', 200)
            fat_g = macros.get('fat_g', 70)
            
            # Calculate percentages
            protein_cal = protein_g * 4
            carbs_cal = carbs_g * 4
            fat_cal = fat_g * 9
            
            protein_pct = int((protein_cal / total_calories) * 100) if total_calories > 0 else 30
            carbs_pct = int((carbs_cal / total_calories) * 100) if total_calories > 0 else 45
            fat_pct = int((fat_cal / total_calories) * 100) if total_calories > 0 else 25
            
            # Ensure percentages add up to 100
            total_pct = protein_pct + carbs_pct + fat_pct
            if total_pct != 100:
                diff = 100 - total_pct
                carbs_pct += diff  # Adjust carbs if there's a difference
            
            # Create and place the macronutrient chart 
            if self.macro_chart:
                self.macro_chart.destroy()
            
            self.macro_chart = MacronutrientChart(
                self.macro_frame, 
                protein=protein_pct, 
                carbs=carbs_pct, 
                fat=fat_pct
            )
            self.macro_chart.pack(fill="both", expand=True, padx=15, pady=15)
            
            # Update calorie info
            goal = macros.get('goal', 'maintain_weight').replace('_', ' ').title()
            self.calories_card.update_values(int(total_calories), goal)
            
            # Update meal-based food recommendations
            self.meal_recommendations.update_recommendations(meal_recommendations)
            
        except Exception as e:
            print(f"Error processing recommendation data: {str(e)}")
            # Fallback to basic display
            self._show_fallback_recommendations()
    
    def _show_fallback_recommendations(self):
        """Show fallback recommendations when data loading fails"""
        try:
            # Set default macronutrient chart
            if self.macro_chart:
                self.macro_chart.destroy()
            
            self.macro_chart = MacronutrientChart(
                self.macro_frame, 
                protein=30, 
                carbs=45, 
                fat=25
            )
            self.macro_chart.pack(fill="both", expand=True, padx=15, pady=15)
            
            # Set default calorie info
            self.calories_card.update_values(2000, "Maintain Weight")
            
            # Set fallback meal recommendations
            fallback_meals = {
                'breakfast': [
                    {
                        'Food_Item': 'Greek Yogurt',
                        'Enhanced_Category': 'dairy_proteins',
                        'Calories_kcal': 150,
                        'Protein_g': 15,
                        'Carbohydrates_g': 20,
                        'Fat_g': 3,
                        'Fiber_g': 3,
                        'Sugars_g': 15,
                        'Sodium_mg': 50,
                        'Portion_Recommendation': '150-200g',
                        'Overall_Quality': 9,
                        'Ectomorph_Score': 8,
                        'Mesomorph_Score': 9,
                        'Endomorph_Score': 7,
                        'Cholesterol_mg': 10
                    }
                ],
                'lunch': [
                    {
                        'Food_Item': 'Chicken Breast',
                        'Enhanced_Category': 'lean_proteins',
                        'Calories_kcal': 165,
                        'Protein_g': 31,
                        'Carbohydrates_g': 0,
                        'Fat_g': 3.6,
                        'Fiber_g': 0,
                        'Sugars_g': 0,
                        'Sodium_mg': 74,
                        'Portion_Recommendation': '100-150g',
                        'Overall_Quality': 9,
                        'Ectomorph_Score': 7,
                        'Mesomorph_Score': 9,
                        'Endomorph_Score': 8,
                        'Cholesterol_mg': 85
                    }
                ],
                'dinner': [
                    {
                        'Food_Item': 'Salmon',
                        'Enhanced_Category': 'healthy_fats',
                        'Calories_kcal': 208,
                        'Protein_g': 28.5,
                        'Carbohydrates_g': 0,
                        'Fat_g': 9.1,
                        'Fiber_g': 0,
                        'Sugars_g': 0,
                        'Sodium_mg': 69,
                        'Portion_Recommendation': '100-150g',
                        'Overall_Quality': 10,
                        'Ectomorph_Score': 8,
                        'Mesomorph_Score': 9,
                        'Endomorph_Score': 8,
                        'Cholesterol_mg': 70
                    }
                ],
                'snack': [
                    {
                        'Food_Item': 'Mixed Nuts',
                        'Enhanced_Category': 'healthy_fats',
                        'Calories_kcal': 607,
                        'Protein_g': 20,
                        'Carbohydrates_g': 21,
                        'Fat_g': 54,
                        'Fiber_g': 8,
                        'Sugars_g': 4,
                        'Sodium_mg': 16,
                        'Portion_Recommendation': '30-40g',
                        'Overall_Quality': 8,
                        'Ectomorph_Score': 9,
                        'Mesomorph_Score': 8,
                        'Endomorph_Score': 6,
                        'Cholesterol_mg': 0
                    }
                ]
            }
            
            # Store fallback meal recommendations data for testing/debugging
            self.meal_recommendations_data = fallback_meals
            
            self.meal_recommendations.update_recommendations(fallback_meals)
            
        except Exception as e:
            print(f"Error showing fallback recommendations: {str(e)}")
    
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