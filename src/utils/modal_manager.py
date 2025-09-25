"""
Modal utilities for consistent modal window behavior across the application.
Provides standardized modal creation, centering, and styling.
"""
import customtkinter as ctk
from utils.theme_manager import ThemeManager


class ModalManager:
    """Utility class for creating and managing modal windows with consistent behavior"""
    
    @staticmethod
    def create_modal(parent, title, width=500, height=600, resizable=False):
        """
        Create a standardized modal window with proper centering and styling
        
        Args:
            parent: Parent window
            title: Modal window title
            width: Modal width (default: 500)
            height: Modal height (default: 600)
            resizable: Whether the modal should be resizable (default: False)
            
        Returns:
            CTkToplevel: Configured modal window
        """
        modal = ctk.CTkToplevel(parent)
        modal.title(title)
        modal.geometry(f"{width}x{height}")
        modal.resizable(resizable, resizable)
        
        # Set modal properties
        modal.transient(parent)
        modal.lift()
        modal.focus_set()
        
        # Center the modal
        ModalManager._center_window(modal, width, height)
        
        # Grab focus after a short delay to ensure proper modal behavior
        modal.after(100, lambda: modal.grab_set() if modal.winfo_exists() else None)
        
        # Configure theme-consistent background
        try:
            modal.configure(fg_color=ThemeManager.get_bg_color())
        except AttributeError:
            # Fallback to default background if method doesn't exist
            modal.configure(fg_color=ThemeManager.BG_COLOR)
        
        return modal
    
    @staticmethod
    def _center_window(window, width, height):
        """
        Center a window on the screen
        
        Args:
            window: Window to center
            width: Window width
            height: Window height
        """
        window.update_idletasks()
        
        # Get screen dimensions
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        # Calculate position
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # Ensure window doesn't go off-screen
        x = max(0, x)
        y = max(0, y)
        
        window.geometry(f"{width}x{height}+{x}+{y}")
    
    @staticmethod
    def create_modal_content_frame(modal):
        """
        Create a standardized content frame for modal content
        
        Args:
            modal: Modal window to add content frame to
            
        Returns:
            CTkFrame: Content frame ready for content
        """
        # Configure main grid
        modal.grid_columnconfigure(0, weight=1)
        modal.grid_rowconfigure(0, weight=1)
        
        # Create main content frame
        content_frame = ctk.CTkFrame(
            modal,
            fg_color=ThemeManager.get_card_fg_color(),
            corner_radius=15,
            border_width=2,
            border_color=ThemeManager.PRIMARY_COLOR + "20"  # Semi-transparent border
        )
        content_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        
        return content_frame
    
    @staticmethod
    def create_scrollable_content_frame(modal, height=400):
        """
        Create a scrollable content frame for modal content
        
        Args:
            modal: Modal window to add scrollable frame to
            height: Height of the scrollable area
            
        Returns:
            CTkScrollableFrame: Scrollable frame ready for content
        """
        # Configure main grid
        modal.grid_columnconfigure(0, weight=1)
        modal.grid_rowconfigure(0, weight=1)
        modal.grid_rowconfigure(1, weight=0)
        
        # Create scrollable content frame
        content_frame = ctk.CTkScrollableFrame(
            modal,
            fg_color="transparent",
            corner_radius=0,
            height=height
        )
        content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        content_frame.grid_columnconfigure(0, weight=1)
        
        return content_frame
    
    @staticmethod
    def create_modal_close_button(modal, text="Close", command=None):
        """
        Create a standardized close button for modals
        
        Args:
            modal: Modal window to add close button to
            text: Button text (default: "Close")
            command: Custom close command (default: modal.destroy)
            
        Returns:
            CTkButton: Close button
        """
        if command is None:
            command = modal.destroy
        
        close_button = ctk.CTkButton(
            modal,
            text=text,
            font=ThemeManager.get_label_font(),
            command=command,
            width=120,
            height=40,
            fg_color=ThemeManager.PRIMARY_COLOR,
            hover_color=ThemeManager.HOVER_COLOR,
            corner_radius=8
        )
        close_button.grid(row=1, column=0, pady=(10, 20))
        
        return close_button
    
    @staticmethod
    def create_modal_title(parent, title, icon="", row=0):
        """
        Create a standardized title for modal content
        
        Args:
            parent: Parent frame
            title: Title text
            icon: Optional emoji icon
            row: Grid row position
            
        Returns:
            CTkLabel: Title label
        """
        title_text = f"{icon} {title}".strip()
        title_label = ctk.CTkLabel(
            parent,
            text=title_text,
            font=ThemeManager.get_title_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        title_label.grid(row=row, column=0, pady=(20, 15), padx=20)
        
        return title_label
    
    @staticmethod
    def create_info_section(parent, title, content, row, icon="", wraplength=450):
        """
        Create a standardized information section
        
        Args:
            parent: Parent frame
            title: Section title
            content: Section content (string or list)
            row: Grid row position
            icon: Optional emoji icon
            wraplength: Text wrapping width
            
        Returns:
            tuple: (title_label, content_label)
        """
        # Title with icon
        title_text = f"{icon} {title}".strip() if icon else title
        title_label = ctk.CTkLabel(
            parent,
            text=title_text,
            font=ThemeManager.get_subtitle_font(),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        title_label.grid(row=row, column=0, pady=(15, 5), sticky="w", padx=20)
        
        # Content
        if isinstance(content, list):
            content_text = ", ".join([str(item).title() for item in content if item])
        else:
            content_text = str(content) if content else "Not available"
        
        content_label = ctk.CTkLabel(
            parent,
            text=content_text,
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.GRAY_DARK,
            wraplength=wraplength,
            anchor="w",
            justify="left"
        )
        content_label.grid(row=row, column=0, pady=(25, 0), sticky="ew", padx=(30, 20))
        
        return title_label, content_label