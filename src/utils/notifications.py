"""
Toast notification system for the Diet Recommendation System.
Creates non-intrusive notifications that appear centered on the screen.
"""
import customtkinter as ctk
import threading
from utils.theme_manager import ThemeManager


class ToastNotification(ctk.CTkToplevel):
    """A toast notification that appears in the top-right corner of the screen"""
    
    def __init__(self, parent, message, notification_type="info", duration=3000):
        super().__init__(parent)
        
        self.message = message
        self.notification_type = notification_type
        self.duration = duration
        
        # Configure window
        self.overrideredirect(True)  # Remove window decorations
        self.attributes('-topmost', True)  # Keep on top
        
        # Calculate dynamic size based on message length
        self._calculate_size()
        
        # Set size and position
        self._position_window()
        
        # Configure colors based on type
        self._configure_colors()
        
        # Create content
        self._create_content()
        
        # Auto-dismiss after duration
        self.after(self.duration, self.dismiss)
        
        # Start fade-in animation
        self._animate_in()
    
    def _calculate_size(self):
        """Calculate dynamic size based on message length"""
        # More compact base dimensions
        base_width = 380  # Reduced for tighter layout
        base_height = 70   # Reduced height to minimize empty space
        
        # Calculate needed width based on message length
        message_chars = len(self.message)
        if message_chars > 40:
            # Moderate expansion for longer messages
            additional_width = min((message_chars - 40) * 3.5, 140)
            self.window_width = base_width + additional_width
        else:
            self.window_width = base_width
            
        # Calculate height for multi-line messages with tighter spacing
        estimated_lines = max(1, message_chars // 45)
        if estimated_lines > 1:
            self.window_height = base_height + ((estimated_lines - 1) * 22)  # Better line spacing
        else:
            self.window_height = base_height
    
    def _position_window(self):
        """Position the notification in the top-left corner of the screen"""
        # Update to get current screen dimensions
        self.update_idletasks()
        
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculate top-left position with margin
        margin = 10
        
        # TOP-LEFT positioning (simple and reliable)
        x = margin
        y = margin
        
        # Use simple geometry format
        self.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")
    
    def _adjust_position_for_stack(self, stack_offset):
        """Adjust position for notification stacking"""
        try:
            # Get current position
            margin = 10
            
            # TOP-LEFT positioning with stack offset
            x = margin
            y = margin + stack_offset
            
            # Simple geometry format
            self.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")
        except Exception as e:
            print(f"Error adjusting notification position: {e}")
    
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
        """Create the notification content with improved layout"""
        # Main container with minimal padding to reduce empty space
        self.container = ctk.CTkFrame(
            self,
            fg_color=self.bg_color,
            corner_radius=12,
            border_width=0
        )
        self.container.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Content frame with optimized padding
        self.content_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=14, pady=8)
        self.content_frame.grid_columnconfigure(1, weight=1)  # Message column expands
        
        # Icon - normal size and positioning
        self.icon_label = ctk.CTkLabel(
            self.content_frame,
            text=self.icon,
            font=ctk.CTkFont(size=20),  # Back to normal icon size
            text_color=self.text_color,
            width=24
        )
        self.icon_label.grid(row=0, column=0, padx=(0, 12), sticky="w")
        
        # Message - larger font with simplified width calculation
        # Simple calculation: total width minus icon area (36) and close button area (40) and padding (28)
        message_width = self.window_width - 104
        
        self.message_label = ctk.CTkLabel(
            self.content_frame,
            text=self.message,
            font=ctk.CTkFont(size=15),  # Larger, more readable font
            text_color=self.text_color,
            justify="left",
            wraplength=message_width,
            anchor="w"
        )
        self.message_label.grid(row=0, column=1, sticky="ew", padx=(0, 12))
        
        # Close button - compact but usable
        self.close_button = ctk.CTkButton(
            self.content_frame,
            text="×",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.text_color,
            fg_color="transparent",
            hover_color=("white", "gray70"),
            width=24,
            height=24,
            corner_radius=12,
            command=self.dismiss
        )
        self.close_button.grid(row=0, column=2, sticky="e")
    
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
        try:
            self._fade_out(1.0)
        except Exception as e:
            print(f"Error dismissing notification: {e}")
            # Fallback: destroy immediately
            try:
                self.destroy()
            except:
                pass
    
    def _fade_out(self, alpha):
        """Gradually decrease opacity"""
        try:
            if alpha > 0.0:
                self.attributes('-alpha', alpha)
                self.after(50, lambda: self._fade_out(alpha - 0.1))
            else:
                self.destroy()
        except Exception as e:
            print(f"Error in fade out animation: {e}")
            # Fallback: destroy immediately
            try:
                self.destroy()
            except:
                pass


class NotificationManager:
    """Manages toast notifications for the application"""
    
    _notification_stack = []  # Track active notifications for stacking
    
    @staticmethod
    def show_success(parent, message, duration=3000):
        """Show a success notification"""
        NotificationManager._show_notification(parent, message, "success", duration)
    
    @staticmethod
    def show_error(parent, message, duration=4000):
        """Show an error notification"""
        NotificationManager._show_notification(parent, message, "error", duration)
    
    @staticmethod
    def show_warning(parent, message, duration=3500):
        """Show a warning notification"""
        NotificationManager._show_notification(parent, message, "warning", duration)
    
    @staticmethod
    def show_info(parent, message, duration=3000):
        """Show an info notification"""
        NotificationManager._show_notification(parent, message, "info", duration)
    
    @staticmethod
    def _show_notification(parent, message, notification_type, duration):
        """Create and position notification with stacking support"""
        try:
            notification = ToastNotification(parent, message, notification_type, duration)
            
            # Calculate stacking position with tighter spacing for compact notifications
            stack_offset = len(NotificationManager._notification_stack) * 85  # Reduced from 110px
            notification._adjust_position_for_stack(stack_offset)
            
            # Add to stack
            NotificationManager._notification_stack.append(notification)
            
            # Remove from stack when dismissed
            def on_dismiss():
                if notification in NotificationManager._notification_stack:
                    NotificationManager._notification_stack.remove(notification)
                    # Reposition remaining notifications
                    NotificationManager._reposition_stack()
            
            notification.bind('<Destroy>', lambda e: on_dismiss())
            
        except Exception as e:
            print(f"Error showing notification: {e}")
    
    @staticmethod
    def _reposition_stack():
        """Reposition remaining notifications in the stack"""
        for i, notification in enumerate(NotificationManager._notification_stack):
            stack_offset = i * 85  # Match the tighter spacing
            notification._adjust_position_for_stack(stack_offset)