import tkinter as tk
import os
from tkinter import filedialog
from tkinter import messagebox

#not sure if I want this here or not (might be at bottom or inside of the control panel idk)
class ExcelSearchFrame(tk.Frame):

    def __init__(self,parent,controller):
        tk.Frame.__init__(self, parent, highlightbackground="blue", highlightthickness=5)
        self.controller = controller
        label = tk.Label(self, text="this is the Excel Search Frame")
        label.pack(side="top", fill="x", pady=10)

        self.ExcelFilePath = None #storing this here for now, might move it over to a different class

        #TODO reformat these buttons sometime
        self.FindFileBtn = tk.Button(self,text="Open CSV/Excel File", command=lambda: self.FileFind())
        self.FindFileBtn.pack()
        self.PreviousEntryBtn = tk.Button(self,text="Previous",command=lambda: self.PreviousEntry())
        self.PreviousEntryBtn.pack()
        self.NextEntryBtn = tk.Button(self,text="Next",command=lambda: self.NextEntry())
        self.NextEntryBtn.pack()
        pass
    
    def FileFind(self):
        ExcelFilePath = filedialog.askopenfilename(title="CSV to process in",filetypes=(("csv files","*.csv"),("Excel Files","*.xlsx"),("All Files","*.*")))
        if os.path.exists(ExcelFilePath):
            print("Saved Filepath")
            #if the filepath is not none and works, we update the filepath in the main frontend display file and show the data entry frame
            #This will be updated later to also get the labels for each column but for now is just a toggle and rigid categories
            #TODO do the above comment
            self.ExcelFilePath = ExcelFilePath
            self.controller.showFrame("EntryFrame")
            
        else:
           messagebox.showerror("Error", "Did Not Save Filepath")

    def updateFilePath(self,newFilePath):
        self.ExcelFilePath = newFilePath

    def PreviousEntry(self):
        pass

    def NextEntry(self):
        pass