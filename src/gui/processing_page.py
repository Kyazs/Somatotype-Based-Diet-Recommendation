"""
Processing Page for the Diet Recommendation System.
Shows animated processing steps as data is analyzed.
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

from src.utils.utils import CNN_DIR, VENV_DIR, CLASSIFIER_DIR, RECOMMENDER_DIR
from utils.theme_manager import ThemeManager, IMAGES_DIR

class ProcessingStep(ctk.CTkFrame):
    """A visual step in the processing pipeline"""
    
    def __init__(self, parent, step_title, step_icon=None, step_description=""):
        super().__init__(parent, fg_color="transparent")
        
        # Configure grid
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Status values
        self.STATUS_WAITING = "waiting"
        self.STATUS_PROCESSING = "processing"
        self.STATUS_COMPLETE = "complete"
        self.STATUS_ERROR = "error"
        
        # Icon frame (left side)
        self.icon_frame = ctk.CTkFrame(
            self,
            width=40,
            height=40,
            corner_radius=20,
            fg_color=ThemeManager.GRAY_LIGHT
        )
        self.icon_frame.grid(row=0, column=0, padx=(0, 15), sticky="nw")
        self.icon_frame.grid_propagate(False)  # Maintain size
        
        # Icon label
        self.icon_text = ctk.CTkLabel(
            self.icon_frame,
            text="●",
            font=ctk.CTkFont(size=20),
            text_color=ThemeManager.GRAY_MEDIUM
        )
        self.icon_text.place(relx=0.5, rely=0.5, anchor="center")
        
        # Content frame (right side)
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="ew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title = ctk.CTkLabel(
            self.content_frame,
            text=step_title,
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.GRAY_DARK,
            anchor="w"
        )
        self.title.grid(row=0, column=0, sticky="w")
        
        # Description
        self.description = ctk.CTkLabel(
            self.content_frame,
            text=step_description,
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.GRAY_MEDIUM,
            anchor="w",
            justify="left",
            wraplength=400
        )
        self.description.grid(row=1, column=0, sticky="w", pady=(2, 5))
        
        # Progress bar
        self.progress_container = ctk.CTkFrame(
            self.content_frame,
            fg_color=ThemeManager.GRAY_LIGHT,
            height=6,
            corner_radius=3
        )
        self.progress_container.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        self.progress_container.grid_propagate(False)
        
        # Animated progress fill
        self.progress_fill = ctk.CTkFrame(
            self.progress_container,
            fg_color=ThemeManager.PRIMARY_COLOR,
            height=6,
            corner_radius=3
        )
        self.progress_fill.place(relx=0, rely=0, relwidth=0, relheight=1)
        
        # Set initial state
        self.current_status = self.STATUS_WAITING
        self.progress = 0.0
    
    def update_status(self, status, description=None, progress=None):
        """Update the step's status and appearance"""
        self.current_status = status
        
        # Update description if provided
        if description:
            self.description.configure(text=description)
            
        # Update progress bar if provided
        if progress is not None and 0 <= progress <= 1:
            self.progress = progress
            self.progress_fill.place(relwidth=progress)
            
        # Update appearance based on status
        if status == self.STATUS_WAITING:
            self.icon_frame.configure(fg_color=ThemeManager.GRAY_LIGHT)
            self.icon_text.configure(text="●", text_color=ThemeManager.GRAY_MEDIUM)
            self.title.configure(text_color=ThemeManager.GRAY_DARK)
            self.progress_fill.configure(fg_color=ThemeManager.PRIMARY_COLOR)
            
        elif status == self.STATUS_PROCESSING:
            self.icon_frame.configure(fg_color=ThemeManager.PRIMARY_COLOR)
            self.icon_text.configure(text="⟳", text_color="white")
            self.title.configure(text_color=ThemeManager.PRIMARY_COLOR)
            self.progress_fill.configure(fg_color=ThemeManager.PRIMARY_COLOR)
            
        elif status == self.STATUS_COMPLETE:
            self.icon_frame.configure(fg_color=ThemeManager.SUCCESS_COLOR)
            self.icon_text.configure(text="✓", text_color="white")
            self.title.configure(text_color=ThemeManager.SUCCESS_COLOR)
            self.progress_fill.configure(fg_color=ThemeManager.SUCCESS_COLOR)
            self.progress_fill.place(relwidth=1.0)  # Full width
            
        elif status == self.STATUS_ERROR:
            self.icon_frame.configure(fg_color=ThemeManager.DANGER_COLOR)
            self.icon_text.configure(text="!", text_color="white")
            self.title.configure(text_color=ThemeManager.DANGER_COLOR)
            self.progress_fill.configure(fg_color=ThemeManager.DANGER_COLOR)
            
