import cv2
import mediapipe as mp
import numpy as np
import tkinter as tk
from tkinter import messagebox, Label, Entry, Button, Frame
from threading import Thread
import csv
from PIL import Image, ImageTk
import os
import time

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
            h, w, c = img.shape
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                cz = lm.z * w  # Approximate depth scaling
                lmList.append([id, cx, cy, cz])
                if draw:
                    cv2.circle(img, (cx, cy), 7, (255, 0, 0), cv2.FILLED)
        return lmList


    def isFullBodyVisible(self, lmList, img_shape):
        h, w, _ = img_shape
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


def load_user_data():
    """Load user data from the CSV file if it exists."""
    if os.path.exists("user_data.csv"):
        with open("user_data.csv", mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                return row
    return None

def save_user_data(gender, height, weight):
    """Save or update user data in the CSV file."""
    with open("user_data.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["gender", "stature_cm", "weight_kg"])
        writer.writerow([gender, height, weight])

def capture_images(detector, front_img_label, side_img_label):
    cap = cv2.VideoCapture(0)
    front_captured = False
    side_captured = False

    while cap.isOpened():
        success, img = cap.read()
        if not success:
            print("Failed to read from camera. Exiting...")
            break

        img = detector.findPose(img)
        lmList = detector.findPosition(img)

        if len(lmList) != 0:
            if not front_captured and detector.isFrontPose(lmList, img.shape):
                print("Front pose detected. Capturing in 3 seconds...")
                time.sleep(1)
                success, img = cap.read()
                if success:
                    # Process pose detection on a copy of the image
                    img_with_pose = detector.findPose(img.copy())
                    cv2.imwrite("front_pose.jpg", img)  # Save the original image without annotations
                    print("Front pose captured!")
                    front_captured = True

                    # Display the captured front image
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img_pil = Image.fromarray(img_rgb)
                    img_pil = img_pil.resize((480, 360))
                    img_tk = ImageTk.PhotoImage(img_pil)
                    front_img_label.config(image=img_tk)
                    front_img_label.image = img_tk

            elif front_captured and not side_captured and detector.isSidePose(lmList, img.shape):
                print("Side pose detected. Capturing in 3 seconds...")
                time.sleep(1)
                success, img = cap.read()
                if success:
                    # Process pose detection on a copy of the image
                    img_with_pose = detector.findPose(img.copy())
                    cv2.imwrite("side_pose.jpg", img)  # Save the original image without annotations
                    print("Side pose captured!")
                    side_captured = True

                    # Display the captured side image
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img_pil = Image.fromarray(img_rgb)
                    img_pil = img_pil.resize((480, 360))
                    img_tk = ImageTk.PhotoImage(img_pil)
                    side_img_label.config(image=img_tk)
                    side_img_label.image = img_tk

        if front_captured and side_captured:
            print("Both poses captured. Exiting...")
            break

        cv2.imshow("Live Feed", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def start_capture(detector, front_img_label, side_img_label):
    capture_thread = Thread(target=capture_images, args=(detector, front_img_label, side_img_label))
    capture_thread.daemon = True
    capture_thread.start()

def setup_dashboard():
    root = tk.Tk()
    root.title("Pose Capture Dashboard")
    root.geometry("1000x800")  # Adjusted window size for larger images
    root.configure(bg="#f0f0f0")

    detector = PoseDetector()

    # Header
    header = Label(root, text="Pose Capture Dashboard", font=("Arial", 18, "bold"), bg="#f0f0f0", fg="#333")
    header.pack(pady=10)

    # User input frame
    input_frame = Frame(root, bg="#f0f0f0")
    input_frame.pack(pady=10)

    Label(input_frame, text="Gender:", font=("Arial", 12), bg="#f0f0f0").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    gender_entry = Entry(input_frame, font=("Arial", 12))
    gender_entry.grid(row=0, column=1, padx=10, pady=5)

    Label(input_frame, text="Height (cm):", font=("Arial", 12), bg="#f0f0f0").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    height_entry = Entry(input_frame, font=("Arial", 12))
    height_entry.grid(row=1, column=1, padx=10, pady=5)

    Label(input_frame, text="Weight (kg):", font=("Arial", 12), bg="#f0f0f0").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    weight_entry = Entry(input_frame, font=("Arial", 12))
    weight_entry.grid(row=2, column=1, padx=10, pady=5)

    # Load existing data into input fields
    user_data = load_user_data()
    if user_data:
        gender_entry.insert(0, user_data["gender"])
        height_entry.insert(0, user_data["stature_cm"])
        weight_entry.insert(0, user_data["weight_kg"])

    def save_data():
        gender = gender_entry.get()
        height = height_entry.get()
        weight = weight_entry.get()
        save_user_data(gender, height, weight)
        messagebox.showinfo("Data Saved", "User data saved successfully!")

    save_button = Button(input_frame, text="Save Data", command=save_data, font=("Arial", 12), bg="blue", fg="white")
    save_button.grid(row=3, column=0, columnspan=2, pady=10)

    # Image display frame
    image_frame = Frame(root, bg="#f0f0f0")
    image_frame.pack(pady=10)

    front_label = Label(image_frame, text="Front Pose", font=("Arial", 12), bg="#f0f0f0")
    front_label.grid(row=0, column=0, padx=10, pady=5)

    side_label = Label(image_frame, text="Side Pose", font=("Arial", 12), bg="#f0f0f0")
    side_label.grid(row=0, column=1, padx=10, pady=5)

    front_img_label = Label(image_frame, bg="#dcdcdc", width=400, height=360)  # Increased size
    front_img_label.grid(row=1, column=0, padx=10, pady=5)

    side_img_label = Label(image_frame, bg="#dcdcdc", width=400, height=360)  # Increased size
    side_img_label.grid(row=1, column=1, padx=10, pady=5)

    # Load existing images if available
    if os.path.exists("front_pose.jpg"):
        front_img = Image.open("front_pose.jpg")
        front_img = front_img.resize((480, 360))  # Resized to match larger label
        front_img_tk = ImageTk.PhotoImage(front_img)
        front_img_label.config(image=front_img_tk)
        front_img_label.image = front_img_tk

    if os.path.exists("side_pose.jpg"):
        side_img = Image.open("side_pose.jpg")
        side_img = side_img.resize((480, 360))  # Resized to match larger label
        side_img_tk = ImageTk.PhotoImage(side_img)
        side_img_label.config(image=side_img_tk)
        side_img_label.image = side_img_tk

    # Start capture button
    start_button = Button(root, text="Start Capture", font=("Arial", 12), bg="green", fg="white",
                        command=lambda: start_capture(detector, front_img_label, side_img_label))
    start_button.pack(pady=20)

    root.protocol("WM_DELETE_WINDOW", lambda: (root.destroy(), cv2.destroyAllWindows()))
    root.mainloop()

if __name__ == "__main__":
    setup_dashboard()
