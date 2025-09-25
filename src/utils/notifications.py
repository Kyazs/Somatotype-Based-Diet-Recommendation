"""
Toast notification system for the Diet Recommendation System.
Creates non-intrusive notifications that appear centered on the screen.
"""
import customtkinter as ctk
import threading
from utils.theme_manager import ThemeManager


class ToastNotification(ctk.CTkToplevel):
    """A toast notification that appears centered on the screen"""
    
    def __init__(self, parent, message, notification_type="info", duration=3000):
        super().__init__(parent)
        
        self.message = message
        self.notification_type = notification_type
        self.duration = duration
        
        # Configure window
        self.overrideredirect(True)  # Remove window decorations
        self.attributes('-topmost', True)  # Keep on top
        
        # Set size and position
        self.geometry("350x80")
        self._position_window()
        
        # Configure colors based on type
        self._configure_colors()
        
        # Create content
        self._create_content()
        
        # Auto-dismiss after duration
        self.after(self.duration, self.dismiss)
        
        # Start fade-in animation
        self._animate_in()
    
    def _position_window(self):
        """Position the notification in the center of the screen"""
        # Update to get current screen dimensions
        self.update_idletasks()
        
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculate center position
        window_width = 350
        window_height = 80
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    def _configure_colors(self):
        """Configure colors based on notification type"""
        if self.notification_type == "success":
            self.bg_color = ThemeManager.SUCCESS_COLOR
            self.text_color = "white"
            self.icon = "✓"
        elif self.notification_type == "error":
            self.bg_color = ThemeManager.DANGER_COLOR
            self.text_color = "white"
            self.icon = "✕"
        elif self.notification_type == "warning":
            self.bg_color = ThemeManager.WARNING_COLOR
            self.text_color = "white"
            self.icon = "⚠"
        else:  # info
            self.bg_color = ThemeManager.PRIMARY_COLOR
            self.text_color = "white"
            self.icon = "ℹ"
    
    def _create_content(self):
        """Create the notification content"""
        # Main container
        self.container = ctk.CTkFrame(
            self,
            fg_color=self.bg_color,
            corner_radius=12,
            border_width=0
        )
        self.container.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Content frame
        self.content_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=16, pady=12)
        self.content_frame.grid_columnconfigure(1, weight=1)
        
        # Icon
        self.icon_label = ctk.CTkLabel(
            self.content_frame,
            text=self.icon,
            font=ctk.CTkFont(size=20),
            text_color=self.text_color,
            width=30
        )
        self.icon_label.grid(row=0, column=0, padx=(0, 12), sticky="w")
        
        # Message
        self.message_label = ctk.CTkLabel(
            self.content_frame,
            text=self.message,
            font=ctk.CTkFont(size=14),
            text_color=self.text_color,
            justify="left",
            wraplength=250
        )
        self.message_label.grid(row=0, column=1, sticky="w")
        
        # Close button (small x)
        self.close_button = ctk.CTkButton(
            self.content_frame,
            text="×",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.text_color,
            fg_color="transparent",
            hover_color=("white", "gray70"),
            width=20,
            height=20,
            corner_radius=10,
            command=self.dismiss
        )
        self.close_button.grid(row=0, column=2, padx=(12, 0), sticky="e")
    
    def _animate_in(self):
        """Animate the notification sliding in"""
        self.attributes('-alpha', 0.0)
        self._fade_in(0.0)
    
    def _fade_in(self, alpha):
        """Gradually increase opacity"""
        if alpha < 1.0:
            self.attributes('-alpha', alpha)
            self.after(50, lambda: self._fade_in(alpha + 0.1))
        else:
            self.attributes('-alpha', 1.0)
    
    def dismiss(self):
        """Dismiss the notification with fade-out animation"""
        self._fade_out(1.0)
    
    def _fade_out(self, alpha):
        """Gradually decrease opacity"""
        if alpha > 0.0:
            self.attributes('-alpha', alpha)
            self.after(50, lambda: self._fade_out(alpha - 0.1))
        else:
            self.destroy()


class NotificationManager:
    """Manages toast notifications for the application"""
    
    @staticmethod
    def show_success(parent, message, duration=3000):
        """Show a success notification"""
        ToastNotification(parent, message, "success", duration)
    
    @staticmethod
    def show_error(parent, message, duration=4000):
        """Show an error notification"""
        ToastNotification(parent, message, "error", duration)
    
    @staticmethod
    def show_warning(parent, message, duration=3500):
        """Show a warning notification"""
        ToastNotification(parent, message, "warning", duration)
    
    @staticmethod
    def show_info(parent, message, duration=3000):
        """Show an info notification"""
        ToastNotification(parent, message, "info", duration)