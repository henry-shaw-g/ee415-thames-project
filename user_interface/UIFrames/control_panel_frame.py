import tkinter as tk
import tkinter.ttk as ttk

class ControlPanelFrame(tk.Frame):

    def __init__(self,parent,controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="this is the Control Panel")
        label.pack(side="top", fill="x", pady=10)
        #Variable for toggling Camera/Image Frames
        self.FrameToggle = 0

        self.toggleButton = tk.Button(text="Switch to Camera / Image View", command=lambda: self.CPFtoggleframes())
        self.toggleButton.pack()
        pass

    def CPFtoggleframes(self): 
        #function for button to toggle camera/image frames 
        #will link back to the toggle in frontend display
        if self.FrameToggle == 0:
            self.controller.showFrame("CameraFrame")
            self.FrameToggle = 1
            print("toggling frames")
        else:
            self.controller.showFrame("ImageFrame")
            self.FrameToggle = 0
            print("toggling frames")
        pass