class VisualCard(ctk.CTkFrame):
    """Visual card that shows the current processing step with animation"""
    
    def __init__(self, parent):
        super().__init__(parent, corner_radius=10, fg_color=ThemeManager.SECONDARY_COLOR)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Content
        self.grid_rowconfigure(2, weight=0)  # Footer
        
        # Header
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=15, pady=(15, 0), sticky="ew")
        
        self.header = ctk.CTkLabel(
            self.header_frame,
            text="Analyzing Your Data",
            font=ThemeManager.get_subtitle_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        self.header.grid(row=0, column=0, sticky="w")
        
        # Content area where different visualizations will be shown
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, padx=15, pady=10, sticky="nsew")
        
        # Footer with estimate time
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="ew")
        
        self.time_label = ctk.CTkLabel(
            self.footer_frame,
            text="Estimated time remaining: 30 seconds",
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.GRAY_MEDIUM
        )
        self.time_label.grid(row=0, column=0)
        
        # Visual elements for different steps
        self.visuals = {}
        self.setup_visuals()
        self.current_visual = None
        self.show_visual("initializing")
        
    def setup_visuals(self):
        """Set up different visual elements for each processing step"""
        
        # 1. Initializing visual
        init_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        init_label = ctk.CTkLabel(
            init_frame,
            text="Initializing analysis...",
            font=ThemeManager.get_label_font()
        )
        init_label.pack(pady=40)
        self.visuals["initializing"] = init_frame
        
        # 2. User data visual
        user_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        user_frame.grid_columnconfigure((0, 1), weight=1)
        
        fields = ["Name", "Age", "Gender", "Height", "Weight", "Goal"]
        for i, field in enumerate(fields):
            row, col = i // 2, i % 2
            field_frame = ctk.CTkFrame(
                user_frame,
                fg_color=ThemeManager.BG_COLOR,
                corner_radius=5
            )
            field_frame.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
            
            field_name = ctk.CTkLabel(
                field_frame,
                text=field,
                font=ThemeManager.get_small_font(),
                text_color=ThemeManager.GRAY_MEDIUM
            )
            field_name.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="w")
            
            field_value = ctk.CTkFrame(
                field_frame,
                height=10,
                width=100,
                # Fix: Use a light blue color instead of hex with alpha
                fg_color=ThemeManager.GRAY_LIGHT,
                corner_radius=3
            )
            field_value.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="ew")
            
        self.visuals["user_data"] = user_frame
        
        # 3. Image processing visual
        img_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        img_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Placeholder for front image with scanning animation
        front_container = ctk.CTkFrame(
            img_frame,
            width=150,
            height=200,
            fg_color=ThemeManager.BG_COLOR,
            corner_radius=5
        )
        front_container.grid(row=0, column=0, padx=10, pady=10)
        front_container.grid_propagate(False)
        
        front_label = ctk.CTkLabel(
            front_container,
            text="Front View",
            font=ThemeManager.get_small_font()
        )
        front_label.pack(pady=(5, 0))
        
        front_img = ctk.CTkFrame(
            front_container,
            width=120,
            height=160,
            # Fix: Use a light blue color instead of hex with alpha
            fg_color=ThemeManager.GRAY_LIGHT
        )
        front_img.pack(pady=10)
        
        # Animated scan line
        self.front_scan = ctk.CTkFrame(
            front_img,
            height=4,
            width=120,
            fg_color=ThemeManager.PRIMARY_COLOR
        )
        self.front_scan.place(relx=0, rely=0, relwidth=1)
        
        # Placeholder for side image with scanning animation
        side_container = ctk.CTkFrame(
            img_frame,
            width=150,
            height=200,
            fg_color=ThemeManager.BG_COLOR,
            corner_radius=5
        )
        side_container.grid(row=0, column=1, padx=10, pady=10)
        side_container.grid_propagate(False)
        
        side_label = ctk.CTkLabel(
            side_container,
            text="Side View",
            font=ThemeManager.get_small_font()
        )
        side_label.pack(pady=(5, 0))
        
        side_img = ctk.CTkFrame(
            side_container,
            width=120,
            height=160,
            # Fix: Use a light blue color instead of hex with alpha
            fg_color=ThemeManager.GRAY_LIGHT
        )
        side_img.pack(pady=10)
        
        # Animated scan line
        self.side_scan = ctk.CTkFrame(
            side_img,
            height=4,
            width=120,
            fg_color=ThemeManager.PRIMARY_COLOR
        )
        self.side_scan.place(relx=0, rely=0, relwidth=1)
        
        self.visuals["image_processing"] = img_frame
        
        # 4. Measurements visual
        measurements_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        
        body_metrics = [
            ("Height", "175 cm"),
            ("Chest", "95 cm"),
            ("Waist", "80 cm"),
            ("Hips", "95 cm"),
            ("Thigh", "55 cm"),
            ("Weight", "72 kg")
        ]
        
        for i, (metric, value) in enumerate(body_metrics):
            row, col = i // 3, i % 3
            metric_frame = ctk.CTkFrame(
                measurements_frame,
                fg_color=ThemeManager.BG_COLOR,
                corner_radius=5
            )
            metric_frame.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
            
            metric_label = ctk.CTkLabel(
                metric_frame,
                text=metric,
                font=ThemeManager.get_small_font(),
                text_color=ThemeManager.GRAY_MEDIUM
            )
            metric_label.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="w")
            
            metric_value = ctk.CTkLabel(
                metric_frame,
                text=value,
                font=ThemeManager.get_label_font(),
                text_color=ThemeManager.PRIMARY_COLOR
            )
            metric_value.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="w")
            
        self.visuals["measurements"] = measurements_frame
        
        # 5. Somatotype visual
        somatotype_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        
        # Triangle visualization would go here - simplified for now
        types_frame = ctk.CTkFrame(somatotype_frame, fg_color="transparent")
        types_frame.pack(pady=10)
        
        # Three somatotype circles with percentages
        types_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Ectomorph
        ecto_frame = ctk.CTkFrame(types_frame, fg_color="transparent")
        ecto_frame.grid(row=0, column=0, padx=15)
        
        ecto_circle = ctk.CTkFrame(
            ecto_frame,
            width=80,
            height=80,
            corner_radius=40,
            fg_color=ThemeManager.BG_COLOR,
            border_color=ThemeManager.PRIMARY_COLOR,
            border_width=2
        )
        ecto_circle.pack(pady=5)
        ecto_circle.grid_propagate(False)
        
        ecto_value = ctk.CTkLabel(
            ecto_circle,
            text="32%",
            font=ThemeManager.get_subtitle_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        ecto_value.place(relx=0.5, rely=0.5, anchor="center")
        
        ecto_label = ctk.CTkLabel(
            ecto_frame,
            text="Ectomorph",
            font=ThemeManager.get_small_font()
        )
        ecto_label.pack()
        
        # Mesomorph
        meso_frame = ctk.CTkFrame(types_frame, fg_color="transparent")
        meso_frame.grid(row=0, column=1, padx=15)
        
        meso_circle = ctk.CTkFrame(
            meso_frame,
            width=80,
            height=80,
            corner_radius=40,
            fg_color=ThemeManager.BG_COLOR,
            border_color=ThemeManager.PRIMARY_COLOR,
            border_width=2
        )
        meso_circle.pack(pady=5)
        meso_circle.grid_propagate(False)
        
        meso_value = ctk.CTkLabel(
            meso_circle,
            text="45%",
            font=ThemeManager.get_subtitle_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        meso_value.place(relx=0.5, rely=0.5, anchor="center")
        
        meso_label = ctk.CTkLabel(
            meso_frame,
            text="Mesomorph",
            font=ThemeManager.get_small_font()
        )
        meso_label.pack()
        
        # Endomorph
        endo_frame = ctk.CTkFrame(types_frame, fg_color="transparent")
        endo_frame.grid(row=0, column=2, padx=15)
        
        endo_circle = ctk.CTkFrame(
            endo_frame,
            width=80,
            height=80,
            corner_radius=40,
            fg_color=ThemeManager.BG_COLOR,
            border_color=ThemeManager.PRIMARY_COLOR,
            border_width=2
        )
        endo_circle.pack(pady=5)
        endo_circle.grid_propagate(False)
        
        endo_value = ctk.CTkLabel(
            endo_circle,
            text="23%",
            font=ThemeManager.get_subtitle_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        endo_value.place(relx=0.5, rely=0.5, anchor="center")
        
        endo_label = ctk.CTkLabel(
            endo_frame,
            text="Endomorph",
            font=ThemeManager.get_small_font()
        )
        endo_label.pack()
        
        self.visuals["somatotype"] = somatotype_frame
        
        # 6. Diet recommendations visual
        diet_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        
        # Macronutrient ratio visualization
        macros_frame = ctk.CTkFrame(
            diet_frame,
            fg_color=ThemeManager.BG_COLOR,
            corner_radius=10
        )
        macros_frame.pack(pady=10, fill="x")
        
        macro_label = ctk.CTkLabel(
            macros_frame,
            text="Calculating Optimal Macronutrient Ratio",
            font=ThemeManager.get_label_font()
        )
        macro_label.pack(pady=(10, 5))
        
        macro_bar = ctk.CTkFrame(
            macros_frame,
            height=20,
            corner_radius=10,
            fg_color=ThemeManager.GRAY_LIGHT
        )
        macro_bar.pack(padx=15, pady=(0, 15), fill="x")
        
        # Protein segment
        protein_fill = ctk.CTkFrame(
            macro_bar,
            height=20,
            corner_radius=10,
            fg_color=ThemeManager.SUCCESS_COLOR
        )
        protein_fill.place(relx=0, rely=0, relwidth=0.3, relheight=1)
        
        # Carbs segment
        carbs_fill = ctk.CTkFrame(
            macro_bar,
            height=20,
            corner_radius=0,
            fg_color=ThemeManager.WARNING_COLOR
        )
        carbs_fill.place(relx=0.3, rely=0, relwidth=0.45, relheight=1)
        
        # Fats segment
        fats_fill = ctk.CTkFrame(
            macro_bar,
            height=20,
            corner_radius=0,
            fg_color=ThemeManager.PRIMARY_COLOR
        )
        fats_fill.place(relx=0.75, rely=0, relwidth=0.25, relheight=1)
        
        # Legend
        legend_frame = ctk.CTkFrame(macros_frame, fg_color="transparent")
        legend_frame.pack(pady=(0, 10), fill="x")
        legend_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Protein
        protein_legend = ctk.CTkFrame(legend_frame, fg_color="transparent")
        protein_legend.grid(row=0, column=0)
        
        protein_color = ctk.CTkFrame(
            protein_legend,
            width=12,
            height=12,
            corner_radius=6,
            fg_color=ThemeManager.SUCCESS_COLOR
        )
        protein_color.grid(row=0, column=0, padx=(0, 5))
        
        protein_text = ctk.CTkLabel(
            protein_legend,
            text="Protein: 30%",
            font=ThemeManager.get_small_font()
        )
        protein_text.grid(row=0, column=1)
        
        # Carbs
        carbs_legend = ctk.CTkFrame(legend_frame, fg_color="transparent")
        carbs_legend.grid(row=0, column=1)
        
        carbs_color = ctk.CTkFrame(
            carbs_legend,
            width=12,
            height=12,
            corner_radius=6,
            fg_color=ThemeManager.WARNING_COLOR
        )
        carbs_color.grid(row=0, column=0, padx=(0, 5))
        
        carbs_text = ctk.CTkLabel(
            carbs_legend,
            text="Carbs: 45%",
            font=ThemeManager.get_small_font()
        )
        carbs_text.grid(row=0, column=1)
        
        # Fats
        fats_legend = ctk.CTkFrame(legend_frame, fg_color="transparent")
        fats_legend.grid(row=0, column=2)
        
        fats_color = ctk.CTkFrame(
            fats_legend,
            width=12,
            height=12,
            corner_radius=6,
            fg_color=ThemeManager.PRIMARY_COLOR
        )
        fats_color.grid(row=0, column=0, padx=(0, 5))
        
        fats_text = ctk.CTkLabel(
            fats_legend,
            text="Fats: 25%",
            font=ThemeManager.get_small_font()
        )
        fats_text.grid(row=0, column=1)
        
        self.visuals["diet"] = diet_frame
        
    def show_visual(self, visual_name):
        """Show a specific visual and hide others"""
        if self.current_visual:
            self.visuals[self.current_visual].grid_forget()
            
        if visual_name in self.visuals:
            self.visuals[visual_name].grid(row=0, column=0, sticky="nsew")
            self.current_visual = visual_name
            
    def update_time_estimate(self, seconds):
        """Update the estimated time remaining"""
        self.time_label.configure(text=f"Estimated time remaining: {seconds} seconds")
        
    def animate_scan(self, is_front=True):
        """Animate scanning line across image"""
        scan_line = self.front_scan if is_front else self.side_scan
        
        # Start at top
        scan_line.place(rely=0)
        
        def move_scan(progress=0):
            if progress <= 1.0:
                scan_line.place(rely=progress)
                self.after(50, lambda: move_scan(progress + 0.05))
            else:
                # Reset to top
                scan_line.place(rely=0)
        
        move_scan()

class ProcessingPage(ctk.CTkFrame):
    """Page that shows processing steps as data is analyzed"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=ThemeManager.BG_COLOR)
        self.controller = controller
        
        # Configure the layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=0)  # Progress
        self.grid_rowconfigure(2, weight=1)  # Content
        
        # Header with title
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(20, 0), padx=20)
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Analyzing Your Data",
            font=ThemeManager.get_title_font()
        )
        self.title_label.grid(row=0, column=0)
        
        # Subtitle
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Please wait while our AI processes your information",
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.GRAY_DARK
        )
        self.subtitle_label.grid(row=1, column=0, pady=(5, 0))
        
        # Main content area with two columns
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=1)  # Steps
        self.content_frame.grid_columnconfigure(1, weight=1)  # Visual card
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Left column - Processing steps
        self.steps_frame = ThemeManager.create_card_frame(self.content_frame)
        self.steps_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        self.steps_frame.grid_columnconfigure(0, weight=1)
        
        # Step title
        self.steps_title = ctk.CTkLabel(
            self.steps_frame,
            text="Processing Steps",
            font=ThemeManager.get_subtitle_font()
        )
        self.steps_title.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")
        
        # Processing steps - each step is a visual element showing progress
        self.steps_container = ctk.CTkFrame(self.steps_frame, fg_color="transparent")
        self.steps_container.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")
        self.steps_container.grid_columnconfigure(0, weight=1)
        
        # Create the steps
        self.processing_steps = {}
        
        # Step 1: Fetching User Input
        self.processing_steps["user_input"] = ProcessingStep(
            self.steps_container,
            "Fetching User Input",
            step_description="Loading your personal details for analysis"
        )
        self.processing_steps["user_input"].grid(row=0, column=0, pady=10, sticky="ew")
        
        # Step 2: Processing Images
        self.processing_steps["image_processing"] = ProcessingStep(
            self.steps_container,
            "Processing Images",
            step_description="Analyzing your body measurements from captured images"
        )
        self.processing_steps["image_processing"].grid(row=1, column=0, pady=10, sticky="ew")
        
        # Step 3: Extracting Measurements
        self.processing_steps["measurements"] = ProcessingStep(
            self.steps_container,
            "Extracting Measurements",
            step_description="Calculating key body metrics and proportions"
        )
        self.processing_steps["measurements"].grid(row=2, column=0, pady=10, sticky="ew")
        
        # Step 4: Somatotype Classification
        self.processing_steps["classification"] = ProcessingStep(
            self.steps_container,
            "Somatotype Classification",
            step_description="Determining your unique body type composition"
        )
        self.processing_steps["classification"].grid(row=3, column=0, pady=10, sticky="ew")
        
        # Step 5: Generating Diet Plan
        self.processing_steps["diet_plan"] = ProcessingStep(
            self.steps_container,
            "Generating Diet Plan",
            step_description="Creating personalized nutrition recommendations"
        )
        self.processing_steps["diet_plan"].grid(row=4, column=0, pady=10, sticky="ew")
        
        # Cancel button at bottom of steps
        self.cancel_button = ThemeManager.create_secondary_button(
            self.steps_frame,
            "Cancel Process",
            self.cancel_processing
        )
        self.cancel_button.grid(row=2, column=0, padx=15, pady=15)
        
        # Right column - Visualization card
        self.visual_card = VisualCard(self.content_frame)
        self.visual_card.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        
        # Internal state tracking for animations and progress
        self.current_step = None
        self.progress_thread = None
        self.stop_requested = False
        
        # Ensure the ProcessingPage has reference to the state manager
        self.state_manager = controller.state_manager if hasattr(controller, 'state_manager') else None
        
    def update_step(self, step_name, status, description=None, progress=None):
        """Update a processing step's status and appearance"""
        if step_name in self.processing_steps:
            self.processing_steps[step_name].update_status(status, description, progress)
            
    def update_all_progress(self, step_index, total_progress):
        """Update progress for all steps based on overall progress"""
        step_names = list(self.processing_steps.keys())
        
        for i, step_name in enumerate(step_names):
            if i < step_index:
                # Steps before current are complete
                self.update_step(step_name, self.processing_steps[step_name].STATUS_COMPLETE, progress=1.0)
            elif i == step_index:
                # Current step is in progress
                self.update_step(step_name, self.processing_steps[step_name].STATUS_PROCESSING, progress=total_progress)
            else:
                # Future steps are waiting
                self.update_step(step_name, self.processing_steps[step_name].STATUS_WAITING, progress=0.0)
                
    def run_process_threaded(self):
        """Start the processing in a separate thread"""
        self.stop_requested = False
        
        if self.progress_thread is None or not self.progress_thread.is_alive():
            self.progress_thread = threading.Thread(target=self.run_process)
            self.progress_thread.daemon = True
            self.progress_thread.start()
            
    def run_process(self):
        """Run the actual processing steps"""
        try:
            # Step 1: Fetch User Input
            self.update_step("user_input", self.processing_steps["user_input"].STATUS_PROCESSING, 
                           "Loading and validating your personal information...")
            self.current_step = "user_input"
            self.visual_card.show_visual("user_data")
            
            # Simulate progress for user input step
            for progress in [0.2, 0.4, 0.6, 0.8, 1.0]:
                if self.stop_requested:
                    return
                time.sleep(0.5)  # Simulate some processing time
                self.update_step("user_input", self.processing_steps["user_input"].STATUS_PROCESSING, 
                               progress=progress)
                
            # Mark user input as complete
            self.update_step("user_input", self.processing_steps["user_input"].STATUS_COMPLETE, 
                           "Personal information loaded successfully")
            
            # Step 2: Process Images
            if self.stop_requested:
                return
            self.update_step("image_processing", self.processing_steps["image_processing"].STATUS_PROCESSING, 
                           "Processing front and side images...")
            self.current_step = "image_processing"
            self.visual_card.show_visual("image_processing")
            
            # Simulate front image scanning
            self.visual_card.animate_scan(is_front=True)
            time.sleep(1)
            self.update_step("image_processing", self.processing_steps["image_processing"].STATUS_PROCESSING, 
                           "Analyzing front pose...", progress=0.3)
            
            # Now run the actual CNN model processing
            self.update_step("image_processing", self.processing_steps["image_processing"].STATUS_PROCESSING, 
                           "Running image analysis algorithm...", progress=0.5)
            
            success = self.run_cnn_model()
            if not success or self.stop_requested:
                self.update_step("image_processing", self.processing_steps["image_processing"].STATUS_ERROR, 
                               "Error processing images. Please try again.")
                return
            
            # Mark image processing as complete
            self.update_step("image_processing", self.processing_steps["image_processing"].STATUS_COMPLETE, 
                           "Images processed successfully")
            
            # Step 3: Extract Measurements
            if self.stop_requested:
                return
            self.update_step("measurements", self.processing_steps["measurements"].STATUS_PROCESSING, 
                           "Calculating body measurements...")
            self.current_step = "measurements"
            self.visual_card.show_visual("measurements")
            
            # Simulate measurement extraction progress
            for progress in [0.2, 0.4, 0.6, 0.8, 1.0]:
                if self.stop_requested:
                    return
                time.sleep(0.5)  # Simulate some processing time
                self.update_step("measurements", self.processing_steps["measurements"].STATUS_PROCESSING, 
                               progress=progress)
            
            # Mark measurements as complete
            self.update_step("measurements", self.processing_steps["measurements"].STATUS_COMPLETE, 
                           "Body measurements calculated successfully")
            
            # Step 4: Classification
            if self.stop_requested:
                return
            self.update_step("classification", self.processing_steps["classification"].STATUS_PROCESSING, 
                           "Determining your somatotype...")
            self.current_step = "classification"
            self.visual_card.show_visual("somatotype")
            
            # Run the actual classifier
            success = self.run_classifier()
            if not success or self.stop_requested:
                self.update_step("classification", self.processing_steps["classification"].STATUS_ERROR, 
                               "Error in classification. Please try again.")
                return
            
            # Mark classification as complete
            self.update_step("classification", self.processing_steps["classification"].STATUS_COMPLETE, 
                           "Somatotype classification complete")
            
            # Step 5: Diet Recommendations
            if self.stop_requested:
                return
            self.update_step("diet_plan", self.processing_steps["diet_plan"].STATUS_PROCESSING, 
                           "Generating personalized diet recommendations...")
            self.current_step = "diet_plan"
            self.visual_card.show_visual("diet")
            
            # Run the actual recommender
            success = self.run_recommender()
            if not success or self.stop_requested:
                self.update_step("diet_plan", self.processing_steps["diet_plan"].STATUS_ERROR, 
                               "Error generating diet plan. Please try again.")
                return
            
            # Mark diet plan as complete
            self.update_step("diet_plan", self.processing_steps["diet_plan"].STATUS_COMPLETE, 
                           "Diet recommendations generated successfully")
            
            # All steps complete - load results in state manager
            if self.state_manager:
                self.state_manager.load_analysis_results()
            
            # Wait a moment to show completion
            time.sleep(1.5)
            
            # Navigate to results page
            if not self.stop_requested:
                self.controller.after(100, lambda: self.controller.show_frame("DietPage"))
                
        except Exception as e:
            print(f"Error during processing: {str(e)}")
            # Show error on current step
            if self.current_step:
                self.update_step(self.current_step, self.processing_steps[self.current_step].STATUS_ERROR, 
                               f"An unexpected error occurred")

    def run_cnn_model(self):
        """Run the CNN model to extract measurements from images"""
        try:
            # Update the visual to show image processing
            self.visual_card.animate_scan(is_front=False)
            
            # Activate the virtual environment and run the CNN script
            activate_script = os.path.join(VENV_DIR, "cnn_env", "Scripts", "activate")
            cnn_script = os.path.join(CNN_DIR, "photos2avatar.py")
            
            command = f'cmd.exe /c "{activate_script} && python {cnn_script}"'
            
            self.update_step("image_processing", self.processing_steps["image_processing"].STATUS_PROCESSING, 
                           "Running CNN model for measurement extraction...", progress=0.7)
            
            process = subprocess.Popen(
                command,
                cwd=CNN_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                shell=True
            )

            process.wait()  # Wait for the process to complete

            return process.returncode == 0
        except Exception as e:
            print(f"CNN model error: {str(e)}")
            return False

    def run_classifier(self):
        """Run the classifier to determine somatotype"""
        try:
            classifier_script = os.path.join(CLASSIFIER_DIR, "classifier.py")
            command = f'cmd.exe /c "python {classifier_script}"'
            
            # Update progress visually
            for progress in [0.2, 0.4, 0.6, 0.8]:
                if self.stop_requested:
                    return False
                time.sleep(0.5)  # Simulate some processing time
                self.update_step("classification", self.processing_steps["classification"].STATUS_PROCESSING, 
                               progress=progress)
            
            process = subprocess.Popen(
                command,
                cwd=CLASSIFIER_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                shell=True
            )

            process.wait()  # Wait for the process to complete

            return process.returncode == 0
        except Exception as e:
            print(f"Classifier error: {str(e)}")
            return False

    def run_recommender(self):
        """Run the recommender to generate diet plan"""
        try:
            recommender_script = os.path.join(RECOMMENDER_DIR, "recommender.py")
            command = f'cmd.exe /c "python {recommender_script}"'
            
            # Update progress visually
            for progress in [0.2, 0.4, 0.6, 0.8]:
                if self.stop_requested:
                    return False
                time.sleep(0.5)  # Simulate some processing time
                self.update_step("diet_plan", self.processing_steps["diet_plan"].STATUS_PROCESSING, 
                               progress=progress)
            
            process = subprocess.Popen(
                command,
                cwd=RECOMMENDER_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                shell=True
            )

            process.wait()  # Wait for the process to complete

            return process.returncode == 0
        except Exception as e:
            print(f"Recommender error: {str(e)}")
            return False

    def cancel_processing(self):
        """Cancel the processing and return to capture page"""
        self.stop_requested = True
        self.controller.after(100, lambda: self.controller.show_frame("CapturePage"))

    def on_show(self):
        """Called when the page is shown"""
        # Reset all steps to waiting
        for step_name in self.processing_steps:
            self.update_step(step_name, self.processing_steps[step_name].STATUS_WAITING, progress=0.0)
        
        # Start with the first step
        self.update_step("user_input", self.processing_steps["user_input"].STATUS_PROCESSING, progress=0.0)
        
        # Start the processing thread
        self.run_process_threaded()

if __name__ == "__main__":
    # For standalone testing
    class DummyController:
        def show_frame(self, frame_name):
            print(f"Switching to frame: {frame_name}")
        def after(self, ms, func):
            func()
            
        class StateManager:
            def __init__(self):
                pass
                
            def load_analysis_results(self):
                print("Loading analysis results")

    controller = DummyController()
    controller.state_manager = controller.StateManager()
    
    # Create and run app
    root = ctk.CTk()
    root.title("Processing Page Test")
    root.geometry("1000x700")
    ThemeManager.setup_theme()
    
    app = ProcessingPage(root, controller)
    app.pack(fill="both", expand=True)
    app.on_show()
    
    root.mainloop()
