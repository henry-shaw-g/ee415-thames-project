'''
authors: Henry Shaw
date: 2025-04-05

notes:
This module is for the demo. This will handle non-interactive gui of algorithm
output. TUI and worker logic should interface with this.
To use, the entry point needs to start the frontend object and pass its 
worker / TUI code, which will be ran in a separate thread. The frontend will then be able to call the TUI methods to update the display.
'''

import tkinter as tk
import threading, time

class FrontendDisplay:

    def __init__(self):
        self.main = None

    def start(self):
        # Create the main window
        self.root = tk.Tk()
        self.root.title("Bee Count Display")
        
        # Create a label to display the count
        self.label = tk.Label(self.root, text="Bee Count: 0", font=("Helvetica", 24))
        self.label.pack(pady=20)
        
        # Start program through its 'main' entry point.
        thread = threading.Thread(target=self.main)
        thread.daemon = True # is not necessary but might be safer
        thread.start()

        # Start the Tkinter main loop
        self.root.mainloop()

if __name__ == "__main__":
    def test_thread():
        while True:
            print("does printing work?")
            time.sleep(0.5)

    threading.Thread(target=test_thread).start()