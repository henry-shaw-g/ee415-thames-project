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
import threading, time
from PIL import Image, ImageTk
import cv2 as cv

import queue
from queue import Queue

QUEUE_CHECK_PERIOD = 100 # ms

class FrontendDisplay:

    def __init__(self):
        self.main = None
        self._q = Queue()


        # create Tk gui instances
        self.root = tk.Tk()
        self.root.title("Bee Count Display")
        self.root.geometry("1920x1080")

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
        self.empty_label.pack(anchor=tk.CENTER, side=tk.TOP)
        # create a canvas to display images

        self.result_frame = ttk.Frame(self.top_frame)
        self.result_frame.grid(row=0, column=0, sticky="nsew")
        
        self.result_tkimage = None
        # self.result_canvas = tk.Canvas(self.result_frame, bg="green")
        # self.result_canvas.pack(anchor=tk.CENTER, fill=tk.BOTH, expand=True)
        self.result_imglabel = ttk.Label(self.result_frame)
        self.result_imglabel.pack(anchor=tk.CENTER, expand=True, fill=tk.BOTH)

        self.empty_frame.tkraise()


    def start(self):
        # Start program through its 'main' entry point.
        thread = threading.Thread(target=self.main, args=(self,))
        thread.daemon = True # is not necessary but might be safer
        thread.start()

        self.root.update()
        # Start the queue loop to communicate with TUI & working logic
        self.root.after(QUEUE_CHECK_PERIOD, self._queue_loop)

        # Start the Tkinter main loop
        self.root.mainloop()

    def _queue_loop(self):
        
        try:
            msg = self._q.get_nowait()
            kind, *data = msg
            if kind == "empty":
                pass
            elif kind == "static_result":
                self._on_static_result(*data)
            elif kind == "livecamera":
                pass
        
        except queue.Empty:
            # end of queue
            pass
        except Exception as e:
            print("Error in frontend_display queue loop.")
            raise

        self.root.after(QUEUE_CHECK_PERIOD, self._queue_loop)
    
    def push_empty():
        pass

    '''
    Send messaage to display to show result of static image bee counting.
    output_img: BGR openCV image
    '''
    def push_static_result(self, output_img: cv.typing.MatLike):
        print("pushing static result")
        self._q.put(("static_result", output_img))

    '''
    Send data update containing live camera image, etc.
    '''
    def push_live_camera_result(self, output_img: cv.typing.MatLike):
        pass

    def _on_static_result(self, output_img):
        print("on static result")
        cv2_img = cv.cvtColor(output_img, cv.COLOR_BGR2RGB)
        pil_img = Image.fromarray(cv2_img)

        w, h = pil_img.width, pil_img.height
        pil_img = pil_img.resize((int(w / 3), int(h/3)))

        self.result_tkimg = ImageTk.PhotoImage(pil_img)
        self.result_imglabel.config(image=self.result_tkimg)
        # self.result_canvas.create_image((0, 0), image=self.result_tkimg)
        self.result_frame.tkraise()

if __name__ == "__main__":
    # This is for testing the FrontendDisplay class

    def main(display: FrontendDisplay):
        img = cv.imread("images/bee-image-samples/bee-image-1.jpg")
        
        cv.circle(img, (100, 100), 50, (0, 255, 0), 3)
        cv.putText(img, "ooga booga", (10, 10), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0))

        display.push_static_result(img)

    display = FrontendDisplay()
    display.main = main
    display.start()
    print("Bee Count Tool: exiting ...")