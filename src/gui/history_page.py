"""
History Page for the Diet Recommendation System.
Displays analysis history as a full page instead of modal dialog.
Uses the same design language as other pages in the system.
"""
import customtkinter as ctk
import os
import sys
from datetime import datetime
from PIL import Image, ImageTk

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.theme_manager import ThemeManager
from utils.database import DatabaseManager


class HistoryPage(ctk.CTkFrame):
    """Full page for viewing analysis history with modern UI design"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=ThemeManager.BG_COLOR)
        self.controller = controller
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        
        # Initialize basic layout immediately for fast load
        self._init_basic_layout()
        
        # Flag to track if content has been loaded
        self._content_loaded = False
        
    def _init_basic_layout(self):
        """Initialize basic layout structure quickly"""
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
    def load_content(self):
        """Load the actual content when page is shown"""
        if self._content_loaded:
            return
            
        # Load actual content immediately - no loading indicator
        self._init_content_layout()
        self._content_loaded = True
        
    def _init_content_layout(self):
        """Initialize the full content layout"""
        # Configure main grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Header section
        self._create_header()
        
        # Stats section
        self._create_stats_section()
        
        # History content section
        self._create_content_section()
        
        # Footer navigation
        self._create_footer()
        
    def _create_header(self):
        """Create page header with title and controls"""
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=32, pady=(24, 0))
        self.header_frame.grid_columnconfigure(1, weight=1)
        
        # Back button
        self.back_button = ctk.CTkButton(
            self.header_frame,
            text="← Back",
            font=ctk.CTkFont(size=14),
            width=80,
            height=32,
            corner_radius=16,
            fg_color="transparent",
            text_color=ThemeManager.GRAY_DARK,
            hover_color=ThemeManager.GRAY_LIGHT,
            command=self._go_back
        )
        self.back_button.grid(row=0, column=0, sticky="w")
        
        # Title and subtitle
        self.title_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.title_frame.grid(row=0, column=1, sticky="")
        
        self.title_label = ctk.CTkLabel(
            self.title_frame,
            text="Analysis History",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=ThemeManager.GRAY_DARK
        )
        self.title_label.grid(row=0, column=0)
        
        self.subtitle_label = ctk.CTkLabel(
            self.title_frame,
            text="View your past diet recommendations and analysis results",
            font=ctk.CTkFont(size=14),
            text_color=ThemeManager.GRAY_MEDIUM
        )
        self.subtitle_label.grid(row=1, column=0, pady=(4, 0))
        
        # Refresh button
        self.refresh_button = ctk.CTkButton(
            self.header_frame,
            text="🔄 Refresh",
            font=ctk.CTkFont(size=14),
            width=100,
            height=32,
            corner_radius=16,
            fg_color=ThemeManager.PRIMARY_COLOR,
            hover_color=ThemeManager.PRIMARY_HOVER,
            command=self._refresh_history
        )
        self.refresh_button.grid(row=0, column=2, sticky="e")
        
    def _create_stats_section(self):
        """Create statistics cards section"""
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.grid(row=1, column=0, sticky="ew", padx=32, pady=24)
        self.stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Total analyses card
        self.total_card = self._create_stats_card(
            self.stats_frame, 
            "📊 Total Analyses", 
            "0", 
            "Completed sessions"
        )
        self.total_card.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        
        # This week card  
        self.week_card = self._create_stats_card(
            self.stats_frame,
            "📅 This Week",
            "0",
            "Recent activity"
        )
        self.week_card.grid(row=0, column=1, sticky="ew", padx=8)
        
        # Latest analysis card
        self.latest_card = self._create_stats_card(
            self.stats_frame,
            "🕒 Latest Analysis", 
            "Never",
            "Most recent session"
        )
        self.latest_card.grid(row=0, column=2, sticky="ew", padx=(8, 0))
        
    def _create_stats_card(self, parent, title, value, subtitle):
        """Create individual statistics card"""
        card = ctk.CTkFrame(parent, corner_radius=16, fg_color="white", border_width=2, border_color=ThemeManager.GRAY_LIGHT)
        
        card.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=ThemeManager.GRAY_DARK
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 8))
        
        # Value
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=ThemeManager.PRIMARY_COLOR
        )
        value_label.grid(row=1, column=0, padx=20, pady=0)
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            card,
            text=subtitle,
            font=ctk.CTkFont(size=12),
            text_color=ThemeManager.GRAY_MEDIUM
        )
        subtitle_label.grid(row=2, column=0, padx=20, pady=(4, 20))
        
        # Store labels for updates
        card.value_label = value_label
        
        return card
        
    def _create_content_section(self):
        """Create scrollable content section for history items"""
        # Content header
        self.content_header = ctk.CTkFrame(self, fg_color="transparent")
        self.content_header.grid(row=2, column=0, sticky="ew", padx=32, pady=(0, 16))
        self.content_header.grid_columnconfigure(1, weight=1)
        
        self.content_title = ctk.CTkLabel(
            self.content_header,
            text="Recent Analyses",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=ThemeManager.GRAY_DARK
        )
        self.content_title.grid(row=0, column=0, sticky="w")
        
        # Filter/search options (placeholder for future enhancement)
        self.filter_frame = ctk.CTkFrame(self.content_header, fg_color="transparent")
        self.filter_frame.grid(row=0, column=1, sticky="e")
        
        # Scrollable history list
        self.history_scrollable = ctk.CTkScrollableFrame(
            self,
            fg_color=ThemeManager.SECONDARY_COLOR,
            corner_radius=0,  # Reduces rendering overhead
            border_width=0   # Reduces border redraw issues
        )
        self.history_scrollable.grid(row=3, column=0, sticky="nsew", padx=32, pady=(0, 24))
        self.history_scrollable.grid_columnconfigure(0, weight=1)
        
        # Add scroll throttling to prevent UI distortion
        self.history_scrollable.bind("<MouseWheel>", self._on_mousewheel)
        self.history_scrollable.bind("<Button-4>", self._on_mousewheel)  # Linux
        self.history_scrollable.bind("<Button-5>", self._on_mousewheel)  # Linux
        
        # Scroll throttling variables
        self._scroll_job = None
        self._last_scroll_time = 0
        
    def _create_footer(self):
        """Create footer with navigation buttons"""
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.grid(row=4, column=0, sticky="ew", padx=32, pady=(0, 24))
        self.footer_frame.grid_columnconfigure(1, weight=1)
        
        # Clear history button
        self.clear_button = ctk.CTkButton(
            self.footer_frame,
            text="🗑️ Clear History",
            font=ctk.CTkFont(size=14),
            width=140,
            height=44,
            corner_radius=22,
            fg_color=ThemeManager.WARNING_COLOR,
            hover_color="#DC2626",
            command=self._clear_history
        )
        self.clear_button.grid(row=0, column=0, sticky="w")
        
        # New analysis button
        self.new_analysis_button = ctk.CTkButton(
            self.footer_frame,
            text="+ New Analysis",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=140,
            height=44,
            corner_radius=22,
            fg_color=ThemeManager.SUCCESS_COLOR,
            hover_color=ThemeManager.PRIMARY_HOVER,
            command=self._new_analysis
        )
        self.new_analysis_button.grid(row=0, column=2, sticky="e")
        
    def _refresh_history(self):
        """Refresh the history display"""
        try:
            # Clear existing items
            for widget in self.history_scrollable.winfo_children():
                widget.destroy()
            
            # Get history from database
            history_data = self.db_manager.get_user_history(50)  # Get last 50 entries
            
            # Update statistics
            self._update_stats(history_data)
            
            if not history_data:
                # Show no history message
                self._show_no_history_message()
                return
            
            # Display history items
            for i, record in enumerate(history_data):
                self._create_history_item(record, i)
                
        except Exception as e:
            # Show error message
            print(f"Error in _refresh_history: {e}")
            import traceback
            traceback.print_exc()
            self._show_error_message(str(e))
            
    def _update_stats(self, history_data):
        """Update statistics cards with current data"""
        try:
            # Get database stats
            stats = self.db_manager.get_database_stats()
            
            # Update total analyses
            total_analyses = stats.get('analysis_sessions', 0)
            self.total_card.value_label.configure(text=str(total_analyses))
            
            # Update this week
            week_analyses = stats.get('sessions_last_7_days', 0)
            self.week_card.value_label.configure(text=str(week_analyses))
            
            # Update latest analysis date
            if history_data:
                latest_date = self._format_date(history_data[0].get('session_date', ''))
                # Shorten the date for the card
                if 'at' in latest_date:
                    latest_date = latest_date.split(' at')[0]  # Remove time part
                self.latest_card.value_label.configure(text=latest_date)
            else:
                self.latest_card.value_label.configure(text="Never")
                
        except Exception as e:
            print(f"Error updating stats: {e}")
            
    def _show_no_history_message(self):
        """Show message when no history is available"""
        no_history_frame = ctk.CTkFrame(
            self.history_scrollable, 
            fg_color="white", 
            corner_radius=16,
            height=200
        )
        no_history_frame.grid(row=0, column=0, sticky="ew", pady=40, padx=40)
        no_history_frame.grid_propagate(False)
        no_history_frame.grid_columnconfigure(0, weight=1)
        
        # Icon
        icon_label = ctk.CTkLabel(
            no_history_frame,
            text="📈",
            font=ctk.CTkFont(size=48)
        )
        icon_label.grid(row=0, column=0, pady=(40, 16))
        
        # Title
        title_label = ctk.CTkLabel(
            no_history_frame,
            text="No Analysis History",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=ThemeManager.GRAY_DARK
        )
        title_label.grid(row=1, column=0, pady=(0, 8))
        
        # Description
        desc_label = ctk.CTkLabel(
            no_history_frame,
            text="Start your first analysis to see your history here.\nYour results will be saved automatically.",
            font=ctk.CTkFont(size=14),
            text_color=ThemeManager.GRAY_MEDIUM,
            justify="center"
        )
        desc_label.grid(row=2, column=0, pady=(0, 40))
        
    def _show_error_message(self, error_text):
        """Show error message when data loading fails"""
        error_frame = ctk.CTkFrame(
            self.history_scrollable,
            fg_color="white",
            corner_radius=16,
            height=160
        )
        error_frame.grid(row=0, column=0, sticky="ew", pady=40, padx=40)
        error_frame.grid_propagate(False)
        error_frame.grid_columnconfigure(0, weight=1)
        
        # Error icon
        icon_label = ctk.CTkLabel(
            error_frame,
            text="❌",
            font=ctk.CTkFont(size=36)
        )
        icon_label.grid(row=0, column=0, pady=(30, 12))
        
        # Error message
        error_label = ctk.CTkLabel(
            error_frame,
            text=f"Error Loading History\n{error_text}",
            font=ctk.CTkFont(size=14),
            text_color=ThemeManager.WARNING_COLOR,
            justify="center"
        )
        error_label.grid(row=1, column=0, pady=(0, 30))
        
    def _create_history_item(self, record, index):
        """Create a single history item widget"""
        # Main item frame
        item_frame = ctk.CTkFrame(
            self.history_scrollable,
            fg_color="white",
            corner_radius=16,
            border_width=2,
            border_color=ThemeManager.GRAY_LIGHT,
            height=120
        )
        item_frame.grid(row=index, column=0, sticky="ew", pady=8, padx=20)
        item_frame.grid_propagate(False)
        item_frame.grid_columnconfigure(2, weight=1)
        
        # Status indicator
        status_color = {
            'completed': ThemeManager.SUCCESS_COLOR,
            'processing': ThemeManager.PRIMARY_COLOR,
            'failed': ThemeManager.WARNING_COLOR,
            'cancelled': ThemeManager.GRAY_MEDIUM
        }.get(record.get('status', 'unknown'), ThemeManager.GRAY_MEDIUM)
        
        status_indicator = ctk.CTkFrame(
            item_frame,
            width=6,
            height=100,
            corner_radius=3,
            fg_color=status_color
        )
        status_indicator.grid(row=0, column=0, sticky="ns", padx=(20, 16), pady=10)
        status_indicator.grid_propagate(False)
        
        # Profile section
        profile_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        profile_frame.grid(row=0, column=1, sticky="ns", pady=20, padx=(0, 16))
        
        # Profile picture placeholder
        profile_bg = ctk.CTkFrame(
            profile_frame,
            width=60,
            height=60,
            corner_radius=30,
            fg_color=ThemeManager.PRIMARY_COLOR
        )
        profile_bg.grid(row=0, column=0)
        profile_bg.grid_propagate(False)
        
        # Profile initials
        name = record.get('name', 'Unknown User')
        initials = ''.join([word[0].upper() for word in name.split() if word])[:2]
        
        profile_label = ctk.CTkLabel(
            profile_bg,
            text=initials,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        profile_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Content area
        content_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        content_frame.grid(row=0, column=2, sticky="nsew", padx=(0, 16), pady=16)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Header row
        name_label = ctk.CTkLabel(
            content_frame,
            text=name,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=ThemeManager.GRAY_DARK,
            anchor="w"
        )
        name_label.grid(row=0, column=0, sticky="w", columnspan=2)
        
        # Date
        date_str = self._format_date(record.get('session_date', ''))
        date_label = ctk.CTkLabel(
            content_frame,
            text=date_str,
            font=ctk.CTkFont(size=12),
            text_color=ThemeManager.GRAY_MEDIUM,
            anchor="e"
        )
        date_label.grid(row=0, column=2, sticky="e")
        
        # Details row
        age = record.get('age', 'N/A')
        gender = record.get('gender', 'N/A')
        goal = record.get('goal', 'N/A')
        
        details_text = f"Age: {age} • {gender.title()} • {goal}"
        details_label = ctk.CTkLabel(
            content_frame,
            text=details_text,
            font=ctk.CTkFont(size=13),
            text_color=ThemeManager.GRAY_MEDIUM,
            anchor="w"
        )
        details_label.grid(row=1, column=0, sticky="w", columnspan=3, pady=(4, 8))
        
        # Results row
        somatotype = record.get('somatotype_class', None)
        calories = record.get('calories', None)
        
        if somatotype and calories:
            results_text = f"🏃 {somatotype} • 🍽️ {calories} cal/day"
            results_color = ThemeManager.PRIMARY_COLOR
        else:
            results_text = "⏳ Analysis in progress..."
            results_color = ThemeManager.GRAY_MEDIUM
            
        results_label = ctk.CTkLabel(
            content_frame,
            text=results_text,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=results_color,
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
        status_label.grid(row=2, column=2, sticky="e")
        
        # Make item clickable
        self._make_clickable(item_frame, record)
        
    def _make_clickable(self, widget, record):
        """Make widget clickable to view details"""
        def on_click(event=None):
            # Only allow viewing completed analyses
            if record.get('status') == 'completed':
                self._view_details(record)
            else:
                # Show message for incomplete analyses
                pass
        
        def on_enter(event=None):
            if record.get('status') == 'completed':
                widget.configure(border_color=ThemeManager.PRIMARY_COLOR)
        
        def on_leave(event=None):
            widget.configure(border_color=ThemeManager.GRAY_LIGHT)
        
        # Bind events to all child widgets recursively
        def bind_recursive(w):
            w.bind("<Button-1>", on_click)
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            for child in w.winfo_children():
                bind_recursive(child)
        
        bind_recursive(widget)
        
    def _view_details(self, record):
        """Navigate to detailed view of history record"""
        try:
            # Store the record in controller for the detail page
            self.controller.current_history_record = record
            self.controller.show_frame("HistoryDetailPage")
        except Exception as e:
            print(f"Error in _view_details: {e}")
            import traceback
            traceback.print_exc()
        
    def _format_date(self, date_string):
        """Format date string for display"""
        if not date_string:
            return "Unknown Date"
        try:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.strftime("%b %d, %Y at %I:%M %p")
        except:
            return date_string
            
    def _clear_history(self):
        """Clear all history after confirmation"""
        # Create confirmation dialog
        confirm_dialog = ctk.CTkToplevel(self)
        confirm_dialog.title("Confirm Clear History")
        confirm_dialog.geometry("450x250")
        confirm_dialog.transient(self)
        confirm_dialog.grab_set()
        
        # Center the dialog
        confirm_dialog.grid_columnconfigure(0, weight=1)
        confirm_dialog.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(confirm_dialog, fg_color=ThemeManager.WARNING_COLOR, corner_radius=12)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))
        
        warning_label = ctk.CTkLabel(
            header_frame,
            text="⚠️ Clear All History",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        warning_label.pack(pady=16)
        
        # Message
        message_frame = ctk.CTkFrame(confirm_dialog, fg_color="transparent")
        message_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
        message_label = ctk.CTkLabel(
            message_frame,
            text="This will permanently delete all your analysis history.\n\nThis action cannot be undone.\nAre you sure you want to continue?",
            font=ctk.CTkFont(size=14),
            text_color=ThemeManager.GRAY_DARK,
            justify="center"
        )
        message_label.pack(expand=True)
        
        # Buttons
        buttons_frame = ctk.CTkFrame(confirm_dialog, fg_color="transparent")
        buttons_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        buttons_frame.grid_columnconfigure((0, 1), weight=1)
        
        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            border_width=2,
            border_color=ThemeManager.GRAY_LIGHT,
            text_color=ThemeManager.GRAY_DARK,
            hover_color=ThemeManager.GRAY_LIGHT,
            command=confirm_dialog.destroy
        )
        cancel_button.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        
        confirm_button = ctk.CTkButton(
            buttons_frame,
            text="Clear All History",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=ThemeManager.WARNING_COLOR,
            hover_color="#DC2626",
            command=lambda: self._perform_clear_history(confirm_dialog)
        )
        confirm_button.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        
    def _perform_clear_history(self, confirm_dialog):
        """Actually clear the history"""
        try:
            # TODO: Implement actual database clearing
            confirm_dialog.destroy()
            self._refresh_history()
        except Exception as e:
            print(f"Error clearing history: {e}")
            
    def _new_analysis(self):
        """Start new analysis"""
        self.controller.show_frame("InputPage")
        
    def _go_back(self):
        """Go back to landing page"""
        self.controller.show_frame("LandingPage")
        
    def on_show(self):
        """Called when page is shown"""
        # Load content lazily when page is first shown
        self.load_content()
        
        # Refresh history data
        if hasattr(self, '_refresh_history'):
            self._refresh_history()
    
    def _on_mousewheel(self, event):
        """Throttled scroll handler to prevent UI distortion"""
        import time
        
        current_time = time.time()
        
        # Cancel previous scroll job if it exists
        if self._scroll_job:
            self.after_cancel(self._scroll_job)
        
        # Only process scroll if enough time has passed (throttling)
        if current_time - self._last_scroll_time > 0.016:  # ~60fps limit
            self._last_scroll_time = current_time
            
            # Let the default scroll behavior handle it immediately
            return
        else:
            # Defer the scroll to prevent rapid updates
            self._scroll_job = self.after(16, lambda: self._deferred_scroll(event))
            return "break"  # Prevent default handling
            
    def _deferred_scroll(self, event):
        """Handle deferred scroll events"""
        try:
            # Manually scroll the content
            if event.delta:
                delta = -int(event.delta/120)  # Windows
            else:
                delta = -1 if event.num == 4 else 1  # Linux
                
            # Get current scroll position and update it smoothly
            try:
                current_pos = self.history_scrollable._parent_canvas.canvasy(0)
                scroll_unit = 3  # Smaller scroll units for smoothness
                new_pos = current_pos + (delta * scroll_unit)
                
                # Apply the scroll
                bbox = self.history_scrollable._parent_canvas.bbox("all")
                if bbox and bbox[3] > 0:
                    self.history_scrollable._parent_canvas.yview_moveto(new_pos / bbox[3])
            except AttributeError:
                # Fallback to simple yview_scroll if _parent_canvas is not accessible
                self.history_scrollable._parent_canvas.yview_scroll(delta * 3, "units")
                
        except Exception as e:
            print(f"History scroll error: {e}")
        finally:
            self._scroll_job = None


if __name__ == "__main__":
    # Test the history page
    class DummyController:
        def show_frame(self, frame_name):
            print(f"Navigating to: {frame_name}")
    
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.title("History Page Test")
    root.geometry("1200x800")
    
    ThemeManager.setup_theme()
    
    controller = DummyController()
    app = HistoryPage(root, controller)
    app.pack(fill="both", expand=True)
    app.on_show()
    
    root.mainloop()