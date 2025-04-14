import customtkinter as ctk
import pandas as pd
import os
import sys
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# ---------------
# CONFIGURATION
# ---------------
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(PROJECT_DIR)

from src.utils.utils import OUTPUT_FILES_DIR


class DietPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        ctk.set_default_color_theme("dark-blue")
        
        # Configure the frame
        self.grid_rowconfigure(0, weight=0)  # Title row
        self.grid_rowconfigure(1, weight=1)  # Main content row
        self.grid_rowconfigure(2, weight=0)  # Button row
        self.grid_columnconfigure(0, weight=1)  # Center horizontally

        # Title Label
        self.title_label = ctk.CTkLabel(
            self, text="🍽️ Diet Recommendation", 
            font=ctk.CTkFont(size=32, weight="bold")
        )
        self.title_label.grid(row=0, column=0, pady=30)

        # Main Frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=1, column=0, padx=30, pady=(0, 20), sticky="nsew")

        # Configure grid weights for main_frame
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=3)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Left Frame for Pie Chart
        self.pie_frame = ctk.CTkFrame(self.main_frame, corner_radius=15)
        self.pie_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        # Right Frame for Suggested Foods
        self.food_frame = ctk.CTkFrame(self.main_frame, corner_radius=15)
        self.food_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Legend Frame below Pie Chart
        self.legend_frame = ctk.CTkFrame(self.main_frame, corner_radius=15)
        self.legend_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

        # Back to Home Button
        self.home_button = ctk.CTkButton(
            self, text="Back to Home", 
            font=ctk.CTkFont(size=16),
            command=lambda: controller.show_frame("LandingPage")
        )
        self.home_button.grid(row=2, column=0, pady=20)
        
        # Load data when this frame is shown for the first time
        self.data_loaded = False

    def on_show_frame(self):
        """Called when the frame is shown"""
        if not self.data_loaded:
            self.load_data()
            self.data_loaded = True

    def load_data(self):
        try:
            file_path = os.path.join(OUTPUT_FILES_DIR, "output_recommendation.csv")
            data = pd.read_csv(file_path)

            macronutrient_data = data.iloc[:4]
            suggested_foods = data.iloc[5:, 0].tolist()

            self.display_pie_chart(macronutrient_data)
            self.display_suggested_foods(suggested_foods)
            self.display_legend(macronutrient_data)

        except FileNotFoundError:
            self.display_error("Output file not found. Please complete the processing step first.")
        except Exception as e:
            self.display_error(str(e))

    def display_error(self, message):
        error_label = ctk.CTkLabel(
            self,
            text=f"⚠️ Error: {message}",
            font=ctk.CTkFont(size=16),
            text_color="red",
        )
        error_label.grid(row=1, column=0, pady=10)

    def display_pie_chart(self, macronutrient_data):
        labels = macronutrient_data["Macronutrient"]
        values = macronutrient_data["Value"]

        fig, ax = plt.subplots(figsize=(4, 4))
        ax.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            startangle=90,
            colors=plt.cm.Set2.colors,
            textprops={"fontsize": 10}
        )
        ax.axis("equal")

        canvas = FigureCanvasTkAgg(fig, master=self.pie_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        canvas.draw()

    def display_legend(self, macronutrient_data):
        legend_label = ctk.CTkLabel(
            self.legend_frame,
            text="Macronutrient Breakdown",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        legend_label.pack(pady=10)

        for _, row in macronutrient_data.iterrows():
            item_label = ctk.CTkLabel(
                self.legend_frame,
                text=f"{row['Macronutrient']}: {row['Value']}",
                font=ctk.CTkFont(size=16)
            )
            item_label.pack(anchor="w", padx=20)

    def display_suggested_foods(self, suggested_foods):
        food_label = ctk.CTkLabel(
            self.food_frame,
            text="Suggested Foods",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        food_label.pack(pady=10)

        food_box = ctk.CTkTextbox(
            self.food_frame,
            width=350,
            height=400,
            font=ctk.CTkFont(size=14),
            fg_color="#2e2e2e"
        )
        food_box.pack(fill="both", expand=True, padx=15, pady=10)

        for food in suggested_foods:
            food_box.insert("end", f"• {food}\n")
        food_box.configure(state="disabled")


if __name__ == "__main__":
    class DummyController:
        def show_frame(self, frame_name):
            print(f"Switching to frame: {frame_name}")

    controller = DummyController()
    app = ctk.CTk()
    app.geometry("800x600")
    frame = DietPage(app, controller)
    frame.pack(fill="both", expand=True)
    # Call on_show_frame to simulate showing the frame
    frame.on_show_frame()
    app.mainloop()