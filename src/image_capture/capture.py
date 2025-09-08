import cv2
import mediapipe as mp
import customtkinter as ctk
from threading import Thread
from PIL import Image, ImageTk
import os
import time
import sys

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(PROJECT_DIR)

from src.utils.utils import INPUT_FILES_DIR


class AdvancedPoseDetector:
    """
    Advanced Pose Detector using MediaPipe Tasks API for improved accuracy.
    Following the latest MediaPipe documentation for pose landmarker.
    """
    
    def __init__(self):
        # Initialize MediaPipe pose landmarker with improved configuration
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Enhanced pose configuration for better accuracy
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,  # Use more complex model for better accuracy
            enable_segmentation=True,  # Enable segmentation for better body detection
            min_detection_confidence=0.7,  # Increased confidence threshold
            min_tracking_confidence=0.7    # Increased tracking confidence
        )
        
        # Store the latest pose results
        self.results = None
        
        # Create output directory if it doesn't exist
        self.output_dir = "captured_poses"
        os.makedirs(self.output_dir, exist_ok=True)

    def detect_pose(self, image, draw_landmarks=True):
        """
        Detect pose landmarks in the given image.
        Returns the processed image with landmarks drawn (if enabled).
        """
        # Convert BGR to RGB for MediaPipe processing
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process the image and detect pose landmarks
        self.results = self.pose.process(rgb_image)
        
        # Draw landmarks if requested and pose is detected
        if draw_landmarks and self.results.pose_landmarks:
            # Draw pose landmarks with enhanced styling
            self.mp_drawing.draw_landmarks(
                image,
                self.results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
            )
            
            # Draw additional visual feedback for pose quality
            self._draw_pose_quality_indicators(image)
        
        return image

    def get_landmarks(self):
        """
        Get the normalized landmarks as a list of [id, x, y, z, visibility, presence].
        Returns empty list if no pose is detected.
        """
        landmarks = []
        if self.results and self.results.pose_landmarks:
            for idx, landmark in enumerate(self.results.pose_landmarks.landmark):
                landmarks.append([
                    idx,
                    landmark.x,
                    landmark.y,
                    landmark.z,
                    landmark.visibility,
                    getattr(landmark, 'presence', 0.0)  # Some versions might not have presence
                ])
        return landmarks

    def _draw_pose_quality_indicators(self, image):
        """Draw visual indicators for pose quality assessment."""
        h, w = image.shape[:2]
        
        # Draw frame boundaries for pose assessment
        cv2.rectangle(image, (int(w*0.1), int(h*0.05)), (int(w*0.9), int(h*0.95)), (0, 255, 0), 2)
        
        # Add text overlay for pose status
        pose_status = self._assess_pose_quality()
        cv2.putText(image, pose_status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    def _assess_pose_quality(self):
        """Assess the quality of the current pose detection."""
        if not self.results or not self.results.pose_landmarks:
            return "No pose detected"
        
        landmarks = self.get_landmarks()
        if len(landmarks) < 33:
            return "Incomplete pose"
        
        # Check visibility scores
        avg_visibility = sum(lm[4] for lm in landmarks) / len(landmarks)
        
        if avg_visibility > 0.8:
            return "Excellent pose quality"
        elif avg_visibility > 0.6:
            return "Good pose quality"
        elif avg_visibility > 0.4:
            return "Fair pose quality"
        else:
            return "Poor pose quality"

    def is_full_body_visible(self, landmarks=None):
        """
        Check if the full body is visible in the frame with improved accuracy.
        Uses visibility scores and landmark positions for better assessment.
        """
        if landmarks is None:
            landmarks = self.get_landmarks()
        
        if len(landmarks) < 33:
            return False
        
        # Key landmarks for full body assessment
        nose = landmarks[0]
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        left_hip = landmarks[23]
        right_hip = landmarks[24]
        left_ankle = landmarks[27]
        right_ankle = landmarks[28]
        left_foot_index = landmarks[31]
        right_foot_index = landmarks[32]
        
        # Check if key landmarks are visible with good confidence
        key_landmarks = [nose, left_shoulder, right_shoulder, left_hip, right_hip, 
                        left_ankle, right_ankle, left_foot_index, right_foot_index]
        
        # All key landmarks should have good visibility
        min_visibility = 0.6
        visible_landmarks = [lm for lm in key_landmarks if lm[4] > min_visibility]
        
        if len(visible_landmarks) < 8:  # At least 8 out of 9 key landmarks should be visible
            return False
        
        # Check if head and feet are in appropriate positions
        head_y = nose[2]
        feet_y = max(left_foot_index[2], right_foot_index[2])
        
        # Head should be in upper portion, feet in lower portion
        head_in_upper = head_y < 0.3
        feet_in_lower = feet_y > 0.7
        
        return head_in_upper and feet_in_lower

    def is_front_pose(self, landmarks=None):
        """
        Detect if the person is in a front-facing pose with improved accuracy.
        Uses shoulder symmetry, hip alignment, and body orientation.
        """
        if landmarks is None:
            landmarks = self.get_landmarks()
        
        if not self.is_full_body_visible(landmarks):
            return False
        
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        left_hip = landmarks[23]
        right_hip = landmarks[24]
        left_wrist = landmarks[15]
        right_wrist = landmarks[16]
        
        # Check shoulder symmetry (y-coordinates should be similar)
        shoulder_y_diff = abs(left_shoulder[2] - right_shoulder[2])
        shoulder_symmetry = shoulder_y_diff < 0.05  # 5% of image height
        
        # Check hip symmetry
        hip_y_diff = abs(left_hip[2] - right_hip[2])
        hip_symmetry = hip_y_diff < 0.05
        
        # Check if arms are spread (for T-pose or A-pose)
        shoulder_width = abs(left_shoulder[1] - right_shoulder[1])
        arm_spread = abs(left_wrist[1] - right_wrist[1]) > shoulder_width * 1.2
        
        # Check z-depth symmetry (both shoulders should be at similar depth)
        shoulder_z_diff = abs(left_shoulder[3] - right_shoulder[3])
        depth_symmetry = shoulder_z_diff < 0.1
        
        # All visibility checks
        min_visibility = 0.7
        visibility_check = all(lm[4] > min_visibility for lm in 
                             [left_shoulder, right_shoulder, left_hip, right_hip])
        
        return (shoulder_symmetry and hip_symmetry and arm_spread and 
                depth_symmetry and visibility_check)

    def is_side_pose(self, landmarks=None):
        """
        Detect if the person is in a side pose with improved accuracy.
        Uses depth differences and body alignment patterns.
        """
        if landmarks is None:
            landmarks = self.get_landmarks()
        
        if not self.is_full_body_visible(landmarks):
            return False
        
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        left_hip = landmarks[23]
        right_hip = landmarks[24]
        nose = landmarks[0]
        left_wrist = landmarks[15]
        right_wrist = landmarks[16]
        
        # Check for significant depth difference between shoulders (side view indicator)
        shoulder_z_diff = abs(left_shoulder[3] - right_shoulder[3])
        significant_depth_diff = shoulder_z_diff > 0.15
        
        # Check vertical alignment of body parts (shoulders, hips should align vertically)
        shoulder_x_diff = abs(left_shoulder[1] - right_shoulder[1])
        hip_x_diff = abs(left_hip[1] - right_hip[1])
        vertical_alignment = shoulder_x_diff < 0.1 and hip_x_diff < 0.1
        
        # Check if arms are down (not spread)
        arms_down_left = abs(left_wrist[2] - left_shoulder[2]) > 0.15
        arms_down_right = abs(right_wrist[2] - right_shoulder[2]) > 0.15
        arms_down = arms_down_left and arms_down_right
        
        # Check visibility of key landmarks
        min_visibility = 0.6
        visibility_check = all(lm[4] > min_visibility for lm in 
                             [left_shoulder, right_shoulder, left_hip, right_hip, nose])
        
        return (significant_depth_diff and vertical_alignment and 
                arms_down and visibility_check)

    # Legacy method compatibility
    def findPose(self, img, draw=True):
        """Legacy compatibility method"""
        return self.detect_pose(img, draw)
    
    def findPosition(self, img, draw=False):
        """Legacy compatibility method"""
        landmarks = self.get_landmarks()
        # Convert to old format for compatibility
        old_format = []
        h, w = img.shape[:2]
        for lm in landmarks:
            old_format.append([lm[0], int(lm[1] * w), int(lm[2] * h), lm[3]])
        return old_format
    
    def isFullBodyVisible(self, lmList, img_shape):
        """Legacy compatibility method"""
        return self.is_full_body_visible()
    
    def isFrontPose(self, lmList, img_shape):
        """Legacy compatibility method"""
        return self.is_front_pose()
    
    def isSidePose(self, lmList, img_shape):
        """Legacy compatibility method"""
        return self.is_side_pose()


# Keep old class for backward compatibility
class PoseDetector():
    
    def __init__(self):
        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose()

    def findPose(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)
        
        if self.results.pose_landmarks and draw:
            self.mpDraw.draw_landmarks(img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)

        return img

    def findPosition(self, img, draw=False):
        lmList = []
        if self.results.pose_landmarks:
            h, w = img.shape[:2]  # Removed unused variable 'c'
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                cz = lm.z * w  # Approximate depth scaling
                lmList.append([id, cx, cy, cz])
                if draw:
                    cv2.circle(img, (cx, cy), 7, (255, 0, 0), cv2.FILLED)
        return lmList

    def isFullBodyVisible(self, lmList, img_shape):
        h = img_shape[0]  # Removed unused variable 'w' and '_'
        if len(lmList) < 33:
            return False

        nose = lmList[0]
        left_foot, right_foot = lmList[31], lmList[32]
        left_shoulder, right_shoulder = lmList[11], lmList[12]

        # Nose must be in upper 20% of screen height
        head_in_frame = 0 < nose[2] < h * 0.15
        # Both feet must be in lower 15% of screen height
        feet_in_frame = left_foot[2] > h * 0.85 and right_foot[2] > h * 0.85
        # Shoulders should not be clipped
        shoulders_in_frame = left_shoulder[2] < h * 0.5 and right_shoulder[2] < h * 0.5

        return head_in_frame and feet_in_frame and shoulders_in_frame

    def isFrontPose(self, lmList, img_shape):
        # Ensures the subject is in a front pose with full-body visible
        if not self.isFullBodyVisible(lmList, img_shape):
            return False

        left_shoulder, right_shoulder = lmList[11], lmList[12]
        left_wrist, right_wrist = lmList[15], lmList[16]

        shoulders_aligned = abs(left_shoulder[2] - right_shoulder[2]) < 30
        arms_out = abs(left_wrist[1] - right_wrist[1]) > 100

        return shoulders_aligned and arms_out

    def isSidePose(self, lmList, img_shape):
        if not self.isFullBodyVisible(lmList, img_shape):
            return False

        if len(lmList) < 33:
            return False

        left_shoulder, right_shoulder = lmList[11], lmList[12]
        left_hip, right_hip = lmList[23], lmList[24]
        left_ankle, right_ankle = lmList[27], lmList[28]
        nose = lmList[0]
        left_wrist, right_wrist = lmList[15], lmList[16]

        # Shoulders, hips, and ankles should be horizontally aligned
        shoulders_aligned = abs(left_shoulder[1] - right_shoulder[1]) < 30
        hips_aligned = abs(left_hip[1] - right_hip[1]) < 30
        ankles_aligned = abs(left_ankle[1] - right_ankle[1]) < 30

        # Strong z-difference means one shoulder is much closer (side view)
        shoulders_depth_diff = abs(left_shoulder[3] - right_shoulder[3]) > 80
        # Head (nose) must also be offset from both shoulders in depth
        nose_depth_diff = abs(nose[3] - left_shoulder[3]) > 50 and abs(nose[3] - right_shoulder[3]) > 50

        # Arms should be roughly vertical (straight down) – y-diff between shoulder and wrist large
        arms_down = (
            abs(left_wrist[2] - left_shoulder[2]) > 100 and
            abs(right_wrist[2] - right_shoulder[2]) > 100
        )

        return all([
            shoulders_aligned,
            hips_aligned,
            ankles_aligned,
            shoulders_depth_diff,
            nose_depth_diff,
            arms_down
        ])


# The following code is only used when this file is run directly (not imported)
if __name__ == "__main__":
    # Create a standalone version of the capture functionality
    def setup_dashboard():
        app = ctk.CTk()
        app.title("Pose Capture Dashboard")
        app.geometry("800x600")
        app.resizable(False, False)
        app.configure(bg="#f0f0f0")

        detector = PoseDetector()

        # Grid layout for entire window
        app.grid_columnconfigure((0, 1), weight=1, uniform="col")
        app.grid_rowconfigure(1, weight=1)
        app.grid_rowconfigure(2, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            app, text="Pose Capture Dashboard",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#333"
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(10, 5))

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
        front_frame, front_img_label = create_pose_frame(app, "Front Pose")
        front_frame.grid(row=1, column=0, padx=10, pady=5, sticky="n")

        side_frame, side_img_label = create_pose_frame(app, "Side Pose")
        side_frame.grid(row=1, column=1, padx=10, pady=5, sticky="n")

        # Live Feed
        live_feed_frame = ctk.CTkFrame(app, width=300, height=300, corner_radius=10)
        live_feed_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="n")
        live_feed_frame.grid_propagate(False)

        live_feed_label = ctk.CTkLabel(live_feed_frame, fg_color="#e0e0e0", width=300, height=300, text="")
        live_feed_label.pack(padx=10, pady=5)

        # Countdown Label
        countdown_label = ctk.CTkLabel(app, text="", font=ctk.CTkFont(size=16, weight="bold"), text_color="red")
        countdown_label.grid(row=2, column=0, columnspan=2, pady=(5, 0))
        
        def capture_images(detector, front_img_label, side_img_label, live_feed_label, countdown_label):
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

            while cap.isOpened():
                success, img = cap.read()
                if not success:
                    print("Failed to read from camera. Exiting...")
                    break

                # Resize the frame to match the live feed container dimensions
                img = cv2.resize(img, (live_feed_width, live_feed_height))

                img = detector.findPose(img)
                lmList = detector.findPosition(img)

                # Check for full body visibility and pose detection
                if len(lmList) != 0 and detector.isFullBodyVisible(lmList, img.shape):
                    if not front_captured and detector.isFrontPose(lmList, img.shape):
                        if countdown_pose != "front":
                            countdown_start = time.time()
                            countdown_pose = "front"
                            print("Front pose detected. Starting countdown...")
                    elif front_captured and not side_captured and detector.isSidePose(lmList, img.shape):
                        if countdown_pose != "side":
                            countdown_start = time.time()
                            countdown_pose = "side"
                            print("Side pose detected. Starting countdown...")
                    else:
                        countdown_start = None
                        countdown_pose = None
                        countdown_label.configure(text="")  # Clear countdown label
                else:
                    countdown_start = None
                    countdown_pose = None
                    countdown_label.configure(text="")  # Clear countdown label

                # Handle countdown logic
                if countdown_start and countdown_pose:
                    elapsed_time = time.time() - countdown_start
                    remaining_time = max(0, 5 - int(elapsed_time))
                    countdown_label.configure(text=f"Capturing in {remaining_time}s")

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
                                front_img_label.configure(image=img_tk)
                                front_img_label.image = img_tk
                            elif countdown_pose == "side":
                                cv2.imwrite(side_image_path, img)
                                print(f"Side pose captured and saved to {side_image_path}!")
                                side_captured = True

                                # Display the captured side image
                                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                                img_pil = Image.fromarray(img_rgb)
                                img_tk = ImageTk.PhotoImage(img_pil)
                                side_img_label.configure(image=img_tk)
                                side_img_label.image = img_tk

                            countdown_start = None
                            countdown_pose = None
                            countdown_label.configure(text="")  # Clear countdown label

                # Update live feed
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img_pil = Image.fromarray(img_rgb)
                img_tk = ImageTk.PhotoImage(img_pil)
                live_feed_label.configure(image=img_tk)
                live_feed_label.image = img_tk

                if front_captured and side_captured:
                    print("Both poses captured. Exiting...")
                    break

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()

        def start_capture(detector, front_img_label, side_img_label, live_feed_label, countdown_label):
            capture_thread = Thread(target=capture_images, args=(detector, front_img_label, side_img_label, live_feed_label, countdown_label))
            capture_thread.daemon = True
            capture_thread.start()

        # Start Button
        start_button = ctk.CTkButton(
            app, text="Start Capture", font=ctk.CTkFont(size=14),
            command=lambda: start_capture(detector, front_img_label, side_img_label, live_feed_label, countdown_label)
        )
        start_button.grid(row=3, column=0, columnspan=2, pady=10)

        app.protocol("WM_DELETE_WINDOW", lambda: (app.destroy(), cv2.destroyAllWindows()))
        app.mainloop()

    setup_dashboard()
