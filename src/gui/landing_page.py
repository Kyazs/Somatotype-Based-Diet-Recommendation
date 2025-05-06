"""
Landing Page for the Diet Recommendation System.
This is the first screen users see when launching the application.
"""
import os
import customtkinter as ctk
from PIL import Image
from utils.theme_manager import ThemeManager, IMAGES_DIR

class LandingPage(ctk.CTkFrame):
    """Landing page with modern UI design"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=ThemeManager.BG_COLOR)
        self.controller = controller
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main content frame to center all elements
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure((0, 1, 2, 3, 4), weight=0)  # Header and buttons rows
        self.content_frame.grid_rowconfigure(5, weight=1)  # Bottom spacing
        
        # Try to load logo image
        self.logo_image = None
        logo_path = os.path.join(IMAGES_DIR, "app_logo.png")
        if os.path.exists(logo_path):
            self.logo_image = ctk.CTkImage(
                light_image=Image.open(logo_path),
                dark_image=Image.open(logo_path),
                size=(200, 200)
            )
            
            self.logo_label = ctk.CTkLabel(self.content_frame, image=self.logo_image, text="")
            self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
            
        # Header
        self.title_label = ctk.CTkLabel(
            self.content_frame,
            text="Somatotype Analysis",
            font=ThemeManager.get_title_font()
        )
        self.title_label.grid(row=1, column=0, padx=20, pady=(10, 0))
        
        self.subtitle_label = ctk.CTkLabel(
            self.content_frame,
            text="Personalized Diet Recommendations",
            font=ThemeManager.get_subtitle_font(),
            text_color=ThemeManager.GRAY_DARK
        )
        self.subtitle_label.grid(row=2, column=0, padx=20, pady=(5, 30))
        
        # Create card frame for buttons
        self.button_card = ThemeManager.create_card_frame(self.content_frame)
        self.button_card.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.button_card.grid_columnconfigure(0, weight=1)
        self.button_card.grid_rowconfigure((0, 1, 2), weight=0)
        
        # Start button with icon
        self.start_button = ThemeManager.create_primary_button(
            self.button_card,
            "Get Started",
            lambda: self.controller.show_frame("InputPage")
        )
        self.start_button.grid(row=0, column=0, padx=30, pady=(30, 15), sticky="ew")
        
        # About button
        self.about_button = ThemeManager.create_secondary_button(
            self.button_card,
            "About",
            self.show_about
        )
        self.about_button.grid(row=1, column=0, padx=30, pady=(0, 15), sticky="ew")
        
        # Exit button
        self.exit_button = ThemeManager.create_secondary_button(
            self.button_card,
            "Exit",
            self.exit_app
        )
        self.exit_button.grid(row=2, column=0, padx=30, pady=(0, 30), sticky="ew")
        
        # Footer text
        self.footer_text = ctk.CTkLabel(
            self.content_frame,
            text="This system uses computer vision to analyze your body type\nand provide personalized diet recommendations.",
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.GRAY_MEDIUM
        )
        self.footer_text.grid(row=4, column=0, padx=20, pady=(20, 0))
        
    def show_about(self):
        """Show about dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("About")
        dialog.geometry("500x400")
        dialog.transient(self)  # Make dialog modal
        dialog.grab_set()
        
        # Configure dialog layout
        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_rowconfigure(0, weight=1)
        
        # Create frame for content
        frame = ThemeManager.create_card_frame(dialog)
        frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            frame,
            text="Diet Recommendation System",
            font=ThemeManager.get_subtitle_font()
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Version
        version_label = ctk.CTkLabel(
            frame,
            text="Version 1.0",
            font=ThemeManager.get_label_font()
        )
        version_label.grid(row=1, column=0, padx=20, pady=(0, 20))
        
        # Description
        description_text = (
            "This application uses Deep Learning and Computer Vision techniques to analyze "
            "your body's somatotype (body type) and provide personalized diet recommendations "
            "based on your specific body composition and goals.\n\n"
            "The system captures front and side images, processes them through a CNN model "
            "to extract key measurements, and then classifies your body type to generate tailored "
            "nutritional advice."
        )
        description_label = ctk.CTkLabel(
            frame,
            text=description_text,
            font=ThemeManager.get_small_font(),
            wraplength=400,
            justify="left"
        )
        description_label.grid(row=2, column=0, padx=20, pady=10)
        
        # How it works section
        how_title = ctk.CTkLabel(
            frame,
            text="How it works",
            font=ThemeManager.get_label_font(),
            anchor="w"
        )
        how_title.grid(row=3, column=0, padx=20, pady=(20, 5), sticky="w")
        
        steps_text = (
            "1. Input your personal details\n"
            "2. Capture front and side images\n"
            "3. AI analyzes your body measurements\n"
            "4. System classifies your somatotype\n"
            "5. Receive personalized diet recommendations"
        )
        steps_label = ctk.CTkLabel(
            frame,
            text=steps_text,
            font=ThemeManager.get_small_font(),
            justify="left",
            anchor="w"
        )
        steps_label.grid(row=4, column=0, padx=20, pady=5, sticky="w")
        
        # Close button
        close_button = ThemeManager.create_primary_button(
            frame,
            "Close",
            dialog.destroy
        )
        close_button.grid(row=5, column=0, padx=20, pady=20)

    def exit_app(self):
        """Exit the application"""
        self.controller.destroy()
        
    def on_show(self):
        """Called when this page is shown"""
        # Reset state when returning to landing page
        self.controller.state_manager.reset_state()

if __name__ == "__main__":
    class DummyController:
        def show_frame(self, frame_name):
            print(f"Switching to frame: {frame_name}")

    controller = DummyController()
    app = LandingPage(None, controller)
    app.mainloop()