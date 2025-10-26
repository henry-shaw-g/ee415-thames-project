import tkinter as tk
from tkinter import filedialog
import os

class ExcelBeforeFrame(tk.Frame):

    def __init__(self,parent,controller):
        self.controller = controller
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="this is the Excel before data frame")
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Find CSV/Excel File", command=lambda: self.findFile())
        button.pack()

        
    def findFile(self):
        #This function finds a suitable file to put the data into then also stores the file 
        ExcelFilePath = None
        ExcelFilePath = filedialog.askopenfilename(title="CSV to process in",filetypes=(("csv files","*.csv"),("Excel Files","*.xlsx"),("All Files","*.*")))
        if os.path.exists(ExcelFilePath):
            print("Error: Did Not Save Filepath")
            print("Saved Filepath")
            #if the filepath is not none and works, we update the filepath in the main frontend display file and show the data entry frame
            #This will be updated later to also get the labels for each column but for now is just a toggle and rigid categories
            self.controller.updateExcelFilePath(ExcelFilePath)
            self.controller.showFrame("EntryFrame")
        else:
            print("Error: Did Not Save Filepath")