import tkinter as tk
from tkinter import filedialog
import os
from tkinter import messagebox

class ExcelBeforeFrame(tk.Frame):
    #Purpose of this class is to make sure that before data is entered they have a connected csv or excel file (i.e. another check to make sure we don't save to nothing)
    def __init__(self,parent,controller):
        self.controller = controller
        tk.Frame.__init__(self, parent, highlightbackground="yellow", highlightthickness=5)
        #label = tk.Label(self, text="this is the Excel before data frame")
        #label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Find CSV/Excel File", command=lambda: self.findFile())
        button.pack()
        label = tk.Label(self,text="Or")
        label.pack()
        button2 = tk.Button(self,text="Use without CSV/Excel File", command=lambda: self.NoExcel())
        button2.pack()

        
    def findFile(self):
        #This function finds a suitable file to put the data into then also stores the file 
        ExcelFilePath = filedialog.askopenfilename(title="CSV to process in",filetypes=(("csv files","*.csv"),("Excel Files","*.xlsx"),("All Files","*.*")))
        if os.path.exists(ExcelFilePath):
            print("Saved Filepath")
            #if the filepath is not none and works, we update the filepath in the main frontend display file and show the data entry frame
            #This will be updated later to also get the labels for each column but for now is just a toggle and rigid categories
            self.controller.updateExcelFilePath(ExcelFilePath)
            self.controller.showFrame("EntryFrame")
            self.controller.createDataIOObj(ExcelFilePath)
            self.controller.isExcelFrameUsed = True
        else:
            messagebox.showerror("Error","Did not save Excel/CSV filepath") 

    def NoExcel(self):
        #command brings up frame for just a bee count. updates logic in frontend display as well to keep track of frames for processing
        self.controller.showFrame("BeeOnlyFrame")
        #just in case I want to call this again sometime, need to reset this check variable
        self.controller.isExcelFrameUsed = False
        pass