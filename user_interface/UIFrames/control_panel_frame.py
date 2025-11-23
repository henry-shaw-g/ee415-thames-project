import tkinter as tk
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

        self.processCameraShowBTN = tk.Button(self, text="Open Camera", command=lambda: self.controller.frames["CameraFrame"].showCameraFrame())
        self.processCameraShowBTN.grid(row=1,column=1)
        self.cameraToggle = True #true means camera is not on yet

        self.captureImageButton = tk.Button(self,text="Take Photo", command=lambda: self.TakePhoto())
        self.captureImageButton.grid(row=1, column=2)

        self.importImageButton = tk.Button(self,text="Import Photo", command=lambda: self.ImportImage())
        self.importImageButton.grid(row=1,column=3)

        self.processImageButton = tk.Button(self,text="Process Image", command=lambda: self.ProcessImage())
        self.processImageButton.grid(row=1,column=4)

        self.detectCameraButton = tk.Button(self,text="Detect Camera", command=lambda: self.detectCamera())
        self.detectCameraButton.grid(row=1,column=5)

    def CPFtoggleframes(self): 
        #function for button to toggle camera/image frames 
        #will link back to the toggle in frontend display
        self.controller.toggleCamImg(0)

    def TakePhoto(self):
        #takes and processes photo
        #TODO link this with the other code to get the photo (will need camera set up before hand)
        if self.controller.state.get() == self.controller.state.State.IMAGE_PROCESSING:
            print("Error: Currently Processing Photo")
            return

        if self.controller.state.get() != self.controller.state.State.IMAGE_PENDING:
            self.controller.state.reset()

        self.controller.StateVariable = "Processing" #change state to processing (will be changed at end of processing)
        print("Taking Photo pressed")
        #run function to get 4k image from camera
        image = self.controller.frames["CameraFrame"].TakePhotoFromCamera() 
        command = self.controller.state.load_image(image_data=image)
        if command != self.controller.state.OutputCommand.PROCEED:
            print("Error loading image:", self.controller.state.get_halt_reason())
            return

        self.controller.frames["ImageFrame"].show_image_from_data(image)

    def ImportImage(self):
        #Import Image
        # TODO: check state first
        path = filedialog.askopenfilename(title="Image To Process",filetypes=(("jpg files","*.jpg"),("png files","*.png"),("All Files","*.*")))

        command = self.controller.state.load_image(path=path)
        if command != self.controller.state.OutputCommand.PROCEED:
            print("Error loading image:", self.controller.state.get_halt_reason())
            return

        self.controller.frames["ImageFrame"].show_image(self.controller.state.get_loaded_image())

    def ProcessImage(self):
        if self.controller.state.get() != self.controller.state.State.IMAGE_LOADED:
            print("Not able to process image in current state.")
            return

        command = self.controller.state.ready_process_image()
        if command != self.controller.state.OutputCommand.PROCEED:
            print("Error preparing to process image:", self.controller.state.get_halt_reason())
            return

        # uh i think we should lock the UI here while processing

        command = self.controller.state.process_image()
        if command != self.controller.state.OutputCommand.PROCEED:
            print("Error processing image:", self.controller.state.get_halt_reason())
            return
        
        command = self.controller.state.show_results()
        if command != self.controller.state.OutputCommand.PROCEED:
            print("Error showing results:", self.state.get_halt_reason())
            return
        
        output = self.controller.state.get_algorithm_output()
        output.annotate_output_standard()
        image_handle = output.image_handle
        bee_count = output.bee_count
        self.controller.frames["ImageFrame"].show_image_from_data(image_handle.get_image(image_handle.type.OUTPUT))
        #Will update this to either show in frame w/out excel or frame with excel depending on logic (this way they can either use the excel connection or not, up to user)
        self.controller.showFrame("EntryFrame")
        self.controller.frames["EntryFrame"].updateBeeCount(bee_count)

    def detectCamera(self):
        self.controller.frames["CameraFrame"].detectCamera()