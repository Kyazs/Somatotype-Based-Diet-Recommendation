import customtkinter as ctk
from tkinter import messagebox

class LandingPage(ctk.CTkFrame):  # Change from CTk to CTkFrame
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Configure the frame
        self.grid_rowconfigure(0, weight=1)  # Center vertically
        self.grid_columnconfigure(0, weight=1)  # Center horizontally

        # Title Label
        self.title_label = ctk.CTkLabel(
            self, 
            text="Somatotype Based Diet Recommendation System", 
            font=("Arial", 24, "bold")
        )
        self.title_label.grid(row=0, column=0, pady=20)

        # Start Button
        self.start_button = ctk.CTkButton(
            self, 
            text="Start", 
            command=lambda: controller.show_frame("InputPage"),  # Navigate to InputPage
            width=200, 
            height=40, 
            font=("Arial", 14)
        )
        self.start_button.grid(row=1, column=0, pady=10)

        # About Button
        self.about_button = ctk.CTkButton(
            self, 
            text="About", 
            command=self.show_about, 
            width=200, 
            height=40, 
            font=("Arial", 14)
        )
        self.about_button.grid(row=2, column=0, pady=10)

        # Exit Button
        self.exit_button = ctk.CTkButton(
            self, 
            text="Exit", 
            command=self.exit_app, 
            width=200, 
            height=40, 
            font=("Arial", 14)
        )
        self.exit_button.grid(row=3, column=0, pady=10)

    def show_about(self):
        messagebox.showinfo(
            "About", 
            "Diet Recommendation System\nUsing Somatotype Analysis\nVersion 1.0"
        )

    def exit_app(self):
        self.controller.destroy()

if __name__ == "__main__":
    class DummyController:
        def show_frame(self, frame_name):
            print(f"Switching to frame: {frame_name}")

    controller = DummyController()
    app = LandingPage(None, controller)
    app.mainloop()