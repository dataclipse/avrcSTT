import tkinter as tk
from tkinter import ttk
import sv_ttk
import pywinstyles, sys

class CustomWindow():
    def __init__(self, root):
        self.root = root

        # Create the main application window
        self.root.title("avrcSTT")

        # Set window size
        self.root.geometry("1280x720")

        # Create a text display (Text widget)
        self.text_display = tk.Text(root, wrap="word", height=15, width=60)
        self.text_display.pack(padx=10, pady=10, fill="both", expand=True)

        # Create a frame for the label, combobox, and buttons
        self.bottom_frame = ttk.Frame(root)
        self.bottom_frame.pack(pady=10, padx=10, fill="x")

        # Left-aligned label and combobox
        self.label = ttk.Label(self.bottom_frame, text="Select Transcribe Model:")
        self.label.grid(row=0, column=0, padx=5, sticky="w")

        self.combo_box = ttk.Combobox(self.bottom_frame, values=["OpenAI Whisper", "Google Voice Recognition"])
        self.combo_box.set("OpenAI Whisper")  # Set default value
        self.combo_box.grid(row=0, column=1, padx=5, sticky="w")

        # Create a frame for the right-aligned buttons
        self.button_frame = ttk.Frame(self.bottom_frame)
        self.button_frame.grid(row=0, column=2, padx=5, sticky="e")

        # Right-aligned buttons
        self.button1 = ttk.Button(self.button_frame, text="Start STT")
        self.button1.pack(side="left", padx=5)

        self.button2 = ttk.Button(self.button_frame, text="Stop STT")
        self.button2.pack(side="left", padx=5)

        # Configure the grid so that it expands properly
        self.bottom_frame.grid_columnconfigure(1, weight=1)  # Ensure column 1 (combo_box) expands

        sv_ttk.set_theme("dark")
        self.apply_theme_to_titlebar(root)
        
    def apply_theme_to_titlebar(self, root):
        version = sys.getwindowsversion()

        if version.major == 10 and version.build >= 22000:
            # Set the title bar color to the background color on Windows 11 for better appearance
            pywinstyles.change_header_color(root, "#1c1c1c" if sv_ttk.get_theme() == "dark" else "#fafafa")
        elif version.major == 10:
            pywinstyles.apply_style(root, "dark" if sv_ttk.get_theme() == "dark" else "normal")

            # A hacky way to update the title bar's color on Windows 10 (it doesn't update instantly like on Windows 11)
            root.wm_attributes("-alpha", 0.99)
            root.wm_attributes("-alpha", 1)