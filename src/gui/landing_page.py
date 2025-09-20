"""
Landing Page for the Diet Recommendation System.
This is the first screen users see when launching the application.
"""
import os
from datetime import datetime
import customtkinter as ctk
from PIL import Image
from utils.theme_manager import ThemeManager, IMAGES_DIR
from utils.database import DatabaseManager

class LandingPage(ctk.CTkFrame):
    """Landing page with modern UI design"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=ThemeManager.BG_COLOR)
        self.controller = controller
        
        # Initialize basic layout immediately for fast load
        self._init_basic_layout()
        
        # Flag to track if content has been loaded
        self._content_loaded = False
        
    def _init_basic_layout(self):
        """Initialize basic layout structure quickly"""
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main content frame - create immediately but empty
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure((0, 1, 2, 3, 4), weight=0)
        self.content_frame.grid_rowconfigure(5, weight=1)
        
    def load_content(self):
        """Load the actual content when page is shown"""
        if self._content_loaded:
            return
            
        # Load actual content immediately - no loading indicator
        self._init_content_layout()
        self._content_loaded = True
        
    def _init_content_layout(self):
        """Initialize the full content layout"""
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
        self.button_card.grid_rowconfigure((0, 1, 2, 3), weight=0)
        
        # Start button with icon
        self.start_button = ThemeManager.create_primary_button(
            self.button_card,
            "Get Started",
            lambda: self.controller.show_frame("InputPage")
        )
        self.start_button.grid(row=0, column=0, padx=30, pady=(30, 15), sticky="ew")
        
        # View History button (new)
        self.history_button = ThemeManager.create_secondary_button(
            self.button_card,
            "View History",
            self.show_history
        )
        self.history_button.grid(row=1, column=0, padx=30, pady=(0, 15), sticky="ew")
        
        # About button
        self.about_button = ThemeManager.create_secondary_button(
            self.button_card,
            "About",
            self.show_about
        )
        self.about_button.grid(row=2, column=0, padx=30, pady=(0, 15), sticky="ew")
        
        # Exit button
        self.exit_button = ThemeManager.create_secondary_button(
            self.button_card,
            "Exit",
            self.exit_app
        )
        self.exit_button.grid(row=3, column=0, padx=30, pady=(0, 30), sticky="ew")
        
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

    def show_history(self):
        """Navigate to history page"""
        self.controller.show_frame("HistoryPage")

    def refresh_history(self, parent_frame):
        """Refresh the history display"""
        try:
            # Clear existing items
            for widget in parent_frame.winfo_children():
                widget.destroy()
            
            # Get history from database
            db_manager = DatabaseManager()
            history_data = db_manager.get_user_history(20)  # Get last 20 entries
            
            if not history_data:
                # Show no history message
                no_history_frame = ctk.CTkFrame(parent_frame, fg_color="white", corner_radius=8)
                no_history_frame.grid(row=0, column=0, sticky="ew", pady=20, padx=20)
                
                no_history_label = ctk.CTkLabel(
                    no_history_frame,
                    text="📈 No analysis history found\n\nComplete an analysis to see your history here.",
                    font=ThemeManager.get_label_font(),
                    text_color=ThemeManager.GRAY_MEDIUM,
                    justify="center"
                )
                no_history_label.pack(pady=40)
                return
            
            # Display history items
            for i, record in enumerate(history_data):
                self.create_history_item(parent_frame, record, i)
                
        except Exception as e:
            # Show error message
            error_frame = ctk.CTkFrame(parent_frame, fg_color="white", corner_radius=8)
            error_frame.grid(row=0, column=0, sticky="ew", pady=20, padx=20)
            
            error_label = ctk.CTkLabel(
                error_frame,
                text=f"❌ Error loading history: {str(e)}",
                font=ThemeManager.get_label_font(),
                text_color=ThemeManager.WARNING_COLOR
            )
            error_label.pack(pady=20)

    def create_history_item(self, parent_frame, record, index):
        """Create a single history item widget"""
        # Main item frame
        item_frame = ctk.CTkFrame(parent_frame, fg_color="white", corner_radius=8, border_width=1, border_color=ThemeManager.GRAY_LIGHT)
        item_frame.grid(row=index, column=0, sticky="ew", pady=8, padx=20)
        item_frame.grid_columnconfigure(1, weight=1)
        
        # Status indicator
        status_color = {
            'completed': ThemeManager.SUCCESS_COLOR,
            'processing': ThemeManager.PRIMARY_COLOR,
            'failed': ThemeManager.WARNING_COLOR,
            'cancelled': ThemeManager.GRAY_MEDIUM
        }.get(record.get('status', 'unknown'), ThemeManager.GRAY_MEDIUM)
        
        status_frame = ctk.CTkFrame(item_frame, width=4, height=80, corner_radius=2, fg_color=status_color)
        status_frame.grid(row=0, column=0, sticky="ns", padx=(16, 12), pady=16)
        status_frame.grid_propagate(False)
        
        # Content area
        content_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        content_frame.grid(row=0, column=1, sticky="ew", padx=(0, 16), pady=16)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Date and name
        date_str = self.format_date(record.get('session_date', ''))
        name_text = record.get('name', 'Unknown User')
        
        header_label = ctk.CTkLabel(
            content_frame,
            text=f"{name_text} • {date_str}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=ThemeManager.GRAY_DARK,
            anchor="w"
        )
        header_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 4))
        
        # User details
        age = record.get('age', 'N/A')
        gender = record.get('gender', 'N/A')
        goal = record.get('goal', 'N/A')
        
        details_label = ctk.CTkLabel(
            content_frame,
            text=f"Age: {age} • Gender: {gender.title()} • Goal: {goal}",
            font=ThemeManager.get_small_font(),
            text_color=ThemeManager.GRAY_MEDIUM,
            anchor="w"
        )
        details_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 8))
        
        # Somatotype and macros (if available)
        somatotype = record.get('somatotype_class', 'N/A')
        calories = record.get('calories', 'N/A')
        
        if somatotype != 'N/A' and calories != 'N/A':
            results_label = ctk.CTkLabel(
                content_frame,
                text=f"🏃 {somatotype} • 🍽️ {calories} calories",
                font=ThemeManager.get_small_font(),
                text_color=ThemeManager.PRIMARY_COLOR,
                anchor="w"
            )
            results_label.grid(row=2, column=0, sticky="w")
        
        # Status badge
        status_text = {
            'completed': '✅ Completed',
            'processing': '🔄 Processing',
            'failed': '❌ Failed',
            'cancelled': '⏹️ Cancelled'
        }.get(record.get('status', 'unknown'), '❓ Unknown')
        
        status_label = ctk.CTkLabel(
            content_frame,
            text=status_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=status_color
        )
        status_label.grid(row=2, column=1, sticky="e")
        
        # Click handler for detailed view
        item_frame.bind("<Button-1>", lambda e, r=record: self.show_detailed_history(r))
        for child in item_frame.winfo_children():
            child.bind("<Button-1>", lambda e, r=record: self.show_detailed_history(r))

    def show_detailed_history(self, record):
        """Show detailed view of a history record"""
        detail_dialog = ctk.CTkToplevel(self)
        detail_dialog.title("Analysis Details")
        detail_dialog.geometry("700x500")
        detail_dialog.transient(self)
        detail_dialog.grab_set()
        
        # Configure layout
        detail_dialog.grid_columnconfigure(0, weight=1)
        detail_dialog.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(detail_dialog, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=f"Analysis Details - {record.get('name', 'Unknown')}",
            font=ThemeManager.get_title_font(),
            text_color=ThemeManager.GRAY_DARK
        )
        title_label.pack()
        
        # Scrollable content
        content_scrollable = ctk.CTkScrollableFrame(
            detail_dialog, 
            fg_color=ThemeManager.SECONDARY_COLOR,
            corner_radius=0,
            border_width=0
        )
        content_scrollable.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        content_scrollable.grid_columnconfigure(0, weight=1)
        
        # Add scroll optimization for the popup dialog
        def _on_mousewheel_dialog(event):
            """Throttled scroll handler for dialog to prevent UI distortion"""
            import time
            
            if not hasattr(content_scrollable, '_scroll_job'):
                content_scrollable._scroll_job = None
                content_scrollable._last_scroll_time = 0
            
            current_time = time.time()
            
            # Cancel previous scroll job if it exists
            if content_scrollable._scroll_job:
                detail_dialog.after_cancel(content_scrollable._scroll_job)
            
            # Only process scroll if enough time has passed (throttling)
            if current_time - content_scrollable._last_scroll_time > 0.016:  # ~60fps limit
                content_scrollable._last_scroll_time = current_time
                return
            else:
                # Defer the scroll to prevent rapid updates
                content_scrollable._scroll_job = detail_dialog.after(16, lambda: _deferred_scroll_dialog(event))
                return "break"
                
        def _deferred_scroll_dialog(event):
            """Handle deferred scroll events for dialog"""
            try:
                if event.delta:
                    delta = -int(event.delta/120)  # Windows
                else:
                    delta = -1 if event.num == 4 else 1  # Linux
                    
                # Apply smooth scrolling
                try:
                    content_scrollable._parent_canvas.yview_scroll(delta * 3, "units")
                except AttributeError:
                    pass  # Ignore if _parent_canvas is not accessible
                    
            except Exception as e:
                print(f"Dialog scroll error: {e}")
            finally:
                content_scrollable._scroll_job = None
                
        # Bind mousewheel events
        content_scrollable.bind("<MouseWheel>", _on_mousewheel_dialog)
        content_scrollable.bind("<Button-4>", _on_mousewheel_dialog)  # Linux
        content_scrollable.bind("<Button-5>", _on_mousewheel_dialog)  # Linux
        
        # Display detailed information
        info_text = f"""
