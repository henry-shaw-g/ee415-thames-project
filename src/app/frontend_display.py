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
import tkinter.ttk as ttk
from tkinter import filedialog
import threading, time
# from PIL import Image, ImageTk
import cv2 as cv
import numpy as np
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure

import queue
from queue import Queue

from data_io import DataIO

QUEUE_CHECK_PERIOD = 100 # ms

class FrontendDisplay:

    def __init__(self):
        self.main = None
        self._q = Queue()
        self._livecam_q = Queue(maxsize=1)
        self._img_ptr_readonly = None

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
        ax_im = ax.imshow(np.zeros((1080, 1920, 3), dtype=np.uint8))
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
        self.result_ax_im = ax_im

        self.result_frame.tkraise()

        #Data Inputs:
        #Bee Count
        self.BeeCount = tk.IntVar()
        self.lbl1BeeCount = ttk.Label(self.result_frame_right, text = "Bee Count: ").grid(row=9,column=1,sticky="W")
        self.lblBeeCount = ttk.Label(self.result_frame_right, textvariable=self.BeeCount)
        self.lblBeeCount.grid(row=9,column=2)

        #Date Sampled
        self.lblDateSample = tk.Label(self.result_frame_right,text="Date Sampled: ").grid(row=0,column=1,sticky="W")
        self.entDateSample = tk.Entry(self.result_frame_right)
        self.entDateSample.grid(row=0,column=2)
        #Date Processed (todo: get date from time)
        self.lblDateProcess = tk.Label(self.result_frame_right,text="Date Processed: ").grid(row=1,column=1,sticky="W")
        self.entDateProcess = tk.Entry(self.result_frame_right)
        self.entDateProcess.grid(row=1,column=2)
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
        #self.ifCSV = bool #want to add .xlsx handling later

        tk.Button(self.result_frame_right,text="Find Photo",command=self.getimg).grid(row=0,column=0,sticky="W")
        tk.Button(self.result_frame_right,text="Process Photo",command=self.processimg).grid(row=1,column=0,sticky="W")
        tk.Button(self.result_frame_right,text="Submit",command=self.submit).grid(row=2,column=0,sticky="W")
        tk.Button(self.result_frame_right,text="Settings",command=self.editparam).grid(row=3,column=0,sticky="W")
        tk.Button(self.result_frame_right,text="Exit",command=self.root.destroy).grid(row=4,column=0,sticky="W")
        tk.Button(self.result_frame_right,text="Find CSV",command=self.findExcelFile).grid(row=5,column=0,sticky="W")
        


    def submit(self):
        #Variable Pass in Order: mite_num,date_sample,date_process,hive_num,shaker_num,inits,diet,acn,notes,csvfilepath,imgfilepath,settingsfilepath
        self.BeeData = DataIO(self.MiteNum,self.entDateSample,self.entDateProcess,self.entHiveNum,self.entShakerNum,self.entInits,self.entDiet
                              ,self.entACN,self.entnotes,self.ExcelFilePath,self.imgFilePath,self.SettingsFilePath)
        print("submitting data")
        self.BeeData._record_results_to_excel()

    #Function of "settings" button that updates algorithm settings based on provided text file
    def editparam(self):
        print("editing parameters")
        self.SettingsFilePath = filedialog.askopenfilename(title="Text file for changing values",filetypes=(("text files","*.txt"),("all file types","*.*")))
        print(self.SettingsFilePath)


    #Function of "get photo button". Returns an image filepath, opened image object and displays said image
    def getimg(self):
        self.imgFilePath = filedialog.askopenfilename(title="Image to be Processed",filetypes=(("jpg","*.jpg"),("png","*.png")))
        print(self.imgFilePath)
        self.OpenedImage = cv.imread(self.imgFilePath)
        self._on_static_result(self.OpenedImage)

    #Function of "process photo" button. Starts algorithm to process image
    # use either image opened image
    #returns self.BeeCount
    def processimg(self):
       # if self.OpenedImage != None: #makes sure that image has been opened before running alg.
        print("processing image")
        #image processing alg here (bee count number here for now, update later)
        self.BeeCount.set(350)

    #Function returns excel file
    def findExcelFile(self):
        self.ExcelFilePath = filedialog.askopenfilename(title="CSV to process in",filetypes=(("csv files","*.csv"),("Excel Files","*.xlsx"),("All Files","*.*")))
        if self.ExcelFilePath is None:
            print("Error: Did Not Save Filepath")
        else:
            print("Saved Filepath")
 
    

        


    def start(self):
        # Start program through its 'main' entry point.
        thread = threading.Thread(target=self.main, args=(self,))
        thread.daemon = True # is not necessary but might be safer

        self.root.update()
        # Start the queue loop to communicate with TUI & working logic
        self.root.after(QUEUE_CHECK_PERIOD, self._queue_loop)

        # startup
        thread.start()
        self.root.mainloop()

    def _queue_loop(self):
        try:
            msg = self._livecam_q.get_nowait()
            kind, *data = msg
            if kind == "livecamera":
                self._on_live_camera_result(*data)
        except queue.Empty:
            pass
        except Exception as e:
            print("Error in frontend_display live cam queue loop.")
            raise

        try:
            msg = self._q.get_nowait()
            kind, *data = msg
            if kind == "empty":
                self._on_empty()
            elif kind == "static_result":
                self._on_static_result(*data)
        
        except queue.Empty:
            # end of queue
            pass
        except Exception as e:
            print("Error in frontend_display queue loop.")
            raise

        self.root.after(QUEUE_CHECK_PERIOD, self._queue_loop)
    
    def push_empty(self):
        self._q.put(("empty",))

    '''
    Send messaage to display to show result of static image bee counting.
    output_img: BGR openCV image
    '''
    def push_static_result(self, output_img: cv.typing.MatLike):
        self._q.put(("static_result", output_img))

    '''
    Send data update containing live camera image, etc.
    '''
    def push_live_camera_result(self, output_img: cv.typing.MatLike):
        self._img_ptr_readonly = output_img
        try:
            self._livecam_q.put_nowait(("livecamera",))
        except:
            pass # queue is full, ignore

    def _on_empty(self):
        print("on empty")
        self.empty_frame.tkraise()
        self.empty_label.update()
        self.empty_frame.update()
        self.result_frame.lower()

    def _on_static_result(self, output_img):
        matplot_img = cv.cvtColor(output_img, cv.COLOR_BGR2RGB)
        self.result_ax_im.set_data(matplot_img)
        # self.result_ax.clear()
        # self.result_ax.axis("off")
        self.result_ax.imshow(matplot_img)
        self.result_canvas.draw_idle()
        self.result_toolbar.update()
        self.result_frame.update()
        self.result_frame.tkraise()

    def _on_live_camera_result(self):
        start = time.time_ns()
        
        output_img = self._img_ptr_readonly

        # matplot_img = cv.cvtColor(output_img, cv.COLOR_BGR2RGB)
        s1 = time.time_ns()
        matplot_img = output_img[:,:,::-1]
        t1 = time.time_ns() - s1
        s2 = time.time_ns()
        self._display_img_data(matplot_img)
        t2 = time.time_ns() - s2
        self.result_frame.tkraise()
        print("live camera result processing times: ", t1, t2)

        '''
        img_data: RGB channel image
        '''
    def _display_img_data(self, img_data):
        self.result_ax_im.set_data(img_data)
        self.result_canvas.draw()
        self.result_frame.update()

# tests
def _test_frontend_display_window():
    def main(display: FrontendDisplay):
        img = cv.imread("images/bee-image-samples/bee-image-1.jpg")
        
        cv.circle(img, (100, 100), 50, (0, 255, 0), 3)
        cv.putText(img, "ooga booga", (10, 10), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0))

        display.push_static_result(img)

    display = FrontendDisplay()
    display.main = main
    display.start()
    print("Bee Count Tool: exiting ...")

def _test_frontend_display_live():
    cam = cv.VideoCapture(1) # 1 for macos, 0 for other systems
    if not cam.isOpened():
        cam.open()
    
    def main(display: FrontendDisplay):
        while True:
            ret, frame = cam.read()
            if not ret:
                break

            print("sending frame")
            display.push_live_camera_result(frame)
            time.sleep(0.05)

    display = FrontendDisplay()
    display.main = main
    display.start()

def _test_frontend_display_empty():
    def main(display: FrontendDisplay):
        display.push_empty()

    display = FrontendDisplay()
    display.main = main
    display.start()

if __name__ == "__main__":
    _test_frontend_display_live()

# Popup class for data input
# TO DO for final: add a confirmation window before exporting data

