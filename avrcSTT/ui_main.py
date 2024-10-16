import tkinter as tk
from tkinter import ttk, scrolledtext
import sv_ttk
import pywinstyles, sys
from STTOSCWhisper import STTOSCWhisper

class CustomWindow():
    def __init__(self, root):
        self.root = root

        # Create the main application window
        self.root.title("avrcSTT")

        # Set window size
        self.root.geometry("1280x720")

        self.whisper_model = STTOSCWhisper(log_callback=self.update_log)

        # Create a text display (Text widget)
        self.text_display = scrolledtext.ScrolledText(root, wrap="word", height=15, width=60)
        self.text_display.pack(padx=10, pady=10, fill="both", expand=True)

        # Create a frame for the label, combobox, and buttons
        self.bottom_frame = ttk.Frame(root)
        self.bottom_frame.pack(pady=10, padx=10, fill="x")

        font_style = ('Roboto', 16)

        # Left-aligned label and combobox
        self.label = ttk.Label(self.bottom_frame, text="Status: Inactive", font=font_style)
        self.label.grid(row=0, column=0, padx=5, sticky="w")

        # Create a frame for the right-aligned buttons
        self.button_frame = ttk.Frame(self.bottom_frame)
        self.button_frame.grid(row=0, column=2, padx=5, sticky="e")

        # Right-aligned buttons
        self.start_button = ttk.Button(self.button_frame, text="Start STT", command=self.start_transcription)
        self.start_button.pack(side="left", padx=5)

        self.stop_button = ttk.Button(self.button_frame, text="Stop STT", command=self.stop_transcription)
        self.stop_button.pack(side="left", padx=5)

        # Configure the grid so that it expands properly
        self.bottom_frame.grid_columnconfigure(1, weight=1)  # Ensure column 1 (combo_box) expands

        sv_ttk.set_theme("dark")
        self.apply_theme_to_titlebar(root)

    def update_log(self, message):
        self.text_display.insert(tk.END, message + '\n')
        self.text_display.yview(tk.END)
        
    def start_transcription(self):
        self.whisper_model.start()
        self.label.config(text="Status: Active")

    def stop_transcription(self):
        self.whisper_model.stop()
        self.label.config(text="Status: Inactive")

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