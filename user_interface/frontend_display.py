'''
authors: Henry Shaw, John Pratt
date: 2025-09-28

notes:

'''
# library dependancies
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import time
# from PIL import Image, ImageTk
import cv2 as cv
import numpy as np
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
# files to import from




class FrontendDisplay:

    def __init__(self, counting_settings,default_counting_settings):
        #filepaths for both the normal and default counting setting JSON files
        self.counting_settings = counting_settings
        self.defualt_counting_settings = default_counting_settings

        #TODO change this number later to something better
        self._image_view_size = (800, 600)

        # create Tk gui instances
        self.root = tk.Tk()
        self.root.title("Bee Count Display")
        self.root.geometry(f"{self._image_view_size[0]}x{self._image_view_size[1]}")

        self.style = ttk.Style(self.root)
        self.style.theme_use("classic")

        
        self.top_frame = ttk.Frame(self.root)
        self.top_frame.grid_rowconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # starting frame which shows black background and pending input text:
        self.empty_frame = ttk.Frame(self.top_frame)
        self.empty_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.empty_label = ttk.Label(self.empty_frame, text="Awaiting input...")
        self.empty_label.pack(anchor=tk.CENTER, side=tk.TOP, fill=tk.Y, expand=True)
        # create a canvas to display images

        self.result_frame = ttk.Frame(self.top_frame)
        self.result_frame.grid(row=0, column=0, sticky="nsew")
        self.result_frame.grid_rowconfigure(0, weight=1)
        self.result_frame.grid_columnconfigure(0, weight=3)
        self.result_frame.grid_columnconfigure(1, weight=1)

        self.result_frame_left = ttk.Frame(self.result_frame)
        self.result_frame_left.grid(row=0, column=0, sticky="nsew")
        self.result_frame_right = ttk.Frame(self.result_frame)
        self.result_frame_right.grid(row=0, column=1, sticky="nsew")
        
        # create a matlab figure canvas for image display, hook up input events for navigation
        fig = Figure(figsize=(self._image_view_size[0] / 100, self._image_view_size[1] / 100), dpi=100)
        ax = fig.add_axes([0, 0, 1, 1])
        # ax_im = ax.imshow(np.zeros((1080, 1920, 3), dtype=np.uint8))
        # ax.axis("off")
        ax.imshow(np.zeros((1080, 1920), dtype=np.uint8))
        ax.axis("off")

        # ax.imshow(np.zeros((1, 1, 3), dtype=np.uint8))
        canvas = FigureCanvasTkAgg(fig, master=self.result_frame_left)
        canvas.draw()
        toolbar = NavigationToolbar2Tk(canvas, self.result_frame_left, pack_toolbar=False)
        toolbar.update()
        canvas.mpl_connect("key_press_event", key_press_handler)
        canvas.get_tk_widget().bind("<Configure>", lambda event: () )

        canvas.get_tk_widget().pack(side=tk.TOP, anchor=tk.NW, fill=tk.X)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        self.result_canvas = canvas
        self.result_toolbar = toolbar
        self.result_fig = fig
        self.result_ax = ax
        # self.result_ax_im = ax_im

        self.result_frame.tkraise()

        #Data Inputs:
        #Bee Count
        self.BeeCount = tk.IntVar()
        self.lbl1BeeCount = ttk.Label(self.result_frame_right, text = "Bee Count: ").grid(row=9,column=1,sticky="W")
        self.lblBeeCount = ttk.Label(self.result_frame_right, textvariable=self.BeeCount)
        self.lblBeeCount.grid(row=9,column=2,sticky="W")

        #Date Sampled
        self.lblDateSample = tk.Label(self.result_frame_right,text="Date Sampled: ").grid(row=0,column=1,sticky="W")
        self.entDateSample = tk.Entry(self.result_frame_right)
        self.entDateSample.grid(row=0,column=2)
        #Date Processed 
        self.lblDateProcess = tk.Label(self.result_frame_right,text="Date Processed: ").grid(row=1,column=1,sticky="W")
        self.entDateProcess = tk.Label(self.result_frame_right,text=time.strftime("%D",time.localtime()))
        self.entDateProcess.grid(row=1,column=2,sticky="W")
        #Hive number
        self.lblHiveNum = tk.Label(self.result_frame_right,text="Hive Number: ").grid(row=2,column=1,sticky="W")
        self.entHiveNum = tk.Entry(self.result_frame_right)
        self.entHiveNum.grid(row=2,column=2)
        #Shaker number
        self.lblShakerNum = tk.Label(self.result_frame_right,text="Shaker Number: ").grid(row=3,column=1,sticky="W")
        self.entShakerNum = tk.Entry(self.result_frame_right)
        self.entShakerNum.grid(row=3,column=2)
        #Mite Count
        self.MiteNum = tk.Label(self.result_frame_right,text="Number of Mites: ").grid(row=4,column=1,sticky="W")
        self.entMiteNum = tk.Entry(self.result_frame_right)
        self.entMiteNum.grid(row=4,column=2)
        #Initials
        self.lblInits = tk.Label(self.result_frame_right,text="Initials: ").grid(row=5,column=1,sticky="W")
        self.entInits = tk.Entry(self.result_frame_right)
        self.entInits.grid(row=5,column=2)
        #Diet
        self.lblDiet = tk.Label(self.result_frame_right,text="Diet: ").grid(row=6,column=1,sticky="W")
        self.entDiet = tk.Entry(self.result_frame_right)
        self.entDiet.grid(row=6,column=2)
        #APIX 1-2, COMP,NF (Make radio buttons later? or drop down menu?)
        self.lblACN = tk.Label(self.result_frame_right,text="APIX 1/2, COMP or NF: ").grid(row=7,column=1,sticky="W")
        self.entACN = tk.Entry(self.result_frame_right)
        self.entACN.grid(row=7,column=2)
        #notes
        self.lblnotes = tk.Label(self.result_frame_right,text="Additional Notes: ").grid(row=8,column=1,sticky="W")
        self.entnotes = tk.Entry(self.result_frame_right)
        self.entnotes.grid(row=8,column=2)

        #File Paths
        self.imgFilePath = tk.StringVar()
        self.SettingsFilePath = tk.StringVar()
        self.OpenedImage = None
        self.ExcelFilePath = None
        self.BeeData = None
        #self.ifCSV = bool #want to add .xlsx handling later

        #tk.Button(self.result_frame_right,text="Find Photo",command=self.getimg).grid(row=0,column=0,sticky="W")
       # tk.Button(self.result_frame_right,text="Process Photo",command=self.processimg).grid(row=1,column=0,sticky="W")
       # tk.Button(self.result_frame_right,text="Submit",command=self.submit).grid(row=2,column=0,sticky="W")
       # tk.Button(self.result_frame_right,text="Settings",command=self.editparam).grid(row=3,column=0,sticky="W")
       # tk.Button(self.result_frame_right,text="Exit",command=self.root.destroy).grid(row=4,column=0,sticky="W")
       # tk.Button(self.result_frame_right,text="Find CSV",command=self.findExcelFile).grid(row=5,column=0,sticky="W")

    #Menu Bar:
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        self.Filemenu = tk.Menu(self.menubar,tearoff=0)
        self.Editmenu = tk.Menu(self.menubar,tearoff=0)
        self.Helpmenu = tk.Menu(self.menubar,tearoff=0)
        
        self.menubar.add_cascade(label="File",menu=self.Filemenu)
        self.menubar.add_cascade(label="Edit",menu=self.Editmenu)
        self.menubar.add_cascade(label="Help",menu=self.Helpmenu)

        #File menubar
        self.Filemenu.add_command(label="New Excel/CSV File",command=lambda: self.FileMB_new_file())
        self.Filemenu.add_command(label="Open Excel/CSV File",command=lambda: self.findExcelFile())
        self.Filemenu.add_separator()
        self.Filemenu.add_command(label="Save File",command=lambda: self.FileMB_save_file())
        self.Filemenu.add_command(label="Save File As",command=lambda: self.FileMB_save_file_as())
        self.Filemenu.add_separator()
        self.Filemenu.add_command(label="Find Image", command=lambda: self.getimg())
        self.Filemenu.add_separator
        self.Filemenu.add_command(label="Exit",command=lambda: self.FileMB_exit_program())

        #Edit menubar
        self.Editmenu.add_command(label="Edit Parameters",command=lambda: self.OpenAlgSettingsWindow())

        #Help menubar
        self.Helpmenu.add_command(label="FAQ")



    #alg settings window
    def OpenAlgSettingsWindow(self):
        #TODO code this
        pass
        
    def FileMB_new_file(self):
        pass

    def FileMB_save_file(self):
        pass

    def FileMB_save_file_as(self):
        pass

    def FileMB_exit_program(self):
        #TODO add popup confirmation
        self.root.destroy()

    def HelpMB_FAQ(self):
        pass

    def findExcelFile(self):
        self.ExcelFilePath = filedialog.askopenfilename(title="CSV to process in",filetypes=(("csv files","*.csv"),("Excel Files","*.xlsx"),("All Files","*.*")))
        if self.ExcelFilePath is None:
            print("Error: Did Not Save Filepath")
        else:
            print("Saved Filepath")

    def getimg(self):
        self.imgFilePath = filedialog.askopenfilename(title="Image to be Processed",filetypes=(("jpg","*.jpg"),("png","*.png")))
        print(self.imgFilePath)
        self.OpenedImage = cv.imread(self.imgFilePath)
        # self._on_static_result(self.OpenedImage)
        self.show_img_in_viewer(self.OpenedImage)
