import time
import tkinter as tk
import cv2 as cv
from PIL import Image
from PIL import ImageTk
# from cv2_enumerate_cameras import enumerate_cameras

DEVICE_NAME = "UVC Camera"                 # exact name from Device Manager

# def find_camera_index(device_name=DEVICE_NAME):
#     print("Enumerating cameras...")
#     cameras = enumerate_cameras()
#     for camera_info in cameras:
#         index = camera_info.index
#         name = camera_info.name
#         print("Found camera:", index, name)
#         if name == device_name:
#             print("Using camera index:", index)
#             return index
#     return None


class CameraFrame(tk.Frame):

    def __init__(self,parent,controller):
        self.controller = controller
        tk.Frame.__init__(self, parent)
        #TODO add script here (testing with my webcam rn)
        # self.cameraIndexNum = find_camera_index(DEVICE_NAME)
        self.no_live_read = False
        self.cameraIndexNum = 0
        self.capture = cv.VideoCapture(self.cameraIndexNum, cv.CAP_DSHOW) #Get the correct camera
        if self.capture.isOpened() is not True:
            print("Error: Could not find correct camera. Using default camera")
            self.capture = cv.VideoCapture(0)  #If we can't find the correct device name then we just use the default

        self.capture.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
        self.capture.set(cv.CAP_PROP_FRAME_HEIGHT, 720)

        self.canvas = tk.Canvas(self,width=1280,height=720)
        self.canvas.grid(row=0,column=0)

        self.cameraToggle = True #true means camera is not on yet
        self.update()
        self.showCameraFrame()

    def showCameraFrame(self):
        #ret = False
        #if not self.no_live_read:
        ret, frame = self.capture.read()

        if ret:
            #CV2 uses BGR, GUI needs to show RGB
            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            #frame = cv.resize(frame, (1280, 720))
            # convert to PIL image
            img = Image.fromarray(frame)
            #convert to imageTk image
            self.imgtk = ImageTk.PhotoImage(image=img)
            #configure new image to be displayed
            w, h = img.size
            self.canvas.create_image(0, 0,image=self.imgtk,anchor=tk.NW)
            self.canvas.update()
        #call this again to get frame TODO (will prob need to change number)
        self.after(100, self.showCameraFrame)

    def checkCamera(self):
        self.capture = cv.VideoCapture(self.cameraIndexNum) #Try to get the correct camera again
        if self.capture.isOpened() is not True:
            print("Error: Could not find correct camera. Using default camera")
            self.capture = cv.VideoCapture(0)  #If we can't find the correct device name then we just use the default again

    def TakePhotoFromCamera(self):
        #assuming self.capture is not none so we just have access to it
        print("Taking photo")
        if self.capture.isOpened(): # not sure if I need this but we run it

            #time.sleep(1)
                
            #set to 4k image here
            self.set_capture_size_photo()

            #4k check
            width = self.capture.get(cv.CAP_PROP_FRAME_WIDTH)
            height = self.capture.get(cv.CAP_PROP_FRAME_HEIGHT)
            print(f"width: {width}, heigth: {height}") 
            ret,frame = self.capture.read() #actually get the photo

                #reset capture size back to live here after we get photo
            self.set_capture_size_live()

            if ret: #return image through function only if the capture worked
                return frame
            else:
                print("Error: No Frame Available")
                return None
        else:
            print("Error: Wrong Camera attatched, please attach correct camera")
            self.no_live_read = False
            return None
        
    def detectCamera(self):
        #essentially toggles through cameras until we either get a new camera or loop around back to the default (0)
        self.cameraIndexNum = self.cameraIndexNum + 1
        self.capTest = cv.VideoCapture(self.cameraIndexNum, cv.CAP_DSHOW)
        if self.capTest.isOpened():
            self.capture = self.capTest #If the test camera works and is open, then that is the new video stream to pull from
        else: #if its not open (aka cam doesnt exist)
            self.cameraIndexNum = 0 #set to default
            self.capture = cv.VideoCapture(self.cameraIndexNum, cv.CAP_DSHOW) #show default cam

    def set_capture_size_live(self):
        self.capture.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
        self.capture.set(cv.CAP_PROP_FRAME_HEIGHT, 720)

    def set_capture_size_photo(self):
        self.capture.set(cv.CAP_PROP_FRAME_WIDTH, 3840) #4k width
        self.capture.set(cv.CAP_PROP_FRAME_HEIGHT, 2160) #4k height
