'''
authors: Henry Shaw, John Pratt
date: 2025-09-28

notes:

'''
# library dependancies
import tkinter as tk

# files to import from
from .UIFrames.camera_frame import CameraFrame
from .UIFrames.entry_frame import EntryFrame
from .UIFrames.image_frame import ImageFrame
from .UIFrames.control_panel_frame import ControlPanelFrame
from .UIFrames.excel_search_frame import ExcelSearchFrame
from .UIFrames.excel_before_frame import ExcelBeforeFrame
from .UIFrames.bee_count_frame import BeeCountOnlyFrame
#from .UIFrames.menu_bar import MenuBar

# import intermediate algorithm controller and counting algorithm
from counting import algorithm
from user_interface.frontend_state import FrontendState



class FrontendDisplay(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        #configure and define the containter frame here
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        #stretches to match screen dimensions
        self.windowWidth = self.winfo_screenwidth()
        self.windowHeight = self.winfo_screenheight()
        self.geometry(f"{self.windowWidth}x{self.windowHeight}")

        # Configure window styling
        self.title("WSU Bee Lab Counting Tool")
        self.iconbitmap("resources/wsu_bee_lab_icon.ico")

        #Then we define each frame here in an index of frames
        self.frames = {}
        self.frames["CameraFrame"] = CameraFrame(parent=container, controller=self)
        self.frames["EntryFrame"] = EntryFrame(parent=container, controller=self)
        self.frames["ImageFrame"] = ImageFrame(parent=container, controller=self)
        self.frames["ExcelSearchFrame"] = ExcelSearchFrame(parent=container, controller=self)
        self.frames["ExcelBeforeFrame"] = ExcelBeforeFrame(parent=container, controller=self)
        self.frames["ControlPanelFrame"] = ControlPanelFrame(parent=container, controller=self)
        self.frames["BeeOnlyFrame"] = BeeCountOnlyFrame(parent=container, controller = self)

        #After that we grid configure the frames here
        self.frames["CameraFrame"].grid(row=0,column=0,sticky="nsew")
        self.frames["ImageFrame"].grid(row=0,column=0,sticky="nsew")
        self.frames["ExcelSearchFrame"].grid(row=1,column=1,sticky="nsew")
        self.frames["ExcelBeforeFrame"].grid(row=0,rowspan=2,column=1, sticky="nsew")
        self.frames["ControlPanelFrame"].grid(row=1,column=0,sticky="nsew")
        self.frames["EntryFrame"].grid(row=0,column=1,sticky="nsew")
        self.frames["BeeOnlyFrame"].grid(row=0,rowspan=2,column=1, sticky="nsew")

        #by default we raise the camera frame over the image frame
        self.showFrame("CameraFrame")
        #we also raise the excel before frame over the data entries
        self.showFrame("ExcelBeforeFrame")
        #Add menu bar here
        #self.menubar = MenuBar(parent=container,controller=self)
        #container.config(menu=self.menubar)

        #Create variable for dataio here to communicate with csv filehandling

        #variable for toggling camera/
        self.toggleVar = 0

        #variable for keeping track of beeonly frame vs excel frame (starts as false = bee count only frame)
        self.isExcelFrameUsed = False

        #State Variable to prevent spam and overloading
        # self.StateVariable = None
        self.state = FrontendState(counting_module=algorithm, default_counting_settings=algorithm.get_settings(None))
        #None = good to process
        #Processing = processing, will halt all further attempts to process things

    def showFrame(self, frameLabel):
        #takes in a frame label name and pushes it to the top over every other frame
        frame = self.frames[frameLabel]
        frame.tkraise()

    def toggleCamImg(self,setToggle):
        #setToggle Key: 0 = normal toggle, go off of the toggle variable in class
        #1 = forced toggle to show the image frame
        #2 = forced toggle to show the camera frame
        match setToggle:
            case 0: #normal toggle using the button
                print("no set toggle")
                if self.toggleVar == 0:
                    self.showFrame("ImageFrame")
                    self.toggleVar = 1
                    print("toggling frame to show image")
                else:
                    self.showFrame("CameraFrame")
                    self.toggleVar = 0
                    print("toggling frame to show camera")
            
            case 1: #forced toggle to image frame
                self.showFrame("ImageFrame")
                self.toggleVar = 1
                print("toggling frame to show image")

            case 2: #forced toggle to show camera frame
                self.showFrame("CameraFrame")
                self.toggleVar = 0
                print("toggling frame to show camera")

            case _: #error handling: if an invalid number is given to the function run this
                print("error: invalid input into toggle camera")

    def updateExcelFilePath(self, updatedPath):
        self.frames["ExcelSearchFrame"].updateFilePath(updatedPath)
        self.frames["EntryFrame"].updateFilePath(updatedPath)

