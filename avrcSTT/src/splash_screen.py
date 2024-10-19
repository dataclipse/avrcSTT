import tkinter as tk
from tkinter import ttk
import sv_ttk

class SplashScreen:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        # Set size of the splash screen
        width = 300
        height = 120
        self.root.geometry(f"{width}x{height}")
        # Center the splash screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"+{x}+{y}")
        self.label = ttk.Label(root, text="Loading... Please Wait", font=("Roboto", 16))
        self.label.pack(expand=True)
        # Create a progress bar
        self.progress = ttk.Progressbar(root, orient="horizontal", length=250, mode="indeterminate")
        self.progress.pack(pady=10)
        self.progress.start()
        sv_ttk.use_dark_theme()

    def close(self):
        self.progress.stop()
        self.root.destroy()