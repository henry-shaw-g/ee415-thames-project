import tkinter as tk
import tkinter.ttk as ttk

class BeeCountOnlyFrame(tk.Frame):
    #Purpose of this class is to display a frame to just show the bee count in case they don't want to use the excel frame
    def __init__(self,parent,controller):
        self.controller = controller
        tk.Frame.__init__(self, parent, highlightbackground="yellow", highlightthickness=5)
        label = tk.Label(self, text="this is the bee count only frame")
        label.grid(row=0,column=0, columnspan=2, sticky="nsew")

        FONT = "Arial, 24"

        #Bee count label here
        self.BeeCount = tk.IntVar()
        self.lbl1BeeCount = ttk.Label(self, text = "Bee Count: ", font=FONT).grid(row=1,column=0,sticky="nsew")
        self.lblBeeCount = ttk.Label(self, textvariable=self.BeeCount, font=FONT)
        self.lblBeeCount.grid(row=1,column=1,sticky="nsew")

    def updateBeeCount(self,beeCount):
        self.BeeCount.set(f"{beeCount:d}")
        pass
        