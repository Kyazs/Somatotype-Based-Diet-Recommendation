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
"""
Input Page for the Diet Recommendation System.
Collects user personal information needed for diet recommendations.
"""
import customtkinter as ctk
from tkinter import messagebox
import os
import sys
from utils.theme_manager import ThemeManager

class InputPage(ctk.CTkFrame):
    """Input page with modern UI design for user data collection"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=ThemeManager.BG_COLOR)
        self.controller = controller
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create scrollable frame to contain all content
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Header with title and back button
        self.header_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.header_frame.grid_columnconfigure(1, weight=1)
        
        # Back button
        self.back_button = ThemeManager.create_secondary_button(
            self.header_frame,
            "Back",
            lambda: controller.show_frame("LandingPage")
        )
        self.back_button.grid(row=0, column=0, padx=(0, 20))
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="Personal Information",
            font=ThemeManager.get_title_font()
        )
        self.title_label.grid(row=0, column=1)
        
        # Subtitle with instructions
        self.subtitle_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="Please provide your details so we can create a personalized diet plan.",
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.GRAY_DARK
        )
        self.subtitle_label.grid(row=1, column=0, pady=(0, 20))
        
        # Main form card
        self.form_card = ThemeManager.create_card_frame(self.scrollable_frame)
        self.form_card.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        self.form_card.grid_columnconfigure((0, 1), weight=1)
        
        # Form fields
        # Name
        self.name_label = ThemeManager.create_label(self.form_card, "Full Name", bold=True)
        self.name_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))
        
        self.name_entry = ThemeManager.create_entry(self.form_card, "Enter your full name")
        self.name_entry.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15), columnspan=2)
        
        # Gender
        self.gender_label = ThemeManager.create_label(self.form_card, "Gender", bold=True)
        self.gender_label.grid(row=2, column=0, sticky="w", padx=20, pady=(0, 5))
        
        # Gender as radio buttons in a frame for better layout
        self.gender_frame = ctk.CTkFrame(self.form_card, fg_color="transparent")
        self.gender_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 15), columnspan=2)
        
        self.gender_var = ctk.StringVar(value="male")
        
        self.male_radio = ctk.CTkRadioButton(
            self.gender_frame, 
            text="Male",
            variable=self.gender_var,
            value="male",
            font=ThemeManager.get_label_font()
        )
        self.male_radio.grid(row=0, column=0, padx=(0, 20))
        
        self.female_radio = ctk.CTkRadioButton(
            self.gender_frame, 
            text="Female",
            variable=self.gender_var,
            value="female",
            font=ThemeManager.get_label_font()
        )
        self.female_radio.grid(row=0, column=1)
        
        # Age, split into two columns from here
        self.age_label = ThemeManager.create_label(self.form_card, "Age", bold=True)
        self.age_label.grid(row=4, column=0, sticky="w", padx=20, pady=(0, 5))
        
        self.age_entry = ThemeManager.create_entry(self.form_card, "Enter your age")
        self.age_entry.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        # Height
        self.height_label = ThemeManager.create_label(self.form_card, "Height (cm)", bold=True)
        self.height_label.grid(row=4, column=1, sticky="w", padx=20, pady=(0, 5))
        
        self.height_entry = ThemeManager.create_entry(self.form_card, "Enter your height")
        self.height_entry.grid(row=5, column=1, sticky="ew", padx=20, pady=(0, 15))
        
        # Weight
        self.weight_label = ThemeManager.create_label(self.form_card, "Weight (kg)", bold=True)
        self.weight_label.grid(row=6, column=0, sticky="w", padx=20, pady=(0, 5))
        
        self.weight_entry = ThemeManager.create_entry(self.form_card, "Enter your weight")
        self.weight_entry.grid(row=7, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        # Goal
        self.goal_label = ThemeManager.create_label(self.form_card, "Your Goal", bold=True)
        self.goal_label.grid(row=6, column=1, sticky="w", padx=20, pady=(0, 5))
        
        self.goal_options = ["Maintain Weight", "Lose Weight", "Gain Weight"]
        self.goal_dropdown = ThemeManager.create_dropdown(self.form_card, self.goal_options)
        self.goal_dropdown.grid(row=7, column=1, sticky="ew", padx=20, pady=(0, 15))
        
        # Activity Level
        self.activity_label = ThemeManager.create_label(self.form_card, "Activity Level", bold=True)
        self.activity_label.grid(row=8, column=0, sticky="w", padx=20, pady=(0, 5), columnspan=2)
        
        self.activity_options = [
            "Sedentary (little or no exercise)",
            "Lightly active (light exercise/sports 1-3 days/week)",
            "Moderately active (moderate exercise/sports 3-5 days/week)",
            "Very active (hard exercise/sports 6-7 days a week)",
            "Extra active (very hard exercise & physical job or 2x training)"
        ]
        self.activity_dropdown = ThemeManager.create_dropdown(self.form_card, self.activity_options)
        self.activity_dropdown.grid(row=9, column=0, sticky="ew", padx=20, pady=(0, 15), columnspan=2)
        
        # Allergies/Dietary Restrictions (Optional)
        # self.allergies_label = ThemeManager.create_label(self.form_card, "Allergies or Dietary Restrictions (Optional)", bold=True)
        # self.allergies_label.grid(row=10, column=0, sticky="w", padx=20, pady=(0, 5), columnspan=2)
        
        # # Allergies as checkboxes
        # self.allergies_frame = ctk.CTkFrame(self.form_card, fg_color="transparent")
        # self.allergies_frame.grid(row=11, column=0, sticky="ew", padx=20, pady=(0, 20), columnspan=2)
        # self.allergies_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # # Create allergy checkboxes
        # self.allergy_vars = {}
        # allergy_options = ["Dairy", "Eggs", "Peanuts", "Tree Nuts", "Soy", "Wheat", "Gluten", "Fish", "Shellfish", "Sesame"]
        
        # for i, allergy in enumerate(allergy_options):
        #     # Calculate row and column (3 columns grid)
        #     row_idx = i // 3
        #     col_idx = i % 3
            
        #     self.allergy_vars[allergy] = ctk.BooleanVar(value=False)
        #     checkbox = ctk.CTkCheckBox(
        #         self.allergies_frame,
        #         text=allergy,
        #         variable=self.allergy_vars[allergy],
        #         font=ThemeManager.get_small_font(),
        #         checkbox_height=20,
        #         checkbox_width=20
        #     )
        #     checkbox.grid(row=row_idx, column=col_idx, padx=10, pady=5, sticky="w")
        
        # Submit button
        self.submit_button = ThemeManager.create_primary_button(
            self.form_card,
            "Continue to Image Capture",
            self.submit_details
        )
        self.submit_button.grid(row=12, column=0, padx=20, pady=20, columnspan=2, sticky="ew")
        
        # Privacy note
        self.privacy_text = ctk.CTkLabel(
            self.scrollable_frame,
            text="Your data is securely processed and will only be used for generating your personalized diet recommendations.",
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.GRAY_MEDIUM,
            wraplength=600
        )
        self.privacy_text.grid(row=3, column=0, pady=(20, 10))
        
    def submit_details(self):
        """Validate and submit user details"""
        # Get form values
        name = self.name_entry.get().strip()
        age = self.age_entry.get().strip()
        weight = self.weight_entry.get().strip()
        height = self.height_entry.get().strip()
        gender = self.gender_var.get()
        goal = self.goal_dropdown.get()
        activity_level = self.activity_dropdown.get()
        
        # Collect selected allergies
        # allergies = []
        # for allergy, var in self.allergy_vars.items():
        #     if var.get():
        #         allergies.append(allergy)
        
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
            
        # Update the state manager with form data
        self.controller.state_manager.update_user_data(
            name=name,
            gender=gender,
            age=age,
            weight=weight,
            height=height,
            goal=goal,
            activity_level=activity_level,
            # allergies=allergies
        )
        
        # Save data to input files
        self.controller.state_manager.save_user_input_files()
        
        # Show success message
        messagebox.showinfo("Success", "Your information has been saved successfully.")
        
        # Navigate to capture page
        self.controller.show_frame("CapturePage")
        
    def on_show(self):
        """Called when this page is shown"""
        # Prefill form with any existing data
        user_data = self.controller.state_manager.user_data
        
        if user_data["name"]:
            self.name_entry.delete(0, "end")
            self.name_entry.insert(0, user_data["name"])
            
        self.gender_var.set(user_data["gender"])
        
        if user_data["age"]:
            self.age_entry.delete(0, "end")
            self.age_entry.insert(0, user_data["age"])
            
        if user_data["weight"]:
            self.weight_entry.delete(0, "end")
            self.weight_entry.insert(0, user_data["weight"])
            
        if user_data["height"]:
            self.height_entry.delete(0, "end")
            self.height_entry.insert(0, user_data["height"])
            
        self.goal_dropdown.set(user_data["goal"])
        self.activity_dropdown.set(user_data["activity_level"])
        
        # # Set allergies checkboxes
        # for allergy, var in self.allergy_vars.items():
        #     var.set(allergy in user_data["allergies"])

if __name__ == "__main__":
    # For standalone testing
    class DummyController:
        def show_frame(self, frame_name):
            print(f"Switching to frame: {frame_name}")
            
        class StateManager:
            def __init__(self):
                self.user_data = {
                    "name": "John Doe",
                    "gender": "male",
                    "age": "32",
                    "weight": "75",
                    "height": "178",
                    "goal": "Maintain Weight",
                    "activity_level": "Moderately active",
                    "allergies": ["Dairy", "Peanuts"]
                }
                
            def update_user_data(self, **kwargs):
                self.user_data.update(kwargs)
                print(f"Updated user data: {self.user_data}")
                
            def save_user_input_files(self):
                print("Saving user input files...")
                return True
    
    controller = DummyController()
    controller.state_manager = controller.StateManager()
    
    # Create and run app
    root = ctk.CTk()
    root.title("Input Page Test")
    root.geometry("900x700")
    ThemeManager.setup_theme()
    
    app = InputPage(root, controller)
    app.pack(fill="both", expand=True)
    app.on_show()  # Populate with test data
    
    root.mainloop()