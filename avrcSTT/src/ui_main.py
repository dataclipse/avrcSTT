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

        font_style_label = ('Roboto', 16)
        font_style_textbox = ('Roboto', 12)

        self.whisper_model = STTOSCWhisper(log_callback=self.update_log)

        # Create a text display (Text widget)
        self.text_display = scrolledtext.ScrolledText(root, wrap="word", height=15, width=60, font=font_style_textbox)
        self.text_display.pack(padx=10, pady=10, fill="both", expand=True)
        self.text_display.config(state=tk.DISABLED)

        # Create a frame for the label, combobox, and buttons
        self.bottom_frame = ttk.Frame(root)
        self.bottom_frame.pack(pady=10, padx=10, fill="x")

        # Left-aligned label and combobox
        self.label = ttk.Label(self.bottom_frame, text="Status: Inactive", font=font_style_label)
        self.label.grid(row=0, column=0, padx=5, sticky="w")

        # Create a frame for the right-aligned buttons
        self.button_frame = ttk.Frame(self.bottom_frame)
        self.button_frame.grid(row=0, column=2, padx=5, sticky="e")

        # Right-aligned buttons
        self.start_button = ttk.Button(self.button_frame, text="Start STT", command=self.start_transcription)
        self.start_button.pack(side="left", padx=5)
        self.start_button.config(state=tk.NORMAL)

        self.stop_button = ttk.Button(self.button_frame, text="Stop STT", command=self.stop_transcription)
        self.stop_button.pack(side="left", padx=5)
        self.stop_button.config(state=tk.DISABLED)

        # Configure the grid so that it expands properly
        self.bottom_frame.grid_columnconfigure(1, weight=1)  # Ensure column 1 (combo_box) expands

        sv_ttk.use_dark_theme()
        self.apply_theme_to_titlebar(root)

    def update_log(self, message):
        self.text_display.config(state=tk.NORMAL)
        self.text_display.insert(tk.END, message + '\n')
        self.text_display.yview(tk.END)
        self.text_display.config(state=tk.DISABLED)
        
    def start_transcription(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.whisper_model.start()
        self.label.config(text="Status: Active")
        

    def stop_transcription(self):
        self.stop_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)
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