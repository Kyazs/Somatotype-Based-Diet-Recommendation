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
            min_tracking_confidence=0.7,  # Increased tracking confidence
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
        The original image is NOT modified.
        """
        # Convert BGR to RGB for MediaPipe processing
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Process the image and detect pose landmarks
        self.results = self.pose.process(rgb_image)

        # Create a copy for drawing if landmarks should be drawn
        if draw_landmarks and self.results.pose_landmarks:
            # Work on a copy to preserve the original image
            display_image = image.copy()
            
            # Draw pose landmarks with enhanced styling
            self.mp_drawing.draw_landmarks(
                display_image,
                self.results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style(),
            )

            # Draw additional visual feedback for pose quality
            self._draw_pose_quality_indicators(display_image)
            
            return display_image
        else:
            # Return original image unchanged if no drawing needed
            return image

    def get_landmarks(self):
        """
        Get the normalized landmarks as a list of [id, x, y, z, visibility, presence].
        Returns empty list if no pose is detected.
        """
        landmarks = []
        if self.results and self.results.pose_landmarks:
            for idx, landmark in enumerate(self.results.pose_landmarks.landmark):
                landmarks.append(
                    [
                        idx,
                        landmark.x,
                        landmark.y,
                        landmark.z,
                        landmark.visibility,
                        getattr(
                            landmark, "presence", 0.0
                        ),  # Some versions might not have presence
                    ]
                )
        return landmarks

    def _draw_pose_quality_indicators(self, image):
        """Draw enhanced visual indicators for pose quality assessment with modern styling."""
        h, w = image.shape[:2]

        # Get pose quality assessment
        pose_status = self._assess_pose_quality()
        landmarks = self.get_landmarks()

        # Define colors based on pose quality
        color_mapping = {
            "Excellent pose quality": (34, 197, 94),  # Green
            "Good pose quality": (59, 130, 246),  # Blue
            "Fair pose quality": (245, 158, 11),  # Orange
            "Poor pose quality": (239, 68, 68),  # Red
            "Incomplete pose": (156, 163, 175),  # Gray
            "No pose detected": (107, 114, 128),  # Dark Gray
        }

        # Get appropriate color
        indicator_color = color_mapping.get(pose_status, (107, 114, 128))

        # Draw modern frame boundaries with rounded corners effect
        frame_thickness = 3
        corner_length = 30

        # Top-left corner
        cv2.line(
            image,
            (int(w * 0.1), int(h * 0.05)),
            (int(w * 0.1) + corner_length, int(h * 0.05)),
            indicator_color,
            frame_thickness,
        )
        cv2.line(
            image,
            (int(w * 0.1), int(h * 0.05)),
            (int(w * 0.1), int(h * 0.05) + corner_length),
            indicator_color,
            frame_thickness,
        )

        # Top-right corner
        cv2.line(
            image,
            (int(w * 0.9) - corner_length, int(h * 0.05)),
            (int(w * 0.9), int(h * 0.05)),
            indicator_color,
            frame_thickness,
        )
        cv2.line(
            image,
            (int(w * 0.9), int(h * 0.05)),
            (int(w * 0.9), int(h * 0.05) + corner_length),
            indicator_color,
            frame_thickness,
        )

        # Bottom-left corner
        cv2.line(
            image,
            (int(w * 0.1), int(h * 0.95) - corner_length),
            (int(w * 0.1), int(h * 0.95)),
            indicator_color,
            frame_thickness,
        )
        cv2.line(
            image,
            (int(w * 0.1), int(h * 0.95)),
            (int(w * 0.1) + corner_length, int(h * 0.95)),
            indicator_color,
            frame_thickness,
        )

        # Bottom-right corner
        cv2.line(
            image,
            (int(w * 0.9) - corner_length, int(h * 0.95)),
            (int(w * 0.9), int(h * 0.95)),
            indicator_color,
            frame_thickness,
        )
        cv2.line(
            image,
            (int(w * 0.9), int(h * 0.95) - corner_length),
            (int(w * 0.9), int(h * 0.95)),
            indicator_color,
            frame_thickness,
        )

        # Create modern status badge
        self._draw_status_badge(image, pose_status, indicator_color)

        # Draw pose guidance if needed
        if len(landmarks) > 0:
            self._draw_pose_guidance(image, landmarks)

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

    def _draw_status_badge(self, image, status_text, color):
        """Draw a modern status badge with rounded background."""
        h, w = image.shape[:2]

        # Calculate text size for badge sizing
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        thickness = 2
        (text_w, text_h), baseline = cv2.getTextSize(
            status_text, font, font_scale, thickness
        )

        # Badge dimensions with modern styling
        badge_padding_x = 20
        badge_padding_y = 12
        badge_w = text_w + 2 * badge_padding_x
        badge_h = text_h + 2 * badge_padding_y

        # Badge position (top-left with margin)
        badge_x = 15
        badge_y = 15

        # Create semi-transparent overlay with shadow effect
        overlay = image.copy()

        # Draw shadow
        shadow_offset = 3
        cv2.rectangle(
            overlay,
            (badge_x + shadow_offset, badge_y + shadow_offset),
            (badge_x + badge_w + shadow_offset, badge_y + badge_h + shadow_offset),
            (0, 0, 0),
            -1,
        )

        # Draw main badge background
        cv2.rectangle(
            overlay,
            (badge_x, badge_y),
            (badge_x + badge_w, badge_y + badge_h),
            color,
            -1,
        )

        # Draw subtle border
        cv2.rectangle(
            overlay,
            (badge_x, badge_y),
            (badge_x + badge_w, badge_y + badge_h),
            (255, 255, 255),
            2,
        )

        # Blend with original image for transparency
        alpha = 0.9
        cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

        # Add main text with better positioning
        text_x = badge_x + badge_padding_x
        text_y = badge_y + badge_padding_y + text_h
        cv2.putText(
            image,
            status_text,
            (text_x, text_y),
            font,
            font_scale,
            (255, 255, 255),
            thickness,
        )

        # Add quality indicator icon
        icon_size = 16
        icon_x = badge_x + badge_w - icon_size - 8
        icon_y = badge_y + 8

        # Draw different icons based on status
        if "Excellent" in status_text:
            # Checkmark circle
            cv2.circle(
                image,
                (icon_x, icon_y + icon_size // 2),
                icon_size // 2,
                (255, 255, 255),
                -1,
            )
            cv2.putText(
                image,
                "✓",
                (icon_x - 6, icon_y + icon_size // 2 + 4),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
            )
        elif "Good" in status_text:
            # Circle with dot
            cv2.circle(
                image,
                (icon_x, icon_y + icon_size // 2),
                icon_size // 2,
                (255, 255, 255),
                2,
            )
            cv2.circle(image, (icon_x, icon_y + icon_size // 2), 3, (255, 255, 255), -1)
        elif "Fair" in status_text:
            # Warning triangle
            cv2.circle(
                image,
                (icon_x, icon_y + icon_size // 2),
                icon_size // 2,
                (255, 255, 255),
                -1,
            )
            cv2.putText(
                image,
                "!",
                (icon_x - 3, icon_y + icon_size // 2 + 4),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                color,
                2,
            )
        elif "Poor" in status_text:
            # X mark
            cv2.circle(
                image,
                (icon_x, icon_y + icon_size // 2),
                icon_size // 2,
                (255, 255, 255),
                -1,
            )
            cv2.putText(
                image,
                "X",
                (icon_x - 4, icon_y + icon_size // 2 + 4),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                color,
                2,
            )

        # Add progress bar for pose stability
        if len(self.get_landmarks()) > 0:
            self._draw_stability_indicator(image, badge_x, badge_y + badge_h + 10)

    def _draw_stability_indicator(self, image, x, y):
        """Draw a stability/confidence progress bar."""
        landmarks = self.get_landmarks()
        if len(landmarks) < 33:
            return

        # Calculate average visibility as stability metric
        avg_visibility = sum(lm[4] for lm in landmarks) / len(landmarks)
        stability_score = min(1.0, avg_visibility)

        # Progress bar dimensions
        bar_width = 200
        bar_height = 8
        border_thickness = 1

        # Background bar
        cv2.rectangle(image, (x, y), (x + bar_width, y + bar_height), (60, 60, 60), -1)

        # Progress fill
        fill_width = int(bar_width * stability_score)
        if stability_score > 0.8:
            fill_color = (34, 197, 94)  # Green
        elif stability_score > 0.6:
            fill_color = (59, 130, 246)  # Blue
        elif stability_score > 0.4:
            fill_color = (245, 158, 11)  # Orange
        else:
            fill_color = (239, 68, 68)  # Red

        if fill_width > 0:
            cv2.rectangle(
                image, (x, y), (x + fill_width, y + bar_height), fill_color, -1
            )

        # Border
        cv2.rectangle(
            image,
            (x, y),
            (x + bar_width, y + bar_height),
            (255, 255, 255),
            border_thickness,
        )

        # Label
        label_y = y + bar_height + 15
        cv2.putText(
            image,
            f"Stability: {int(stability_score * 100)}%",
            (x, label_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (255, 255, 255),
            1,
        )

    def _draw_pose_guidance(self, image, landmarks):
        """Draw helpful guidance for pose positioning with enhanced visuals."""
        h, w = image.shape[:2]

        if len(landmarks) < 33:
            return

        # Get key landmarks
        nose = landmarks[0]
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        left_hip = landmarks[23]
        right_hip = landmarks[24]

        # Enhanced center line for alignment guidance
        center_x = w // 2
        cv2.line(
            image,
            (center_x, int(h * 0.1)),
            (center_x, int(h * 0.9)),
            (100, 200, 255),
            2,
        )

        # Add center line label
        cv2.putText(
            image,
            "CENTER",
            (center_x - 30, int(h * 0.95)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (100, 200, 255),
            1,
        )

        # Body center calculation
        body_center_x = int((left_shoulder[1] + right_shoulder[1]) * w / 2)

        # Enhanced alignment indicator with smooth feedback
        alignment_diff = abs(center_x - body_center_x)
        if alignment_diff > 20:  # More sensitive threshold
            # Animated alignment arrows with gradient effect
            arrow_y = int(h * 0.25)
            arrow_length = min(80, alignment_diff)

            if body_center_x < center_x:
                # Move right arrow with pulsing effect
                arrow_start = body_center_x + 30
                arrow_end = arrow_start + arrow_length

                # Draw gradient arrow
                for i in range(0, arrow_length, 5):
                    alpha = 1.0 - (i / arrow_length) * 0.5
                    color_intensity = int(255 * alpha)
                    cv2.circle(
                        image,
                        (arrow_start + i, arrow_y),
                        3,
                        (color_intensity, color_intensity, 0),
                        -1,
                    )

                cv2.arrowedLine(
                    image,
                    (arrow_start, arrow_y),
                    (arrow_end, arrow_y),
                    (255, 255, 0),
                    3,
                )

                # Instruction text with background
                self._draw_instruction_text(
                    image,
                    "👉 Step Right",
                    arrow_start - 20,
                    arrow_y - 25,
                    (255, 255, 0),
                )
            else:
                # Move left arrow with pulsing effect
                arrow_start = body_center_x - 30
                arrow_end = arrow_start - arrow_length

                # Draw gradient arrow
                for i in range(0, arrow_length, 5):
                    alpha = 1.0 - (i / arrow_length) * 0.5
                    color_intensity = int(255 * alpha)
                    cv2.circle(
                        image,
                        (arrow_start - i, arrow_y),
                        3,
                        (color_intensity, color_intensity, 0),
                        -1,
                    )

                cv2.arrowedLine(
                    image,
                    (arrow_start, arrow_y),
                    (arrow_end, arrow_y),
                    (255, 255, 0),
                    3,
                )

                # Instruction text with background
                self._draw_instruction_text(
                    image, "👈 Step Left", arrow_end - 20, arrow_y - 25, (255, 255, 0)
                )

        # Distance guidance
        if len(landmarks) > 0:
            self._draw_distance_guidance(image, landmarks)

    def _draw_instruction_text(self, image, text, x, y, color):
        """Draw instruction text with modern styling."""
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2

        # Get text size for background
        (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)

        # Draw background rectangle
        bg_padding = 8
        cv2.rectangle(
            image,
            (x - bg_padding, y - text_h - bg_padding),
            (x + text_w + bg_padding, y + baseline + bg_padding),
            (0, 0, 0),
            -1,
        )

        # Draw border
        cv2.rectangle(
            image,
            (x - bg_padding, y - text_h - bg_padding),
            (x + text_w + bg_padding, y + baseline + bg_padding),
            color,
            2,
        )

        # Draw text
        cv2.putText(image, text, (x, y), font, font_scale, (255, 255, 255), thickness)

    def _draw_distance_guidance(self, image, landmarks):
        """Draw guidance for optimal distance from camera."""
        h, w = image.shape[:2]

        # Calculate body height in frame
        nose = landmarks[0]
        left_foot = landmarks[31] if len(landmarks) > 31 else landmarks[27]
        right_foot = landmarks[32] if len(landmarks) > 32 else landmarks[28]

        # Use the lower foot for height calculation
        foot_y = max(left_foot[2], right_foot[2])
        body_height_ratio = foot_y - nose[2]

        # Optimal body height should be 70-85% of frame height
        optimal_min = 0.70
        optimal_max = 0.85

        if body_height_ratio < optimal_min:
            # Too far - move closer
            self._draw_instruction_text(
                image, "📍 Step Closer", int(w * 0.4), int(h * 0.9), (255, 165, 0)
            )
        elif body_height_ratio > optimal_max:
            # Too close - step back
            self._draw_instruction_text(
                image, "📍 Step Back", int(w * 0.4), int(h * 0.9), (255, 165, 0)
            )
        else:
            # Good distance
            self._draw_instruction_text(
                image, "✅ Perfect Distance", int(w * 0.4), int(h * 0.9), (34, 197, 94)
            )

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
        key_landmarks = [
            nose,
            left_shoulder,
            right_shoulder,
            left_hip,
            right_hip,
            left_ankle,
            right_ankle,
            left_foot_index,
            right_foot_index,
        ]

        # All key landmarks should have good visibility
        min_visibility = 0.6
        visible_landmarks = [lm for lm in key_landmarks if lm[4] > min_visibility]

        if (
            len(visible_landmarks) < 8
        ):  # At least 8 out of 9 key landmarks should be visible
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
        visibility_check = all(
            lm[4] > min_visibility
            for lm in [left_shoulder, right_shoulder, left_hip, right_hip]
        )

        return (
            shoulder_symmetry
            and hip_symmetry
            and arm_spread
            and depth_symmetry
            and visibility_check
        )

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
        visibility_check = all(
            lm[4] > min_visibility
            for lm in [left_shoulder, right_shoulder, left_hip, right_hip, nose]
        )

        return (
            significant_depth_diff
            and vertical_alignment
            and arms_down
            and visibility_check
        )

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
class PoseDetector:

    def __init__(self):
        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose()

    def findPose(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)

        if self.results.pose_landmarks and draw:
            # Work on a copy to preserve the original image
            display_img = img.copy()
            self.mpDraw.draw_landmarks(
                display_img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS
            )
            return display_img
        
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
        nose_depth_diff = (
            abs(nose[3] - left_shoulder[3]) > 50
            and abs(nose[3] - right_shoulder[3]) > 50
        )

        # Arms should be roughly vertical (straight down) – y-diff between shoulder and wrist large
        arms_down = (
            abs(left_wrist[2] - left_shoulder[2]) > 100
            and abs(right_wrist[2] - right_shoulder[2]) > 100
        )

        return all(
            [
                shoulders_aligned,
                hips_aligned,
                ankles_aligned,
                shoulders_depth_diff,
                nose_depth_diff,
                arms_down,
            ]
        )


# The following code is only used when this file is run directly (not imported)
if __name__ == "__main__":
    # Modern color scheme
    COLORS = {
        "primary": "#3B82F6",  # Blue
        "primary_hover": "#2563EB",  # Darker blue
        "success": "#10B981",  # Green
        "warning": "#F59E0B",  # Orange
        "error": "#EF4444",  # Red
        "background": "#F8FAFC",  # Light gray
        "surface": "#FFFFFF",  # White
        "text_primary": "#1F2937",  # Dark gray
        "text_secondary": "#6B7280",  # Medium gray
        "border": "#E5E7EB",  # Light border
    }

    # Create a standalone version of the capture functionality
    def setup_dashboard():
        # Set modern theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        app = ctk.CTk()
        app.title("🎥 Advanced Pose Capture Studio")
        app.geometry("1000x700")
        app.resizable(True, True)
        app.configure(fg_color=COLORS["background"])

        detector = AdvancedPoseDetector()

        # Configure main grid with better proportions
        app.grid_columnconfigure(0, weight=1)
        app.grid_rowconfigure(0, weight=0)  # Header
        app.grid_rowconfigure(1, weight=1)  # Main content
        app.grid_rowconfigure(2, weight=0)  # Footer

        # Modern header section
        header_frame = ctk.CTkFrame(
            app, fg_color=COLORS["surface"], corner_radius=15, height=80
        )
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_propagate(False)

        # Header content
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=30, pady=20)

        title_label = ctk.CTkLabel(
            header_content,
            text="Pose Capture Studio",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["text_primary"],
        )
        title_label.pack(side="left")

        subtitle_label = ctk.CTkLabel(
            header_content,
            text="AI-powered body scanning for personalized recommendations",
            font=ctk.CTkFont(size=14),
            text_color=COLORS["text_secondary"],
        )
        subtitle_label.pack(side="left", padx=(20, 0))

        # Main content area with improved layout
        main_frame = ctk.CTkFrame(app, fg_color="transparent")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        main_frame.grid_columnconfigure((0, 1), weight=1, uniform="col")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # Enhanced pose frame creator with modern styling
        def create_modern_pose_frame(parent, text, icon, row, col):
            frame = ctk.CTkFrame(
                parent,
                width=320,
                height=320,
                corner_radius=20,
                fg_color=COLORS["surface"],
                border_width=2,
                border_color=COLORS["border"],
            )
            frame.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            frame.grid_propagate(False)

            # Header section with icon and title
            header = ctk.CTkFrame(frame, fg_color="transparent", height=60)
            header.pack(fill="x", padx=20, pady=(20, 10))
            header.pack_propagate(False)

            icon_label = ctk.CTkLabel(header, text=icon, font=ctk.CTkFont(size=24))
            icon_label.pack(side="left")

            title_label = ctk.CTkLabel(
                header,
                text=text,
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=COLORS["text_primary"],
            )
            title_label.pack(side="left", padx=(10, 0))

            # Status indicator
            status_frame = ctk.CTkFrame(
                header, width=80, height=24, corner_radius=12, fg_color=COLORS["border"]
            )
            status_frame.pack(side="right")

            status_label = ctk.CTkLabel(
                status_frame,
                text="Pending",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=COLORS["text_secondary"],
            )
            status_label.pack()

            # Image display area with better styling
            image_container = ctk.CTkFrame(
                frame,
                fg_color=COLORS["background"],
                corner_radius=15,
                border_width=1,
                border_color=COLORS["border"],
            )
            image_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

            image_holder = ctk.CTkLabel(
                image_container,
                text="📷\nReady to capture",
                font=ctk.CTkFont(size=16),
                text_color=COLORS["text_secondary"],
                fg_color="transparent",
            )
            image_holder.pack(expand=True, pady=20)

            return frame, image_holder, status_label

        # Create enhanced pose frames
        front_frame, front_img_label, front_status = create_modern_pose_frame(
            main_frame, "Front Pose", "🧍", 0, 0
        )
        side_frame, side_img_label, side_status = create_modern_pose_frame(
            main_frame, "Side Pose", "🚶", 0, 1
        )

        # Modern live feed section
        live_feed_frame = ctk.CTkFrame(
            main_frame,
            corner_radius=20,
            fg_color=COLORS["surface"],
            border_width=2,
            border_color=COLORS["border"],
        )
        live_feed_frame.grid(
            row=1, column=0, columnspan=2, padx=15, pady=15, sticky="nsew"
        )

        # Live feed header
        feed_header = ctk.CTkFrame(live_feed_frame, fg_color="transparent", height=50)
        feed_header.pack(fill="x", padx=25, pady=(20, 10))
        feed_header.pack_propagate(False)

        feed_icon = ctk.CTkLabel(feed_header, text="📹", font=ctk.CTkFont(size=20))
        feed_icon.pack(side="left")

        feed_title = ctk.CTkLabel(
            feed_header,
            text="Live Camera Feed",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"],
        )
        feed_title.pack(side="left", padx=(10, 0))

        # Recording indicator
        recording_dot = ctk.CTkLabel(
            feed_header, text="●", font=ctk.CTkFont(size=12), text_color=COLORS["error"]
        )
        recording_dot.pack(side="right", padx=(0, 5))

        recording_text = ctk.CTkLabel(
            feed_header,
            text="LIVE",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["error"],
        )
        recording_text.pack(side="right")

        # Live feed display
        live_feed_container = ctk.CTkFrame(
            live_feed_frame, fg_color="#000000", corner_radius=15
        )
        live_feed_container.pack(fill="both", expand=True, padx=25, pady=(0, 25))

        live_feed_label = ctk.CTkLabel(
            live_feed_container,
            text="🎥\nCamera feed will appear here\nClick 'Start Capture' to begin",
            font=ctk.CTkFont(size=16),
            text_color="white",
            fg_color="transparent",
        )
        live_feed_label.pack(expand=True)

        # Modern countdown overlay
        countdown_frame = ctk.CTkFrame(
            live_feed_container,
            width=120,
            height=120,
            corner_radius=60,
            fg_color=COLORS["primary"],
            border_width=3,
            border_color="white",
        )

        countdown_label = ctk.CTkLabel(
            countdown_frame,
            text="",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="white",
        )
        countdown_label.pack(expand=True)

        def capture_images(
            detector,
            front_img_label,
            side_img_label,
            live_feed_label,
            countdown_label,
            front_status,
            side_status,
        ):
            try:
                cap = cv2.VideoCapture(0)

                # Enhanced error handling for camera initialization
                if not cap.isOpened():
                    error_msg = "❌ Camera Error\nUnable to access camera\nCheck camera permissions"
                    live_feed_label.configure(
                        text=error_msg, text_color=COLORS["error"]
                    )
                    print("🚨 Error: Could not open camera. Please check:")
                    print("   • Camera permissions")
                    print("   • Camera is not being used by another app")
                    print("   • Camera drivers are installed")
                    return

                front_captured = False
                side_captured = False
                consecutive_good_poses = 0
                required_stability = 10  # Frames of stable pose required

                # Enhanced capture settings with error handling
                try:
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    cap.set(cv2.CAP_PROP_FPS, 30)
                except Exception as e:
                    print(f"⚠️ Warning: Could not set camera properties: {e}")

                # Set the dimensions of the live feed and video frame
                live_feed_width = 400
                live_feed_height = 300

                countdown_start = None
                countdown_pose = None
                last_instruction = ""
                error_count = 0
                max_errors = 5

                # Define file paths for saving images
                front_image_path = os.path.join(INPUT_FILES_DIR, "input_front.png")
                side_image_path = os.path.join(INPUT_FILES_DIR, "input_side.png")

                print("📋 Capture Session Started!")
                print("💡 Instructions:")
                print("   • For front pose: Face camera with arms spread (T-pose)")
                print("   • For side pose: Turn 90° with arms at your sides")
                print("   • Press 'Q' to quit anytime")

                while cap.isOpened():
                    try:
                        success, img = cap.read()
                        if not success:
                            error_count += 1
                            if error_count > max_errors:
                                error_msg = f"📱 Camera Connection Lost\nTried {error_count} times\nRestarting capture..."
                                live_feed_label.configure(
                                    text=error_msg, text_color=COLORS["error"]
                                )
                                print(
                                    f"🚨 Error: Failed to read from camera {error_count} consecutive times"
                                )
                                break
                            continue
                        else:
                            error_count = 0  # Reset error count on successful read

                        # Resize and flip for better UX
                        img = cv2.resize(img, (live_feed_width, live_feed_height))
                        img = cv2.flip(img, 1)  # Mirror the image

                        # Create a copy for display (with UI elements) and keep original clean for capture
                        display_img = img.copy()
                        
                        # Process pose detection on display copy
                        display_img = detector.findPose(display_img)
                        lmList = detector.findPosition(display_img, draw=False)  # Don't draw additional landmarks

                        # Enhanced status text display with user guidance
                        instruction_text = ""
                        countdown_text = ""
                        pose_quality = ""

                        # Detailed guidance based on current state
                        if len(lmList) == 0:
                            instruction_text = (
                                "🔍 No person detected - step into camera view"
                            )
                            consecutive_good_poses = 0
                        elif not detector.isFullBodyVisible(lmList, img.shape):
                            instruction_text = "👤 Full body not visible - step back to show head to feet"
                            consecutive_good_poses = 0
                        else:
                            # Full body is visible, check pose type
                            if not front_captured:
                                if detector.isFrontPose(lmList, img.shape):
                                    consecutive_good_poses += 1
                                    if consecutive_good_poses >= required_stability:
                                        instruction_text = (
                                            "🎯 Perfect front pose! Hold steady..."
                                        )
                                        if countdown_pose != "front":
                                            countdown_start = time.time()
                                            countdown_pose = "front"
                                            print(
                                                "🎯 Stable front pose detected. Starting countdown..."
                                            )
                                    else:
                                        stability_percent = int(
                                            (
                                                consecutive_good_poses
                                                / required_stability
                                            )
                                            * 100
                                        )
                                        instruction_text = f"🔄 Front pose detected - stabilizing {stability_percent}%"
                                else:
                                    consecutive_good_poses = 0
                                    # Provide specific guidance for front pose
                                    if len(lmList) >= 16:
                                        left_wrist = lmList[15]
                                        right_wrist = lmList[16]
                                        shoulder_width = abs(
                                            lmList[11][1] - lmList[12][1]
                                        )
                                        arm_spread = abs(left_wrist[1] - right_wrist[1])

                                        if arm_spread < shoulder_width * 1.2:
                                            instruction_text = (
                                                "🤲 Spread your arms wider (T-pose)"
                                            )
                                        else:
                                            instruction_text = "📐 Face the camera directly with arms spread"
                                    else:
                                        instruction_text = "🧍 Stand facing camera with arms spread wide"

                            elif front_captured and not side_captured:
                                if detector.isSidePose(lmList, img.shape):
                                    consecutive_good_poses += 1
                                    if consecutive_good_poses >= required_stability:
                                        instruction_text = (
                                            "🎯 Perfect side pose! Hold steady..."
                                        )
                                        if countdown_pose != "side":
                                            countdown_start = time.time()
                                            countdown_pose = "side"
                                            print(
                                                "🎯 Stable side pose detected. Starting countdown..."
                                            )
                                    else:
                                        stability_percent = int(
                                            (
                                                consecutive_good_poses
                                                / required_stability
                                            )
                                            * 100
                                        )
                                        instruction_text = f"🔄 Side pose detected - stabilizing {stability_percent}%"
                                else:
                                    consecutive_good_poses = 0
                                    # Provide specific guidance for side pose
                                    instruction_text = (
                                        "🚶 Turn 90° to your side, arms at your sides"
                                    )
                            else:
                                instruction_text = "✨ All poses captured successfully!"

                        # Reset countdown if pose quality drops
                        if (
                            countdown_pose
                            and consecutive_good_poses < required_stability
                        ):
                            countdown_start = None
                            countdown_pose = None
                            countdown_frame.place_forget()

                        # Handle countdown logic with enhanced visuals and stability check
                        if (
                            countdown_start
                            and countdown_pose
                            and consecutive_good_poses >= required_stability
                        ):
                            elapsed_time = time.time() - countdown_start
                            remaining_time = max(0, 5 - int(elapsed_time))

                            if remaining_time > 0:
                                countdown_text = str(remaining_time)
                                countdown_label.configure(text=countdown_text)
                                countdown_frame.place(
                                    relx=0.5, rely=0.5, anchor="center"
                                )

                                # Enhanced countdown feedback
                                if remaining_time <= 2:
                                    instruction_text = f"📸 Capturing in {remaining_time}... Stay perfectly still!"

                            if remaining_time == 0:
                                # Final capture with quality verification
                                # Read a fresh, clean frame from camera for capture
                                capture_success_read, fresh_capture_img = cap.read()
                                if capture_success_read:
                                    # Process the fresh frame without UI elements
                                    fresh_capture_img = cv2.resize(fresh_capture_img, (live_feed_width, live_feed_height))
                                    fresh_capture_img = cv2.flip(fresh_capture_img, 1)
                                    
                                    # Use this clean image for capture
                                    capture_img = fresh_capture_img.copy()
                                    
                                    # Verify the captured image quality using a separate copy for testing only
                                    test_img = capture_img.copy()
                                    test_pose = detector.findPose(test_img, draw=False)  # No drawing on test image
                                    test_landmarks = detector.findPosition(test_img, draw=False)  # No drawing on test image

                                capture_success = False

                                if (
                                    countdown_pose == "front"
                                    and detector.isFrontPose(
                                        test_landmarks, capture_img.shape
                                    )
                                ):
                                    capture_success = True
                                elif (
                                    countdown_pose == "side"
                                    and detector.isSidePose(
                                        test_landmarks, capture_img.shape
                                    )
                                ):
                                    capture_success = True

                                if capture_success:
                                    os.makedirs(INPUT_FILES_DIR, exist_ok=True)

                                    if countdown_pose == "front":
                                        cv2.imwrite(front_image_path, capture_img)
                                        print(
                                            f"📸 Front pose captured successfully! → {front_image_path}"
                                        )
                                        front_captured = True
                                        front_status.configure(
                                            text="✅ Captured",
                                            fg_color=COLORS["success"],
                                        )

                                        # Display captured image
                                        img_rgb = cv2.cvtColor(
                                            capture_img, cv2.COLOR_BGR2RGB
                                        )
                                        img_pil = Image.fromarray(img_rgb)
                                        img_pil = img_pil.resize(
                                            (280, 280), Image.Resampling.LANCZOS
                                        )
                                        img_tk = ImageTk.PhotoImage(img_pil)
                                        front_img_label.configure(
                                            image=img_tk, text=""
                                        )
                                        front_img_label.image = img_tk

                                        instruction_text = "🎉 Front pose saved! Now turn to your side..."

                                    elif countdown_pose == "side":
                                        cv2.imwrite(side_image_path, capture_img)
                                        print(
                                            f"📸 Side pose captured successfully! → {side_image_path}"
                                        )
                                        side_captured = True
                                        side_status.configure(
                                            text="✅ Captured",
                                            fg_color=COLORS["success"],
                                        )

                                        # Display captured image
                                        img_rgb = cv2.cvtColor(
                                            capture_img, cv2.COLOR_BGR2RGB
                                        )
                                        img_pil = Image.fromarray(img_rgb)
                                        img_pil = img_pil.resize(
                                            (280, 280), Image.Resampling.LANCZOS
                                        )
                                        img_tk = ImageTk.PhotoImage(img_pil)
                                        side_img_label.configure(
                                            image=img_tk, text=""
                                        )
                                        side_img_label.image = img_tk

                                        instruction_text = (
                                            "🎉 Side pose saved! Session complete!"
                                        )
                                else:
                                    print(
                                        "⚠️ Capture failed - pose changed during countdown. Please try again."
                                    )
                                    instruction_text = "⚠️ Pose changed during capture - please try again"
                                
                                # Reset capture state
                                countdown_start = None
                                countdown_pose = None
                                consecutive_good_poses = 0
                                countdown_frame.place_forget()
                                countdown_label.configure(text="")
                                
                            else:
                                # Failed to read fresh frame for capture
                                print("⚠️ Failed to capture fresh frame")
                                instruction_text = "⚠️ Capture failed - please try again"
                                countdown_start = None
                                countdown_pose = None
                                consecutive_good_poses = 0
                                countdown_frame.place_forget()
                                countdown_label.configure(text="")
                        else:
                            countdown_frame.place_forget()
                            countdown_label.configure(text="")

                        # Enhanced instruction feedback with emojis and colors
                        if instruction_text and instruction_text != last_instruction:
                            print(f"💡 {instruction_text}")
                            last_instruction = instruction_text

                        # Update live feed with display image (includes UI elements)
                        display_img_rgb = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)
                        img_pil = Image.fromarray(display_img_rgb)
                        img_tk = ImageTk.PhotoImage(img_pil)
                        live_feed_label.configure(image=img_tk, text="")
                        live_feed_label.image = img_tk

                        # Check completion with celebration
                        if front_captured and side_captured:
                            print("🎉✨ CAPTURE SESSION COMPLETE! ✨🎉")
                            print("📁 Images saved to input files directory")
                            print("🚀 Ready for body analysis!")

                            # Show success message with animation effect
                            success_messages = [
                                "🎉 SUCCESS! 🎉",
                                "✨ PERFECT CAPTURES! ✨",
                                "🚀 READY FOR ANALYSIS! 🚀",
                            ]

                            for i, msg in enumerate(success_messages):
                                live_feed_label.configure(
                                    text=f"{msg}\n\nBoth poses captured successfully!\nProcessing will begin shortly...",
                                    image=None,
                                    text_color=COLORS["success"],
                                    font=ctk.CTkFont(size=16, weight="bold"),
                                )
                                time.sleep(1)

                            time.sleep(2)
                            break

                        # Quit on 'q' key
                        if cv2.waitKey(1) & 0xFF == ord("q"):
                            print("🔚 User quit capture session")
                            break

                    except Exception as frame_error:
                        print(f"⚠️ Frame processing error: {frame_error}")
                        error_count += 1
                        if error_count > max_errors:
                            break
                        continue

            except Exception as e:
                error_msg = (
                    f"❌ Unexpected Error\n{str(e)}\nPlease restart the application"
                )
                live_feed_label.configure(text=error_msg, text_color=COLORS["error"])
                print(f"🚨 Critical Error: {e}")
            finally:
                try:
                    cap.release()
                    cv2.destroyAllWindows()
                    print("🔒 Camera resources released")
                except:
                    pass

        def start_capture(
            detector,
            front_img_label,
            side_img_label,
            live_feed_label,
            countdown_label,
            front_status,
            side_status,
        ):
            # Update UI to show capture is starting
            live_feed_label.configure(
                text="🔄 Initializing camera...\nPlease wait", text_color="white"
            )

            capture_thread = Thread(
                target=capture_images,
                args=(
                    detector,
                    front_img_label,
                    side_img_label,
                    live_feed_label,
                    countdown_label,
                    front_status,
                    side_status,
                ),
            )
            capture_thread.daemon = True
            capture_thread.start()

        # Enhanced footer with modern buttons
        footer_frame = ctk.CTkFrame(app, fg_color="transparent", height=80)
        footer_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(10, 20))
        footer_frame.grid_propagate(False)
        footer_frame.grid_columnconfigure(1, weight=1)

        # Start capture button with modern styling
        start_button = ctk.CTkButton(
            footer_frame,
            text="🚀 Start Capture Session",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=50,
            width=250,
            corner_radius=25,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=lambda: start_capture(
                detector,
                front_img_label,
                side_img_label,
                live_feed_label,
                countdown_label,
                front_status,
                side_status,
            ),
        )
        start_button.grid(row=0, column=0, padx=(0, 10))

        # Help button
        help_button = ctk.CTkButton(
            footer_frame,
            text="❓ Help & Tips",
            font=ctk.CTkFont(size=14),
            height=50,
            width=120,
            corner_radius=25,
            fg_color="transparent",
            border_width=2,
            border_color=COLORS["border"],
            text_color=COLORS["text_secondary"],
            hover_color=COLORS["border"],
            command=lambda: show_help_dialog(app),
        )
        help_button.grid(row=0, column=1, padx=10, sticky="e")

        # Instructions panel
        instructions_frame = ctk.CTkFrame(
            footer_frame, fg_color=COLORS["surface"], corner_radius=10
        )
        instructions_frame.grid(row=0, column=2, sticky="e", padx=(10, 0))

        instructions_label = ctk.CTkLabel(
            instructions_frame,
            text="💡 Tips: Face camera directly → Spread arms → Turn to side → Keep arms down",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
        )
        instructions_label.pack(padx=15, pady=15)

        app.protocol(
            "WM_DELETE_WINDOW", lambda: (app.destroy(), cv2.destroyAllWindows())
        )
        app.mainloop()

    def show_help_dialog(parent):
        """Show a modern help dialog with capture tips."""
        dialog = ctk.CTkToplevel(parent)
        dialog.title("📋 Capture Help & Tips")
        dialog.geometry("500x600")
        dialog.configure(fg_color=COLORS["background"])
        dialog.transient(parent)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f"500x600+{x}+{y}")

        # Content frame
        content = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title = ctk.CTkLabel(
            content,
            text="How to Get Perfect Captures",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text_primary"],
        )
        title.pack(pady=(0, 20))

        # Tips sections
        tips_data = [
            (
                "🧍 Front Pose Tips",
                [
                    "• Stand 6-8 feet from the camera",
                    "• Face the camera directly",
                    "• Spread your arms out to form a T-shape",
                    "• Keep your feet shoulder-width apart",
                    "• Look straight at the camera",
                    "• Wear form-fitting clothes for best results",
                ],
            ),
            (
                "🚶 Side Pose Tips",
                [
                    "• Turn 90 degrees to your right or left",
                    "• Keep your arms straight down at your sides",
                    "• Stand up straight with good posture",
                    "• Keep your feet together",
                    "• Look straight ahead (not at camera)",
                    "• Make sure your full body is visible",
                ],
            ),
            (
                "🎥 General Tips",
                [
                    "• Ensure good lighting in the room",
                    "• Use a plain background if possible",
                    "• Remove any bulky clothing or accessories",
                    "• Stay still during the 5-second countdown",
                    "• Be patient - the AI needs clear poses",
                    "• Press 'Q' to quit anytime",
                ],
            ),
        ]

        for section_title, tips in tips_data:
            # Section header
            section_frame = ctk.CTkFrame(
                content, fg_color=COLORS["surface"], corner_radius=10
            )
            section_frame.pack(fill="x", pady=(0, 15))

            section_header = ctk.CTkLabel(
                section_frame,
                text=section_title,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=COLORS["text_primary"],
            )
            section_header.pack(anchor="w", padx=20, pady=(15, 5))

            # Tips list
            for tip in tips:
                tip_label = ctk.CTkLabel(
                    section_frame,
                    text=tip,
                    font=ctk.CTkFont(size=12),
                    text_color=COLORS["text_secondary"],
                    anchor="w",
                    justify="left",
                )
                tip_label.pack(anchor="w", padx=20, pady=2)

            # Add some bottom padding
            ctk.CTkLabel(section_frame, text="", height=10).pack()

        # Close button
        close_btn = ctk.CTkButton(
            dialog,
            text="Got it! 👍",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=dialog.destroy,
        )
        close_btn.pack(pady=20)

    setup_dashboard()
