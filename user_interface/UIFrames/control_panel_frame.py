import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog

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
        self.processImageButton = tk.Button(self,text="Process Image", command=lambda: self.ProcessPhoto)
        self.processImageButton.grid(row=1,column=1)
        pass

    def CPFtoggleframes(self): 
        #function for button to toggle camera/image frames 
        #will link back to the toggle in frontend display
        self.controller.toggleCamImg(0)

    def TakePhoto(self):
        #takes and processes photo
        #TODO link this with the other code to get the photo (will need camera set up before hand)
        if self.controller.StateVariable is None:
            self.controller.StateVariable = "Processing" #change state to processing (will be changed at end of processing)
            print("TakingPhoto")
            #add photo processing call here
        else:    
            print("Error: Already Processing Photo")
        pass

    def ProcessPhoto(self):
        BeeImage = filedialog.askopenfilename(title="Image To Process",filetypes=(("jpg files","*.jpg"),("jpeg files","*.jpeg"),("All Files","*.*")))
        #Call processing in here
        self.controller.frames["ImageFrame"].showImage(BeeImage)
        pass