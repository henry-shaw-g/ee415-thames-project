import tkinter as tk
import tkinter.ttk as ttk

class CameraFrame(tk.Frame):

    def __init__(self,parent,controller):
        self.controller = controller
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="this is the Camera")
        label.pack(side="top", fill="x", pady=10)
        


        #TODO code in camera functionality here
        pass