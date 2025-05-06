"""
Main application for Diet Recommendation System.
Integrates all pages with improved UI design and logic flow.
"""
import os
import sys
import customtkinter as ctk
import traceback

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Import theme and state managers
    from utils.theme_manager import ThemeManager
    from utils.state_manager import StateManager

    # Import all pages
    from gui.landing_page import LandingPage
    from gui.input_page import InputPage
    from gui.capture_page import CapturePage
    from gui.processing_page import ProcessingPage
    from gui.diet_page import DietPage
except Exception as e:
    print(f"ERROR IMPORTING MODULES: {str(e)}")
    traceback.print_exc()
    input("Press Enter to exit...")
    sys.exit(1)

class DietRecommendationApp(ctk.CTk):
    """Main application class with redesigned UI and improved logic flow"""
    
    def __init__(self):
        try:
            super().__init__()
            
            # Set up app window properties
            self.title("Diet Recommendation System")
            self.geometry("900x700")
            self.minsize(800, 600)
            
            print("Setting up theme...")
            # Apply theme settings
            ThemeManager.setup_theme()
            
            print("Initializing state manager...")
            # Initialize state manager
            self.state_manager = StateManager()
            
            # Configure the window layout
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0, weight=1)
            
            print("Creating container frame...")
            # Create a container frame for all pages
            self.container = ctk.CTkFrame(self)
            self.container.grid(row=0, column=0, sticky="nsew")
            self.container.grid_columnconfigure(0, weight=1)
            self.container.grid_rowconfigure(0, weight=1)
            
            # Initialize all pages
            self.frames = {}
            print("Initializing frames...")
            self.initialize_frames()
            
            print("Showing landing page...")
            # Show landing page
            self.show_frame("LandingPage")
            print("Application setup complete")
            
        except Exception as e:
            print(f"ERROR INITIALIZING APP: {str(e)}")
            traceback.print_exc()
            messagebox_error("Initialization Error", f"An error occurred during app initialization:\n{str(e)}")
        
    def initialize_frames(self):
        """Initialize all application frames/pages"""
        try:
            # List of pages to initialize
            page_classes = {
                "LandingPage": LandingPage,
                "InputPage": InputPage,
                "CapturePage": CapturePage,
                "ProcessingPage": ProcessingPage,
                "DietPage": DietPage
            }
            
            # Create each page and add to frames dictionary
            for page_name, page_class in page_classes.items():
                print(f"Creating frame: {page_name}")
                frame = page_class(self.container, self)
                self.frames[page_name] = frame
                frame.grid(row=0, column=0, sticky="nsew")
                
        except Exception as e:
            print(f"ERROR INITIALIZING FRAMES: {str(e)}")
            traceback.print_exc()
            messagebox_error("Frame Initialization Error", f"An error occurred while initializing {page_name}:\n{str(e)}")
            raise
            
    def show_frame(self, page_name):
        """Show the specified frame"""
        try:
            frame = self.frames[page_name]
            frame.tkraise()
            
            # If the page has an on_show method, call it
            if hasattr(frame, 'on_show') and callable(frame.on_show):
                frame.on_show()
                
        except Exception as e:
            print(f"ERROR SHOWING FRAME {page_name}: {str(e)}")
            traceback.print_exc()
            messagebox_error("Navigation Error", f"An error occurred while showing {page_name}:\n{str(e)}")
            
    def reset_application(self):
        """Reset the application state and return to landing page"""
        self.state_manager.reset_state()
        self.show_frame("LandingPage")

def messagebox_error(title, message):
    """Create a simple error messagebox"""
    try:
        # Use tkinter's messagebox
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        messagebox.showerror(title, message)
        root.destroy()
    except:
        # Fallback to console output if messagebox fails
        print(f"\nERROR - {title}:")
        print(message)

if __name__ == "__main__":
    try:
        print("Starting Diet Recommendation System...")
        app = DietRecommendationApp()
        app.mainloop()
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        traceback.print_exc()
        messagebox_error("Application Error", f"A critical error has occurred:\n{str(e)}")
        input("Press Enter to exit...")