# main.py
import os
import sys
import subprocess
from tkinter import messagebox

from utils.utils import VENV_DIR

import customtkinter as ctk

from gui.landing_page import LandingPage
from gui.input_page import InputPage


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Diet Recommendation System")
        self.geometry("800x600")
        self.frames = {}

        # Configure grid weights for the main container
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Initialize frames
        for F in (LandingPage, InputPage):
            frame_container = ctk.CTkFrame(self)
            frame_container.grid(row=0, column=0, sticky="nsew") 
            frame_container.grid_remove()

            # Configure grid weights for the frame container
            frame_container.grid_rowconfigure(0, weight=1)
            frame_container.grid_columnconfigure(0, weight=1)

            frame = F(frame_container, self)  # Pass the container as the parent
            self.frames[F.__name__] = frame_container
            frame.pack(fill="both", expand=True)

        self.show_frame("LandingPage")

    def show_frame(self, frame_name):
        # Hide all frames
        for frame in self.frames.values():
            frame.grid_remove()

        # Show the requested frame
        frame = self.frames[frame_name]
        frame.grid()

def main():
    try:
        # Activate the virtual environment
        capture_venv = os.path.join(VENV_DIR, "capture_env", "Scripts", "activate")
        subprocess.run(f"{capture_venv}", shell=True, check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"An error occurred while activating the virtual environment: {e}")
        return  # Exit the function if the subprocess fails
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")
        return  # Exit the function if an unexpected error occurs
    # Start the application
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()