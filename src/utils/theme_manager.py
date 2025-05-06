"""
Theme manager for the application.
Provides consistent styling across all pages.
"""
import os
import customtkinter as ctk
from PIL import Image
import platform

# Base directory for assets
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

# Create images directory if it doesn't exist
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
os.makedirs(IMAGES_DIR, exist_ok=True)

class ThemeManager:
    # Color palette
    PRIMARY_COLOR = "#3b82f6"  # Blue 600
    PRIMARY_HOVER = "#2563eb"  # Blue 700
    PRIMARY_COLOR_HOVER = "#2563eb"  # Same as PRIMARY_HOVER for backwards compatibility
    SECONDARY_COLOR = "#f8fafc"  # Gray 50
    SUCCESS_COLOR = "#10b981"  # Green 500
    WARNING_COLOR = "#f59e0b"  # Yellow 500
    DANGER_COLOR = "#ef4444"  # Red 500
    GRAY_LIGHT = "#e5e7eb"  # Gray 200
    GRAY_MEDIUM = "#9ca3af"  # Gray 400
    GRAY_DARK = "#4b5563"  # Gray 600
    BG_COLOR = "#f3f4f6"  # Gray 100
    
    # Choose default font based on platform
    if platform.system() == "Windows":
        FONT_FAMILY = "Segoe UI"
    elif platform.system() == "Darwin":  # macOS
        FONT_FAMILY = "SF Pro"
    else:  # Linux and others
        FONT_FAMILY = "Helvetica"
    
    # Font sizes
    FONT_SIZE_SMALL = 12
    FONT_SIZE_MEDIUM = 14
    FONT_SIZE_LARGE = 18
    FONT_SIZE_XL = 24
    FONT_SIZE_XXL = 32
    
    @classmethod
    def setup_theme(cls):
        """Set up the global theme settings for CustomTkinter"""
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
    
    @classmethod
    def get_title_font(cls):
        """Returns font for page titles"""
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=cls.FONT_SIZE_XL, weight="bold")
    
    @classmethod
    def get_subtitle_font(cls):
        """Returns font for subtitles"""
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=cls.FONT_SIZE_LARGE, weight="bold")
    
    @classmethod
    def get_button_font(cls):
        """Returns font for buttons"""
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=cls.FONT_SIZE_MEDIUM, weight="bold")
    
    @classmethod
    def get_label_font(cls):
        """Returns font for regular labels"""
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=cls.FONT_SIZE_MEDIUM)
    
    @classmethod
    def get_small_font(cls):
        """Returns font for small text"""
        return ctk.CTkFont(family=cls.FONT_FAMILY, size=cls.FONT_SIZE_SMALL)
    
    @classmethod
    def create_card_frame(cls, parent):
        """Create a card-like frame with rounded corners and shadow effect"""
        card = ctk.CTkFrame(
            parent,
            fg_color=cls.SECONDARY_COLOR,
            corner_radius=10,
            border_width=1,
            border_color=cls.GRAY_LIGHT
        )
        return card
    
    @classmethod
    def create_primary_button(cls, parent, text, command):
        """Create a styled primary button"""
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            font=cls.get_button_font(),
            fg_color=cls.PRIMARY_COLOR,
            hover_color=cls.PRIMARY_HOVER,
            corner_radius=8,
            height=40
        )
    
    @classmethod
    def create_secondary_button(cls, parent, text, command):
        """Create a styled secondary button"""
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            font=cls.get_button_font(),
            fg_color="transparent",
            text_color=cls.PRIMARY_COLOR,
            hover_color=cls.GRAY_LIGHT,
            corner_radius=8,
            border_width=1,
            border_color=cls.PRIMARY_COLOR,
            height=40
        )
    
    @classmethod
    def create_label(cls, parent, text, bold=False):
        """Create a styled label"""
        return ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(
                family=cls.FONT_FAMILY, 
                size=cls.FONT_SIZE_MEDIUM,
                weight="bold" if bold else "normal"
            )
        )

    @classmethod
    def create_entry(cls, parent, placeholder_text=""):
        """Create a styled entry field"""
        return ctk.CTkEntry(
            parent,
            placeholder_text=placeholder_text,
            height=40,
            corner_radius=8,
            border_width=1,
            border_color=cls.GRAY_LIGHT
        )
    
    @classmethod
    def create_dropdown(cls, parent, values):
        """Create a styled dropdown menu"""
        return ctk.CTkOptionMenu(
            parent,
            values=values,
            height=40,
            corner_radius=8,
            dropdown_fg_color=cls.SECONDARY_COLOR,
            dropdown_text_color=cls.GRAY_DARK,
            dropdown_hover_color=cls.GRAY_LIGHT,
            fg_color=cls.PRIMARY_COLOR,
            button_color=cls.PRIMARY_HOVER,
            button_hover_color=cls.PRIMARY_HOVER,
            text_color="#ffffff",
            font=cls.get_label_font()
        )
    
    @classmethod
    def get_card_fg_color(cls):
        """Returns the foreground color for card elements"""
        return cls.SECONDARY_COLOR
        
    @classmethod
    def load_image(cls, image_path, size=(20, 20)):
        """Load an image and resize it for use in the UI"""
        try:
            return ctk.CTkImage(Image.open(image_path), size=size)
        except Exception as e:
            print(f"Error loading image {image_path}: {str(e)}")
            return None