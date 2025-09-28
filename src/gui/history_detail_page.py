"""
History Detail Page for the Diet Recommendation System.
Shows detailed view of a historical analysis with diet recommendations and captured images.
Reuses the diet_page.py layout but loads data from the database instead of files.
"""
import customtkinter as ctk
import pandas as pd
import os
import sys
import time
from PIL import Image, ImageTk
import json
from datetime import datetime

# Configuration
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(PROJECT_DIR)

from utils.theme_manager import ThemeManager
from utils.database import DatabaseManager
from gui.diet_page import MacronutrientChart, SomatotypeVisual, CalorieInfoCard, MealBasedFoodRecommendations, ExerciseRecommendations, DietPrinciples, FitnessStrategy


class HistoryDetailPage(ctk.CTkFrame):
    """Page showing detailed view of historical analysis results"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=ThemeManager.BG_COLOR)
        self.controller = controller
        self.current_record = None
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        
        # Initialize basic layout immediately for fast load
        self._init_basic_layout()
        
        # Flag to track if content has been loaded
        self._content_loaded = False
        
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
        
        # Header with title and navigation
        self._create_header()
        
        # Main content area with scrollable container
        self._create_content_area()
        
    def _create_header(self):
        """Create page header with back button and export button"""
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=32, pady=(24, 0))
        self.header_frame.grid_columnconfigure(1, weight=1)
        
        # Back button (left aligned)
        self.back_button = ctk.CTkButton(
            self.header_frame,
            text="← Back",
            font=ctk.CTkFont(size=14),
            width=80,
            height=36,
            corner_radius=18,
            fg_color=ThemeManager.SECONDARY_COLOR,
            text_color=ThemeManager.PRIMARY_COLOR,
            hover_color=ThemeManager.GRAY_LIGHT,
            border_width=1,
            border_color=ThemeManager.PRIMARY_COLOR,
            command=self._go_back
        )
        self.back_button.grid(row=0, column=0, sticky="w")
        
        # Title section (centered)
        self.title_section = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.title_section.grid(row=0, column=1, sticky="")
        
        self.title_label = ctk.CTkLabel(
            self.title_section,
            text="Your Personalized Diet Plan",
            font=ThemeManager.get_title_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        self.title_label.grid(row=0, column=0)
        
        # Date label (updated when record is loaded)
        self.date_label = ctk.CTkLabel(
            self.title_section,
            text="Based on your body measurements and somatotype analysis",
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.GRAY_DARK
        )
        self.date_label.grid(row=1, column=0, pady=(5, 0))
        
        # Export button (right aligned)
        self.export_button = ctk.CTkButton(
            self.header_frame,
            text="📤 Export",
            font=ctk.CTkFont(size=14),
            width=100,
            height=32,
            corner_radius=16,
            fg_color=ThemeManager.PRIMARY_COLOR,
            hover_color=ThemeManager.PRIMARY_HOVER,
            command=self._export_results
        )
        self.export_button.grid(row=0, column=2, sticky="e")
        
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
        
        # Row 0: Captured Images Section
        self._create_images_section()
        
        # Row 1: User Summary
        self._create_user_summary()
        
        # Row 2: Calories & Macronutrients
        self._create_nutrition_section()
        
        # Row 3: Somatotype Visualization
        self._create_somatotype_section()
        
        # Row 4: Diet Recommendations
        self._create_diet_section()
        
    def _create_images_section(self):
        """Create section showing captured images"""
        self.images_frame = ctk.CTkFrame(
            self.content_scroll, 
            fg_color=ThemeManager.get_card_fg_color(), 
            corner_radius=10
        )
        self.images_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 15))
        self.images_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Section title
        self.images_title = ctk.CTkLabel(
            self.images_frame,
            text="📸 Captured Images",
            font=ThemeManager.get_subtitle_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        self.images_title.grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 10), sticky="w")
        
        # Front image
        self.front_image_frame = ctk.CTkFrame(self.images_frame, fg_color="transparent")
        self.front_image_frame.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        self.front_image_frame.grid_columnconfigure(0, weight=1)
        
        self.front_label = ctk.CTkLabel(
            self.front_image_frame,
            text="Front View",
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.GRAY_DARK
        )
        self.front_label.grid(row=0, column=0, pady=(0, 5))
        
        self.front_image_container = ctk.CTkFrame(
            self.front_image_frame,
            width=200,
            height=300,
            fg_color=ThemeManager.GRAY_LIGHT,
            corner_radius=8
        )
        self.front_image_container.grid(row=1, column=0, sticky="ew")
        self.front_image_container.grid_propagate(False)
        
        # Side image
        self.side_image_frame = ctk.CTkFrame(self.images_frame, fg_color="transparent")
        self.side_image_frame.grid(row=1, column=1, padx=15, pady=(0, 15), sticky="nsew")
        self.side_image_frame.grid_columnconfigure(0, weight=1)
        
        self.side_label = ctk.CTkLabel(
            self.side_image_frame,
            text="Side View",
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.GRAY_DARK
        )
        self.side_label.grid(row=0, column=0, pady=(0, 5))
        
        self.side_image_container = ctk.CTkFrame(
            self.side_image_frame,
            width=200,
            height=300,
            fg_color=ThemeManager.GRAY_LIGHT,
            corner_radius=8
        )
        self.side_image_container.grid(row=1, column=0, sticky="ew")
        self.side_image_container.grid_propagate(False)
        
    def _create_user_summary(self):
        """Create user summary section"""
        self.user_summary_frame = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        self.user_summary_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15))
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
        self.calories_card.grid(row=2, column=0, sticky="nsew", padx=(0, 10), pady=(0, 15))
        
        # Macronutrient chart container
        self.macro_frame = ctk.CTkFrame(
            self.content_scroll, 
            fg_color=ThemeManager.get_card_fg_color(), 
            corner_radius=10
        )
        self.macro_frame.grid(row=2, column=1, sticky="nsew", padx=(10, 0), pady=(0, 15))
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
        self.soma_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(0, 15))
        self.soma_frame.grid_columnconfigure(0, weight=1)
        
        # Somatotype visualization (initialized when data is loaded)
        self.soma_visual = None
        
    def _create_diet_section(self):
        """Create diet recommendations section with improved two-column layout"""
        # Diet principles and fitness strategy in two columns
        self.diet_principles = DietPrinciples(self.content_scroll)
        self.diet_principles.grid(row=4, column=0, sticky="nsew", pady=(0, 15), padx=(0, 10))
        
        self.fitness_strategy = FitnessStrategy(self.content_scroll)
        self.fitness_strategy.grid(row=4, column=1, sticky="nsew", pady=(0, 15), padx=(10, 0))
        
        # Meal recommendations section with food click callback (full width)
        self.meal_recommendations = HistoryMealBasedFoodRecommendations(self.content_scroll)
        self.meal_recommendations.grid(row=5, column=0, columnspan=2, sticky="nsew", pady=(0, 15))
        
        # Exercise recommendations section (full width)
        self.exercise_recommendations = HistoryExerciseRecommendations(self.content_scroll)
        self.exercise_recommendations.grid(row=6, column=0, columnspan=2, sticky="nsew", pady=(0, 15))
        
    def load_record_data(self, record_data):
        """Load and display data from a history record"""
        try:
            self.current_record = record_data
            
            # Update header
            session_date = record_data.get('session_date', '')
            if session_date:
                formatted_date = self._format_date(session_date)
                self.date_label.configure(text=f"Based on analysis from {formatted_date}")
            else:
                self.date_label.configure(text="Based on your body measurements and somatotype analysis")
            
            # Update user summary
            name = record_data.get('name', 'Unknown User')
            gender = record_data.get('gender', 'Unknown')
            age = record_data.get('age', 'N/A')
            goal = record_data.get('goal', 'Not specified')
            
            self.user_info.configure(text=f"Diet Plan for {name}")
            self.body_info.configure(text=f"{gender.title()}, {age} years old | Goal: {goal}")
            
            # Load captured images
            self._load_captured_images(record_data)
            
            # Load nutrition data
            self._load_nutrition_data(record_data)
            
            # Load somatotype data
            self._load_somatotype_data(record_data)
            
            # Load diet recommendations
            self._load_diet_recommendations(record_data)
            
        except Exception as e:
            print(f"Error loading record data: {e}")
            self._show_error(f"Failed to load analysis details: {str(e)}")
            
    def _load_captured_images(self, record_data):
        """Load and display captured images"""
        try:
            front_image_path = record_data.get('front_image_path')
            side_image_path = record_data.get('side_image_path')
            
            # Load front image
            if front_image_path and os.path.exists(front_image_path):
                self._load_image_to_container(front_image_path, self.front_image_container)
            else:
                self._show_image_placeholder(self.front_image_container, "Front image not available")
                
            # Load side image
            if side_image_path and os.path.exists(side_image_path):
                self._load_image_to_container(side_image_path, self.side_image_container)
            else:
                self._show_image_placeholder(self.side_image_container, "Side image not available")
                
        except Exception as e:
            print(f"Error loading images: {e}")
            self._show_image_placeholder(self.front_image_container, "Error loading image")
            self._show_image_placeholder(self.side_image_container, "Error loading image")
            
    def _load_image_to_container(self, image_path, container):
        """Load an image and display it in the container"""
        try:
            # Open and resize image
            img = Image.open(image_path)
            
            # Calculate size to fit container while maintaining aspect ratio
            container_width = 200
            container_height = 300
            
            img_width, img_height = img.size
            aspect_ratio = img_width / img_height
            
            if aspect_ratio > container_width / container_height:
                # Image is wider, fit to width
                new_width = container_width
                new_height = int(container_width / aspect_ratio)
            else:
                # Image is taller, fit to height
                new_height = container_height
                new_width = int(container_height * aspect_ratio)
            
            # Resize image
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            # Clear container and add image
            for widget in container.winfo_children():
                widget.destroy()
                
            image_label = ctk.CTkLabel(
                container,
                image=photo,
                text=""
            )
            image_label.image = photo  # Keep a reference
            image_label.place(relx=0.5, rely=0.5, anchor="center")
            
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            self._show_image_placeholder(container, "Error loading image")
            
    def _show_image_placeholder(self, container, message):
        """Show placeholder when image cannot be loaded"""
        for widget in container.winfo_children():
            widget.destroy()
            
        placeholder_label = ctk.CTkLabel(
            container,
            text=f"📷\n{message}",
            font=ctk.CTkFont(size=14),
            text_color=ThemeManager.GRAY_MEDIUM,
            justify="center"
        )
        placeholder_label.place(relx=0.5, rely=0.5, anchor="center")
        
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
            
    def _format_date(self, date_string):
        """Format date string for display"""
        if not date_string:
            return "Unknown Date"
        try:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.strftime("%B %d, %Y at %I:%M %p")
        except:
            return date_string
            
    def _show_error(self, message):
        """Show error message to user"""
        error_dialog = ctk.CTkToplevel(self)
        error_dialog.title("Error")
        error_dialog.geometry("400x200")
        error_dialog.transient(self)
        error_dialog.grab_set()
        
        # Center the dialog
        error_dialog.grid_columnconfigure(0, weight=1)
        error_dialog.grid_rowconfigure(0, weight=1)
        
        error_label = ctk.CTkLabel(
            error_dialog,
            text=message,
            font=ctk.CTkFont(size=14),
            text_color=ThemeManager.GRAY_DARK,
            wraplength=350,
            justify="center"
        )
        error_label.grid(row=0, column=0, padx=20, pady=20)
        
        close_button = ctk.CTkButton(
            error_dialog,
            text="Close",
            command=error_dialog.destroy
        )
        close_button.grid(row=1, column=0, pady=(0, 20))
    
    def _go_back(self):
        """Navigate back to history page"""
        try:
            self.controller.show_frame("HistoryPage")
        except Exception as e:
            print(f"Error navigating back: {e}")
        
    def _export_results(self):
        """Export analysis results to PDF"""
        if not self.current_record:
            self._show_error("No analysis data available to export.")
            return
        
        try:
            # Import PDF exporter
            from utils.pdf_exporter import PDFExporter, create_export_directory, generate_export_filename
            
            # Show progress dialog
            progress_dialog = self._create_progress_dialog("Generating PDF report...")
            self.update()
            
            # Create exporter and generate PDF
            exporter = PDFExporter()
            export_dir = create_export_directory()
            filename = generate_export_filename(self.current_record, is_history=True)
            output_path = os.path.join(export_dir, filename)
            
            # Export to PDF
            success = exporter.export_history_detail(self.current_record, output_path)
            
            # Close progress dialog
            progress_dialog.destroy()
            
            if success:
                self._show_export_success_dialog(output_path)
            else:
                self._show_error("Failed to generate PDF report. Please check the logs for details.")
                
        except ImportError as e:
            self._show_error(f"PDF export dependencies not installed. Please install required packages:\n{str(e)}")
        except Exception as e:
            print(f"Export error: {e}")
            self._show_error(f"An error occurred while generating the PDF report:\n{str(e)}")
            
    def _create_progress_dialog(self, message):
        """Create a progress dialog"""
        progress_dialog = ctk.CTkToplevel(self)
        progress_dialog.title("Exporting...")
        progress_dialog.geometry("350x120")
        progress_dialog.transient(self)
        progress_dialog.grab_set()
        
        # Center the dialog
        progress_dialog.update_idletasks()
        x = (progress_dialog.winfo_screenwidth() // 2) - (350 // 2)
        y = (progress_dialog.winfo_screenheight() // 2) - (120 // 2)
        progress_dialog.geometry(f"350x120+{x}+{y}")
        
        # Progress message
        progress_label = ctk.CTkLabel(
            progress_dialog,
            text=message,
            font=ctk.CTkFont(size=14),
            text_color=ThemeManager.GRAY_DARK
        )
        progress_label.pack(expand=True)
        
        # Progress bar
        progress_bar = ctk.CTkProgressBar(progress_dialog)
        progress_bar.pack(padx=20, pady=(0, 20), fill="x")
        progress_bar.set(0.8)  # Show indeterminate progress
        
        return progress_dialog
        
    def _show_export_success_dialog(self, file_path):
        """Show success dialog with options to open file or folder"""
        success_dialog = ctk.CTkToplevel(self)
        success_dialog.title("Export Successful")
        success_dialog.geometry("450x200")
        success_dialog.transient(self)
        success_dialog.grab_set()
        
        # Center the dialog
        success_dialog.update_idletasks()
        x = (success_dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (success_dialog.winfo_screenheight() // 2) - (200 // 2)
        success_dialog.geometry(f"450x200+{x}+{y}")
        
        # Success message
        success_label = ctk.CTkLabel(
            success_dialog,
            text="✅ PDF report generated successfully!",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        success_label.pack(pady=(20, 10))
        
        # File path
        file_label = ctk.CTkLabel(
            success_dialog,
            text=f"Saved to:\n{file_path}",
            font=ctk.CTkFont(size=11),
            text_color=ThemeManager.GRAY_MEDIUM,
            wraplength=400,
            justify="center"
        )
        file_label.pack(pady=(0, 20))
        
        # Buttons
        button_frame = ctk.CTkFrame(success_dialog, fg_color="transparent")
        button_frame.pack(pady=(0, 20))
        
        # Open file button
        open_file_btn = ctk.CTkButton(
            button_frame,
            text="Open PDF",
            command=lambda: self._open_file(file_path),
            fg_color=ThemeManager.PRIMARY_COLOR,
            hover_color=ThemeManager.PRIMARY_HOVER
        )
        open_file_btn.pack(side="left", padx=(0, 10))
        
        # Open folder button
        open_folder_btn = ctk.CTkButton(
            button_frame,
            text="Open Folder",
            command=lambda: self._open_folder(file_path),
            fg_color=ThemeManager.SECONDARY_COLOR,
            text_color=ThemeManager.PRIMARY_COLOR,
            hover_color=ThemeManager.GRAY_LIGHT,
            border_width=1,
            border_color=ThemeManager.PRIMARY_COLOR
        )
        open_folder_btn.pack(side="left", padx=(10, 10))
        
        # Close button
        close_btn = ctk.CTkButton(
            button_frame,
            text="Close",
            command=success_dialog.destroy,
            fg_color=ThemeManager.GRAY_MEDIUM,
            hover_color=ThemeManager.GRAY_DARK
        )
        close_btn.pack(side="left", padx=(10, 0))
        
    def _open_file(self, file_path):
        """Open the exported PDF file"""
        try:
            import subprocess
            import platform
            
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', file_path])
            else:  # Linux
                subprocess.run(['xdg-open', file_path])
        except Exception as e:
            print(f"Error opening file: {e}")
            self._show_error(f"Could not open file: {str(e)}")
            
    def _open_folder(self, file_path):
        """Open the folder containing the exported file"""
        try:
            import subprocess
            import platform
            
            folder_path = os.path.dirname(file_path)
            
            if platform.system() == 'Windows':
                subprocess.run(['explorer', folder_path])
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', folder_path])
            else:  # Linux
                subprocess.run(['xdg-open', folder_path])
        except Exception as e:
            print(f"Error opening folder: {e}")
            self._show_error(f"Could not open folder: {str(e)}")
        
    # def _delete_record(self):
    #     """Delete the current record after confirmation"""
    #     # TODO: Implement delete functionality with confirmation dialog
    #     print("Delete functionality not yet implemented")
        
    # def _rerun_analysis(self):
    #     """Rerun analysis with the same parameters"""
    #     # TODO: Implement rerun functionality
    #     print("Rerun functionality not yet implemented")
        
    # def _go_back(self):
    #     """Go back to history page"""
    #     self.controller.show_frame("HistoryPage")
        
    def on_show(self):
        """Called when page is shown"""
        # Load content lazily when page is first shown
        self.load_content()
        
        # Load the current record data if available
        if hasattr(self.controller, 'current_history_record') and self.controller.current_history_record:
            if hasattr(self, 'load_record_data'):
                self.load_record_data(self.controller.current_history_record)
    
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
    

class HistoryMealBasedFoodRecommendations(MealBasedFoodRecommendations):
    """Custom MealBasedFoodRecommendations with modal support for history detail page"""
    
    def _show_food_details(self, food_data):
        """Show detailed food information in a modal"""
        try:
            from gui.diet_page import MacronutrientDetailModal
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


class HistoryExerciseRecommendations(ExerciseRecommendations):
    """Custom ExerciseRecommendations with modal support for history detail page"""
    
    def _show_exercise_details(self, exercise_data):
        """Show detailed exercise information in a modal window"""
        try:
            from gui.diet_page import ExerciseDetailModal
            ExerciseDetailModal(self, exercise_data)
        except Exception as e:
            print(f"Error showing exercise details: {e}")


if __name__ == "__main__":
    import sys
    import os
    # Add parent directory to path for imports
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    # Test the history detail page
    class DummyController:
        def __init__(self):
            self.current_history_record = {
                'session_id': 1,
                'name': 'John Doe',
                'gender': 'male',
                'age': 25,
                'goal': 'Build Muscle',
                'session_date': '2024-01-15T10:30:00',
                'calories': 2500,
                'front_image_path': '',
                'side_image_path': '',
                'somatotype_class': 'Mesomorph'
            }
            
        def show_frame(self, frame_name):
            print(f"Navigating to: {frame_name}")
    
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.title("History Detail Page Test")
    root.geometry("1200x800")
    
    ThemeManager.setup_theme()
    
    controller = DummyController()
    app = HistoryDetailPage(root, controller)
    app.pack(fill="both", expand=True)
    app.on_show()
    
    root.mainloop()