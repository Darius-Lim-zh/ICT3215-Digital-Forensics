import tkinter as tk
class ToolTip:
    """Tooltip class to display tooltips for widgets."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        """Show the tooltip."""
        if self.tooltip_window is not None:
            return  # Tooltip is already visible
        x = self.widget.winfo_rootx() + 20  # Offset for the tooltip
        y = self.widget.winfo_rooty() + 20
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)  # Remove window decorations
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        # Set a maximum width for the tooltip window
        max_width = 300  # Adjust this width as necessary
        label = tk.Label(self.tooltip_window, text=self.text, background="lightyellow",
                         relief="solid", borderwidth=1, wraplength=max_width)  # Added wraplength
        label.pack(ipadx=1)