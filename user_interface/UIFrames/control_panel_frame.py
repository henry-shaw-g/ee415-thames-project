import tkinter as tk
import tkinter.ttk as ttk

class ControlPanelFrame(tk.Frame):

    def __init__(self,parent,controller):
        tk.Frame.__init__(self, parent, highlightbackground="red", highlightthickness=5)
        self.controller = controller
        label = tk.Label(self, text="this is the Control Panel")
        label.grid(row=0,columnspan=2)
        #Variable for toggling Camera/Image Frames

        self.toggleButton = tk.Button(self,text="Switch to Camera / Image View", command=lambda: self.CPFtoggleframes())
        self.toggleButton.grid(row=1, column = 0)
        self.captureImageButton = tk.Button(self,text="Take Photo")
        self.captureImageButton.grid(row=1, column=1)
        pass

    def CPFtoggleframes(self): 
        #function for button to toggle camera/image frames 
        #will link back to the toggle in frontend display
        self.controller.toggleCamImg(0)

    def TakePhoto(self):
        #takes and processes photo
        #TODO link this with the other code to get the photo (will need camera set up before hand)
        print("TakingPhoto")
        pass
