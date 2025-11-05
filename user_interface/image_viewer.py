import tkinter as tk
import PIL.Image, PIL.ImageTk

class ImageViewer(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.img_view_dims = (800, 600)
        self.bar_height = 20

        self.minsize(self.img_view_dims[0], self.img_view_dims[1] + self.bar_height)
        self.columnconfigure(0, weight=1, minsize=self.img_view_dims[0])
        self.rowconfigure(0, weight=1, minsize=self.img_view_dims[1])

        self.canvas = tk.Canvas(self, bg="black")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.bar = tk.Frame(self, height=self.bar_height, bg="gray")
        self.bar.grid(row=1, column=0, sticky="ew")

    def push_image(self, img_mat):
        pass
    
    def push_image_cvmat(self, img_cvmat):
        pass

if __name__ == "__main__":
    root = tk.Tk()
    viewer = ImageViewer(master=root)
    viewer.pack(fill=tk.BOTH, expand=False)
    root.mainloop()