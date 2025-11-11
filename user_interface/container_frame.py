import tkinter as tk

class ContainerFrame(tk.Frame):
        def __init__(self, frames):
            self.frames = frames
            self.pack(side="top", fill="both", expand=True)
            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure(0, weight=1)

        def show(self, name):
            frame = self.frames[name]
            self.tkraise(frame)