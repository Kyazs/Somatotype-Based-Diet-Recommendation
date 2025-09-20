"""
Processing Page for the Diet Recommendation System.
Shows animated processing steps as data is analyzed.
Follows the original clean design theme with enhanced UX improvements.
"""
import customtkinter as ctk
import subprocess
import threading
import os
import sys
import time
from PIL import Image

# Configuration
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(PROJECT_DIR)

from src.utils.utils import CNN_DIR, VENV_DIR, CLASSIFIER_DIR, RECOMMENDER_DIR, INPUT_FILES_DIR, OUTPUT_FILES_DIR
from src.utils.theme_manager import ThemeManager
from src.utils.database import DatabaseManager

class ProcessingStep(ctk.CTkFrame):
    """Enhanced processing step with visual storytelling and smooth animations"""
    
    def __init__(self, parent, step_title, step_icon="●", step_description=""):
        super().__init__(parent, fg_color=ThemeManager.SECONDARY_COLOR, corner_radius=12, border_width=1, border_color=ThemeManager.GRAY_LIGHT)
        
        # Configure grid with proper padding
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Status values
        self.STATUS_WAITING = "waiting"
        self.STATUS_PROCESSING = "processing"
        self.STATUS_COMPLETE = "complete"
        self.STATUS_ERROR = "error"
        
        # Store the original icon
        self.original_icon = step_icon
        self.is_active = False
        
        # Icon frame (left side) - enhanced visual design
        self.icon_frame = ctk.CTkFrame(
            self,
            width=48,
            height=48,
            corner_radius=24,
            fg_color=ThemeManager.GRAY_LIGHT,
            border_width=0
        )
        self.icon_frame.grid(row=0, column=0, padx=(20, 12), pady=16, sticky="n")
        self.icon_frame.grid_propagate(False)
        
        # Icon label with enhanced typography
        self.icon_text = ctk.CTkLabel(
            self.icon_frame,
            text=step_icon,
            font=ctk.CTkFont(size=18),
            text_color=ThemeManager.GRAY_MEDIUM
        )
        self.icon_text.place(relx=0.5, rely=0.5, anchor="center")
        
        # Content frame (right side) - following original card design
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="ew", padx=(0, 20), pady=16)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Title with enhanced accessibility (larger when active)
        self.title = ctk.CTkLabel(
            self.content_frame,
            text=step_title,
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.GRAY_MEDIUM,
            anchor="w"
        )
        self.title.grid(row=0, column=0, sticky="w")
        
        # Description with better contrast
        self.description = ctk.CTkLabel(
            self.content_frame,
            text=step_description,
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.GRAY_MEDIUM,
            anchor="w",
            justify="left",
            wraplength=350
        )
        self.description.grid(row=1, column=0, sticky="w", pady=(4, 12))
        
        # Enhanced progress bar with smooth transitions
        self.progress_container = ctk.CTkFrame(
            self.content_frame,
            fg_color=ThemeManager.GRAY_LIGHT,
            height=6,
            corner_radius=3
        )
        self.progress_container.grid(row=2, column=0, sticky="ew")
        self.progress_container.grid_propagate(False)
        
        # Progress fill with color-coded states
        self.progress_fill = ctk.CTkFrame(
            self.progress_container,
            fg_color=ThemeManager.GRAY_LIGHT,
            height=6,
            corner_radius=3
        )
        self.progress_fill.place(relx=0, rely=0, relwidth=0, relheight=1)
        
        # Set initial state
        self.current_status = self.STATUS_WAITING
        self.progress = 0.0
        self.is_animating = False
    
    def update_status(self, status, description=None, progress=None):
        """Update the step's status and appearance with smooth animations"""
        self.current_status = status
        
        # Update description if provided
        if description:
            self.description.configure(text=description)
            
        # Animate progress bar if provided
        if progress is not None and 0 <= progress <= 1:
            self.animate_progress_to(progress)
            
        # Color-coded states following original theme with enhanced contrast
        if status == self.STATUS_WAITING:
            self.configure(fg_color=ThemeManager.SECONDARY_COLOR)
            self.icon_frame.configure(fg_color=ThemeManager.GRAY_LIGHT)
            self.icon_text.configure(text=self.original_icon, text_color=ThemeManager.GRAY_MEDIUM)
            self.title.configure(text_color=ThemeManager.GRAY_MEDIUM, font=ThemeManager.get_label_font())
            self.progress_fill.configure(fg_color=ThemeManager.GRAY_LIGHT)
            
        elif status == self.STATUS_PROCESSING:
            # Blue for in progress - enhanced visual feedback
            self.configure(fg_color="white", border_color=ThemeManager.PRIMARY_COLOR)
            self.icon_frame.configure(fg_color=ThemeManager.PRIMARY_COLOR)
            self.icon_text.configure(text_color="white")
            # Bold and larger for active step (accessibility)
            self.title.configure(text_color=ThemeManager.GRAY_DARK, font=ThemeManager.get_subtitle_font())
            self.progress_fill.configure(fg_color=ThemeManager.PRIMARY_COLOR)
            self.animate_processing_icon()
            
        elif status == self.STATUS_COMPLETE:
            # Green for completed
            self.configure(fg_color=ThemeManager.SECONDARY_COLOR, border_color=ThemeManager.SUCCESS_COLOR)
            self.icon_frame.configure(fg_color=ThemeManager.SUCCESS_COLOR)
            self.icon_text.configure(text="✓", text_color="white")
            self.title.configure(text_color=ThemeManager.GRAY_DARK, font=ThemeManager.get_label_font())
            self.progress_fill.configure(fg_color=ThemeManager.SUCCESS_COLOR)
            self.animate_checkmark()
            
        elif status == self.STATUS_ERROR:
            # Orange for warning/error
            self.configure(fg_color=ThemeManager.SECONDARY_COLOR, border_color=ThemeManager.WARNING_COLOR)
            self.icon_frame.configure(fg_color=ThemeManager.WARNING_COLOR)
            self.icon_text.configure(text="⚠", text_color="white")
            self.title.configure(text_color=ThemeManager.WARNING_COLOR, font=ThemeManager.get_label_font())
            self.progress_fill.configure(fg_color=ThemeManager.WARNING_COLOR)
    
    def animate_progress_to(self, target_progress):
        """Smoothly animate progress bar to target value"""
        if self.is_animating:
            return
            
        self.is_animating = True
        current_width = self.progress
        
        def animate_step():
            nonlocal current_width
            if current_width < target_progress:
                current_width = min(current_width + 0.03, target_progress)  # Smoother animation
                self.progress_fill.place(relx=0, rely=0, relwidth=current_width, relheight=1)
                self.after(20, animate_step)  # Smoother 50fps
            else:
                self.progress = target_progress
                self.is_animating = False
                
        animate_step()
    
    def animate_processing_icon(self):
        """Enhanced pulsing animation for processing state"""
        if self.current_status != self.STATUS_PROCESSING:
            return
            
        def pulse():
            if self.current_status != self.STATUS_PROCESSING:
                return
            # Smooth icon animation
            icons = ["⚡", "⚡⚡", "⚡⚡⚡"]
            icon_index = int((time.time() * 3) % len(icons))
            if hasattr(self, 'icon_text'):
                self.icon_text.configure(text=icons[icon_index])
            
            self.after(250, pulse)
            
        pulse()
        
    def animate_checkmark(self):
        """Smooth fade-in effect for completion"""
        def fade_in():
            # Simple checkmark appearance with brief highlight
            if hasattr(self, 'icon_text'):
                self.icon_text.configure(text="✓")
            
        self.after(100, fade_in)

