'''
author: Henry Shaw
version: 0.1
date: 20250227

Utility for testing image processing algorithsm by
displaying the image along with tuninig controls and 
controls to reprocess the output result.
'''

import wx
import wx.adv
import cv2 as cv

class SessionDispatch:
    '''
    Do processing for test session here.
    '''
    def __init__(self, *args, **kwargs):
        self.session = None
        pass

    def process(self, _):
        '''
        Should get new user spec. params and recompute image output.
        '''
        pass


class Session:
    def __init__(self, *args, **kwargs):
        self.dispatch = kwargs.get("session_dispatch")
        self.dispatch.session = self

        self.app = wx.App()
        self.frame = wx.Frame(None, title= kwargs.get('title') or "imgprocx", size=(800, 600))
        self.frame_box_sizer = wx.BoxSizer(wx.VERTICAL)

        self.img_panel = wx.StaticBitmap(self.frame)
        self.frame_box_sizer.Add(self.img_panel, 1, wx.EXPAND)

        self.process_btn = wx.Button(self.frame, label="Recompute")
        self.frame_box_sizer.Add(self.process_btn, 0, wx.CENTER)
        self.process_btn.Bind(wx.EVT_BUTTON, self.dispatch.process)

        self.input_panel = wx.Panel(self.frame)
        self.input_panel.SetMinSize((200, 200))
        self.frame_box_sizer.Add(self.input_panel, 0, wx.EXPAND)
        self.input_box_sizer = wx.BoxSizer(wx.VERTICAL)
        self.input_panel.SetSizer(self.input_box_sizer)
        
        self.input_ctrls = {}

        self.frame.SetSizer(self.frame_box_sizer)

    def run(self):
        self.frame.Layout()
        self.frame.Update()
        self.frame.Show()

        self.app.MainLoop()

    class SliderInput:
        sizer: wx.BoxSizer
        slider: wx.Slider
        nameText: wx.StaticText

    def reg_slider_input(self, id, name, min, max, value, order):
        order = order or 999999999
        slider_input = self.SliderInput()
        slider_input.sizer = wx.BoxSizer(wx.HORIZONTAL)
        slider_input.nameText = wx.StaticText(self.input_panel, label=name)
        slider_input.sizer.Add(slider_input.nameText, 1)
        slider_input.slider = wx.Slider(self.input_panel, value=value, minValue=min, maxValue=max, style=wx.SL_HORIZONTAL|wx.SL_LABELS)
        slider_input.sizer.Add(slider_input.slider, 3)
        self.input_box_sizer.Add(slider_input.sizer, 0, wx.CENTER)
        self.input_ctrls[id] = slider_input
        pass

    def check_slider_input(self, id):
        '''
        Slider id must have been previously registered.
        '''
        slider = self.input_ctrls.get(id)
        if slider is None: raise RuntimeError(f"Slider with id {id} not found.")
        return slider.slider.GetValue()

    def reg_num_input(self, id, value, order):
        order = order or 999999999
        pass

    def check_num_input(self, id):
        '''
        Number input id must have been previously registered.
        '''
        pass

    def push_img(self, img_mat):
        bmp = wx.Bitmap.FromBuffer(img_mat.shape[1], img_mat.shape[0], img_mat)
        self.img_panel.SetBitmap(bmp)
        self.frame.Layout()
        self.frame.Update()
        # todo: enforce correct ndarray and element type of img_mat
        pass

    def show_img(self):
        # load image in open cv and then use the mat data to show the image in self.img_panel
        img = cv.imread('/Users/henryshaw/Desktop/Projects/ee-capstone-bee-mite-detect/image_data/bee-image-1.jpg', cv.IMREAD_COLOR_RGB)
        bmp = wx.Bitmap.FromBuffer(img.shape[1], img.shape[0], img)
        self.img_panel.SetBitmap(bmp)
        self.frame.Layout()
        self.frame.Update()



if __name__ == "__main__":
    class TestDispatch:
        def process(self, _):
            print("Processing.")
            t1 = self.session.check_slider_input("Threshold1")
            print(t1)

    sess = Session(title="imgprocx test", session_dispatch=TestDispatch())
    sess.reg_slider_input("Threshold1", "Threshold1", 0, 255, 70, 1)
    sess.show_img()
    sess.run()
    # sess.app.MainLoop()