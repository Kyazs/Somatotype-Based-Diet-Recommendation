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
        
        # Initialize basic layout immediately for fast load
        self._init_basic_layout()
        
        # Flag to track if content has been loaded
        self._content_loaded = False
        
    def _init_basic_layout(self):
        """Initialize basic layout structure quickly"""
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create scrollable frame to contain all content
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            corner_radius=0,
            border_width=0
        )
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Initialize scroll throttling variables
        self._scroll_job = None
        self._last_scroll_time = 0
        
        # Bind mousewheel event to scrollable frame
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind("<Button-4>", self._on_mousewheel)  # Linux
        self.scrollable_frame.bind("<Button-5>", self._on_mousewheel)  # Linux
        
    def load_content(self):
        """Load the actual content when page is shown"""
        if self._content_loaded:
            return
            
        # Load actual content immediately - no loading indicator
        self._init_content_layout()
        self._content_loaded = True
        
    def _init_content_layout(self):
        """Initialize the full content layout"""
        # Header with title and back button
        self.header_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.header_frame.grid_columnconfigure(1, weight=1)
        
        # Back button
        self.back_button = ThemeManager.create_secondary_button(
            self.header_frame,
            "Back",
            lambda: self.controller.show_frame("LandingPage")
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
        # Name section - separated into first, middle, last
        self.name_label = ThemeManager.create_label(self.form_card, "Name", bold=True)
        self.name_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5), columnspan=2)
        
        # Name fields frame
        self.name_frame = ctk.CTkFrame(self.form_card, fg_color="transparent")
        self.name_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15), columnspan=2)
        self.name_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # First Name
        self.first_name_label = ThemeManager.create_label(self.name_frame, "First Name*", bold=False)
        self.first_name_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.first_name_entry = ThemeManager.create_entry(self.name_frame, "First name")
        self.first_name_entry.grid(row=1, column=0, sticky="ew", padx=(0, 5), pady=(0, 5))
        
        # Middle Name
        self.middle_name_label = ThemeManager.create_label(self.name_frame, "Middle Name", bold=False)
        self.middle_name_label.grid(row=0, column=1, sticky="w", pady=(0, 5))
        
        self.middle_name_entry = ThemeManager.create_entry(self.name_frame, "Middle name (optional)")
        self.middle_name_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=(0, 5))
        
        # Last Name
        self.last_name_label = ThemeManager.create_label(self.name_frame, "Last Name*", bold=False)
        self.last_name_label.grid(row=0, column=2, sticky="w", pady=(0, 5))
        
        self.last_name_entry = ThemeManager.create_entry(self.name_frame, "Last name")
        self.last_name_entry.grid(row=1, column=2, sticky="ew", padx=(5, 0), pady=(0, 5))
        
        # Add input validation callbacks for name fields
        self.first_name_entry.bind('<KeyRelease>', lambda e: self.validate_name_input(e, self.first_name_entry))
        self.middle_name_entry.bind('<KeyRelease>', lambda e: self.validate_name_input(e, self.middle_name_entry))
        self.last_name_entry.bind('<KeyRelease>', lambda e: self.validate_name_input(e, self.last_name_entry))
        
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
        
        # Add input validation for age (integers only)
        self.age_entry.bind('<KeyRelease>', lambda e: self.validate_integer_input(e, self.age_entry))
        
        # Height
        self.height_label = ThemeManager.create_label(self.form_card, "Height (cm)", bold=True)
        self.height_label.grid(row=4, column=1, sticky="w", padx=20, pady=(0, 5))
        
        self.height_entry = ThemeManager.create_entry(self.form_card, "Enter your height")
        self.height_entry.grid(row=5, column=1, sticky="ew", padx=20, pady=(0, 15))
        
        # Add input validation for height (numbers only)
        self.height_entry.bind('<KeyRelease>', lambda e: self.validate_numeric_input(e, self.height_entry))
        
        # Weight
        self.weight_label = ThemeManager.create_label(self.form_card, "Weight (kg)", bold=True)
        self.weight_label.grid(row=6, column=0, sticky="w", padx=20, pady=(0, 5))
        
        self.weight_entry = ThemeManager.create_entry(self.form_card, "Enter your weight")
        self.weight_entry.grid(row=7, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        # Add input validation for weight (numbers only)
        self.weight_entry.bind('<KeyRelease>', lambda e: self.validate_numeric_input(e, self.weight_entry))
        
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
        
    def validate_name(self, name):
        """Validate that name contains only letters, spaces, hyphens, and apostrophes"""
        if not name:
            return False
        # Allow letters, spaces, hyphens, apostrophes, and periods (for initials)
        import re
        return re.match(r"^[a-zA-Z\s\-'.]+$", name) is not None
    
    def validate_numeric(self, value):
        """Validate that value is a valid number (integer or float)"""
        if not value:
            return False
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def validate_integer(self, value):
        """Validate that value is a valid positive integer"""
        if not value:
            return False
        try:
            int_val = int(value)
            return int_val > 0
        except ValueError:
            return False
    
    def validate_name_input(self, event, entry_widget):
        """Real-time validation for name input fields"""
        current_value = entry_widget.get()
        if current_value and not self.validate_name(current_value):
            # Change border color to indicate error
            entry_widget.configure(border_color="red")
        else:
            # Reset to default border color
            entry_widget.configure(border_color=("gray70", "gray30"))
    
    def validate_numeric_input(self, event, entry_widget):
        """Real-time validation for numeric input fields"""
        current_value = entry_widget.get()
        if current_value and not self.validate_numeric(current_value):
            # Change border color to indicate error
            entry_widget.configure(border_color="red")
        else:
            # Reset to default border color
            entry_widget.configure(border_color=("gray70", "gray30"))
    
    def validate_integer_input(self, event, entry_widget):
        """Real-time validation for integer input fields"""
        current_value = entry_widget.get()
        if current_value:
            try:
                int(current_value)
                # Reset to default border color if valid
                entry_widget.configure(border_color=("gray70", "gray30"))
            except ValueError:
                # Change border color to indicate error
                entry_widget.configure(border_color="red")
        else:
            # Reset to default border color if empty
            entry_widget.configure(border_color=("gray70", "gray30"))
        
    def submit_details(self):
        """Validate and submit user details"""
        # Get form values
        first_name = self.first_name_entry.get().strip()
        middle_name = self.middle_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        age = self.age_entry.get().strip()
        weight = self.weight_entry.get().strip()
        height = self.height_entry.get().strip()
        gender = self.gender_var.get()
        goal = self.goal_dropdown.get()
        activity_level = self.activity_dropdown.get()
        
        # Combine names into full name
        name_parts = [first_name]
        if middle_name:  # Add middle name only if provided
            name_parts.append(middle_name)
        name_parts.append(last_name)
        full_name = " ".join(name_parts)
        
        # Validation
        # Name validation
        if not first_name:
            messagebox.showerror("Input Error", "First name is required.")
            return
        if not self.validate_name(first_name):
            messagebox.showerror("Input Error", "First name can only contain letters, spaces, hyphens, and apostrophes.")
            return
            
        if middle_name and not self.validate_name(middle_name):
            messagebox.showerror("Input Error", "Middle name can only contain letters, spaces, hyphens, and apostrophes.")
            return
            
        if not last_name:
            messagebox.showerror("Input Error", "Last name is required.")
            return
        if not self.validate_name(last_name):
            messagebox.showerror("Input Error", "Last name can only contain letters, spaces, hyphens, and apostrophes.")
            return
        
        # Age validation
        if not age:
            messagebox.showerror("Input Error", "Age is required.")
            return
        if not self.validate_integer(age):
            messagebox.showerror("Input Error", "Age must be a valid positive integer.")
            return
        if int(age) <= 0 or int(age) > 120:
            messagebox.showerror("Input Error", "Age must be between 1 and 120.")
            return
            
        # Weight validation
        if not weight:
            messagebox.showerror("Input Error", "Weight is required.")
            return
        if not self.validate_numeric(weight):
            messagebox.showerror("Input Error", "Weight must be a valid number.")
            return
        if float(weight) <= 0 or float(weight) > 500:
            messagebox.showerror("Input Error", "Weight must be a positive number less than or equal to 500 kg.")
            return
            
        # Height validation
        if not height:
            messagebox.showerror("Input Error", "Height is required.")
            return
        if not self.validate_numeric(height):
            messagebox.showerror("Input Error", "Height must be a valid number.")
            return
        if float(height) <= 0 or float(height) > 300:
            messagebox.showerror("Input Error", "Height must be a positive number less than or equal to 300 cm.")
            return
            
        # Update the state manager with form data (using combined full name)
        self.controller.state_manager.update_user_data(
            name=full_name,
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
        # Load content lazily when page is first shown
        self.load_content()
        
        # Prefill form with any existing data
        user_data = self.controller.state_manager.user_data
        
        if user_data["name"]:
            # Split the full name into parts for the separate fields
            name_parts = user_data["name"].split()
            if len(name_parts) >= 1:
                self.first_name_entry.delete(0, "end")
                self.first_name_entry.insert(0, name_parts[0])
            if len(name_parts) >= 3:  # First, Middle, Last
                self.middle_name_entry.delete(0, "end")
                self.middle_name_entry.insert(0, " ".join(name_parts[1:-1]))
                self.last_name_entry.delete(0, "end")
                self.last_name_entry.insert(0, name_parts[-1])
            elif len(name_parts) == 2:  # First, Last (no middle name)
                self.last_name_entry.delete(0, "end")
                self.last_name_entry.insert(0, name_parts[1])
            
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

    def _on_mousewheel(self, event):
        """Throttled scroll handler to prevent UI distortion"""
        import time
        
        current_time = time.time()
        
        # Cancel previous scroll job if it exists
        if self._scroll_job:
            self.after_cancel(self._scroll_job)
        
        # Only process scroll if enough time has passed (throttling)
        if current_time - self._last_scroll_time > 0.016:  # ~60fps limit
            self._last_scroll_time = current_time
            
            # Let the default scroll behavior handle it immediately
            return
        else:
            # Defer the scroll to prevent rapid updates
            self._scroll_job = self.after(16, lambda: self._deferred_scroll(event))
            return "break"  # Prevent default handling
            
    def _deferred_scroll(self, event):
        """Handle deferred scroll events"""
        try:
            # Manually scroll the content
            if event.delta:
                delta = -int(event.delta/120)  # Windows
            else:
                delta = -1 if event.num == 4 else 1  # Linux
                
            # Get current scroll position and update it smoothly
            try:
                current_pos = self.scrollable_frame._parent_canvas.canvasy(0)
                scroll_unit = 3  # Smaller scroll units for smoothness
                new_pos = current_pos + (delta * scroll_unit)
                
                # Apply the scroll
                bbox = self.scrollable_frame._parent_canvas.bbox("all")
                if bbox and bbox[3] > 0:
                    self.scrollable_frame._parent_canvas.yview_moveto(new_pos / bbox[3])
            except AttributeError:
                # Fallback to simple yview_scroll if _parent_canvas is not accessible
                self.scrollable_frame._parent_canvas.yview_scroll(delta * 3, "units")
                
        except Exception as e:
            print(f"Input page scroll error: {e}")
        finally:
            self._scroll_job = None

if __name__ == "__main__":
    # For standalone testing
    class DummyController:
        def show_frame(self, frame_name):
            print(f"Switching to frame: {frame_name}")
            
        class StateManager:
            def __init__(self):
                self.user_data = {
                    "name": "John Michael Doe",  # This will be split into first, middle, last
                    "gender": "male",
                    "age": "32",
                    "weight": "75",
                    "height": "178",
                    "goal": "Maintain Weight",
                    "activity_level": "Moderately active (moderate exercise/sports 3-5 days/week)",
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