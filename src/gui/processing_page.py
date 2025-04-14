import customtkinter as ctk
import subprocess
import threading
import os
import sys
import time

# ---------------
# CONFIGURATION
# ---------------
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(PROJECT_DIR)

from src.utils.utils import CNN_DIR, VENV_DIR, CLASSIFIER_DIR, RECOMMENDER_DIR

class ProcessingPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Configure the frame
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Title
        self.title_label = ctk.CTkLabel(
            self, text="Processing Data", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, pady=(30, 10))

        # Status labels
        self.cnn_status_label = ctk.CTkLabel(
            self, text="CNN Status: Initializing...", 
            font=ctk.CTkFont(size=16)
        )
        self.cnn_status_label.grid(row=1, column=0, pady=10)

        self.classifier_status_label = ctk.CTkLabel(
            self, text="Classifier Status: Waiting...", 
            font=ctk.CTkFont(size=16)
        )
        self.classifier_status_label.grid(row=2, column=0, pady=10)

        self.recommender_status_label = ctk.CTkLabel(
            self, text="Recommender Status: Waiting...", 
            font=ctk.CTkFont(size=16)
        )
        self.recommender_status_label.grid(row=3, column=0, pady=10)

        # Back Button
        self.back_button = ctk.CTkButton(
            self, text="Back", 
            font=ctk.CTkFont(size=16),
            command=lambda: controller.show_frame("CapturePage"),
            width=120
        )
        self.back_button.grid(row=4, column=0, pady=(10, 30), padx=20, sticky="w")

    def on_show_frame(self):
        """This method will be called when the frame is shown"""
        # Start the processing automatically when the page is shown
        self.run_process_threaded()
    
    def run_process_threaded(self):
        # Reset status labels
        self.cnn_status_label.configure(text="CNN Status: Initializing...")
        self.classifier_status_label.configure(text="Classifier Status: Waiting...")
        self.recommender_status_label.configure(text="Recommender Status: Waiting...")
        
        thread = threading.Thread(target=self.run_cnn_model)
        thread.daemon = True
        thread.start()

    def run_cnn_model(self):
        self.cnn_status_label.configure(text="CNN Status: Processing...")
        try:
            # Activate the virtual environment and run the CNN script
            activate_script = os.path.join(VENV_DIR, "cnn_env", "Scripts", "activate")
            cnn_script = os.path.join(CNN_DIR, "photos2avatar.py")
            
            command = f'cmd.exe /c "{activate_script} && python {cnn_script}"'
            process = subprocess.Popen(
                command,
                cwd=CNN_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                shell=True
            )

            process.wait()  # Wait for the process to complete

            if process.returncode == 0:
                self.cnn_status_label.configure(text="CNN Status: ✅ Process Complete")
                self.run_classifier()
            else:
                self.cnn_status_label.configure(text="CNN Status: ❌ Error occurred")
        except Exception as e:
            self.cnn_status_label.configure(text=f"CNN Status: ❌ Unexpected Error")

    def run_classifier(self):
        self.classifier_status_label.configure(text="Classifier Status: Processing...")
        try:
            classifier_script = os.path.join(CLASSIFIER_DIR, "classifier.py")
            command = f'cmd.exe /c "python {classifier_script}"'
            process = subprocess.Popen(
                command,
                cwd=CLASSIFIER_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                shell=True
            )

            process.wait()  # Wait for the process to complete

            if process.returncode == 0:
                self.classifier_status_label.configure(text="Classifier Status: ✅ Process Complete")
                self.run_recommender()
            else:
                self.classifier_status_label.configure(text="Classifier Status: ❌ Error occurred")
        except Exception as e:
            self.classifier_status_label.configure(text=f"Classifier Status: ❌ Unexpected Error: {e}")

    def run_recommender(self):
        self.recommender_status_label.configure(text="Recommender Status: Processing...")
        try:
            recommender_script = os.path.join(RECOMMENDER_DIR, "recommender.py")
            command = f'cmd.exe /c "python {recommender_script}"'
            process = subprocess.Popen(
                command,
                cwd=RECOMMENDER_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                shell=True
            )

            process.wait()  # Wait for the process to complete

            if process.returncode == 0:
                self.recommender_status_label.configure(text="Recommender Status: ✅ Process Complete")
                # Wait for a moment so the user can see the success message
                time.sleep(1.5)
                # Navigate to the diet page
                self.controller.after(100, lambda: self.controller.show_frame("DietPage"))
            else:
                self.recommender_status_label.configure(text="Recommender Status: ❌ Error occurred")
        except Exception as e:
            self.recommender_status_label.configure(text=f"Recommender Status: ❌ Unexpected Error: {e}")


if __name__ == "__main__":
    class DummyController:
        def show_frame(self, frame_name):
            print(f"Switching to frame: {frame_name}")
        def after(self, ms, func):
            func()

    controller = DummyController()
    app = ctk.CTk()
    app.geometry("600x400")
    frame = ProcessingPage(app, controller)
    frame.pack(fill="both", expand=True)
    frame.on_show_frame()  # Simulate showing the frame
    app.mainloop()
