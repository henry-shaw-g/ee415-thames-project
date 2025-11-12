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
        self.processCameraShowBTN = tk.Button(self, text="Open Camera", command=lambda: self.controller.frames["CameraFrame"].showCameraFrame())
        self.processCameraShowBTN.grid(row=1,column=1)
        self.cameraToggle = True #true means camera is not on yet

        self.importImageButton = tk.Button(self,text="Import Photo", command=lambda: self.on_import_photo_clicked())
        self.importImageButton.grid(row=1,column=3)

        self.processImageButton = tk.Button(self,text="Process Image", command=lambda: self.on_process_clicked())
        self.processImageButton.grid(row=2,column=0)

    def CPFtoggleframes(self): 
        #function for button to toggle camera/image frames 
        #will link back to the toggle in frontend display
        self.controller.toggleCamImg(0)

    def TakePhoto(self):
        #takes and processes photo
        #TODO link this with the other code to get the photo (will need camera set up before hand)
        if self.controller.StateVariable is None:
            self.controller.StateVariable = "Processing" #change state to processing (will be changed at end of processing)
            print("Taking Photo")
            #add photo processing call here
            #LOOK INTO FFMPEG PYTHON IMPORTER FOR FULL IMAGE
        else:    
            print("Error: Already Processing Photo")
        pass


    def on_import_photo_clicked(self):
        self.controller.import_image()

    def on_process_clicked(self):
        self.controller.process_image()

    # def ProcessPhoto(self):
    #     BeeImage = filedialog.askopenfilename(title="Image To Process",filetypes=(("jpg files","*.jpg"),("jpeg files","*.jpeg"),("All Files","*.*")))
    #     #Call processing in here
    #     self.controller.frames["ImageFrame"].showImage(BeeImage)
    #     pass