import tkinter as tk
import tkinter.ttk as ttk

#not sure if I want this here or not (might be at bottom or inside of the control panel idk)
class ExcelSearchFrame(tk.Frame):

    def __init__(self,parent,controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="this is the Excel Search Frame")
        label.pack(side="top", fill="x", pady=10)

        FindFileBtn = tk.Button(self,text="Open CSV/Excel File", command=lambda: self.FileFind())
        FindFileBtn.pack()
        pass
    
    def FileFind(self):
        pass