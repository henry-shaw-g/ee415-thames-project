import tkinter as tk
import tkinter.ttk as ttk

class ExcelBeforeFrame(tk.Frame):
    #Purpose of this class is to make sure that before data is entered they have a connected csv or excel file (i.e. another check to make sure we don't save to nothing)
    def __init__(self,parent,controller):
        self.controller = controller
        tk.Frame.__init__(self, parent, highlightbackground="yellow", highlightthickness=5)
        label = tk.Label(self, text="this is the bee count only frame")
        label.pack(side="top", fill="x", pady=10)

        FONT = "Arial, 24"

        #Bee count label here
        self.BeeCount = tk.IntVar()
        self.lbl1BeeCount = ttk.Label(self, text = "Bee Count: ", font=FONT).grid(row=9,column=1,sticky="W")
        self.lblBeeCount = ttk.Label(self, textvariable=self.BeeCount, font=FONT)
        self.lblBeeCount.grid(row=9,column=2,sticky="W")
        