"""
Capture Page for the Diet Recommendation System.
Uses computer vision to detect and capture user's front and side poses.
Enhanced with camera selection, manual image upload, and improved guidance.
"""
import customtkinter as ctk
import cv2
import os
import sys
import time
from threading import Thread
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox

# Import the AdvancedPoseDetector from the capture.py file
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from image_capture.capture import AdvancedPoseDetector
from utils.utils import INPUT_FILES_DIR
from utils.theme_manager import ThemeManager


class StepIndicator(ctk.CTkFrame):
    """Minimal, clean step indicator"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        
        self.grid_columnconfigure(1, weight=1)
        
        # Current step info
        self.step_label = ctk.CTkLabel(
            self,
            text="STEP 1 OF 2",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=ThemeManager.GRAY_DARK
        )
        self.step_label.grid(row=0, column=0, sticky="w")
        
        # Progress bar
        self.progress_frame = ctk.CTkFrame(self, height=4, fg_color=ThemeManager.GRAY_LIGHT)
        self.progress_frame.grid(row=0, column=1, sticky="ew", padx=(20, 0))
        
        self.progress_fill = ctk.CTkFrame(
            self.progress_frame, 
            height=4, 
            fg_color=ThemeManager.PRIMARY_COLOR
        )
        self.progress_fill.place(relx=0, rely=0, relwidth=0.5, relheight=1)
    
    def update_step(self, step, total_steps, title):
        """Update the step indicator"""
        self.step_label.configure(text=f"STEP {step} OF {total_steps}")
        progress = step / total_steps
        self.progress_fill.place(relwidth=progress)


class CaptureCard(ctk.CTkFrame):
    """Individual capture card for front/side poses"""
    
    def __init__(self, parent, pose_type, pose_emoji, instructions):
        super().__init__(parent, corner_radius=20, fg_color="white", border_width=3, border_color=ThemeManager.GRAY_LIGHT, width=450, height=600)
        
        self.pose_type = pose_type
        self.is_captured = False
        self.image_data = None
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="ew", padx=32, pady=(32, 16))
        
        self.icon_label = ctk.CTkLabel(
            self.header,
            text=pose_emoji,
            font=ctk.CTkFont(size=40)
        )
        self.icon_label.grid(row=0, column=0, sticky="w")
        
        self.title_label = ctk.CTkLabel(
            self.header,
            text=f"{pose_type.title()} View",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=ThemeManager.GRAY_DARK
        )
        self.title_label.grid(row=0, column=1, sticky="w", padx=(16, 0))
        
        # Status indicator
        self.status_frame = ctk.CTkFrame(
            self.header,
            fg_color=ThemeManager.GRAY_LIGHT,
            corner_radius=16,
            height=32
        )
        self.status_frame.grid(row=0, column=2, sticky="e")
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Not Captured",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=ThemeManager.GRAY_DARK,
            padx=20,
            pady=8
        )
        self.status_label.pack()
        
        self.header.grid_columnconfigure(1, weight=1)
        
        # Content area (image or placeholder)
        self.content_frame = ctk.CTkFrame(self, fg_color=ThemeManager.SECONDARY_COLOR, corner_radius=16)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=32, pady=(0, 16))
        
        # Placeholder content
        self.placeholder_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.placeholder_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        self.placeholder_icon = ctk.CTkLabel(
            self.placeholder_frame,
            text="📷",
            font=ctk.CTkFont(size=64)
        )
        self.placeholder_icon.pack(pady=(0, 20))
        
        self.placeholder_text = ctk.CTkLabel(
            self.placeholder_frame,
            text=instructions,
            font=ctk.CTkFont(size=20),
            text_color=ThemeManager.GRAY_DARK,
            justify="center",
            wraplength=300
        )
        self.placeholder_text.pack()
        
        # Image display (initially hidden)
        self.image_label = ctk.CTkLabel(
            self.content_frame,
            text="",
            corner_radius=8
        )
        
        # Action buttons
        self.buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.buttons_frame.grid(row=2, column=0, sticky="ew", padx=32, pady=(0, 32))
        self.buttons_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Capture button
        self.capture_button = ctk.CTkButton(
            self.buttons_frame,
            text=f"� Start Camera",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=56,
            corner_radius=28,
            fg_color=ThemeManager.PRIMARY_COLOR,
            hover_color=ThemeManager.PRIMARY_HOVER
        )
        self.capture_button.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        
        # Upload button
        self.upload_button = ctk.CTkButton(
            self.buttons_frame,
            text="📁 Upload",
            font=ctk.CTkFont(size=18),
            height=56,
            corner_radius=28,
            fg_color="transparent",
            border_width=3,
            border_color=ThemeManager.GRAY_LIGHT,
            text_color=ThemeManager.GRAY_DARK,
            hover_color=ThemeManager.GRAY_LIGHT
        )
        self.upload_button.grid(row=0, column=1, sticky="ew", padx=(8, 0))
    
    def set_captured(self, image=None, image_path=None):
        """Mark as captured and display image"""
        self.is_captured = True
        
        # Update status
        self.status_frame.configure(fg_color=ThemeManager.SUCCESS_COLOR)
        self.status_label.configure(
            text="✓ Captured",
            text_color="white"
        )
        
        # Hide placeholder
        self.placeholder_frame.pack_forget()
        
        # Show image if provided
        if image is not None or image_path is not None:
            try:
                if image_path:
                    pil_image = Image.open(image_path)
                else:
                    pil_image = image
                    
                # Resize image to fit
                pil_image.thumbnail((400, 500), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(pil_image)
                
                self.image_label.configure(image=photo)
                self.image_label.image = photo  # Keep reference
                self.image_label.pack(expand=True, fill="both", padx=20, pady=20)
            except Exception as e:
                print(f"Error loading image: {e}")
        
        # Update button text
        self.capture_button.configure(text=f"🔄 Recapture")
    
    def reset(self):
        """Reset to uncaptured state"""
        self.is_captured = False
        self.image_data = None
        
        # Reset status
        self.status_frame.configure(fg_color=ThemeManager.GRAY_LIGHT)
        self.status_label.configure(
            text="Not Captured",
            text_color=ThemeManager.GRAY_DARK
        )
        
        # Hide image and show placeholder
        self.image_label.pack_forget()
        self.placeholder_frame.pack(expand=True, fill="both", padx=40, pady=40)
        
        # Reset button text
        self.capture_button.configure(text=f"� Start Camera")
    
    def update_button_text(self, is_camera_active, is_captured):
        """Update button text based on camera and capture state"""
        if is_captured:
            self.capture_button.configure(text=f"🔄 Recapture")
        elif is_camera_active:
            self.capture_button.configure(text=f"⏹️ Stop Camera")
        else:
            self.capture_button.configure(text=f"📹 Start Camera")


class LiveCameraView(ctk.CTkFrame):
    """Clean live camera view with overlay instructions"""
    
    def __init__(self, parent):
        super().__init__(parent, corner_radius=16, fg_color="white", border_width=2, border_color=ThemeManager.GRAY_LIGHT)
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 12))
        self.header.grid_columnconfigure(1, weight=1)
        
        self.camera_icon = ctk.CTkLabel(
            self.header,
            text="📹",
            font=ctk.CTkFont(size=28)
        )
        self.camera_icon.grid(row=0, column=0)
        
        self.camera_title = ctk.CTkLabel(
            self.header,
            text="Live Camera",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=ThemeManager.GRAY_DARK
        )
        self.camera_title.grid(row=0, column=1, sticky="w", padx=(12, 0))
        
        # Recording status
        self.status_dot = ctk.CTkFrame(
            self.header,
            width=12,
            height=12,
            corner_radius=6,
            fg_color=ThemeManager.GRAY_LIGHT
        )
        self.status_dot.grid(row=0, column=2, padx=(0, 8))
        
        self.status_text = ctk.CTkLabel(
            self.header,
            text="Inactive",
            font=ctk.CTkFont(size=12),
            text_color=ThemeManager.GRAY_DARK
        )
        self.status_text.grid(row=0, column=3)
        
        # Camera view container
        self.camera_container = ctk.CTkFrame(self, fg_color="#000000", corner_radius=12)
        self.camera_container.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        
        # Camera feed
        self.camera_feed = ctk.CTkLabel(
            self.camera_container,
            text=""
        )
        self.camera_feed.place(relx=0.5, rely=0.5, anchor="center")
        
        # Overlay instructions
        self.instruction_overlay = ctk.CTkLabel(
            self.camera_container,
            text="",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white",
            fg_color=ThemeManager.PRIMARY_COLOR,  # Solid color instead of transparent
            corner_radius=8,
            padx=20,
            pady=12
        )
        
        # Countdown overlay
        self.countdown_overlay = ctk.CTkLabel(
            self.camera_container,
            text="",
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color="white",
            fg_color=ThemeManager.PRIMARY_COLOR,
            corner_radius=50,
            width=100,
            height=100
        )
        
        # Camera placeholder
        self.show_placeholder()
    
    def show_placeholder(self):
        """Show camera placeholder when not active"""
        self.camera_feed.configure(
            image=None,
            text="Camera will appear here",
            font=ctk.CTkFont(size=16),
            text_color=ThemeManager.GRAY_DARK
        )
    
    def set_active(self, active=True):
        """Set camera status"""
        if active:
            self.status_dot.configure(fg_color=ThemeManager.SUCCESS_COLOR)
            self.status_text.configure(text="Live", text_color=ThemeManager.SUCCESS_COLOR)
        else:
            self.status_dot.configure(fg_color=ThemeManager.GRAY_LIGHT)
            self.status_text.configure(text="Inactive", text_color=ThemeManager.GRAY_DARK)
    
    def update_feed(self, image_tk):
        """Update camera feed"""
        self.camera_feed.configure(image=image_tk, text="")
        self.camera_feed.image = image_tk
    
    def show_instruction(self, text, position="top"):
        """Show overlay instruction"""
        self.instruction_overlay.configure(text=text)
        if position == "top":
            self.instruction_overlay.place(relx=0.5, y=40, anchor="n")
        else:
            self.instruction_overlay.place(relx=0.5, rely=0.5, anchor="center")
    
    def hide_instruction(self):
        """Hide overlay instruction"""
        self.instruction_overlay.place_forget()
    
    def show_countdown(self, count):
        """Show countdown overlay"""
        self.countdown_overlay.configure(text=str(count))
        self.countdown_overlay.place(relx=0.5, rely=0.5, anchor="center")
    
    def hide_countdown(self):
        """Hide countdown overlay"""
        self.countdown_overlay.place_forget()


class CapturePage(ctk.CTkFrame):
    """Improved capture page with clean UI/UX"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=ThemeManager.BG_COLOR)
        self.controller = controller
        
        # Initialize state
        self.detector = AdvancedPoseDetector()
        self.current_step = 1  # 1: Front pose, 2: Side pose
        self.is_camera_active = False
        self.capture_thread = None
        self.available_cameras = []
        self.selected_camera = 0
        
        # Capture data
        self.front_captured = False
        self.side_captured = False
        self.front_image_path = None
        self.side_image_path = None
        
        # Detect cameras
        self._detect_cameras()
        
        # Configure main grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Header section
        self._create_header()
        
        # Step indicator
        self._create_step_indicator()
        
        # Main content
        self._create_main_content()
        
        # Footer navigation
        self._create_footer()
        
        # Update initial state
        self._update_ui_state()
    
    def _create_header(self):
        """Create clean header with title and back button"""
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=32, pady=(24, 0))
        self.header_frame.grid_columnconfigure(1, weight=1)
        
        # Back button
        self.back_button = ctk.CTkButton(
            self.header_frame,
            text="← Back",
            font=ctk.CTkFont(size=14),
            width=80,
            height=32,
            corner_radius=16,
            fg_color="transparent",
            text_color=ThemeManager.GRAY_DARK,
            hover_color=ThemeManager.GRAY_LIGHT,
            command=self._go_back
        )
        self.back_button.grid(row=0, column=0, sticky="w")
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Body Capture",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=ThemeManager.GRAY_DARK
        )
        self.title_label.grid(row=0, column=1)
    
    def _create_step_indicator(self):
        """Create step indicator"""
        self.step_indicator = StepIndicator(self)
        self.step_indicator.grid(row=1, column=0, sticky="ew", padx=32, pady=(32, 0))
    
    def _create_main_content(self):
        """Create main content area"""
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=2, column=0, sticky="nsew", padx=32, pady=32)
        self.content_frame.grid_columnconfigure((0, 1), weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Left side - Camera view (larger)
        self.camera_view = LiveCameraView(self.content_frame)
        self.camera_view.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        
        # Right side - Current capture card
        self.current_card_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.current_card_frame.grid(row=0, column=1, sticky="nsew")
        self.current_card_frame.grid_columnconfigure(0, weight=1)
        self.current_card_frame.grid_rowconfigure(1, weight=1)
        
        # Camera selection (compact)
        self.camera_selection = ctk.CTkFrame(self.current_card_frame, corner_radius=12, fg_color="white", height=60)
        self.camera_selection.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        self.camera_selection.grid_propagate(False)
        
        self.camera_label = ctk.CTkLabel(
            self.camera_selection,
            text="Camera:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.camera_label.pack(side="left", padx=(16, 8), pady=16)
        
        self.camera_dropdown = ctk.CTkOptionMenu(
            self.camera_selection,
            values=self._get_camera_options(),
            font=ctk.CTkFont(size=14),
            corner_radius=8,
            command=self._on_camera_changed
        )
        self.camera_dropdown.pack(side="left", padx=(0, 16), pady=12)
        
        # Capture cards
        self.front_card = CaptureCard(
            self.current_card_frame,
            "front",
            "🧍",
            "Stand facing the camera with arms slightly away from your body"
        )
        
        self.side_card = CaptureCard(
            self.current_card_frame,
            "side", 
            "🚶",
            "Turn to your right side with arms naturally at your sides"
        )
        
        # Initially show front card
        self.front_card.grid(row=1, column=0, sticky="nsew")
        
        # Bind button commands
        self.front_card.capture_button.configure(command=lambda: self._handle_capture("front"))
        self.front_card.upload_button.configure(command=lambda: self._handle_upload("front"))
        self.side_card.capture_button.configure(command=lambda: self._handle_capture("side"))
        self.side_card.upload_button.configure(command=lambda: self._handle_upload("side"))
    
    def _create_footer(self):
        """Create footer with navigation"""
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.grid(row=3, column=0, sticky="ew", padx=32, pady=(0, 24))
        self.footer_frame.grid_columnconfigure(1, weight=1)
        
        # Previous button
        self.prev_button = ctk.CTkButton(
            self.footer_frame,
            text="← Previous",
            font=ctk.CTkFont(size=14),
            width=120,
            height=44,
            corner_radius=22,
            fg_color="transparent",
            border_width=2,
            border_color=ThemeManager.GRAY_LIGHT,
            text_color=ThemeManager.GRAY_DARK,
            hover_color=ThemeManager.GRAY_LIGHT,
            command=self._go_to_previous
        )
        self.prev_button.grid(row=0, column=0, sticky="w")
        
        # Next button
        self.next_button = ctk.CTkButton(
            self.footer_frame,
            text="Next →",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=120,
            height=44,
            corner_radius=22,
            fg_color=ThemeManager.PRIMARY_COLOR,
            hover_color=ThemeManager.PRIMARY_HOVER,
            command=self._go_to_next
        )
        self.next_button.grid(row=0, column=2, sticky="e")
        
        # Step navigation (center)
        self.step_nav_frame = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        self.step_nav_frame.grid(row=0, column=1)
        
        # Front step button
        self.front_step_button = ctk.CTkButton(
            self.step_nav_frame,
            text="🧍 Front",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=100,
            height=36,
            corner_radius=18,
            fg_color=ThemeManager.PRIMARY_COLOR,
            hover_color=ThemeManager.PRIMARY_HOVER,
            command=lambda: self._switch_to_step(1)
        )
        self.front_step_button.grid(row=0, column=0, padx=(0, 4))
        
        # Side step button
        self.side_step_button = ctk.CTkButton(
            self.step_nav_frame,
            text="🚶 Side",
            font=ctk.CTkFont(size=14),
            width=100,
            height=36,
            corner_radius=18,
            fg_color="transparent",
            border_width=2,
            border_color=ThemeManager.GRAY_LIGHT,
            text_color=ThemeManager.GRAY_DARK,
            hover_color=ThemeManager.GRAY_LIGHT,
            command=lambda: self._switch_to_step(2)
        )
        self.side_step_button.grid(row=0, column=1, padx=(4, 0))
    
    def _detect_cameras(self):
        """Detect available cameras"""
        self.available_cameras = []
        
        for i in range(5):  # Check first 5 camera indices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                self.available_cameras.append(i)
                cap.release()
        
        if not self.available_cameras:
            self.available_cameras = [0]  # Fallback
    
    def _get_camera_options(self):
        """Get camera dropdown options"""
        if self.available_cameras:
            return [f"Camera {i+1}" for i in range(len(self.available_cameras))]
        return ["No Camera Found"]
    
    def _on_camera_changed(self, selection):
        """Handle camera selection change"""
        try:
            camera_index = int(selection.split()[-1]) - 1
            if 0 <= camera_index < len(self.available_cameras):
                self.selected_camera = self.available_cameras[camera_index]
                if self.is_camera_active:
                    self._restart_camera()
        except (ValueError, IndexError):
            pass
    
    def _switch_to_step(self, step):
        """Switch between front and side capture steps"""
        if step == self.current_step:
            return
        
        self.current_step = step
        
        # Hide current card
        self.front_card.grid_remove()
        self.side_card.grid_remove()
        
        # Show appropriate card
        if step == 1:
            self.front_card.grid(row=1, column=0, sticky="nsew")
        else:
            self.side_card.grid(row=1, column=0, sticky="nsew")
        
        # Update UI
        self._update_ui_state()
    
    def _update_ui_state(self):
        """Update UI based on current state"""
        # Update step indicator
        title = "Front Pose Capture" if self.current_step == 1 else "Side Pose Capture"
        self.step_indicator.update_step(self.current_step, 2, title)
        
        # Update step buttons
        if self.current_step == 1:
            self.front_step_button.configure(
                fg_color=ThemeManager.PRIMARY_COLOR,
                text_color="white"
            )
            self.side_step_button.configure(
                fg_color="transparent",
                text_color=ThemeManager.GRAY_DARK
            )
        else:
            self.side_step_button.configure(
                fg_color=ThemeManager.PRIMARY_COLOR,
                text_color="white"
            )
            self.front_step_button.configure(
                fg_color="transparent",
                text_color=ThemeManager.GRAY_DARK
            )
        
        # Update next button state
        if self.front_captured and self.side_captured:
            self.next_button.configure(
                text="Continue →",
                state="normal",
                fg_color=ThemeManager.SUCCESS_COLOR
            )
        else:
            self.next_button.configure(
                text="Next →",
                state="disabled",
                fg_color=ThemeManager.GRAY_LIGHT
            )
        
        # Update camera instructions
        # if self.current_step == 1:
        #     self.camera_view.show_instruction("Stand facing the camera", "top")
        # else:
        #     self.camera_view.show_instruction("Turn to your right side", "top")
    
    def _update_button_states(self):
        """Update capture button states for both cards"""
        self.front_card.update_button_text(self.is_camera_active, self.front_captured)
        self.side_card.update_button_text(self.is_camera_active, self.side_captured)
    
    def _handle_capture(self, pose_type):
        """Handle capture button click"""
        if pose_type == "front" and self.front_captured:
            self._recapture_front()
        elif pose_type == "side" and self.side_captured:
            self._recapture_side()
        elif self.is_camera_active:
            self._stop_capture()
            self._update_button_states()
        else:
            self._start_capture(pose_type)
    
    def _handle_upload(self, pose_type):
        """Handle upload button click - ensures same output format as capture"""
        # Stop camera if active to prevent MediaPipe conflicts
        camera_was_active = self.is_camera_active
        if self.is_camera_active:
            self._stop_capture()
            
        file_path = filedialog.askopenfilename(
            title=f"Select {pose_type} pose image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Show loading state
                target_card = self.front_card if pose_type == "front" else self.side_card
                original_button_text = target_card.upload_button.cget("text")
                target_card.upload_button.configure(text="🔄 Processing...", state="disabled")
                self.update()  # Force UI update
                
                # Load image using OpenCV
                frame = cv2.imread(file_path)
                
                if frame is None:
                    messagebox.showerror("Error", "Could not load the selected image. Please try another file.")
                    return
                
                # Create a fresh detector instance to avoid MediaPipe state conflicts
                temp_detector = AdvancedPoseDetector()
                
                # Process image through pose detector
                processed_frame = temp_detector.detect_pose(frame, draw_landmarks=True)
                
                # Clean up temporary detector
                del temp_detector
                
                # Ensure output directory exists
                os.makedirs(INPUT_FILES_DIR, exist_ok=True)
                
                # Save using OpenCV (same format as capture)
                output_path = os.path.join(INPUT_FILES_DIR, f"input_{pose_type}.png")
                success = cv2.imwrite(output_path, processed_frame)
                
                if not success:
                    messagebox.showerror("Error", "Failed to save the processed image.")
                    return
                
                # Update UI state (same as capture)
                if pose_type == "front":
                    self.front_captured = True
                    self.front_image_path = output_path
                    self.front_card.set_captured(image_path=output_path)
                else:
                    self.side_captured = True  
                    self.side_image_path = output_path
                    self.side_card.set_captured(image_path=output_path)
                
                # Update UI and show success message (same as capture)
                self._update_ui_state()
                messagebox.showinfo("Success", f"{pose_type.title()} image uploaded and processed successfully!\n\nPose landmarks have been detected and applied.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to process uploaded image: {str(e)}")
                print(f"Upload error for {pose_type}: {e}")  # Debug logging
            finally:
                # Reset button state
                try:
                    target_card.upload_button.configure(text=original_button_text, state="normal")
                except:
                    pass
                
                # Update button states after upload
                self._update_button_states()
    
    def _start_capture(self, pose_type):
        """Start camera capture for specific pose"""
        if not self.is_camera_active:
            self.is_camera_active = True
            self.capture_thread = Thread(target=self._capture_loop, args=(pose_type,))
            self.capture_thread.daemon = True
            self.capture_thread.start()
            self.camera_view.set_active(True)
            self._update_button_states()
    
    def _stop_capture(self):
        """Stop camera capture"""
        self.is_camera_active = False
        if self.capture_thread:
            self.capture_thread.join(timeout=1)
        self.camera_view.set_active(False)
        self.camera_view.show_placeholder()
        self._update_button_states()
    
    def _capture_loop(self, pose_type):
        """Main camera capture loop"""
        cap = cv2.VideoCapture(self.selected_camera)
        
        if not cap.isOpened():
            messagebox.showerror("Error", "Could not open camera")
            self.is_camera_active = False
            return
        
        countdown_start = None
        
        try:
            while self.is_camera_active:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Process with pose detector
                processed_frame = self.detector.detect_pose(frame)
                landmarks = self.detector.get_landmarks()
                
                # Check pose quality
                pose_detected = False
                if pose_type == "front":
                    pose_detected = self.detector.is_front_pose(landmarks)
                else:
                    pose_detected = self.detector.is_side_pose(landmarks)
                
                # Handle countdown
                if pose_detected and self.detector.is_full_body_visible(landmarks):
                    if countdown_start is None:
                        countdown_start = time.time()
                    
                    elapsed = time.time() - countdown_start
                    remaining = max(0, 5 - int(elapsed))
                    
                    if remaining > 0:
                        self.camera_view.show_countdown(remaining)
                    else:
                        # Capture image
                        self._capture_image(frame, pose_type)
                        break
                else:
                    countdown_start = None
                    self.camera_view.hide_countdown()
                
                # Convert and display frame
                frame_rgb = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                pil_image.thumbnail((640, 480), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(pil_image)
                
                # Update UI in main thread
                self.after_idle(self.camera_view.update_feed, photo)
                
                time.sleep(0.03)  # ~30 FPS
                
        finally:
            cap.release()
            self.is_camera_active = False
            self.after_idle(self.camera_view.set_active, False)
    
    def _capture_image(self, frame, pose_type):
        """Capture and save image"""
        try:
            os.makedirs(INPUT_FILES_DIR, exist_ok=True)
            output_path = os.path.join(INPUT_FILES_DIR, f"input_{pose_type}.png")
            cv2.imwrite(output_path, frame)
            
            # Update UI
            if pose_type == "front":
                self.front_captured = True
                self.front_image_path = output_path
                self.after_idle(lambda: self.front_card.set_captured(image_path=output_path))
            else:
                self.side_captured = True
                self.side_image_path = output_path
                self.after_idle(lambda: self.side_card.set_captured(image_path=output_path))
            
            self.after_idle(self._update_ui_state)
            self.after_idle(self._update_button_states)
            self.after_idle(lambda: messagebox.showinfo("Success", f"{pose_type.title()} pose captured!"))
            
        except Exception as e:
            self.after_idle(lambda: messagebox.showerror("Error", f"Failed to save image: {str(e)}"))
    
    def _recapture_front(self):
        """Recapture front pose"""
        self.front_card.reset()
        self.front_captured = False
        self.front_image_path = None
        self._update_ui_state()
        self._update_button_states()
        self._start_capture("front")
    
    def _recapture_side(self):
        """Recapture side pose"""
        self.side_card.reset()
        self.side_captured = False
        self.side_image_path = None
        self._update_ui_state()
        self._update_button_states()
        self._start_capture("side")
    
    def _restart_camera(self):
        """Restart camera with new selection"""
        if self.is_camera_active:
            self._stop_capture()
            time.sleep(0.5)
            # Camera will be restarted when user clicks capture again
    
    def _go_back(self):
        """Go back to previous page"""
        self._stop_capture()
        self.controller.show_frame("InputPage")
    
    def _go_to_previous(self):
        """Go to previous step or page"""
        if self.current_step == 2:
            self._switch_to_step(1)
        else:
            self._go_back()
    
    def _go_to_next(self):
        """Go to next step or page"""
        if self.current_step == 1 and not self.front_captured:
            messagebox.showwarning("Incomplete", "Please capture your front pose first.")
            return
        
        if self.current_step == 1:
            self._switch_to_step(2)
        elif self.current_step == 2 and self.side_captured:
            self._stop_capture()
            self.controller.show_frame("ProcessingPage")
        else:
            messagebox.showwarning("Incomplete", "Please capture your side pose first.")
    
    def on_show(self):
        """Called when page is shown"""
        # Reset state if needed
        pass
    
    def on_hide(self):
        """Called when page is hidden"""
        self._stop_capture()


# Test the improved capture page
if __name__ == "__main__":
    class DummyController:
        def show_frame(self, frame_name):
            print(f"Navigating to: {frame_name}")
    
    # Setup theme
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    # Create test app
    root = ctk.CTk()
    root.title("Improved Capture Page Test")
    root.geometry("1200x800")
    
    # Initialize theme manager
    ThemeManager.setup_theme()
    
    controller = DummyController()
    
    app = CapturePage(root, controller)
    app.pack(fill="both", expand=True)
    
    root.mainloop()
