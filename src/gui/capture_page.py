"""
Capture Page for the Diet Recommendation System.
Uses computer vision to detect and capture user's front and side poses.
"""
import customtkinter as ctk
import cv2
import mediapipe as mp
import os
import time
import sys
from threading import Thread
from PIL import Image, ImageTk

# Import the PoseDetector from the capture.py file
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from image_capture.capture import PoseDetector
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
        
        # Initialize pose detector
        self.detector = PoseDetector()
        self.front_captured = False
        self.side_captured = False
        self.capture_thread = None
        self.is_running = False
        self.current_pose = "front"  # Either "front" or "side"
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=0)  # Progress
        self.grid_rowconfigure(2, weight=1)  # Content
        
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
        
        # Main content frame
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        self.content_frame.grid_columnconfigure(0, weight=2)  # Camera feed
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
        
        # Camera feed title
        self.cam_title = ctk.CTkLabel(
            self.camera_header,
            text="Front Pose",
            font=ThemeManager.get_subtitle_font()
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
            text="Not Recording",
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
        
        # Capture button container
        self.button_container = ctk.CTkFrame(self.camera_frame, fg_color="transparent")
        self.button_container.grid(row=2, column=0, padx=10, pady=10)
        self.button_container.grid_columnconfigure(0, weight=1)
        
        # Capture button
        self.capture_button = ThemeManager.create_primary_button(
            self.button_container,
            "Start Camera",
            self.toggle_capture
        )
        self.capture_button.grid(row=0, column=0, pady=5)
        
        # Countdown label
        self.countdown_label = ctk.CTkLabel(
            self.camera_view,
            text="",
            font=ctk.CTkFont(size=60, weight="bold"),
            text_color="white",
            fg_color=ThemeManager.PRIMARY_COLOR,
            corner_radius=40,
            width=80,
            height=80
        )
        
        # Instructions panel
        self.instructions_frame = ThemeManager.create_card_frame(self.content_frame)
        self.instructions_frame.grid(row=0, column=1, sticky="nsew")
        self.instructions_frame.grid_columnconfigure(0, weight=1)
        self.instructions_frame.grid_rowconfigure(0, weight=0)
        self.instructions_frame.grid_rowconfigure(1, weight=1)
        self.instructions_frame.grid_rowconfigure(2, weight=0)
        
        # Instructions header
        self.instructions_title = ctk.CTkLabel(
            self.instructions_frame,
            text="Posing Instructions",
            font=ThemeManager.get_subtitle_font(),
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
        
        # Instructions for front pose
        self.front_instructions = ctk.CTkFrame(
            self.instructions_scroll,
            fg_color="#3b82f6",  # Light blue background with transparency
            corner_radius=10
        )
        self.front_instructions.grid(row=0, column=0, pady=5, sticky="ew")
        
        self.front_instructions_title = ctk.CTkLabel(
            self.front_instructions,
            text="Front Pose Guidelines",
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        self.front_instructions_title.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        front_tips = [
            "Stand facing the camera directly",
            "Keep your arms slightly away from body",
            "Make sure both shoulders are at the same height",
            "Position your feet shoulder-width apart",
            "Stand straight and look directly at the camera",
            "Ensure your entire body is visible in the frame"
        ]
        
        for i, tip in enumerate(front_tips):
            tip_frame = ctk.CTkFrame(self.front_instructions, fg_color="transparent")
            tip_frame.grid(row=i+1, column=0, padx=10, pady=2, sticky="w")
            
            check_label = ctk.CTkLabel(
                tip_frame,
                text="✓",
                font=ThemeManager.get_small_font(),
                text_color=ThemeManager.PRIMARY_COLOR
            )
            check_label.grid(row=0, column=0, padx=(0, 5))
            
            tip_label = ctk.CTkLabel(
                tip_frame,
                text=tip,
                font=ThemeManager.get_small_font(),
                text_color=ThemeManager.GRAY_DARK,
                justify="left",
                anchor="w"
            )
            tip_label.grid(row=0, column=1, sticky="w")
            
        # Instructions for side pose
        self.side_instructions = ctk.CTkFrame(
            self.instructions_scroll,
            fg_color=ThemeManager.GRAY_LIGHT,
            corner_radius=10
        )
        self.side_instructions.grid(row=1, column=0, pady=5, sticky="ew")
        
        self.side_instructions_title = ctk.CTkLabel(
            self.side_instructions,
            text="Side Pose Guidelines",
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.GRAY_DARK
        )
        self.side_instructions_title.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        side_tips = [
            "Turn to your right side facing the wall",
            "Keep your arms naturally at your sides",
            "Stand with feet hip-width apart",
            "Maintain a straight posture, don't lean",
            "Look straight ahead, not at the camera",
            "Ensure your entire body is visible in the frame"
        ]
        
        for i, tip in enumerate(side_tips):
            tip_frame = ctk.CTkFrame(self.side_instructions, fg_color="transparent")
            tip_frame.grid(row=i+1, column=0, padx=10, pady=2, sticky="w")
            
            check_label = ctk.CTkLabel(
                tip_frame,
                text=str(i+1) + ".",
                font=ThemeManager.get_small_font(),
                text_color=ThemeManager.GRAY_DARK
            )
            check_label.grid(row=0, column=0, padx=(0, 5))
            
            tip_label = ctk.CTkLabel(
                tip_frame,
                text=tip,
                font=ThemeManager.get_small_font(),
                text_color=ThemeManager.GRAY_DARK,
                justify="left",
                anchor="w"
            )
            tip_label.grid(row=0, column=1, sticky="w")
            
        # Status panel
        self.status_panel = ctk.CTkFrame(
            self.instructions_frame,
            corner_radius=10,
            border_width=1,
            border_color=ThemeManager.GRAY_LIGHT
        )
        self.status_panel.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        self.status_title = ctk.CTkLabel(
            self.status_panel,
            text="Current Status:",
            font=ThemeManager.get_label_font()
        )
        self.status_title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        
        self.status_message = ctk.CTkLabel(
            self.status_panel,
            text="Click 'Start Camera' to begin capture process",
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.GRAY_DARK,
            justify="left",
            anchor="w",
            wraplength=250
        )
        self.status_message.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        # Bottom navigation
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.grid(row=3, column=0, padx=20, pady=20, sticky="ew")
        self.nav_frame.grid_columnconfigure(0, weight=1)
        self.nav_frame.grid_columnconfigure(1, weight=1)
        
        # Previous button
        self.prev_button = ThemeManager.create_secondary_button(
            self.nav_frame,
            "Previous Step",
            lambda: self.stop_capture_and_go_back()
        )
        self.prev_button.grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        # Next button (initially disabled)
        self.next_button = ThemeManager.create_primary_button(
            self.nav_frame,
            "Continue to Analysis",
            self.go_to_next_page
        )
        self.next_button.grid(row=0, column=1, padx=(10, 0), sticky="e")
        self.next_button.configure(state="disabled")
        
        # Store captured images references
        self.front_image = None
        self.side_image = None
        
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
            # Update title
            self.cam_title.configure(text="Front Pose")
            
            # Update instructions
            self.front_instructions.configure(fg_color=ThemeManager.PRIMARY_COLOR)  # Light blue
            self.side_instructions.configure(fg_color=ThemeManager.GRAY_LIGHT)
            
            self.front_instructions_title.configure(text_color=ThemeManager.PRIMARY_COLOR)
            self.side_instructions_title.configure(text_color=ThemeManager.GRAY_DARK)
        else:
            # Update title
            self.cam_title.configure(text="Side Pose")
            
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
        
    def convert_cv_to_tk(self, img):
        """Convert OpenCV image to Tkinter compatible image"""
        rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        return ctk.CTkImage(pil_image, size=(640, 480))
        
    def go_to_next_page(self):
        """Navigate to processing page after successful capture"""
        # Make sure the camera is stopped
        self.stop_capture()
        
        # Store image data in state manager 
        self.controller.state_manager.update_image_data(
            front_image_path=os.path.join(INPUT_FILES_DIR, "input_front.png"),
            side_image_path=os.path.join(INPUT_FILES_DIR, "input_side.png")
        )
        
        # Navigate to processing page
        self.controller.show_frame("ProcessingPage")
        
    def on_show(self):
        """Called when page is shown"""
        # Reset capture state
        self.front_captured = False
        self.side_captured = False
        self.is_running = False
        self.current_pose = "front"
        
        # Update UI
        self.update_pose_mode()
        self.next_button.configure(state="normal")
        self.capture_button.configure(text="Start Camera", fg_color=ThemeManager.PRIMARY_COLOR)
        self.status_label.configure(text="Not Recording")
        self.status_frame.configure(fg_color=ThemeManager.DANGER_COLOR)
        self.status_message.configure(text="Click 'Start Camera' to begin capture process")
        
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
