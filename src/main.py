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
    from gui.history_page import HistoryPage
    from gui.history_detail_page import HistoryDetailPage
except Exception as e:
    print(f"ERROR IMPORTING MODULES: {str(e)}")
    traceback.print_exc()
    # Use messagebox to notify user in GUI context and exit without blocking on stdin
    try:
        import tkinter as _tk
        from tkinter import messagebox as _mb
        root = _tk.Tk()
        root.withdraw()
        _mb.showerror("Startup Error", f"An error occurred importing modules:\n{str(e)}")
        root.destroy()
    except Exception:
        # Fallback to console output
        pass
    sys.exit(1)

class DietRecommendationApp(ctk.CTk):
    """Main application class with redesigned UI and improved logic flow"""
    
    def __init__(self):
        try:
            super().__init__()
            
            # Initialize fullscreen state
            self._is_fullscreen = True
            
            # Set up app window properties
            self.title("Diet Recommendation System")
            
            # Get desktop size and set window to full desktop size
            self._setup_fullscreen_window()
            
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
            # Ensure Tkinter callback exceptions are handled by our handler
            try:
                # report_callback_exception is called for uncaught exceptions in Tk callbacks
                self.report_callback_exception = self._tk_exception_handler
            except Exception:
                pass
            
        except Exception as e:
            print(f"ERROR INITIALIZING APP: {str(e)}")
            traceback.print_exc()
            # Show GUI-friendly error and avoid blocking console input
            messagebox_error("Initialization Error", f"An error occurred during app initialization:\n{str(e)}")
    
    def _setup_fullscreen_window(self):
        """Setup window to take full desktop size"""
        try:
            # Get screen dimensions
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            
            print(f"Desktop size detected: {screen_width}x{screen_height}")
            
            # Set window size to full desktop size
            self.geometry(f"{screen_width}x{screen_height}+0+0")
            
            # Set minimum size for when user resizes
            self.minsize(800, 600)
            
            # Optional: Remove window decorations for true fullscreen feel
            # Uncomment the next line if you want no title bar/borders
            # self.overrideredirect(True)
            
            # Make window non-resizable to maintain fullscreen
            self.resizable(True, True)  # Keep resizable for flexibility
            
            # Bring window to front
            self.lift()
            self.focus_force()
            
            # Allow user to exit with Escape key (minimize to normal size)
            self.bind('<Escape>', self._toggle_fullscreen)
            self.bind('<F11>', self._toggle_fullscreen)  # Also allow F11 toggle
            
        except Exception as e:
            print(f"Error setting up fullscreen: {e}")
            # Fallback to a large window
            self.geometry("1200x800")
            self.minsize(800, 600)
            self._is_fullscreen = False
    
    def _toggle_fullscreen(self, event=None):
        """Toggle between fullscreen and windowed mode"""
        try:
            if self._is_fullscreen:
                # Exit fullscreen - set to windowed mode
                self.geometry("1200x800+100+50")
                self._is_fullscreen = False
                print("Switched to windowed mode")
            else:
                # Enter fullscreen
                screen_width = self.winfo_screenwidth()
                screen_height = self.winfo_screenheight()
                self.geometry(f"{screen_width}x{screen_height}+0+0")
                self._is_fullscreen = True
                print("Switched to fullscreen mode")
        except Exception as e:
            print(f"Error toggling fullscreen: {e}")
        
    def _tk_exception_handler(self, exc, val, tb):
        """Handle uncaught exceptions from Tkinter callbacks gracefully.

        Tkinter calls this for exceptions that occur in event handlers. By
        overriding it we can show a messagebox instead of letting the app
        crash or writing to an invalid console handle.
        """
        import traceback as _traceback
        _traceback.print_exception(exc, val, tb)
        try:
            messagebox_error("Application Error", f"An unexpected error occurred:\n{val}")
        except Exception:
            print("Error showing error dialog")
            
    def initialize_frames(self):
        """Initialize all application frames/pages"""
        try:
            # List of pages to initialize
            page_classes = {
                "LandingPage": LandingPage,
                "InputPage": InputPage,
                "CapturePage": CapturePage,
                "ProcessingPage": ProcessingPage,
                "DietPage": DietPage,
                "HistoryPage": HistoryPage,
                "HistoryDetailPage": HistoryDetailPage
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
        """Show the specified frame with smooth transition"""
        try:
            # Hide all frames first to prevent visual artifacts
            for frame_name, frame in self.frames.items():
                if frame_name != page_name:
                    frame.grid_remove()
            
            # Show the target frame
            target_frame = self.frames[page_name]
            target_frame.grid(row=0, column=0, sticky="nsew")
            target_frame.tkraise()
            
            # Force immediate UI update to prevent visual lag
            self.update_idletasks()
            
            # If the page has an on_show method, call it after the frame is visible
            if hasattr(target_frame, 'on_show') and callable(target_frame.on_show):
                # Use after_idle to ensure the frame switch happens first
                self.after_idle(target_frame.on_show)
                
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
        # Avoid blocking on console input in GUI mode — can cause WinError 6 if no valid stdin
        try:
            sys.exit(1)
        except Exception:
            pass