class VisualCard(ctk.CTkFrame):
    """Dynamic visual card that changes content based on current processing step"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color=ThemeManager.SECONDARY_COLOR, corner_radius=12, border_width=1, border_color=ThemeManager.GRAY_LIGHT)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Content
        self.grid_rowconfigure(2, weight=0)  # Footer
        
        # Header with dynamic title following original typography
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=24, pady=(24, 0), sticky="ew")
        
        self.header = ctk.CTkLabel(
            self.header_frame,
            text="🔄 Initializing Analysis",
            font=ThemeManager.get_subtitle_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        self.header.grid(row=0, column=0, sticky="w")
        
        # Content area with dynamic visuals
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, padx=24, pady=16, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Footer with enhanced time estimate
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.grid(row=2, column=0, padx=24, pady=(0, 24), sticky="ew")
        self.footer_frame.grid_columnconfigure(0, weight=1)
        
        # Enhanced time estimate container
        self.time_container = ctk.CTkFrame(
            self.footer_frame, 
            fg_color=ThemeManager.GRAY_LIGHT, 
            corner_radius=8,
            height=36
        )
        self.time_container.grid(row=0, column=0, sticky="ew")
        self.time_container.grid_columnconfigure(1, weight=1)
        self.time_container.grid_propagate(False)
        
        # Pulsing clock icon
        self.clock_icon = ctk.CTkLabel(
            self.time_container,
            text="🕐",
            font=ctk.CTkFont(size=16)
        )
        self.clock_icon.grid(row=0, column=0, padx=(12, 8), pady=8)
        
        # Animated countdown
        self.time_label = ctk.CTkLabel(
            self.time_container,
            text="Estimated time: 30 seconds",
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.GRAY_DARK
        )
        self.time_label.grid(row=0, column=1, padx=(0, 12), pady=8, sticky="w")
        
        # Visual elements for different steps
        self.visuals = {}
        self.current_visual = None
        self.remaining_time = 30
        self.setup_visuals()
        self.show_visual("initializing")
        self.start_clock_animation()
        
    def setup_visuals(self):
        """Set up dynamic visual elements for each processing step"""
        
        # 1. Initializing visual
        init_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        init_frame.grid_columnconfigure(0, weight=1)
        
        init_icon = ctk.CTkLabel(
            init_frame,
            text="🚀",
            font=ctk.CTkFont(size=48)
        )
        init_icon.grid(row=0, column=0, pady=(40, 20))
        
        init_label = ctk.CTkLabel(
            init_frame,
            text="Preparing analysis system...",
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.GRAY_DARK
        )
        init_label.grid(row=1, column=0, pady=(0, 40))
        self.visuals["initializing"] = init_frame
        
        # 2. User data visual - show entered details
        user_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        user_frame.grid_columnconfigure(0, weight=1)
        
        user_icon = ctk.CTkLabel(
            user_frame,
            text="👤",
            font=ctk.CTkFont(size=36)
        )
        user_icon.grid(row=0, column=0, pady=(20, 15))
        
        # User details display card
        self.user_details_card = ctk.CTkFrame(
            user_frame, 
            fg_color="white", 
            corner_radius=8,
            border_width=1,
            border_color=ThemeManager.GRAY_LIGHT
        )
        self.user_details_card.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        self.user_details_card.grid_columnconfigure(0, weight=1)
        
        self.user_details_label = ctk.CTkLabel(
            self.user_details_card,
            text="Age: 25 | Height: 170cm | Weight: 70kg\nGoal: Weight Management",
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.GRAY_DARK,
            justify="center"
        )
        self.user_details_label.grid(row=0, column=0, padx=20, pady=16)
        
        self.visuals["user_input"] = user_frame
        
        # 3. Image processing - show silhouette preview
        img_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        img_frame.grid_columnconfigure(0, weight=1)
        
        img_icon = ctk.CTkLabel(
            img_frame,
            text="📸",
            font=ctk.CTkFont(size=36)
        )
        img_icon.grid(row=0, column=0, pady=(20, 15))
        
        # Image processing preview
        img_preview_frame = ctk.CTkFrame(
            img_frame,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color=ThemeManager.GRAY_LIGHT
        )
        img_preview_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        self.img_preview_label = ctk.CTkLabel(
            img_preview_frame,
            text="� Front View    📷 Side View\n🔍 Analyzing body contours...",
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.GRAY_DARK,
            justify="center"
        )
        self.img_preview_label.grid(row=0, column=0, padx=20, pady=16)
        
        self.visuals["image_processing"] = img_frame
        
        # 4. Measurements - show numbers appearing
        meas_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        meas_frame.grid_columnconfigure(0, weight=1)
        
        meas_icon = ctk.CTkLabel(
            meas_frame,
            text="📏",
            font=ctk.CTkFont(size=36)
        )
        meas_icon.grid(row=0, column=0, pady=(20, 15))
        
        # Measurements display
        meas_card = ctk.CTkFrame(
            meas_frame,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color=ThemeManager.GRAY_LIGHT
        )
        meas_card.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        self.measurements_label = ctk.CTkLabel(
            meas_card,
            text="📊 Chest: 98cm  📊 Waist: 82cm\n📊 Hip: 95cm   📊 Height: 170cm",
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.GRAY_DARK,
            justify="center"
        )
        self.measurements_label.grid(row=0, column=0, padx=20, pady=16)
        
        self.visuals["measurements"] = meas_frame
        
        # 5. Classification - show animated percentage dials
        class_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        class_frame.grid_columnconfigure(0, weight=1)
        
        class_icon = ctk.CTkLabel(
            class_frame,
            text="🏃",
            font=ctk.CTkFont(size=36)
        )
        class_icon.grid(row=0, column=0, pady=(20, 15))
        
        # Classification results
        class_card = ctk.CTkFrame(
            class_frame,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color=ThemeManager.GRAY_LIGHT
        )
        class_card.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        self.classification_label = ctk.CTkLabel(
            class_card,
            text="🎯 Endomorph: 45%\n🎯 Mesomorph: 35%\n🎯 Ectomorph: 20%",
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.GRAY_DARK,
            justify="center"
        )
        self.classification_label.grid(row=0, column=0, padx=20, pady=16)
        
        self.visuals["classification"] = class_frame
        
        # 6. Diet plan - show meal preview icons
        diet_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        diet_frame.grid_columnconfigure(0, weight=1)
        
        diet_icon = ctk.CTkLabel(
            diet_frame,
            text="🍽️",
            font=ctk.CTkFont(size=36)
        )
        diet_icon.grid(row=0, column=0, pady=(20, 15))
        
        # Diet plan preview
        diet_card = ctk.CTkFrame(
            diet_frame,
            fg_color="white",
            corner_radius=8,
            border_width=1,
            border_color=ThemeManager.GRAY_LIGHT
        )
        diet_card.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        self.diet_preview_label = ctk.CTkLabel(
            diet_card,
            text="🥗 Breakfast   🍗 Lunch   🥘 Dinner\n📋 Creating personalized meal plan...",
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.GRAY_DARK,
            justify="center"
        )
        self.diet_preview_label.grid(row=0, column=0, padx=20, pady=16)
        
        self.visuals["diet_plan"] = diet_frame
        
    def show_visual(self, visual_name):
        """Show the visual for the current step with smooth transitions"""
        # Hide current visual
        if self.current_visual and self.current_visual in self.visuals:
            self.visuals[self.current_visual].grid_remove()
        
        # Show new visual
        if visual_name in self.visuals:
            self.visuals[visual_name].grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
            self.current_visual = visual_name
            
        # Update header text based on step with more engaging titles
        step_headers = {
            "initializing": "🔄 Initializing Analysis",
            "user_input": "👤 Your Information", 
            "image_processing": "📸 Processing Images",
            "measurements": "📏 Body Measurements",
            "classification": "🏃 Body Type Analysis",
            "diet_plan": "🍽️ Your Diet Plan"
        }
        
        if visual_name in step_headers:
            self.header.configure(text=step_headers[visual_name])
                
    def update_time_estimate(self, seconds):
        """Update the time estimate with animated countdown"""
        self.remaining_time = max(0, seconds)
        minutes = seconds // 60
        secs = seconds % 60
        
        if minutes > 0:
            time_text = f"Estimated time: {minutes}m {secs}s"
        else:
            time_text = f"Estimated time: {secs}s"
            
        self.time_label.configure(text=time_text)
        
    def start_clock_animation(self):
        """Start the pulsing animated clock with countdown"""
        def animate_clock():
            # Pulsing clock animation
            clock_icons = ["🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚", "🕛"]
            clock_index = int((time.time() * 2) % len(clock_icons))
            self.clock_icon.configure(text=clock_icons[clock_index])
            
            # Countdown with color changes
            if self.remaining_time > 0:
                self.remaining_time -= 1
                self.update_time_estimate(self.remaining_time)
                
                # Color urgency feedback
                if self.remaining_time <= 5:
                    self.time_label.configure(text_color=ThemeManager.WARNING_COLOR)
                elif self.remaining_time <= 10:
                    self.time_label.configure(text_color=ThemeManager.PRIMARY_COLOR)
                else:
                    self.time_label.configure(text_color=ThemeManager.GRAY_DARK)
            
            self.after(800, animate_clock)  # Slower, more relaxed pulsing
            
        animate_clock()

class ProcessingPage(ctk.CTkFrame):
    """Enhanced processing page with better visual storytelling and intuitive design"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=ThemeManager.BG_COLOR)
        self.controller = controller
        self.stop_requested = False
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        self.current_session_id = None
        self.current_user_id = None
        
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
        # Configure main grid for better responsive layout
        self.grid_columnconfigure(0, weight=2)  # Left side (steps)
        self.grid_columnconfigure(1, weight=1)  # Right side (visual card)
        self.grid_rowconfigure(0, weight=1)
        
        # Left panel - Processing steps with better visual hierarchy
        self.left_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(24, 12), pady=24)
        self.left_panel.grid_columnconfigure(0, weight=1)
        
        # Header with improved layout and subtle cancel button
        self.header_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 24))
        self.header_frame.grid_columnconfigure(1, weight=1)
        
        # Title following original typography with better hierarchy
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Processing Analysis",
            font=ThemeManager.get_title_font(),
            text_color=ThemeManager.GRAY_DARK
        )
        self.title_label.grid(row=0, column=0, sticky="w")
        
        # Subtle cancel button - gray outline, smaller, less prominent
        self.cancel_button = ctk.CTkButton(
            self.header_frame,
            text="Cancel",
            command=self.cancel_processing,
            font=ThemeManager.get_small_font(),
            fg_color="transparent",
            text_color=ThemeManager.GRAY_MEDIUM,
            hover_color=ThemeManager.GRAY_LIGHT,
            corner_radius=6,
            border_width=1,
            border_color=ThemeManager.GRAY_MEDIUM,
            width=70,
            height=28
        )
        self.cancel_button.grid(row=0, column=1, sticky="e")
        
        # Add tooltip effect for cancel button
        def show_tooltip(event):
            self.cancel_button.configure(text_color=ThemeManager.GRAY_DARK)
        def hide_tooltip(event):
            self.cancel_button.configure(text_color=ThemeManager.GRAY_MEDIUM)
            
        self.cancel_button.bind("<Enter>", show_tooltip)
        self.cancel_button.bind("<Leave>", hide_tooltip)
        
        # Steps container - using regular frame instead of scrollable to show all steps
        self.steps_frame = ctk.CTkFrame(
            self.left_panel, 
            fg_color="transparent"
        )
        self.steps_frame.grid(row=1, column=0, sticky="nsew")
        self.steps_frame.grid_columnconfigure(0, weight=1)
        # Configure row weights to distribute steps evenly
        for i in range(5):  # 5 processing steps
            self.steps_frame.grid_rowconfigure(i, weight=1)
        
        # Right panel - Enhanced visual card
        self.visual_card = VisualCard(self)
        self.visual_card.grid(row=0, column=1, sticky="nsew", padx=(12, 24), pady=24)
        
        # Create processing steps with better icons and action-based descriptions
        self.processing_steps = {}
        steps_data = [
            ("user_input", "👤", "Validating details", "Checking user information and preferences"),
            ("image_processing", "📸", "Detecting body features", "Analyzing front and side view images"), 
            ("measurements", "📏", "Calculating body metrics", "Extracting body measurements and proportions"),
            ("classification", "🏃", "Determining body type", "Classifying somatotype based on measurements"),
            ("diet_plan", "🍽️", "Building nutrition plan", "Creating personalized meal recommendations")
        ]
        
        for i, (step_id, icon, title, description) in enumerate(steps_data):
            step = ProcessingStep(
                self.steps_frame,
                title,
                icon,
                description
            )
            # Remove fixed height and use flexible sizing with proper spacing
            step.grid(row=i, column=0, sticky="ew", pady=(0, 12), padx=8)
            self.processing_steps[step_id] = step
            
    def update_step(self, step_name, status, description=None, progress=None):
        """Update a specific processing step with enhanced visual feedback"""
        if step_name in self.processing_steps:
            self.processing_steps[step_name].update_status(status, description, progress)
            
        # Update visual card based on current step for better user engagement
        if status == self.processing_steps[step_name].STATUS_PROCESSING:
            self.visual_card.show_visual(step_name)
            
            # Update time estimates based on step
            time_estimates = {
                "user_input": 3,
                "image_processing": 15,
                "measurements": 8,
                "classification": 5,
                "diet_plan": 4
            }
            if step_name in time_estimates:
                self.visual_card.remaining_time = time_estimates[step_name]
                self.visual_card.update_time_estimate(time_estimates[step_name])
            
    def run_process_threaded(self):
        """Start the processing in a separate thread"""
        def run_thread():
            self.run_process()
        
        thread = threading.Thread(target=run_thread, daemon=True)
        thread.start()
        
    def run_process(self):
        """Main processing logic with enhanced progress updates and timing"""
        try:
            # Initialize database session at start
            self._initialize_database_session()
            
            # Step 1: Validate user input
            self.update_step("user_input", self.processing_steps["user_input"].STATUS_PROCESSING)
            
            # Simulate progressive loading with more realistic timing
            for i in range(4):
                if self.stop_requested:
                    return
                time.sleep(0.5)
                self.update_step("user_input", self.processing_steps["user_input"].STATUS_PROCESSING, progress=(i+1)/4)
                
            self.update_step("user_input", self.processing_steps["user_input"].STATUS_COMPLETE, "Details validated ✓", progress=1.0)
            time.sleep(0.5)  # Brief pause for visual feedback
            
            # Step 2: Process images
            self.update_step("image_processing", self.processing_steps["image_processing"].STATUS_PROCESSING)
            success = self.run_cnn_model()
            if self.stop_requested:
                return
            if success:
                self.update_step("image_processing", self.processing_steps["image_processing"].STATUS_COMPLETE, "Features detected ✓", progress=1.0)
                # Save body measurements to database after CNN processing
                self._save_body_measurements()
            else:
                self.update_step("image_processing", self.processing_steps["image_processing"].STATUS_ERROR, "Image processing failed")
                self._update_session_status('failed')
                return
                
            time.sleep(0.5)
            
            # Step 3: Extract measurements 
            self.update_step("measurements", self.processing_steps["measurements"].STATUS_PROCESSING)
            
            # Simulate measurement extraction with progress
            for i in range(6):
                if self.stop_requested:
                    return
                time.sleep(0.5)
                self.update_step("measurements", self.processing_steps["measurements"].STATUS_PROCESSING, progress=(i+1)/6)
                
            self.update_step("measurements", self.processing_steps["measurements"].STATUS_COMPLETE, "Metrics calculated ✓", progress=1.0)
            time.sleep(0.5)
            
            # Step 4: Classify somatotype
            self.update_step("classification", self.processing_steps["classification"].STATUS_PROCESSING)
            success = self.run_classifier()
            if self.stop_requested:
                return
            if success:
                self.update_step("classification", self.processing_steps["classification"].STATUS_COMPLETE, "Body type determined ✓", progress=1.0)
                # Save somatotype classification to database
                self._save_somatotype_classification()
            else:
                self.update_step("classification", self.processing_steps["classification"].STATUS_ERROR, "Classification failed")
                self._update_session_status('failed')
                return
                
            time.sleep(0.5)
            
            # Step 5: Generate diet plan
            self.update_step("diet_plan", self.processing_steps["diet_plan"].STATUS_PROCESSING)
            success = self.run_recommender()
            if self.stop_requested:
                return
            if success:
                self.update_step("diet_plan", self.processing_steps["diet_plan"].STATUS_COMPLETE, "Nutrition plan ready ✓", progress=1.0)
                # Save diet recommendations to database
                self._save_diet_recommendations()
                # Mark session as completed
                self._update_session_status('completed')
                # Brief success moment before navigation
                time.sleep(1)
                self.controller.after(500, lambda: self.controller.show_frame("DietPage"))
            else:
                self.update_step("diet_plan", self.processing_steps["diet_plan"].STATUS_ERROR, "Diet generation failed")
                self._update_session_status('failed')
                
        except Exception as e:
            print(f"Processing error: {e}")
            self._update_session_status('failed')
            # Mark current step as error
            for step_name, step in self.processing_steps.items():
                if step.current_status == step.STATUS_PROCESSING:
                    self.update_step(step_name, step.STATUS_ERROR, f"Error: {str(e)}")
                    break

    def run_cnn_model(self):
        """Run CNN model for image processing"""
        try:
            # Use the virtual environment Python path directly
            python_path = "C:/Users/LENOVO/Desktop/Kekious_Maximus/diet-recommendation-somatotype/.venv/cnn_env/Scripts/python.exe"
            cnn_script = os.path.join(CNN_DIR, "photos2avatar.py")
            command = f'"{python_path}" "{cnn_script}"'
            
            print(f"Running CNN command: {command}")
            
            process = subprocess.Popen(
                command, cwd=CNN_DIR, stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, text=True, shell=True
            )
            
            stdout, stderr = process.communicate()
            
            if stdout:
                print(f"CNN stdout: {stdout}")
            if stderr:
                print(f"CNN stderr: {stderr}")
            
            return process.returncode == 0
        except Exception as e:
            print(f"CNN model error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run_classifier(self):
        """Run classifier for somatotype detection"""
        try:
            # Use the virtual environment Python path
            python_path = "C:/Users/LENOVO/Desktop/Kekious_Maximus/diet-recommendation-somatotype/.venv/cnn_env/Scripts/python.exe"
            classifier_script = os.path.join(CLASSIFIER_DIR, "classifier.py")
            command = f'"{python_path}" "{classifier_script}"'
            
            print(f"Running classifier command: {command}")
            
            process = subprocess.Popen(
                command, cwd=CLASSIFIER_DIR, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, text=True, shell=True
            )
            
            stdout, stderr = process.communicate()
            
            if stdout:
                print(f"Classifier stdout: {stdout}")
            if stderr:
                print(f"Classifier stderr: {stderr}")
            
            return process.returncode == 0
        except Exception as e:
            print(f"Classifier error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run_recommender(self):
        """Run recommender for diet plan generation using DietRecommendationEngine"""
        try:
            print("🍽️ Generating diet recommendations...")
            
            # Import and initialize the diet engine
            from src.recommendation.diet_engine import DietRecommendationEngine
            
            # Create the diet engine
            engine = DietRecommendationEngine()
            
            # Generate and save recommendations to CSV file (expected by _save_diet_recommendations)
            csv_path = engine.save_recommendations_to_csv()
            print(f"✅ Saved CSV recommendations to: {csv_path}")
            
            # Also save meal recommendations to JSON for future use
            json_path = engine.save_meal_recommendations_to_json()
            print(f"✅ Saved JSON meal recommendations to: {json_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error generating diet recommendations: {e}")
            import traceback
            traceback.print_exc()
            return False

    def cancel_processing(self):
        """Cancel processing and return to previous page with gentle feedback"""
        self.stop_requested = True
        # Update session status if it exists
        if self.current_session_id:
            self._update_session_status('cancelled')
        # Provide subtle feedback that cancellation is processing
        self.cancel_button.configure(text="Stopping...", text_color=ThemeManager.WARNING_COLOR)
        self.controller.after(300, lambda: self.controller.show_frame("CapturePage"))

    def _initialize_database_session(self):
        """Initialize database session with user data and image paths"""
        try:
            # Get user data from state manager
            state_manager = getattr(self.controller, 'state_manager', None)
            if not state_manager or not hasattr(state_manager, 'user_data'):
                print("⚠️  No state manager or user data found")
                return
                
            user_data = state_manager.user_data
            
            # Insert user into database
            self.current_user_id = self.db_manager.insert_user(user_data)
            
            # Get captured image paths (from captured_poses folder)
            captured_poses_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "database", "captured_poses")
            
            # Try to get the most recent captured images
            front_captured_path = None
            side_captured_path = None
            
            if os.path.exists(captured_poses_dir):
                # Get list of front and side images
                import glob
                front_images = sorted(glob.glob(os.path.join(captured_poses_dir, "*_front*.png")), reverse=True)
                side_images = sorted(glob.glob(os.path.join(captured_poses_dir, "*_side*.png")), reverse=True)
                
                # Get the most recent ones
                if front_images:
                    front_captured_path = front_images[0]
                if side_images:
                    side_captured_path = side_images[0]
            
            # Also check input files as fallback
            front_input_path = os.path.join(INPUT_FILES_DIR, "input_front.png") if os.path.exists(os.path.join(INPUT_FILES_DIR, "input_front.png")) else None
            side_input_path = os.path.join(INPUT_FILES_DIR, "input_side.png") if os.path.exists(os.path.join(INPUT_FILES_DIR, "input_side.png")) else None
            
            # Create analysis session with captured paths
            self.current_session_id = self.db_manager.create_analysis_session(
                self.current_user_id,
                front_captured_path or front_input_path,
                side_captured_path or side_input_path
            )
            
            # Update session status to processing
            self._update_session_status('processing')
            
        except Exception as e:
            print(f"❌ Error initializing database session: {e}")
    
    def _update_session_status(self, status):
        """Update session status in database"""
        try:
            if self.current_session_id:
                self.db_manager.update_session_status(self.current_session_id, status)
        except Exception as e:
            print(f"❌ Error updating session status: {e}")
    
    def _save_body_measurements(self):
        """Save body measurements from CNN output to database"""
        try:
            if not self.current_session_id:
                return
            
            # Read CNN output file
            measurements_path = os.path.join(OUTPUT_FILES_DIR, "output_data_avatar_male_fromImg.csv")
            if not os.path.exists(measurements_path):
                print(f"⚠️  Measurements file not found: {measurements_path}")
                return
            
            import pandas as pd
            df = pd.read_csv(measurements_path, delimiter='|')
            
            measurements = []
            for _, row in df.iterrows():
                measurement_name = str(row['Measurement']).strip()
                if measurement_name and measurement_name != 'Measurement':  # Skip header row
                    measurements.append({
                        'type': measurement_name,
                        'basic_input': self._safe_float(row['Basic-Input']),
                        'predicted_input': self._safe_float(row['Predicted-Input']),
                        'avatar_output': self._safe_float(row['3D Avatar-Output']),
                        'unit': 'cm' if 'girth' in measurement_name.lower() or 'stature' in measurement_name.lower() else 'kg'
                    })
            
            # Insert measurements into database
            if measurements:
                self.db_manager.insert_body_measurements(self.current_session_id, measurements)
                
        except Exception as e:
            print(f"❌ Error saving body measurements: {e}")
    
    def _save_somatotype_classification(self):
        """Save somatotype classification from classifier output to database"""
        try:
            if not self.current_session_id:
                return
                
            # Read classification output file
            classification_path = os.path.join(OUTPUT_FILES_DIR, "output_classification.csv")
            if not os.path.exists(classification_path):
                print(f"⚠️  Classification file not found: {classification_path}")
                return
            
            import pandas as pd
            df = pd.read_csv(classification_path)
            
            if len(df) > 0:
                row = df.iloc[0]  # Get first row
                classification_data = {
                    'endomorphy': self._safe_float(row['Endomorphy']),
                    'mesomorphy': self._safe_float(row['Mesomorphy']),
                    'ectomorphy': self._safe_float(row['Ectomorphy']),
                    'somatotype_class': str(row['Somatotype']),
                    'confidence_score': 0.85  # Default confidence
                }
                
                self.db_manager.insert_somatotype_classification(self.current_session_id, classification_data)
                
        except Exception as e:
            print(f"❌ Error saving somatotype classification: {e}")
    
    def _save_diet_recommendations(self):
        """Save diet recommendations from recommender output to database"""
        try:
            if not self.current_session_id:
                return
                
            # Read recommendation output file
            recommendation_path = os.path.join(OUTPUT_FILES_DIR, "output_recommendation.csv")
            if not os.path.exists(recommendation_path):
                print(f"⚠️  Recommendation file not found: {recommendation_path}")
                return
            
            import pandas as pd
            import json
            
            # Read the CSV file carefully since it has multiple sections
            with open(recommendation_path, 'r') as file:
                lines = file.readlines()
            
            # Parse macronutrients section
            macros = {}
            foods = []
            insights = ""
            
            in_macros = True
            in_foods = False
            in_insights = False
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line == "Suggested Foods":
                    in_macros = False
                    in_foods = True
                    continue
                elif line == "Nutrition Insights":
                    in_foods = False
                    in_insights = True
                    continue
                
                if in_macros and "," in line:
                    key, value = line.split(",", 1)
                    if key.strip() in ['calories', 'protein', 'carbs', 'fat', 'bmr', 'tdee']:
                        macros[key.strip()] = self._safe_int(value.strip())
                    elif key.strip() == 'somatotype':
                        insights = f"Somatotype: {value.strip()}"
                        
                elif in_foods and line and line not in ['Suggested Foods', 'Nutrition Insights']:
                    foods.append(line.strip())
                    
                elif in_insights and line:
                    if insights:
                        insights += " | " + line.strip()
                    else:
                        insights = line.strip()
            
            # Read meal recommendations JSON file
            meal_recommendations_json = "{}"
            meal_json_path = os.path.join(OUTPUT_FILES_DIR, "meal_recommendations.json")
            if os.path.exists(meal_json_path):
                try:
                    with open(meal_json_path, 'r') as f:
                        meal_data = json.load(f)
                        meal_recommendations_json = json.dumps(meal_data)
                        print(f"✅ Loaded meal recommendations from {meal_json_path}")
                except Exception as e:
                    print(f"⚠️  Error reading meal recommendations JSON: {e}")
            else:
                print(f"⚠️  Meal recommendations JSON not found: {meal_json_path}")
            
            # Prepare recommendation data
            recommendation_data = {
                'calories': macros.get('calories', 2000),
                'protein': macros.get('protein', 150),
                'carbs': macros.get('carbs', 200),
                'fat': macros.get('fat', 80),
                'bmr': macros.get('bmr', 1500),
                'tdee': macros.get('tdee', 2000),
                'nutrition_insights': insights,
                'meal_recommendations': meal_recommendations_json
            }
            
            # Calculate macronutrient percentages
            total_calories = recommendation_data['calories']
            if total_calories > 0:
                recommendation_data['protein_percentage'] = round((recommendation_data['protein'] * 4) / total_calories * 100, 1)
                recommendation_data['carbs_percentage'] = round((recommendation_data['carbs'] * 4) / total_calories * 100, 1)
                recommendation_data['fat_percentage'] = round((recommendation_data['fat'] * 9) / total_calories * 100, 1)
            
            # Insert diet recommendation
            recommendation_id = self.db_manager.insert_diet_recommendation(self.current_session_id, recommendation_data)
            
            # Insert recommended foods
            if foods and recommendation_id:
                self.db_manager.insert_recommended_foods(recommendation_id, foods)
                
        except Exception as e:
            print(f"❌ Error saving diet recommendations: {e}")
            import traceback
            traceback.print_exc()
    
    def _safe_float(self, value):
        """Safely convert value to float"""
        try:
            return float(str(value).strip())
        except (ValueError, TypeError):
            return 0.0
    
    def _safe_int(self, value):
        """Safely convert value to int"""
        try:
            return int(float(str(value).strip()))
        except (ValueError, TypeError):
            return 0

    def on_show(self):
        """Called when the page is shown - reset and start processing"""
        # Load content lazily when page is first shown
        self.load_content()
        
        self.stop_requested = False
        
        # Reset cancel button
        if hasattr(self, 'cancel_button'):
            self.cancel_button.configure(text="Cancel", text_color=ThemeManager.GRAY_MEDIUM)
        
        # Reset all steps to waiting state
        if hasattr(self, 'processing_steps'):
            for step_name in self.processing_steps:
                self.update_step(step_name, self.processing_steps[step_name].STATUS_WAITING, progress=0.0)
        
        # Reset visual card
        if hasattr(self, 'visual_card'):
            self.visual_card.show_visual("initializing")
        self.visual_card.remaining_time = 35
        
        # Start processing with brief delay for better UX
        self.after(800, self.run_process_threaded)

if __name__ == "__main__":
    # Test the clean design
    class DummyController:
        def show_frame(self, frame_name):
            print(f"Switching to frame: {frame_name}")
        def after(self, ms, func):
            func()

    controller = DummyController()
    
    root = ctk.CTk()
    root.title("Processing Page - Clean Design")
    root.geometry("1200x700")
    ThemeManager.setup_theme()
    
    app = ProcessingPage(root, controller)
    app.pack(fill="both", expand=True)
    app.on_show()
    
    root.mainloop()
