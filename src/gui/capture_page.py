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

class CapturePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.detector = PoseDetector()
        self.front_captured = False
        self.side_captured = False
        self.capture_thread = None
        self.is_running = False

        # Configure the frame
        self.grid_rowconfigure(list(range(5)), weight=1)
        self.grid_columnconfigure((0, 1), weight=1, uniform="col")

        # Title
        self.title_label = ctk.CTkLabel(
            self, text="Pose Capture",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(10, 5))

        # Pose Display Frame Creator
        def create_pose_frame(parent, text):
            frame = ctk.CTkFrame(parent, width=280, height=280, corner_radius=10)
            frame.grid_propagate(False)  # Prevent resizing to content

            label = ctk.CTkLabel(frame, text=text, font=ctk.CTkFont(size=14, weight="bold"))
            label.pack(pady=(10, 5))

            image_holder = ctk.CTkLabel(frame, fg_color="#e0e0e0", width=240, height=240, text="")
            image_holder.pack(padx=10, pady=5)
            return frame, image_holder

        # Front & Side Frames
        self.front_frame, self.front_img_label = create_pose_frame(self, "Front Pose")
        self.front_frame.grid(row=1, column=0, padx=10, pady=5, sticky="n")

        self.side_frame, self.side_img_label = create_pose_frame(self, "Side Pose")
        self.side_frame.grid(row=1, column=1, padx=10, pady=5, sticky="n")

        # Live Feed
        self.live_feed_frame = ctk.CTkFrame(self, width=300, height=300, corner_radius=10)
        self.live_feed_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="n")
        self.live_feed_frame.grid_propagate(False)

        self.live_feed_label = ctk.CTkLabel(self.live_feed_frame, fg_color="#e0e0e0", width=300, height=300, text="")
        self.live_feed_label.pack(padx=10, pady=5)

        # Countdown Label
        self.countdown_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=16, weight="bold"), text_color="red")
        self.countdown_label.grid(row=3, column=0, columnspan=2, pady=(5, 0))

        # Buttons frame
        self.buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.buttons_frame.grid(row=4, column=0, columnspan=2, pady=10)

        # Start Button
        self.start_button = ctk.CTkButton(
            self.buttons_frame, text="Start Capture", font=ctk.CTkFont(size=14),
            command=self.start_capture
        )
        self.start_button.grid(row=0, column=0, padx=10)

        # Back Button
        self.back_button = ctk.CTkButton(
            self.buttons_frame, text="Back", font=ctk.CTkFont(size=14),
            command=lambda: self.controller.show_frame("InputPage")
        )
        self.back_button.grid(row=0, column=1, padx=10)

        # Next Button (initially disabled)
        self.next_button = ctk.CTkButton(
            self.buttons_frame, text="Next", font=ctk.CTkFont(size=14),
            command=self.go_to_next_page, state="disabled"
        )
        self.next_button.grid(row=0, column=2, padx=10)

    def start_capture(self):
        if not self.is_running:
            self.is_running = True
            self.capture_thread = Thread(target=self.capture_images)
            self.capture_thread.daemon = True
            self.capture_thread.start()
            self.start_button.configure(text="Stop Capture", command=self.stop_capture)

    def stop_capture(self):
        self.is_running = False
        self.start_button.configure(text="Start Capture", command=self.start_capture)

    def capture_images(self):
        cap = cv2.VideoCapture(0)
        front_captured = False
        side_captured = False

        # Set the dimensions of the live feed and video frame
        live_feed_width = 300
        live_feed_height = 300

        countdown_start = None  # Track countdown start time
        countdown_pose = None  # Track which pose is being counted down

        # Define file paths for saving images
        front_image_path = os.path.join(INPUT_FILES_DIR, "input_front.png")
        side_image_path = os.path.join(INPUT_FILES_DIR, "input_side.png")
        
        print("DEBUG MODE: Press 'c' key to manually capture images")
        print("First press will capture front pose, second press will capture side pose")

        while cap.isOpened() and self.is_running:
            success, img = cap.read()
            if not success:
                print("Failed to read from camera. Exiting...")
                break

            # Resize the frame to match the live feed container dimensions
            img = cv2.resize(img, (live_feed_width, live_feed_height))

            img = self.detector.findPose(img)
            lmList = self.detector.findPosition(img)

            # DEBUG: Manual capture with keyboard
            key = cv2.waitKey(1) & 0xFF
            if key == ord('c'):
                if not front_captured:
                    # Save front pose
                    os.makedirs(INPUT_FILES_DIR, exist_ok=True)
                    cv2.imwrite(front_image_path, img)
                    print(f"DEBUG: Front pose manually captured and saved to {front_image_path}!")
                    front_captured = True
                    
                    # Display the captured front image
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img_pil = Image.fromarray(img_rgb)
                    img_tk = ImageTk.PhotoImage(img_pil)
                    self.front_img_label.configure(image=img_tk)
                    self.front_img_label.image = img_tk
                
                elif not side_captured:
                    # Save side pose
                    cv2.imwrite(side_image_path, img)
                    print(f"DEBUG: Side pose manually captured and saved to {side_image_path}!")
                    side_captured = True
                    
                    # Display the captured side image
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img_pil = Image.fromarray(img_rgb)
                    img_tk = ImageTk.PhotoImage(img_pil)
                    self.side_img_label.configure(image=img_tk)
                    self.side_img_label.image = img_tk

            # Check for full body visibility and pose detection
            if len(lmList) != 0 and self.detector.isFullBodyVisible(lmList, img.shape):
                if not front_captured and self.detector.isFrontPose(lmList, img.shape):
                    if countdown_pose != "front":
                        countdown_start = time.time()
                        countdown_pose = "front"
                        print("Front pose detected. Starting countdown...")
                elif front_captured and not side_captured and self.detector.isSidePose(lmList, img.shape):
                    if countdown_pose != "side":
                        countdown_start = time.time()
                        countdown_pose = "side"
                        print("Side pose detected. Starting countdown...")
                else:
                    countdown_start = None
                    countdown_pose = None
                    self.countdown_label.configure(text="")  # Clear countdown label
            else:
                countdown_start = None
                countdown_pose = None
                self.countdown_label.configure(text="")  # Clear countdown label

            # Handle countdown logic
            if countdown_start and countdown_pose:
                elapsed_time = time.time() - countdown_start
                remaining_time = max(0, 5 - int(elapsed_time))
                self.countdown_label.configure(text=f"Capturing in {remaining_time}s")

                if remaining_time == 0:
                    success, img = cap.read()
                    if success:
                        img = cv2.resize(img, (live_feed_width, live_feed_height))  # Resize before saving
                        os.makedirs(INPUT_FILES_DIR, exist_ok=True)  # Ensure the directory exists
                        if countdown_pose == "front":
                            cv2.imwrite(front_image_path, img)
                            print(f"Front pose captured and saved to {front_image_path}!")
                            front_captured = True

                            # Display the captured front image
                            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                            img_pil = Image.fromarray(img_rgb)
                            img_tk = ImageTk.PhotoImage(img_pil)
                            self.front_img_label.configure(image=img_tk)
                            self.front_img_label.image = img_tk
                        elif countdown_pose == "side":
                            cv2.imwrite(side_image_path, img)
                            print(f"Side pose captured and saved to {side_image_path}!")
                            side_captured = True

                            # Display the captured side image
                            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                            img_pil = Image.fromarray(img_rgb)
                            img_tk = ImageTk.PhotoImage(img_pil)
                            self.side_img_label.configure(image=img_tk)
                            self.side_img_label.image = img_tk

                    countdown_start = None
                    countdown_pose = None
                    self.countdown_label.configure(text="")  # Clear countdown label

            # Update live feed
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            img_tk = ImageTk.PhotoImage(img_pil)
            self.live_feed_label.configure(image=img_tk)
            self.live_feed_label.image = img_tk

            if front_captured and side_captured:
                self.front_captured = front_captured
                self.side_captured = side_captured
                # Enable the next button when both poses are captured
                self.next_button.configure(state="normal")
                print("Both poses captured. Ready to proceed.")
                break

        cap.release()
        self.is_running = False
        self.start_button.configure(text="Start Capture", command=self.start_capture)

    def go_to_next_page(self):
        # Navigate to the processing page after successful capture
        print("Navigating to processing page")
        self.controller.show_frame("ProcessingPage")  # Updated to navigate to ProcessingPage
