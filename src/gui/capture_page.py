"""
Capture Page for the Diet Recommendation System.
Uses computer vision to detect and capture user's front and side poses.
Enhanced with camera selection, manual image upload, and improved guidance.
"""
import customtkinter as ctk
import cv2
import mediapipe as mp
import os
import time
import sys
from threading import Thread
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox

# Import the AdvancedPoseDetector from the capture.py file
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from image_capture.capture import AdvancedPoseDetector
from utils.utils import INPUT_FILES_DIR
from utils.theme_manager import ThemeManager, IMAGES_DIR

class CaptureProgress(ctk.CTkFrame):
    """Progress indicator for capture process"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        # Configure grid
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        
        # Step indicators
        self.steps = []
        self.current_step = 0
        
        # Create step indicators
        steps = ["Input", "Front Pose", "Side Pose", "Analysis"]
        for i, step_text in enumerate(steps):
            step_frame = ctk.CTkFrame(self, fg_color="transparent")
            step_frame.grid(row=0, column=i, padx=5, pady=10)
            
            # Circle with number
            if i == 0:  # Completed
                circle_color = ThemeManager.SUCCESS_COLOR
                text_color = "white"
                step_status = "complete"
                circle_text = "✓"
            elif i == 1:  # Active
                circle_color = ThemeManager.PRIMARY_COLOR
                text_color = "white"
                step_status = "active"
                circle_text = "2"
            else:  # Upcoming
                circle_color = ThemeManager.GRAY_LIGHT
                text_color = ThemeManager.GRAY_DARK
                step_status = "inactive"
                circle_text = str(i+1)
                
            circle = ctk.CTkButton(
                step_frame,
                text=circle_text,
                width=30,
                height=30,
                corner_radius=15,
                fg_color=circle_color,
                hover=False,
                text_color=text_color
            )
            circle.pack(pady=5)
            
            # Step text
            label = ctk.CTkLabel(
                step_frame,
                text=step_text,
                font=ThemeManager.get_small_font(),
                text_color=ThemeManager.PRIMARY_COLOR if step_status == "active" else ThemeManager.GRAY_DARK
            )
            label.pack()
            
            # Save references
            self.steps.append({
                "frame": step_frame,
                "circle": circle,
                "label": label,
                "status": step_status
            })
            
        # Progress line
        self.progress_frame = ctk.CTkFrame(self, height=4, fg_color=ThemeManager.GRAY_LIGHT)
        self.progress_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(0, 10))
        
        # Progress indicator (filled portion)
        self.progress_indicator = ctk.CTkFrame(self.progress_frame, height=4, fg_color=ThemeManager.PRIMARY_COLOR)
        self.progress_indicator.place(relx=0, rely=0, relwidth=0.25, relheight=1)
    
    def update_progress(self, step_index):
        """Update progress indicator to show current step"""
        # Update statuses
        for i, step in enumerate(self.steps):
            if i < step_index:
                # Completed
                step["circle"].configure(
                    fg_color=ThemeManager.SUCCESS_COLOR,
                    text="✓",
                    text_color="white"
                )
                step["label"].configure(
                    text_color=ThemeManager.SUCCESS_COLOR
                )
                step["status"] = "complete"
            elif i == step_index:
                # Active
                step["circle"].configure(
                    fg_color=ThemeManager.PRIMARY_COLOR,
                    text=str(i+1),
                    text_color="white"
                )
                step["label"].configure(
                    text_color=ThemeManager.PRIMARY_COLOR
                )
                step["status"] = "active"
            else:
                # Inactive
                step["circle"].configure(
                    fg_color=ThemeManager.GRAY_LIGHT,
                    text=str(i+1),
                    text_color=ThemeManager.GRAY_DARK
                )
                step["label"].configure(
                    text_color=ThemeManager.GRAY_DARK
                )
                step["status"] = "inactive"
        
        # Update progress bar
        self.progress_indicator.place(relwidth=(step_index + 1) * 0.25)
        self.current_step = step_index
        
class CapturePage(ctk.CTkFrame):
    """Page for capturing user images with pose detection"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=ThemeManager.BG_COLOR)
        self.controller = controller
        
        # Initialize advanced pose detector
        self.detector = AdvancedPoseDetector()
        self.front_captured = False
        self.side_captured = False
        self.capture_thread = None
        self.is_running = False
        self.current_pose = "front"  # Either "front" or "side"
        self.available_cameras = []
        self.selected_camera = 0
        self.capture_mode = "camera"  # "camera" or "manual"
        
        # Detect available cameras
        self._detect_cameras()
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=0)  # Progress
        self.grid_rowconfigure(2, weight=0)  # Mode selection
        self.grid_rowconfigure(3, weight=1)  # Content
        self.grid_rowconfigure(4, weight=0)  # Navigation
        self.grid_rowconfigure(5, weight=0)  # Preview
        
        # Header with title and back button
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(20, 0), padx=20)
        self.header_frame.grid_columnconfigure(1, weight=1)
        
        # Back button
        self.back_button = ThemeManager.create_secondary_button(
            self.header_frame,
            "Back",
            lambda: self.stop_capture_and_go_back()
        )
        self.back_button.grid(row=0, column=0, padx=(0, 20))
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Body Capture",
            font=ThemeManager.get_title_font()
        )
        self.title_label.grid(row=0, column=1)
        
        # Progress indicator
        self.progress_indicator = CaptureProgress(self)
        self.progress_indicator.grid(row=1, column=0, sticky="ew", pady=10, padx=20)
        
        # Mode selection frame
        self.mode_frame = ThemeManager.create_card_frame(self)
        self.mode_frame.grid(row=2, column=0, sticky="ew", pady=10, padx=20)
        self.mode_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Mode selection title
        self.mode_title = ctk.CTkLabel(
            self.mode_frame,
            text="Capture Method",
            font=ThemeManager.get_subtitle_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        self.mode_title.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Camera mode button
        self.camera_mode_button = ThemeManager.create_primary_button(
            self.mode_frame,
            "📷 Live Camera",
            lambda: self.set_capture_mode("camera")
        )
        self.camera_mode_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        # Manual mode button
        self.manual_mode_button = ThemeManager.create_secondary_button(
            self.mode_frame,
            "📁 Upload Images",
            lambda: self.set_capture_mode("manual")
        )
        self.manual_mode_button.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # Camera selection (only visible in camera mode)
        self.camera_selection_frame = ctk.CTkFrame(self.mode_frame, fg_color="transparent")
        self.camera_selection_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")
        
        self.camera_label = ctk.CTkLabel(
            self.camera_selection_frame,
            text="Select Camera:",
            font=ThemeManager.get_label_font()
        )
        self.camera_label.grid(row=0, column=0, padx=10)
        
        self.camera_dropdown = ctk.CTkOptionMenu(
            self.camera_selection_frame,
            values=[f"Camera {i}" if i in self.available_cameras else "No Camera Found" 
                   for i in range(max(1, len(self.available_cameras)))],
            command=self.on_camera_changed
        )
        self.camera_dropdown.grid(row=0, column=1, padx=10, sticky="ew")
        self.camera_selection_frame.grid_columnconfigure(1, weight=1)
        
        
        # Main content frame
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=10)
        self.content_frame.grid_columnconfigure(0, weight=3)  # Camera feed (increased weight)
        self.content_frame.grid_columnconfigure(1, weight=1)  # Instructions
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Camera feed frame
        self.camera_frame = ThemeManager.create_card_frame(self.content_frame)
        self.camera_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        self.camera_frame.grid_columnconfigure(0, weight=1)
        self.camera_frame.grid_rowconfigure(0, weight=0)
        self.camera_frame.grid_rowconfigure(1, weight=1)
        self.camera_frame.grid_rowconfigure(2, weight=0)
        
        # Camera feed header
        self.camera_header = ctk.CTkFrame(self.camera_frame, fg_color="transparent")
        self.camera_header.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        self.camera_header.grid_columnconfigure(0, weight=1)
        self.camera_header.grid_columnconfigure(1, weight=0)
        
        # Camera feed title - Bigger font for better visibility
        self.cam_title = ctk.CTkLabel(
            self.camera_header,
            text="FRONT POSE",
            font=ctk.CTkFont(size=28, weight="bold")  # Increased from 22 to 28
        )
        self.cam_title.grid(row=0, column=0, sticky="w")
        
        # Recording status indicator
        self.status_frame = ctk.CTkFrame(
            self.camera_header,
            fg_color=ThemeManager.DANGER_COLOR,
            corner_radius=5
        )
        self.status_frame.grid(row=0, column=1, sticky="e")
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Not Active",
            font=ThemeManager.get_small_font(),
            text_color="white",
            padx=8,
            pady=2
        )
        self.status_label.grid(row=0, column=0)
        
        # Camera view container
        self.camera_view = ctk.CTkFrame(
            self.camera_frame,
            fg_color="#1E1E1E",  # Dark background for camera feed
        )
        self.camera_view.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.camera_view.grid_propagate(False)  # Don't resize to contents
        
        # Camera feed label
        self.camera_feed = ctk.CTkLabel(
            self.camera_view,
            text="",
            image=None
        )
        self.camera_feed.place(relx=0.5, rely=0.5, anchor="center")
        
        # Large instruction overlay on camera feed - Bigger font for distance reading
        self.instruction_overlay = ctk.CTkLabel(
            self.camera_view,
            text="",
            font=ctk.CTkFont(size=40, weight="bold"),  # Increased from 32 to 40
            text_color="white",
            fg_color=ThemeManager.PRIMARY_COLOR,
            corner_radius=10,
            padx=30,  # Increased padding
            pady=20   # Increased padding
        )
        
        # Pose quality indicator
        self.pose_quality_label = ctk.CTkLabel(
            self.camera_view,
            text="",
            font=ctk.CTkFont(size=22, weight="bold"),  # Increased from 16 to 22
            text_color="white",
            fg_color=ThemeManager.GRAY_DARK,
            corner_radius=5,
            padx=15,  # Increased padding
            pady=8    # Increased padding
        )
        
        # Button container
        self.button_container = ctk.CTkFrame(self.camera_frame, fg_color="transparent")
        self.button_container.grid(row=2, column=0, padx=10, pady=10)
        self.button_container.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Start/Stop button (for camera mode)
        self.capture_button = ThemeManager.create_primary_button(
            self.button_container,
            "Start Camera",
            self.toggle_capture
        )
        self.capture_button.grid(row=0, column=0, padx=5, pady=5)
        
        # Upload front image button (for manual mode)
        self.upload_front_button = ThemeManager.create_secondary_button(
            self.button_container,
            "Upload Front Image",
            lambda: self.upload_image("front")
        )
        self.upload_front_button.grid(row=0, column=1, padx=5, pady=5)
        
        # Upload side image button (for manual mode)
        self.upload_side_button = ThemeManager.create_secondary_button(
            self.button_container,
            "Upload Side Image",
            lambda: self.upload_image("side")
        )
        self.upload_side_button.grid(row=0, column=2, padx=5, pady=5)
        
        # Countdown label
        self.countdown_label = ctk.CTkLabel(
            self.camera_view,
            text="",
            font=ctk.CTkFont(size=80, weight="bold"),  # Increased from 60 to 80
            text_color="white",
            fg_color=ThemeManager.PRIMARY_COLOR,
            corner_radius=50,  # Increased corner radius
            width=100,  # Increased width
            height=100  # Increased height
        )
        
        
        # Instructions panel (enhanced)
        self.instructions_frame = ThemeManager.create_card_frame(self.content_frame)
        self.instructions_frame.grid(row=0, column=1, sticky="nsew")
        self.instructions_frame.grid_columnconfigure(0, weight=1)
        self.instructions_frame.grid_rowconfigure(0, weight=0)
        self.instructions_frame.grid_rowconfigure(1, weight=1)
        self.instructions_frame.grid_rowconfigure(2, weight=0)
        self.instructions_frame.grid_rowconfigure(3, weight=0)
        
        # Instructions header
        self.instructions_title = ctk.CTkLabel(
            self.instructions_frame,
            text="GUIDELINES",  # Shorter text
            font=ctk.CTkFont(size=26, weight="bold"),  # Much bigger and bolder font
            text_color=ThemeManager.PRIMARY_COLOR
        )
        self.instructions_title.grid(row=0, column=0, padx=10, pady=(10, 0))
        
        # Instructions content
        self.instructions_scroll = ctk.CTkScrollableFrame(
            self.instructions_frame, 
            fg_color="transparent",
            scrollbar_fg_color="transparent"
        )
        self.instructions_scroll.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.instructions_scroll.grid_columnconfigure(0, weight=1)
        
        # Current pose instructions - Enhanced for better visibility
        self.current_instructions = ctk.CTkFrame(
            self.instructions_scroll,
            fg_color=ThemeManager.PRIMARY_COLOR,
            corner_radius=10,
            height=200  # Increased from 160 to 200 for bigger fonts
        )
        self.current_instructions.grid(row=0, column=0, pady=5, sticky="ew")
        self.current_instructions.grid_columnconfigure(0, weight=1)
        
        self.current_instructions_title = ctk.CTkLabel(
            self.current_instructions,
            text="FRONT POSE",
            font=ctk.CTkFont(size=32, weight="bold"),  # Increased from 24 to 32
            text_color="white"
        )
        self.current_instructions_title.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        
        # Dynamic instruction text - Enhanced with bigger font and minimal words
        self.dynamic_instructions = ctk.CTkLabel(
            self.current_instructions,
            text="STAND FACING CAMERA",
            font=ctk.CTkFont(size=28, weight="bold"),  # Increased from 20 to 28 and made bold
            text_color="white",
            justify="center",  # Center alignment for better readability
            anchor="center",
            wraplength=350  # Increased wrap length for bigger text
        )
        self.dynamic_instructions.grid(row=1, column=0, padx=15, pady=(0, 20), sticky="ew")
        
        # Quality indicator - New addition for better feedback
        self.quality_indicator = ctk.CTkLabel(
            self.current_instructions,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#FFD700",  # Gold color for quality status
            justify="center",
            anchor="center"
        )
        self.quality_indicator.grid(row=2, column=0, padx=15, pady=(0, 10), sticky="ew")
        
        # Static front pose tips
        self.front_tips_frame = ctk.CTkFrame(
            self.instructions_scroll,
            fg_color=ThemeManager.GRAY_LIGHT,
            corner_radius=10
        )
        self.front_tips_frame.grid(row=1, column=0, pady=5, sticky="ew")
        
        front_tips_title = ctk.CTkLabel(
            self.front_tips_frame,
            text="📋 Front Pose Tips",
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.GRAY_DARK
        )
        front_tips_title.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        front_tips = [
            "• Stand facing the camera directly",
            "• Spread arms slightly away from body",
            "• Keep shoulders level and aligned",
            "• Position feet shoulder-width apart",
            "• Look straight at the camera",
            "• Ensure full body is in frame"
        ]
        
        for i, tip in enumerate(front_tips):
            tip_label = ctk.CTkLabel(
                self.front_tips_frame,
                text=tip,
                font=ThemeManager.get_small_font(),
                text_color=ThemeManager.GRAY_DARK,
                justify="left",
                anchor="w"
            )
            tip_label.grid(row=i+1, column=0, padx=10, pady=1, sticky="w")
        
        # Static side pose tips
        self.side_tips_frame = ctk.CTkFrame(
            self.instructions_scroll,
            fg_color=ThemeManager.GRAY_LIGHT,
            corner_radius=10
        )
        self.side_tips_frame.grid(row=2, column=0, pady=5, sticky="ew")
        
        side_tips_title = ctk.CTkLabel(
            self.side_tips_frame,
            text="📋 Side Pose Tips",
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.GRAY_DARK
        )
        side_tips_title.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        side_tips = [
            "• Turn to your right side",
            "• Keep arms naturally at sides",
            "• Stand with feet hip-width apart",
            "• Maintain straight posture",
            "• Look straight ahead (not at camera)",
            "• Ensure profile view is clear"
        ]
        
        for i, tip in enumerate(side_tips):
            tip_label = ctk.CTkLabel(
                self.side_tips_frame,
                text=tip,
                font=ThemeManager.get_small_font(),
                text_color=ThemeManager.GRAY_DARK,
                justify="left",
                anchor="w"
            )
            tip_label.grid(row=i+1, column=0, padx=10, pady=1, sticky="w")
        
        # Capture status panel
        self.capture_status_panel = ctk.CTkFrame(
            self.instructions_frame,
            corner_radius=10,
            border_width=1,
            border_color=ThemeManager.GRAY_LIGHT
        )
        self.capture_status_panel.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        self.capture_status_title = ctk.CTkLabel(
            self.capture_status_panel,
            text="📊 Capture Status",
            font=ThemeManager.get_label_font()
        )
        self.capture_status_title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        
        # Front image status
        self.front_status = ctk.CTkLabel(
            self.capture_status_panel,
            text="❌ FRONT: NOT CAPTURED",  # Shorter text
            font=ctk.CTkFont(size=18, weight="bold"),  # Much bigger and bolder font
            text_color=ThemeManager.DANGER_COLOR
        )
        self.front_status.grid(row=1, column=0, padx=10, pady=2, sticky="w")
        
        # Side image status
        self.side_status = ctk.CTkLabel(
            self.capture_status_panel,
            text="❌ SIDE: NOT CAPTURED",  # Shorter text
            font=ctk.CTkFont(size=18, weight="bold"),  # Much bigger and bolder font
            text_color=ThemeManager.DANGER_COLOR
        )
        self.side_status.grid(row=2, column=0, padx=10, pady=2, sticky="w")
        
        # Progress message
        self.progress_message = ctk.CTkLabel(
            self.capture_status_panel,
            text="Select capture method to begin",
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.GRAY_DARK,
            wraplength=250
        )
        self.progress_message.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="w")
        
        # Pose control buttons
        self.pose_control_frame = ctk.CTkFrame(
            self.instructions_frame,
            fg_color="transparent"
        )
        self.pose_control_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        self.pose_control_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Switch to front pose button
        self.front_pose_button = ThemeManager.create_secondary_button(
            self.pose_control_frame,
            "👤 Front Pose",
            lambda: self.switch_pose("front")
        )
        self.front_pose_button.grid(row=0, column=0, padx=5, sticky="ew")
        
        # Switch to side pose button
        self.side_pose_button = ThemeManager.create_secondary_button(
            self.pose_control_frame,
            "🚶 Side Pose",
            lambda: self.switch_pose("side")
        )
        self.side_pose_button.grid(row=0, column=1, padx=5, sticky="ew")
        
        # Bottom navigation
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.grid(row=4, column=0, padx=20, pady=20, sticky="ew")
        self.nav_frame.grid_columnconfigure(0, weight=1)
        self.nav_frame.grid_columnconfigure(1, weight=1)
        
        # Previous button
        self.prev_button = ThemeManager.create_secondary_button(
            self.nav_frame,
            "← Previous Step",
            lambda: self.stop_capture_and_go_back()
        )
        self.prev_button.grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        # Next button (initially disabled)
        self.next_button = ThemeManager.create_primary_button(
            self.nav_frame,
            "Continue to Analysis →",
            self.go_to_next_page
        )
        self.next_button.grid(row=0, column=1, padx=(10, 0), sticky="e")
        self.next_button.configure(state="disabled")
        
        # Image preview frame (scrollable)
        self.preview_scrollable_frame = ctk.CTkScrollableFrame(
            self, 
            corner_radius=10,
            height=450,  # Fixed height to enable scrolling
            fg_color=ThemeManager.BG_COLOR,
            scrollbar_button_color=ThemeManager.PRIMARY_COLOR,
            scrollbar_button_hover_color=ThemeManager.PRIMARY_HOVER
        )
        self.preview_scrollable_frame.grid(row=5, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.preview_scrollable_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Preview title
        self.preview_title = ctk.CTkLabel(
            self.preview_scrollable_frame,
            text="📸 Captured Images Preview",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=ThemeManager.GRAY_DARK
        )
        self.preview_title.grid(row=0, column=0, columnspan=2, pady=15)
        
        # Instructions for preview
        self.preview_instructions = ctk.CTkLabel(
            self.preview_scrollable_frame,
            text="Review your captured images below. Use recapture buttons if you need to retake any image.",
            font=ctk.CTkFont(size=12),
            text_color=ThemeManager.GRAY_DARK,
            wraplength=600
        )
        self.preview_instructions.grid(row=1, column=0, columnspan=2, pady=(0, 15))
        
        # Front image preview section
        self.front_preview_frame = ctk.CTkFrame(self.preview_scrollable_frame, corner_radius=8)
        self.front_preview_frame.grid(row=2, column=0, padx=15, pady=10, sticky="ew")
        
        self.front_preview_label = ctk.CTkLabel(
            self.front_preview_frame,
            text="👤 Front View",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        self.front_preview_label.grid(row=0, column=0, pady=10)
        
        self.front_preview = ctk.CTkLabel(
            self.front_preview_frame,
            text="No image captured",
            width=250,
            height=200,
            fg_color=ThemeManager.SECONDARY_COLOR,
            corner_radius=8,
            font=ctk.CTkFont(size=12)
        )
        self.front_preview.grid(row=1, column=0, padx=10, pady=(0, 10))
        
        self.recapture_front_button = ctk.CTkButton(
            self.front_preview_frame,
            text="🔄 Recapture Front",
            command=self.recapture_front,
            fg_color=ThemeManager.WARNING_COLOR,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=35
        )
        self.recapture_front_button.grid(row=2, column=0, pady=(0, 15), padx=10, sticky="ew")
        
        # Side image preview section
        self.side_preview_frame = ctk.CTkFrame(self.preview_scrollable_frame, corner_radius=8)
        self.side_preview_frame.grid(row=2, column=1, padx=15, pady=10, sticky="ew")
        
        self.side_preview_label = ctk.CTkLabel(
            self.side_preview_frame,
            text="🚶 Side View",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        self.side_preview_label.grid(row=0, column=0, pady=10)
        
        self.side_preview = ctk.CTkLabel(
            self.side_preview_frame,
            text="No image captured",
            width=250,
            height=200,
            fg_color=ThemeManager.SECONDARY_COLOR,
            corner_radius=8,
            font=ctk.CTkFont(size=12)
        )
        self.side_preview.grid(row=1, column=0, padx=10, pady=(0, 10))
        
        self.recapture_side_button = ctk.CTkButton(
            self.side_preview_frame,
            text="🔄 Recapture Side",
            command=self.recapture_side,
            fg_color=ThemeManager.WARNING_COLOR,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=35
        )
        self.recapture_side_button.grid(row=2, column=0, pady=(0, 15), padx=10, sticky="ew")
        
        # Completion actions frame
        self.completion_frame = ctk.CTkFrame(self.preview_scrollable_frame, corner_radius=8)
        self.completion_frame.grid(row=3, column=0, columnspan=2, padx=15, pady=15, sticky="ew")
        self.completion_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.completion_title = ctk.CTkLabel(
            self.completion_frame,
            text="✅ Both Images Captured Successfully!",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=ThemeManager.SUCCESS_COLOR
        )
        self.completion_title.grid(row=0, column=0, columnspan=2, pady=15)
        
        self.completion_message = ctk.CTkLabel(
            self.completion_frame,
            text="Your images are ready for analysis. You can proceed to the next step or recapture any image if needed.",
            font=ctk.CTkFont(size=12),
            text_color=ThemeManager.GRAY_DARK,
            wraplength=500
        )
        self.completion_message.grid(row=1, column=0, columnspan=2, pady=(0, 15))
        
        self.retake_all_button = ctk.CTkButton(
            self.completion_frame,
            text="🔄 Retake Both Images",
            command=self.retake_all_images,
            fg_color=ThemeManager.DANGER_COLOR,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=35
        )
        self.retake_all_button.grid(row=2, column=0, padx=10, pady=(0, 15), sticky="ew")
        
        self.proceed_button = ctk.CTkButton(
            self.completion_frame,
            text="✅ Proceed to Analysis",
            command=self.go_to_next_page,
            fg_color=ThemeManager.SUCCESS_COLOR,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=35
        )
        self.proceed_button.grid(row=2, column=1, padx=10, pady=(0, 15), sticky="ew")
        
        # Initially hide preview frame until both images are captured
        self.preview_scrollable_frame.grid_remove()
        
        # Store captured images references
        self.front_image = None
        self.side_image = None
        
        # Initialize UI state
        self.set_capture_mode("camera")
        self._update_ui_state()
    
    def _detect_cameras(self):
        """Detect available cameras with improved detection"""
        self.available_cameras = []
        
        # Try different camera backends and indices
        backends = [cv2.CAP_DSHOW, cv2.CAP_ANY]  # DirectShow for Windows, then any available
        
        for backend in backends:
            for i in range(10):  # Check more camera indices
                try:
                    cap = cv2.VideoCapture(i, backend)
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    
                    # Try to read a frame to verify camera works
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        if i not in self.available_cameras:
                            self.available_cameras.append(i)
                            print(f"Found camera at index {i} with backend {backend}")
                    
                    cap.release()
                except Exception as e:
                    continue
            
            # If we found cameras with this backend, stop checking others
            if self.available_cameras:
                break
        
        # Fallback: try basic detection without backend specification
        if not self.available_cameras:
            for i in range(3):  # Check first 3 indices only for efficiency
                try:
                    cap = cv2.VideoCapture(i)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret and frame is not None:
                            self.available_cameras.append(i)
                            print(f"Found camera at index {i} (fallback method)")
                        cap.release()
                except:
                    continue
        
        print(f"Total cameras detected: {self.available_cameras}")
        
        # Always have at least one option, even if no cameras detected
        if not self.available_cameras:
            self.available_cameras = [0]  # Default to camera 0 (will show error in capture)
    
    def on_camera_changed(self, camera_name):
        """Handle camera selection change"""
        if "No Camera Found" in camera_name:
            return
        try:
            camera_index = int(camera_name.split()[-1])
            self.selected_camera = camera_index
            if self.is_running:
                self.stop_capture()
                # Small delay before restarting
                self.after(100, self.start_capture)
        except (ValueError, IndexError):
            pass
    
    def set_capture_mode(self, mode):
        """Set the capture mode (camera or manual)"""
        self.capture_mode = mode
        
        if mode == "camera":
            self.camera_mode_button.configure(
                fg_color=ThemeManager.PRIMARY_COLOR,
                text_color="white"
            )
            self.manual_mode_button.configure(
                fg_color=ThemeManager.SECONDARY_COLOR,
                text_color=ThemeManager.GRAY_DARK
            )
            # Show camera controls
            self.camera_selection_frame.grid()
            self.capture_button.grid()
            self.upload_front_button.grid_remove()
            self.upload_side_button.grid_remove()
        else:
            self.manual_mode_button.configure(
                fg_color=ThemeManager.PRIMARY_COLOR,
                text_color="white"
            )
            self.camera_mode_button.configure(
                fg_color=ThemeManager.SECONDARY_COLOR,
                text_color=ThemeManager.GRAY_DARK
            )
            # Show upload controls
            self.camera_selection_frame.grid_remove()
            self.capture_button.grid_remove()
            self.upload_front_button.grid()
            self.upload_side_button.grid()
        
        self._update_ui_state()
    
    def upload_image(self, pose_type):
        """Upload an image manually"""
        file_path = filedialog.askopenfilename(
            title=f"Select {pose_type.title()} Pose Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Load and validate image
                image = cv2.imread(file_path)
                if image is None:
                    messagebox.showerror("Error", "Invalid image file.")
                    return
                
                # Process with pose detector
                processed_img = self.detector.detect_pose(image.copy())
                landmarks = self.detector.get_landmarks()
                
                # Check if pose is appropriate
                is_valid_pose = False
                if pose_type == "front" and self.detector.is_front_pose(landmarks):
                    is_valid_pose = True
                elif pose_type == "side" and self.detector.is_side_pose(landmarks):
                    is_valid_pose = True
                elif not landmarks:
                    # If no pose detected, still allow (user might want to proceed anyway)
                    result = messagebox.askyesno(
                        "Pose Not Detected",
                        f"No clear {pose_type} pose detected in this image. Continue anyway?"
                    )
                    is_valid_pose = result
                else:
                    result = messagebox.askyesno(
                        "Pose Mismatch",
                        f"This image appears to be a different pose than {pose_type}. Continue anyway?"
                    )
                    is_valid_pose = result
                
                if is_valid_pose:
                    # Save image to input directory
                    os.makedirs(INPUT_FILES_DIR, exist_ok=True)
                    save_path = os.path.join(INPUT_FILES_DIR, f"input_{pose_type}.png")
                    cv2.imwrite(save_path, image)
                    
                    # Update UI
                    if pose_type == "front":
                        self.front_captured = True
                        self.front_status.configure(
                            text="✅ FRONT: CAPTURED",  # Shorter text
                            text_color=ThemeManager.SUCCESS_COLOR
                        )
                        # Update preview
                        self._update_image_preview("front")
                    else:
                        self.side_captured = True
                        self.side_status.configure(
                            text="✅ SIDE: CAPTURED",  # Shorter text
                            text_color=ThemeManager.SUCCESS_COLOR
                        )
                        # Update preview
                        self._update_image_preview("side")
                    
                    # Display image in camera view
                    display_img = cv2.resize(processed_img, (640, 480))
                    img_tk = self.convert_cv_to_tk(display_img)
                    self.camera_feed.configure(image=img_tk)
                    self.camera_feed.image = img_tk
                    
                    self._update_ui_state()
                    
                    # Check if both images are now captured
                    if self.front_captured and self.side_captured:
                        # Just update the UI, no popup dialog
                        pass
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process image: {str(e)}")
    
    def switch_pose(self, pose_type):
        """Switch between front and side pose modes"""
        self.current_pose = pose_type
        self.update_pose_mode()
        self._update_ui_state()
    
    def _update_ui_state(self):
        """Update UI elements based on current state"""
        # Update capture status
        has_both_images = self.front_captured and self.side_captured
        
        # Update next button - require both images
        if has_both_images:
            self.next_button.configure(state="normal")
        else:
            self.next_button.configure(state="disabled")
        
        # Update pose control buttons
        if self.current_pose == "front":
            self.front_pose_button.configure(
                fg_color=ThemeManager.PRIMARY_COLOR,
                text_color="white"
            )
            self.side_pose_button.configure(
                fg_color=ThemeManager.SECONDARY_COLOR,
                text_color=ThemeManager.GRAY_DARK
            )
        else:
            self.side_pose_button.configure(
                fg_color=ThemeManager.PRIMARY_COLOR,
                text_color="white"
            )
            self.front_pose_button.configure(
                fg_color=ThemeManager.SECONDARY_COLOR,
                text_color=ThemeManager.GRAY_DARK
            )
        
        # Update progress message
        if self.front_captured and self.side_captured:
            self.progress_message.configure(
                text="Both poses captured! Ready to continue.",
                text_color=ThemeManager.SUCCESS_COLOR
            )
        elif self.front_captured and not self.side_captured:
            self.progress_message.configure(
                text="Front pose captured. Now capture the side pose.",
                text_color=ThemeManager.WARNING_COLOR
            )
        elif not self.front_captured and self.side_captured:
            self.progress_message.configure(
                text="Side pose captured. Now capture the front pose.",
                text_color=ThemeManager.WARNING_COLOR
            )
        else:
            if self.capture_mode == "camera":
                self.progress_message.configure(
                    text="Start camera and capture both front and side poses",
                    text_color=ThemeManager.GRAY_DARK
                )
            else:
                self.progress_message.configure(
                    text="Upload your front and side pose images",
                    text_color=ThemeManager.GRAY_DARK
                )
        
        # Update recapture button states
        if self.front_captured:
            self.recapture_front_button.configure(state="normal")
        else:
            self.recapture_front_button.configure(state="disabled")
            
        if self.side_captured:
            self.recapture_side_button.configure(state="normal")
        else:
            self.recapture_side_button.configure(state="disabled")
    
    def _update_instructions(self, message, pose_quality=None):
        """Update the dynamic instruction display with enhanced visibility"""
        # Update main instruction text
        if message:
            self.dynamic_instructions.configure(text=message)
            
            # Update the pose title based on current mode - Minimal text
            if self.current_pose == "front":
                self.current_instructions_title.configure(text="FRONT POSE")
            else:
                self.current_instructions_title.configure(text="SIDE POSE")
        
        # Update quality indicator with enhanced feedback
        if pose_quality:
            quality_text = ""
            quality_color = "white"
            
            if "excellent" in pose_quality.lower() or "perfect" in pose_quality.lower():
                quality_text = "🎯 Excellent Pose Quality!"
                quality_color = "#00FF7F"  # Spring green
            elif "good" in pose_quality.lower() or "hold" in pose_quality.lower():
                quality_text = "✅ Good Pose - Hold Position"
                quality_color = "#FFD700"  # Gold
            elif "capturing" in pose_quality.lower():
                quality_text = "📸 Capturing Now!"
                quality_color = "#00BFFF"  # Deep sky blue
            elif "complete" in pose_quality.lower():
                quality_text = "🎉 Capture Complete!"
                quality_color = "#00FF7F"  # Spring green
            elif "error" in pose_quality.lower() or "camera error" in pose_quality.lower():
                quality_text = "⚠️ Camera Issue"
                quality_color = "#FF6B6B"  # Light red
            else:
                quality_text = f"📊 {pose_quality}"
                quality_color = "#FFD700"  # Gold
            
            self.quality_indicator.configure(
                text=quality_text,
                text_color=quality_color
            )
        else:
            self.quality_indicator.configure(text="")
        
        # Update instruction frame color based on status
        if pose_quality:
            if "excellent" in pose_quality.lower() or "perfect" in pose_quality.lower():
                self.current_instructions.configure(fg_color=ThemeManager.SUCCESS_COLOR)
            elif "capturing" in pose_quality.lower() or "complete" in pose_quality.lower():
                self.current_instructions.configure(fg_color="#4CAF50")  # Material green
            elif "error" in pose_quality.lower():
                self.current_instructions.configure(fg_color=ThemeManager.DANGER_COLOR)
            else:
                self.current_instructions.configure(fg_color=ThemeManager.PRIMARY_COLOR)
        else:
            self.current_instructions.configure(fg_color=ThemeManager.PRIMARY_COLOR)
    
    def toggle_capture(self):
        """Toggle between starting and stopping capture"""
        if not self.is_running:
            self.start_capture()
        else:
            self.stop_capture()
            
    def start_capture(self):
        """Start the capture process"""
        if not self.is_running:
            self.is_running = True
            
            # Update UI
            self.capture_button.configure(text="Stop Camera", fg_color=ThemeManager.DANGER_COLOR)
            self.status_label.configure(text="Recording")
            self.status_frame.configure(fg_color=ThemeManager.SUCCESS_COLOR)
            self.status_message.configure(text="Camera initialized. Position yourself for a front pose.")
            
            # Start capture thread
            self.capture_thread = Thread(target=self.capture_images)
            self.capture_thread.daemon = True
            self.capture_thread.start()
            
    def stop_capture(self):
        """Stop the capture process"""
        self.is_running = False
        self.capture_button.configure(text="Start Camera", fg_color=ThemeManager.PRIMARY_COLOR)
        self.status_label.configure(text="Not Recording")
        self.status_frame.configure(fg_color=ThemeManager.DANGER_COLOR)
        
    def stop_capture_and_go_back(self):
        """Stop capture and navigate back"""
        self.stop_capture()
        self.controller.show_frame("InputPage")
        
    def update_pose_mode(self):
        """Update UI to show current pose mode (front or side)"""
        if self.current_pose == "front":
            # Update title - Minimal text
            self.cam_title.configure(text="FRONT POSE")
            
            # Update instructions
            self.front_instructions.configure(fg_color=ThemeManager.PRIMARY_COLOR)  # Light blue
            self.side_instructions.configure(fg_color=ThemeManager.GRAY_LIGHT)
            
            self.front_instructions_title.configure(text_color=ThemeManager.PRIMARY_COLOR)
            self.side_instructions_title.configure(text_color=ThemeManager.GRAY_DARK)
        else:
            # Update title - Minimal text
            self.cam_title.configure(text="SIDE POSE")
            
            # Update instructions
            self.front_instructions.configure(fg_color=ThemeManager.GRAY_LIGHT)
            self.side_instructions.configure(fg_color=ThemeManager.PRIMARY_COLOR)  # Light blue
            
            self.front_instructions_title.configure(text_color=ThemeManager.GRAY_DARK)
            self.side_instructions_title.configure(text_color=ThemeManager.PRIMARY_COLOR)
            
    def capture_images(self):
        """Thread function to capture images from camera"""
        cap = cv2.VideoCapture(0)
        
        # Set camera resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Define file paths for saving images
        front_image_path = os.path.join(INPUT_FILES_DIR, "input_front.png")
        side_image_path = os.path.join(INPUT_FILES_DIR, "input_side.png")
        os.makedirs(INPUT_FILES_DIR, exist_ok=True)
        
        # For countdown
        countdown_start = None
        countdown_pose = None
        
        while cap.isOpened() and self.is_running:
            success, img = cap.read()
            if not success:
                print("Failed to read from camera")
                break
                
            # Resize to fit display
            h, w = img.shape[:2]
            display_img = img.copy()
            
            # Find pose landmarks
            display_img = self.detector.findPose(display_img)
            lmList = self.detector.findPosition(display_img)
            
            # Key press handling
            key = cv2.waitKey(1) & 0xFF
            if key == ord('c'):  # Manual capture for debugging
                if not self.front_captured and self.current_pose == "front":
                    cv2.imwrite(front_image_path, img)
                    print(f"DEBUG: Front pose manually captured and saved")
                    self.front_captured = True
                    self.current_pose = "side"
                    self.update_pose_mode()
                    self.front_image = self.convert_cv_to_tk(img)
                    
                    # Update status
                    self.status_message.configure(
                        text="Front pose captured! Now turn to your side for the side pose capture."
                    )
                    
                elif not self.side_captured and self.current_pose == "side":
                    cv2.imwrite(side_image_path, img)
                    print(f"DEBUG: Side pose manually captured and saved")
                    self.side_captured = True
                    self.side_image = self.convert_cv_to_tk(img)
                    
                    # Update status
                    self.status_message.configure(
                        text="Side pose captured! Click 'Continue to Analysis' to proceed."
                    )
                    
                    # Enable next button
                    self.next_button.configure(state="disabled")
            
            # Pose detection logic
            if len(lmList) != 0 and self.detector.isFullBodyVisible(lmList, display_img.shape):
                if not self.front_captured and self.current_pose == "front" and self.detector.isFrontPose(lmList, display_img.shape):
                    if countdown_pose != "front":
                        countdown_start = time.time()
                        countdown_pose = "front"
                        print("Front pose detected. Starting countdown...")
                        
                        # Update status
                        self.status_message.configure(
                            text="Good front pose detected! Hold still for capture."
                        )
                        
                elif self.front_captured and not self.side_captured and self.current_pose == "side" and self.detector.isSidePose(lmList, display_img.shape):
                    if countdown_pose != "side":
                        countdown_start = time.time()
                        countdown_pose = "side"
                        print("Side pose detected. Starting countdown...")
                        
                        # Update status
                        self.status_message.configure(
                            text="Good side pose detected! Hold still for capture."
                        )
                        
                else:
                    countdown_start = None
                    countdown_pose = None
                    
                    # Update status based on current pose target
                    if not self.front_captured:
                        self.status_message.configure(
                            text="Position yourself for a front pose. Stand straight, facing the camera."
                        )
                    else:
                        self.status_message.configure(
                            text="Position yourself for a side pose. Turn to your right side."
                        )
                        
            else:
                countdown_start = None
                countdown_pose = None
                
                # Update status for body not fully visible
                self.status_message.configure(
                    text="Please ensure your full body is visible in the frame."
                )
                
            # Countdown logic
            if countdown_start and countdown_pose:
                elapsed_time = time.time() - countdown_start
                remaining_time = max(0, 3 - int(elapsed_time))
                
                if remaining_time > 0:
                    # Show countdown on UI
                    self.countdown_label.configure(text=str(remaining_time))
                    self.countdown_label.place(relx=0.5, rely=0.5, anchor="center")
                
                if remaining_time == 0:
                    success, img = cap.read()
                    if success:
                        # Hide countdown
                        self.countdown_label.place_forget()
                        
                        if countdown_pose == "front":
                            cv2.imwrite(front_image_path, img)
                            print(f"Front pose captured and saved")
                            self.front_captured = True
                            self.current_pose = "side"
                            self.update_pose_mode()
                            self.front_image = self.convert_cv_to_tk(img)
                            
                            # Update status
                            self.status_message.configure(
                                text="Front pose captured! Now turn to your side for the side pose capture."
                            )
                            
                        elif countdown_pose == "side":
                            cv2.imwrite(side_image_path, img)
                            print(f"Side pose captured and saved")
                            self.side_captured = True
                            self.side_image = self.convert_cv_to_tk(img)
                            
                            # Update status
                            self.status_message.configure(
                                text="Side pose captured! Click 'Continue to Analysis' to proceed."
                            )
                            
                            # Enable next button
                            self.next_button.configure(state="normal")
                            
                    countdown_start = None
                    countdown_pose = None
                    
            # Display image in UI
            img_tk = self.convert_cv_to_tk(display_img)
            self.camera_feed.configure(image=img_tk)
            self.camera_feed.image = img_tk
            
            # Break if both poses are captured
            if self.front_captured and self.side_captured:
                self.next_button.configure(state="normal")
        
        # Clean up
        cap.release()
        self.is_running = False
        self.capture_button.configure(text="Start Camera", fg_color=ThemeManager.PRIMARY_COLOR)
        self.status_label.configure(text="Not Recording")
        self.status_frame.configure(fg_color=ThemeManager.DANGER_COLOR)
    
    def toggle_capture(self):
        """Toggle between starting and stopping capture"""
        if not self.is_running:
            self.start_capture()
        else:
            self.stop_capture()
            
    def start_capture(self):
        """Start the capture process"""
        if not self.is_running and self.capture_mode == "camera":
            self.is_running = True
            
            # Update UI
            self.capture_button.configure(text="Stop Camera", fg_color=ThemeManager.DANGER_COLOR)
            self.status_label.configure(text="Active")
            self.status_frame.configure(fg_color=ThemeManager.SUCCESS_COLOR)
            
            # Start capture thread
            self.capture_thread = Thread(target=self.capture_images)
            self.capture_thread.daemon = True
            self.capture_thread.start()
            
    def stop_capture(self):
        """Stop the capture process"""
        self.is_running = False
        if self.capture_mode == "camera":
            self.capture_button.configure(text="Start Camera", fg_color=ThemeManager.PRIMARY_COLOR)
            self.status_label.configure(text="Not Active")
            self.status_frame.configure(fg_color=ThemeManager.DANGER_COLOR)
            self._update_instructions("", "")
        
    def stop_capture_and_go_back(self):
        """Stop capture and navigate back"""
        self.stop_capture()
        self.controller.show_frame("InputPage")
        
    def update_pose_mode(self):
        """Update UI to show current pose mode (front or side)"""
        if self.current_pose == "front":
            self.cam_title.configure(text="FRONT POSE")  # Minimal text
            self.current_instructions_title.configure(text="FRONT POSE")  # Minimal text
        else:
            self.cam_title.configure(text="SIDE POSE")  # Minimal text
            self.current_instructions_title.configure(text="SIDE POSE")  # Minimal text
        
        # Update current instruction highlighting
        if self.current_pose == "front":
            self.front_tips_frame.configure(fg_color=ThemeManager.PRIMARY_COLOR)
            self.side_tips_frame.configure(fg_color=ThemeManager.GRAY_LIGHT)
        else:
            self.side_tips_frame.configure(fg_color=ThemeManager.PRIMARY_COLOR)
            self.front_tips_frame.configure(fg_color=ThemeManager.GRAY_LIGHT)
            
    def capture_images(self):
        """Optimized thread function to capture images from camera with reduced CPU usage"""
        cap = cv2.VideoCapture(self.selected_camera)
        
        # Set camera resolution and optimize settings - Higher resolution for better visibility
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Increased from 640
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # Increased from 480
        cap.set(cv2.CAP_PROP_FPS, 15)  # Limit FPS to reduce CPU usage
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer size
        
        if not cap.isOpened():
            # Show no camera found message
            self.after(0, lambda: self._update_instructions("No camera found. Please check your camera connection or try manual upload.", "Camera Error"))
            # Display a placeholder image
            placeholder_img = self._create_placeholder_image()
            self.after(0, lambda: self._update_camera_display(placeholder_img))
            return
        
        # Define file paths for saving images
        front_image_path = os.path.join(INPUT_FILES_DIR, "input_front.png")
        side_image_path = os.path.join(INPUT_FILES_DIR, "input_side.png")
        os.makedirs(INPUT_FILES_DIR, exist_ok=True)
        
        # For countdown
        countdown_start = None
        countdown_pose = None
        stable_pose_time = 2.0  # Seconds to hold pose before capture
        
        # For reducing CPU usage and UI updates
        last_instruction = ""
        last_quality = ""
        frame_count = 0
        update_interval = 6  # Update UI every 6 frames to reduce CPU load
        pose_check_interval = 3  # Check pose every 3 frames instead of every frame
        last_pose_check = 0
        
        # Cache pose detection results
        cached_landmarks = None
        cached_pose_quality = ""
        
        while cap.isOpened() and self.is_running:
            success, img = cap.read()
            if not success:
                self.after(0, lambda: self._update_instructions("Failed to read from camera", "Camera Error"))
                break
                
            frame_count += 1
            
            # Only process pose detection every few frames to reduce CPU usage
            if frame_count % pose_check_interval == 0:
                # Process with advanced pose detector
                display_img = self.detector.detect_pose(img.copy())
                cached_landmarks = self.detector.get_landmarks()
                cached_pose_quality = self.detector._assess_pose_quality()
                last_pose_check = frame_count
            else:
                # Use cached results and just display the image
                display_img = img.copy()
            
            # Use cached values for pose logic
            landmarks = cached_landmarks
            pose_quality = cached_pose_quality
            
            # Determine instruction message - Minimal words for easy reading
            instruction_msg = ""
            
            if not landmarks:
                instruction_msg = f"🚶 STEP INTO VIEW"
                countdown_start = None
                countdown_pose = None
                
            elif not self.detector.is_full_body_visible(landmarks):
                instruction_msg = f"↩️ MOVE BACK"
                countdown_start = None
                countdown_pose = None
                
            elif self.current_pose == "front":
                if not self.front_captured:
                    if self.detector.is_front_pose(landmarks):
                        if countdown_pose != "front":
                            countdown_start = time.time()
                            countdown_pose = "front"
                            instruction_msg = f"🎯 HOLD STILL"
                        else:
                            elapsed = time.time() - countdown_start
                            remaining = max(0, stable_pose_time - elapsed)
                            if remaining > 0:
                                instruction_msg = f"⏳ STAY STILL {remaining:.1f}s"
                            else:
                                instruction_msg = "📸 CAPTURING..."
                    else:
                        instruction_msg = "👤 FACE CAMERA"
                        countdown_start = None
                        countdown_pose = None
                else:
                    instruction_msg = "✅ FRONT DONE"
                    
            elif self.current_pose == "side":
                if not self.side_captured:
                    if self.detector.is_side_pose(landmarks):
                        if countdown_pose != "side":
                            countdown_start = time.time()
                            countdown_pose = "side"
                            instruction_msg = f"🎯 HOLD STILL"
                        else:
                            elapsed = time.time() - countdown_start
                            remaining = max(0, stable_pose_time - elapsed)
                            if remaining > 0:
                                instruction_msg = f"⏳ STAY STILL {remaining:.1f}s"
                            else:
                                instruction_msg = "📸 CAPTURING..."
                    else:
                        instruction_msg = "🚶 TURN SIDEWAYS"
                        countdown_start = None
                        countdown_pose = None
                else:
                    instruction_msg = "✅ SIDE DONE"
            
            # Update instructions only if changed and at intervals to reduce flickering
            if (frame_count % update_interval == 0 and 
                (instruction_msg != last_instruction or pose_quality != last_quality)):
                self.after(0, lambda msg=instruction_msg, qual=pose_quality: self._update_instructions(msg, qual))
                last_instruction = instruction_msg
                last_quality = pose_quality
            
            # Countdown logic and capture
            if countdown_start and countdown_pose:
                elapsed_time = time.time() - countdown_start
                remaining_time = max(0, stable_pose_time - elapsed_time)
                
                if remaining_time > 0:
                    # Show countdown
                    countdown_display = int(remaining_time * 10) / 10  # Show tenths
                    self.after(0, lambda cd=countdown_display: self._update_countdown(cd))
                else:
                    # Hide countdown and capture
                    self.after(0, lambda: self.countdown_label.place_forget())
                    
                    # Capture the image
                    success, capture_img = cap.read()
                    if success:
                        if countdown_pose == "front" and not self.front_captured:
                            cv2.imwrite(front_image_path, capture_img)
                            self.front_captured = True
                            self.after(0, lambda: self.front_status.configure(
                                text="✅ FRONT: CAPTURED",  # Shorter text
                                text_color=ThemeManager.SUCCESS_COLOR
                            ))
                            # Update preview
                            self.after(0, lambda: self._update_image_preview("front"))
                            # Auto switch to side pose if not captured
                            if not self.side_captured:
                                self.after(0, lambda: self.switch_pose("side"))
                                
                        elif countdown_pose == "side" and not self.side_captured:
                            cv2.imwrite(side_image_path, capture_img)
                            self.side_captured = True
                            self.after(0, lambda: self.side_status.configure(
                                text="✅ SIDE: CAPTURED",  # Shorter text
                                text_color=ThemeManager.SUCCESS_COLOR
                            ))
                            # Update preview
                            self.after(0, lambda: self._update_image_preview("side"))
                            
                        self.after(0, self._update_ui_state)
                        
                    countdown_start = None
                    countdown_pose = None
            else:
                self.after(0, lambda: self.countdown_label.place_forget())
            
            # Display image in UI - update every frame but don't recreate unnecessarily
            img_tk = self.convert_cv_to_tk(display_img)
            self.after(0, lambda img=img_tk: self._update_camera_display(img))
            
            # Auto-stop if both poses captured
            if self.front_captured and self.side_captured:
                self.after(0, lambda: self._update_instructions("Both poses captured successfully!", "Complete"))
                time.sleep(1)  # Show success message briefly
                break
                
            # Manual capture with 'c' key (for debugging)
            if cv2.waitKey(1) & 0xFF == ord('c'):
                if self.current_pose == "front" and not self.front_captured:
                    cv2.imwrite(front_image_path, img)
                    self.front_captured = True
                    self.after(0, lambda: self.front_status.configure(
                        text="✅ FRONT: CAPTURED",  # Shorter text
                        text_color=ThemeManager.SUCCESS_COLOR
                    ))
                    self.after(0, lambda: self._update_image_preview("front"))
                elif self.current_pose == "side" and not self.side_captured:
                    cv2.imwrite(side_image_path, img)
                    self.side_captured = True
                    self.after(0, lambda: self.side_status.configure(
                        text="✅ SIDE: CAPTURED",  # Shorter text
                        text_color=ThemeManager.SUCCESS_COLOR
                    ))
                    self.after(0, lambda: self._update_image_preview("side"))
                self.after(0, self._update_ui_state)
            
            # Add CPU optimization - sleep to reduce processing load
            time.sleep(0.033)  # ~30 FPS, reduces CPU usage significantly
        
        # Clean up
        cap.release()
        self.is_running = False
        if self.capture_mode == "camera":
            self.after(0, lambda: self.capture_button.configure(text="Start Camera", fg_color=ThemeManager.PRIMARY_COLOR))
            self.after(0, lambda: self.status_label.configure(text="Not Active"))
            self.after(0, lambda: self.status_frame.configure(fg_color=ThemeManager.DANGER_COLOR))
            self.after(0, lambda: self._update_instructions("", ""))
    
    def _update_camera_display(self, img_tk):
        """Safely update camera display"""
        try:
            self.camera_feed.configure(image=img_tk)
            self.camera_feed.image = img_tk
        except:
            pass  # Ignore errors if widget is destroyed
    
    def _update_countdown(self, countdown_display):
        """Safely update countdown display"""
        try:
            self.countdown_label.configure(text=f"{countdown_display:.1f}")
            self.countdown_label.place(relx=0.5, rely=0.5, anchor="center")
        except:
            pass  # Ignore errors if widget is destroyed
    
    def _create_placeholder_image(self):
        """Create a placeholder image for when no camera is found"""
        import numpy as np
        
        # Create a simple placeholder image
        placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
        placeholder.fill(50)  # Dark gray
        
        # Add text
        cv2.putText(placeholder, "No Camera Found", (150, 220), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
        cv2.putText(placeholder, "Try Manual Upload", (170, 260), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)
        
        return self.convert_cv_to_tk(placeholder)
    
    def _update_image_preview(self, image_type):
        """Update the preview display for the specified image type"""
        if image_type == "front":
            front_image_path = os.path.join(INPUT_FILES_DIR, "input_front.png")
            if os.path.exists(front_image_path):
                # Load and display the image
                img = cv2.imread(front_image_path)
                if img is not None:
                    # Resize for preview
                    img_resized = cv2.resize(img, (250, 200))
                    # Convert to RGB for display
                    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
                    img_pil = Image.fromarray(img_rgb)
                    img_tk = ctk.CTkImage(img_pil, size=(250, 200))
                    
                    self.front_preview.configure(image=img_tk, text="")
                    self.front_preview.image = img_tk
                    
        elif image_type == "side":
            side_image_path = os.path.join(INPUT_FILES_DIR, "input_side.png")
            if os.path.exists(side_image_path):
                # Load and display the image
                img = cv2.imread(side_image_path)
                if img is not None:
                    # Resize for preview
                    img_resized = cv2.resize(img, (250, 200))
                    # Convert to RGB for display
                    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
                    img_pil = Image.fromarray(img_rgb)
                    img_tk = ctk.CTkImage(img_pil, size=(250, 200))
                    
                    self.side_preview.configure(image=img_tk, text="")
                    self.side_preview.image = img_tk
        
        # Show preview frame only if both images are captured
        if self.front_captured and self.side_captured:
            self.preview_scrollable_frame.grid()
        else:
            self.preview_scrollable_frame.grid_remove()
    
    def recapture_front(self):
        """Recapture the front image"""
        # Reset front capture status
        self.front_captured = False
        self.front_status.configure(
            text="❌ Front image: Not captured",
            text_color=ThemeManager.DANGER_COLOR
        )
        
        # Reset preview
        self.front_preview.configure(
            image=None,
            text="No image captured",
            fg_color=ThemeManager.SECONDARY_COLOR
        )
        
        # Hide preview frame since we no longer have both images
        self.preview_scrollable_frame.grid_remove()
        
        # Switch to front pose if in camera mode
        if self.capture_mode == "camera":
            self.switch_pose("front")
            # If camera is not running, start it
            if not self.is_running:
                self.start_capture()
        
        # Update UI state
        self._update_ui_state()
    
    def recapture_side(self):
        """Recapture the side image"""
        # Reset side capture status
        self.side_captured = False
        self.side_status.configure(
            text="❌ Side image: Not captured",
            text_color=ThemeManager.DANGER_COLOR
        )
        
        # Reset preview
        self.side_preview.configure(
            image=None,
            text="No image captured",
            fg_color=ThemeManager.SECONDARY_COLOR
        )
        
        # Hide preview frame since we no longer have both images
        self.preview_scrollable_frame.grid_remove()
        
        # Switch to side pose if in camera mode
        if self.capture_mode == "camera":
            self.switch_pose("side")
            # If camera is not running, start it
            if not self.is_running:
                self.start_capture()
        
        # Update UI state
        self._update_ui_state()
    
    def _show_completion_dialog(self):
        """Show completion dialog when both images are captured"""
        result = messagebox.askquestion(
            "Images Captured Successfully!",
            "Both front and side images have been captured.\n\n"
            "Please review the images in the preview below.\n"
            "Are you satisfied with the captured images?\n\n"
            "Click 'Yes' to continue to analysis, or 'No' to recapture.",
            icon='question'
        )
        
        if result == 'yes':
            # Auto-scroll to show preview
            self.preview_frame.tkraise()
            self.update_idletasks()
            
            # Optional: Auto-proceed after showing preview
            self.after(2000, self.go_to_next_page)  # Wait 2 seconds then proceed
        else:
            # User wants to recapture - reset status
            self.front_captured = False
            self.side_captured = False
            self.front_status.configure(
                text="❌ Front image: Not captured",
                text_color=ThemeManager.DANGER_COLOR
            )
            self.side_status.configure(
                text="❌ Side image: Not captured", 
                text_color=ThemeManager.DANGER_COLOR
            )
            
            # Reset previews
            self.front_preview.configure(
                image=None,
                text="No image captured",
                fg_color=ThemeManager.SECONDARY_COLOR
            )
            self.side_preview.configure(
                image=None,
                text="No image captured",
                fg_color=ThemeManager.SECONDARY_COLOR
            )
            
            # Hide preview frame
            self.preview_frame.grid_remove()
            
            # Update UI state
            self._update_ui_state()
            
            # Restart capture if in camera mode
            if self.capture_mode == "camera":
                self.switch_pose("front")
    
    def retake_all_images(self):
        """Reset both front and side images for complete recapture"""
        # Reset both capture statuses
        self.front_captured = False
        self.side_captured = False
        
        # Update status displays
        self.front_status.configure(
            text="❌ Front image: Not captured",
            text_color=ThemeManager.DANGER_COLOR
        )
        self.side_status.configure(
            text="❌ Side image: Not captured",
            text_color=ThemeManager.DANGER_COLOR
        )
        
        # Reset previews
        self.front_preview.configure(
            image=None,
            text="No image captured",
            fg_color=ThemeManager.SECONDARY_COLOR
        )
        self.side_preview.configure(
            image=None,
            text="No image captured",
            fg_color=ThemeManager.SECONDARY_COLOR
        )
        
        # Hide preview frame
        self.preview_scrollable_frame.grid_remove()
        
        # Switch to front pose and restart camera if in camera mode
        if self.capture_mode == "camera":
            self.switch_pose("front")
            if not self.is_running:
                self.start_capture()
        
        # Update UI state
        self._update_ui_state()
        
    def convert_cv_to_tk(self, img):
        """Convert OpenCV image to Tkinter compatible image"""
        # Resize to fit larger display area while maintaining aspect ratio for full visibility
        h, w = img.shape[:2]
        target_w, target_h = 800, 600  # Increased from 640x480 for better visibility
        
        # Calculate scaling factor
        scale = min(target_w/w, target_h/h)
        new_w, new_h = int(w*scale), int(h*scale)
        
        # Resize image
        resized_img = cv2.resize(img, (new_w, new_h))
        
        # Convert to RGB and create PIL image
        rgb_image = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        return ctk.CTkImage(pil_image, size=(new_w, new_h))
        
    def go_to_next_page(self):
        """Navigate to processing page after successful capture"""
        # Make sure the camera is stopped
        self.stop_capture()
        
        # Validate that at least one image was captured
        if not self.front_captured and not self.side_captured:
            messagebox.showwarning(
                "No Images Captured", 
                "Please capture at least one pose image before proceeding."
            )
            return
        
        # Store image data in state manager 
        image_data = {}
        if self.front_captured:
            image_data["front_image_path"] = os.path.join(INPUT_FILES_DIR, "input_front.png")
        if self.side_captured:
            image_data["side_image_path"] = os.path.join(INPUT_FILES_DIR, "input_side.png")
            
        self.controller.state_manager.update_image_data(**image_data)
        
        # Navigate to processing page
        self.controller.show_frame("ProcessingPage")
        
    def on_show(self):
        """Called when page is shown"""
        # Reset capture state
        self.front_captured = False
        self.side_captured = False
        self.is_running = False
        self.current_pose = "front"
        
        # Reset UI status
        self.front_status.configure(
            text="❌ Front image: Not captured",
            text_color=ThemeManager.DANGER_COLOR
        )
        self.side_status.configure(
            text="❌ Side image: Not captured",
            text_color=ThemeManager.DANGER_COLOR
        )
        
        # Update UI
        self.update_pose_mode()
        self._update_ui_state()
        self.capture_button.configure(text="Start Camera", fg_color=ThemeManager.PRIMARY_COLOR)
        self.status_label.configure(text="Not Active")
        self.status_frame.configure(fg_color=ThemeManager.DANGER_COLOR)
        
        # Update progress indicator
        self.progress_indicator.update_progress(1)  # Set to second step (Front Pose)
        
if __name__ == "__main__":
    # For standalone testing
    class DummyController:
        def show_frame(self, frame_name):
            print(f"Switching to frame: {frame_name}")
            
        class StateManager:
            def __init__(self):
                self.image_data = {
                    "front_image_path": None,
                    "side_image_path": None
                }
            def update_image_data(self, **kwargs):
                self.image_data.update(kwargs)
                print(f"Updated image data: {self.image_data}")
    
    controller = DummyController()
    controller.state_manager = controller.StateManager()
    
    # Create and run app
    root = ctk.CTk()
    root.title("Capture Page Test")
    root.geometry("1000x700")
    ThemeManager.setup_theme()
    
    app = CapturePage(root, controller)
    app.pack(fill="both", expand=True)
    app.on_show()
    
    root.mainloop()
