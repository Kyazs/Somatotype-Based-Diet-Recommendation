import customtkinter as ctk
from tkinter import messagebox  # Import messagebox for validation feedback
import csv  # Import csv module for saving data
import os  # Import os module to handle file paths

from utils.utils import (
    INPUT_FILES_DIR,  # Import the directory for input files
)

# Initialize the app
ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"


class InputPage(ctk.CTkFrame):  # Change from CTk to CTkFrame
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Configure the frame
        self.grid_rowconfigure(list(range(15)), weight=1)  # Adjust rows for proper spacing
        self.grid_columnconfigure(0, weight=1)  # Center horizontally

        # Title Label
        self.title_label = ctk.CTkLabel(self, text="Input Your Details", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, pady=20)

        # Name Entry
        self.name_label = ctk.CTkLabel(self, text="Name:")
        self.name_label.grid(row=1, column=0, sticky="w", padx=20)
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Enter your name")
        self.name_entry.grid(row=2, column=0, padx=20, pady=5, sticky="ew")
        
        # Gender Dropdown
        self.gender_label = ctk.CTkLabel(self, text="Gender:")
        self.gender_label.grid(row=3, column=0, sticky="w", padx=20)
        self.gender_options = ["male", "female"]
        self.gender_dropdown = ctk.CTkOptionMenu(self, values=self.gender_options)
        self.gender_dropdown.grid(row=4, column=0, padx=20, pady=5, sticky="ew")

        # Age Entry
        self.age_label = ctk.CTkLabel(self, text="Age:")
        self.age_label.grid(row=5, column=0, sticky="w", padx=20)
        self.age_entry = ctk.CTkEntry(self, placeholder_text="Enter your age")
        self.age_entry.grid(row=6, column=0, padx=20, pady=5, sticky="ew")

        # Weight Entry
        self.weight_label = ctk.CTkLabel(self, text="Weight (kg):")
        self.weight_label.grid(row=7, column=0, sticky="w", padx=20)
        self.weight_entry = ctk.CTkEntry(self, placeholder_text="Enter your weight")
        self.weight_entry.grid(row=8, column=0, padx=20, pady=5, sticky="ew")

        # Height Entry
        self.height_label = ctk.CTkLabel(self, text="Height (cm):")
        self.height_label.grid(row=9, column=0, sticky="w", padx=20)
        self.height_entry = ctk.CTkEntry(self, placeholder_text="Enter your height")
        self.height_entry.grid(row=10, column=0, padx=20, pady=5, sticky="ew")

        # Goal Dropdown
        self.goal_label = ctk.CTkLabel(self, text="Goal:")
        self.goal_label.grid(row=11, column=0, sticky="w", padx=20)
        self.goal_options = ["Gain Weight", "Lose Weight", "Maintain Weight"]
        self.goal_dropdown = ctk.CTkOptionMenu(self, values=self.goal_options)
        self.goal_dropdown.grid(row=12, column=0, padx=20, pady=5, sticky="ew")

        # Submit Button
        self.submit_button = ctk.CTkButton(self, text="Submit", command=self.submit_details)
        self.submit_button.grid(row=13, column=0, pady=20)

        # Back Button
        self.back_button = ctk.CTkButton(
            self, 
            text="Back", 
            command=lambda: controller.show_frame("LandingPage"),  # Navigate to LandingPage
        )
        self.back_button.grid(row=14, column=0, pady=10)

    def submit_details(self):
        name = self.name_entry.get().strip()
        age = self.age_entry.get().strip()
        weight = self.weight_entry.get().strip()
        height = self.height_entry.get().strip()
        goal = self.goal_dropdown.get()
        gender = self.gender_dropdown.get()

        # Validation
        if not name:
            messagebox.showerror("Input Error", "Name cannot be empty. Please enter your name.")
            return
        if not age.isdigit():
            messagebox.showerror("Input Error", "Age must be a valid positive integer.")
            return
        if int(age) <= 0 or int(age) > 120:
            messagebox.showerror("Input Error", "Age must be between 1 and 120.")
            return
        if not weight.replace('.', '', 1).isdigit():
            messagebox.showerror("Input Error", "Weight must be a valid number.")
            return
        if float(weight) <= 0 or float(weight) > 500:
            messagebox.showerror("Input Error", "Weight must be a positive number less than or equal to 500 kg.")
            return
        if not height.replace('.', '', 1).isdigit():
            messagebox.showerror("Input Error", "Height must be a valid number.")
            return
        if float(height) <= 0 or float(height) > 300:
            messagebox.showerror("Input Error", "Height must be a positive number less than or equal to 300 cm.")
            return

        # File paths
        extractor_file_path = os.path.join(INPUT_FILES_DIR, "input_info_extractor.csv")
        recommendation_file_path = os.path.join(INPUT_FILES_DIR, "input_info_recommendation.csv")

        # Ensure directories exist
        os.makedirs(os.path.dirname(extractor_file_path), exist_ok=True)
        os.makedirs(os.path.dirname(recommendation_file_path), exist_ok=True)

        # Write data to input_info_extractor.csv
        with open(extractor_file_path, mode="w", newline="") as extractor_file:
            extractor_writer = csv.writer(extractor_file)
            extractor_writer.writerow(["gender", "stature_cm", "weight_kg"])  # Write header
            extractor_writer.writerow([gender, height, weight])  # Write new data

        # Write data to input_info_recommendation.csv
        with open(recommendation_file_path, mode="w", newline="") as recommendation_file:
            recommendation_writer = csv.writer(recommendation_file)
            recommendation_writer.writerow(["Name", "Age", "Goal"])  # Write header
            recommendation_writer.writerow([name, age, goal])  # Write new data

        print(f"Name: {name}, Gender: {gender}, Age: {age}, Weight: {weight}, Height: {height}, Goal: {goal}")
        messagebox.showinfo("Success", "Details submitted successfully and saved to files!")
        
        # Navigate to CapturePage directly without running external script
        self.controller.show_frame("CapturePage")


if __name__ == "__main__":
    class StandaloneApp(ctk.CTk):  # Wrapper for standalone testing
        def __init__(self):
            super().__init__()
            self.title("Input Page")
            self.geometry("800x600")
            self.resizable(False, False)
            self.input_page = InputPage(self, self)
            self.input_page.pack(fill="both", expand=True)

        def show_frame(self, frame_name):
            # Mock method for navigation
            print(f"Navigation to {frame_name} requested.")

    app = StandaloneApp()
    app.mainloop()