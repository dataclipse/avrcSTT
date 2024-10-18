import tkinter as tk
import ui_main
import splash_screen
import sv_ttk

if __name__ == "__main__":
    splash_root = tk.Tk()
    splash = splash_screen.SplashScreen(splash_root)
    
    # Show the splash screen
    splash_root.update()  # Update splash screen

    # Load the main application
    root = tk.Tk()
    root.withdraw() 
    app = ui_main.CustomWindow(root)
    sv_ttk.use_dark_theme(root)
    
    #app.load()  # Load the main application
    splash.close()  # Close splash screen
    root.deiconify()
    root.mainloop()  # Start the main application
    
    #root = tk.Tk()
    #app = CustomWindow(root)
    #root.mainloop()
