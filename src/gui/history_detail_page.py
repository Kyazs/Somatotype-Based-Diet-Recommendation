"""
History Detail Page for the Diet Recommendation System.
Shows detailed view of a historical analysis with diet recommendations and captured images.
Reuses the diet_page.py layout but loads data from the database instead of files.
"""
import customtkinter as ctk
import pandas as pd
import os
import sys
from PIL import Image, ImageTk
import json
from datetime import datetime

# Configuration
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(PROJECT_DIR)

from utils.theme_manager import ThemeManager
from utils.database import DatabaseManager
from gui.diet_page import MacronutrientChart, SomatotypeVisual, CalorieInfoCard, MealBasedFoodRecommendations


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
            text="← Back to History",
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
            text="Analysis Details",
            font=ThemeManager.get_title_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        self.title_label.grid(row=0, column=0)
        
        # Date label (updated when record is loaded)
        self.date_label = ctk.CTkLabel(
            self.title_section,
            text="",
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.GRAY_DARK
        )
        self.date_label.grid(row=1, column=0, pady=(5, 0))
        
        # Export button
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
        """Create diet recommendations section"""
        self.meal_recommendations = MealBasedFoodRecommendations(self.content_scroll)
        self.meal_recommendations.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=(0, 15))
        
    def _create_footer(self):
        """Create footer with action buttons"""
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.footer_frame.grid_columnconfigure(1, weight=1)
        
        # Delete record button
        self.delete_button = ctk.CTkButton(
            self.footer_frame,
            text="🗑️ Delete Record",
            font=ctk.CTkFont(size=14),
            width=140,
            height=44,
            corner_radius=22,
            fg_color=ThemeManager.WARNING_COLOR,
            hover_color="#DC2626",
            command=self._delete_record
        )
        self.delete_button.grid(row=0, column=0, sticky="w")
        
        # Rerun analysis button
        self.rerun_button = ctk.CTkButton(
            self.footer_frame,
            text="🔄 Rerun Analysis",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=140,
            height=44,
            corner_radius=22,
            fg_color=ThemeManager.PRIMARY_COLOR,
            hover_color=ThemeManager.PRIMARY_HOVER,
            command=self._rerun_analysis
        )
        self.rerun_button.grid(row=0, column=2, sticky="e")
        
    def load_record_data(self, record_data):
        """Load and display data from a history record"""
        try:
            self.current_record = record_data
            
            # Update header
            session_date = record_data.get('session_date', '')
            if session_date:
                formatted_date = self._format_date(session_date)
                self.date_label.configure(text=f"Analysis from {formatted_date}")
            
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
        
    def _export_results(self):
        """Export analysis results"""
        # TODO: Implement export functionality
        print("Export functionality not yet implemented")
        
    def _delete_record(self):
        """Delete the current record after confirmation"""
        # TODO: Implement delete functionality with confirmation dialog
        print("Delete functionality not yet implemented")
        
    def _rerun_analysis(self):
        """Rerun analysis with the same parameters"""
        # TODO: Implement rerun functionality
        print("Rerun functionality not yet implemented")
        
    def _go_back(self):
        """Go back to history page"""
        self.controller.show_frame("HistoryPage")
        
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


if __name__ == "__main__":
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