📅 Date: {self.format_date(record.get('session_date', ''))}
👤 Name: {record.get('name', 'N/A')}
🎂 Age: {record.get('age', 'N/A')}
⚧ Gender: {record.get('gender', 'N/A').title()}
🎯 Goal: {record.get('goal', 'N/A')}
📊 Status: {record.get('status', 'N/A').title()}

🏃 SOMATOTYPE ANALYSIS:
• Endomorphy: {record.get('endomorphy', 'N/A')}
• Mesomorphy: {record.get('mesomorphy', 'N/A')}
• Ectomorphy: {record.get('ectomorphy', 'N/A')}
• Classification: {record.get('somatotype_class', 'N/A')}

🍽️ NUTRITION PLAN:
• Daily Calories: {record.get('calories', 'N/A')}
• Protein: {record.get('protein_g', 'N/A')}g
• Carbohydrates: {record.get('carbs_g', 'N/A')}g
• Fats: {record.get('fat_g', 'N/A')}g
        """
        
        detail_label = ctk.CTkLabel(
            content_scrollable,
            text=info_text.strip(),
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.GRAY_DARK,
            justify="left",
            anchor="nw"
        )
        detail_label.pack(pady=20, padx=20, fill="x")
        
        # Close button
        close_button = ThemeManager.create_primary_button(
            detail_dialog,
            "Close",
            detail_dialog.destroy
        )
        close_button.grid(row=2, column=0, pady=20)

    def clear_history(self, content_frame):
        """Clear all history after confirmation"""
        confirm_dialog = ctk.CTkToplevel(self)
        confirm_dialog.title("Confirm Clear History")
        confirm_dialog.geometry("400x200")
        confirm_dialog.transient(self)
        confirm_dialog.grab_set()
        
        # Center the dialog
        confirm_dialog.grid_columnconfigure(0, weight=1)
        
        message_label = ctk.CTkLabel(
            confirm_dialog,
            text="⚠️ Are you sure you want to clear all history?\n\nThis action cannot be undone.",
            font=ThemeManager.get_label_font(),
            text_color=ThemeManager.GRAY_DARK,
            justify="center"
        )
        message_label.grid(row=0, column=0, pady=30)
        
        buttons_frame = ctk.CTkFrame(confirm_dialog, fg_color="transparent")
        buttons_frame.grid(row=1, column=0, pady=20)
        buttons_frame.grid_columnconfigure((0, 1), weight=1)
        
        cancel_button = ThemeManager.create_secondary_button(
            buttons_frame,
            "Cancel",
            confirm_dialog.destroy
        )
        cancel_button.grid(row=0, column=0, padx=10)
        
        confirm_button = ctk.CTkButton(
            buttons_frame,
            text="Clear All",
            font=ThemeManager.get_label_font(),
            fg_color=ThemeManager.WARNING_COLOR,
            hover_color="#DC2626",
            command=lambda: self.perform_clear_history(confirm_dialog, content_frame)
        )
        confirm_button.grid(row=0, column=1, padx=10)

    def perform_clear_history(self, confirm_dialog, content_frame):
        """Actually clear the history"""
        try:
            # This would implement clearing the database
            # For now, just close the dialog and refresh
            confirm_dialog.destroy()
            
            # TODO: Implement actual database clearing
            # db_manager = DatabaseManager()
            # db_manager.clear_all_history()
            
            self.refresh_history(content_frame)
            
        except Exception as e:
            print(f"Error clearing history: {e}")

    def format_date(self, date_string):
        """Format date string for display"""
        if not date_string:
            return "Unknown Date"
        try:
            # Parse the date string and format it nicely
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.strftime("%b %d, %Y at %I:%M %p")
        except:
            return date_string

    def exit_app(self):
        """Exit the application"""
        self.controller.destroy()
        
    def on_show(self):
        """Called when this page is shown"""
        # Load content lazily when page is first shown
        self.load_content()
        
        # Reset state when returning to landing page
        self.controller.state_manager.reset_state()

if __name__ == "__main__":
    class DummyController:
        def show_frame(self, frame_name):
            print(f"Switching to frame: {frame_name}")

    controller = DummyController()
    app = LandingPage(None, controller)
    app.mainloop()