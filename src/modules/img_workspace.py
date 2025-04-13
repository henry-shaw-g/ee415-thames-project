'''
author: Henry Shaw
version: 0.2
date: 20250227

Utility for testing image processing algorithsm by
displaying the image along with tuninig controls and 
controls to reprocess the output result.
'''

import math
import wx
import wx.adv
import cv2 as cv

def make_named_slider(parent, name, min, max, value, style):
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    nameText = wx.StaticText(parent, label=name)
    sizer.Add(nameText, 1)
    slider = wx.Slider(parent, value=value, minValue=min, maxValue=max, style=style)
    sizer.Add(slider, 3)
    return sizer, slider

class WorkspaceEventHandler:
    '''
    Do processing for test session here.
    '''
    def __init__(self, *args, **kwargs):
        self.workspace = None
        pass

    def process(self, _):
        '''
        Should get new user spec. params and recompute image output.
        '''
        pass

class Workspace:
    class SliderInput:
        sizer: wx.BoxSizer
        nameText: wx.StaticText
        slider: wx.Slider

    class RangeInput:
        sizer: wx.BoxSizer
        nameText: wx.StaticText
        minCtrl: wx.TextCtrl
        maxCtrl: wx.TextCtrl
        range: tuple[int, int]
    
    class ImgDisplay(wx.GenericStaticBitmap):
        def __init__(self, parent, *args, **kwargs):
            kwargs['style'] = kwargs.get('style', 0) | wx.FULL_REPAINT_ON_RESIZE & ~wx.NO_FULL_REPAINT_ON_RESIZE
            super().__init__(parent, *args, **kwargs)
            self.SetScaleMode(wx.GenericStaticBitmap.ScaleMode.Scale_AspectFit)
            # self.Bind(wx.EVT_SIZE, self.on_resize)

        # def on_resize(self, event):
        #     self.Refresh()


    def __init__(self, title="Image Workspace", event_handler=None, *, layout="vertical", auto_process=True):
        self.handler = event_handler
        if self.handler is not None:
            self.handler.workspace = self

        self.auto_process = auto_process

        self.app = wx.App()
        self.frame = wx.Frame(None, title=title, size=(800, 600))
        self.top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.img_seq = None
        self.img_seq_idx = -1

        self.img_panel = self.ImgDisplay(self.frame)
        # self.img_panel.SetScaleMode(wx.GenericStaticBitmap.ScaleMode.Scale_AspectFit)
        self.top_sizer.Add(self.img_panel, 1, wx.EXPAND)

        self.input_panel = wx.Panel(self.frame)
        self.input_panel.SetMinSize((200, 200))
        self.top_sizer.Add(self.input_panel, 0, wx.EXPAND)
        self.input_box_sizer = wx.BoxSizer(wx.VERTICAL)
        self.input_panel.SetSizer(self.input_box_sizer)
        
        self.process_btn = wx.Button(self.input_panel, label="Recompute")
        self.input_box_sizer.Add(self.process_btn, 0, wx.CENTER)
        self.process_btn.Bind(wx.EVT_BUTTON, self._on_process_btn)

        # img_seq_sizer, self.img_seq_slider = make_named_slider(self.input_panel, "Img Select", 0, 0, 0, wx.SL_HORIZONTAL|wx.SL_LABELS)
        # self.input_box_sizer.Add(img_seq_sizer, 0, wx.CENTER)
        # self.img_seq_slider.Bind(wx.EVT_SLIDER, self._on_img_seq_slider)
        self.img_seq_select = wx.Choice(self.input_panel, choices=[])
        self.input_box_sizer.Add(self.img_seq_select, 0, wx.CENTER)
        self.img_seq_select.Bind(wx.EVT_CHOICE, self._on_img_seq_select)

        self.input_ctrls = {}

        self.frame.SetSizer(self.top_sizer)
            

    def run(self):
        self.frame.Layout()
        self.frame.Update()
        self.frame.Show()

        if self.auto_process:
            self._on_process_btn(None)

        self.app.MainLoop()
    # private

    def _on_process_btn(self, event):
        # self.img_seq = []
        # self.handler.process(event)
        # # reconstrain select image slider
        # # self.img_seq_slider.SetMax(len(self.img_seq) - 1)
        # # reconstrain selected image then render
        # idx  = self.img_seq_idx
        # if idx < 0:
        #     idx = len(self.img_seq) - 1
        # else:
        #     idx = min(idx, len(self.img_seq) - 1)
        # self.img_seq_idx = idx

        self.img_seq = []
        self.handler.process(event)
        self.img_seq_idx = len(self.img_seq) - 1

        self.img_seq_select.Clear()
        self.img_seq_select.AppendItems([f"Image {i}" for i in range(len(self.img_seq))])
        self.img_seq_select.SetSelection(self.img_seq_idx)

        self.render_img(self.img_seq[self.img_seq_idx])

    def _on_img_seq_select(self, event):
        # idx = self.img_seq_slider.GetValue()
        idx = self.img_seq_select.GetSelection()
        # idx = 0
        idx = min(max(0, idx), len(self.img_seq) - 1)
        self.img_seq_idx = idx
        self.render_img(self.img_seq[idx])

    # public

    def reg_slider_input(self, id, name, min, max, value, order=None):
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

    def reg_range_input(self, id, name, range, value, order=None):
        # so wx-python doesn't actually have double ended slider so will just use 2 number inputs
        range_input = self.RangeInput()
        range_input.range = range
        range_input.sizer = wx.BoxSizer(wx.HORIZONTAL)
        range_input.nameText = wx.StaticText(self.input_panel, label=name)
        range_input.sizer.Add(range_input.nameText, 1)
        range_input.minCtrl = wx.TextCtrl(self.input_panel, value=str(value[0]), style = wx.TE_DONTWRAP | wx.TE_CENTER)
        range_input.sizer.Add(range_input.minCtrl, 1)
        range_input.maxCtrl = wx.TextCtrl(self.input_panel, value=str(value[1]), style = wx.TE_DONTWRAP | wx.TE_CENTER)
        range_input.sizer.Add(range_input.maxCtrl, 1)
        self.input_box_sizer.Add(range_input.sizer, 0, wx.CENTER)
        self.input_ctrls[id] = range_input
        pass

    def check_range_input(self, id) -> tuple[int, int]:
        # dont feel like doing event handling on the side so for now,
        # just try to parse text inputs, then fall back to the range values

        range_input = self.input_ctrls.get(id)
        if range_input is None: raise RuntimeError(f"RangeInput with id {id} not found.")

        low: float
        try:
            low = float(range_input.minCtrl.GetValue())
        except ValueError:
            low = range_input.range[0]
        
        high: float
        try:
            high = float(range_input.maxCtrl.GetValue())
        except ValueError:
            high = range_input.range[1]

        return (low, high)
        
    def reg_num_input(self, id, value, order=None):
        order = order or 999999999
        pass

    def check_num_input(self, id):
        '''
        Number input id must have been previously registered.
        '''
        pass

    def reg_bool_input(self, id, value: bool, order=None):
        # not implemented
        pass

    def check_bool_input(self, id) -> bool:
        # not implemented
        pass

    def render_img(self, img_mat):
        bmp = wx.Bitmap.FromBuffer(img_mat.shape[1], img_mat.shape[0], img_mat)
        self.img_panel.SetBitmap(bmp)
        self.frame.Layout()
        self.frame.Update()

    def push_img(self, img_mat):
        self.img_seq.append(img_mat)
        
    def push_img_bgr(self, img_mat):
        img_mat = cv.cvtColor(img_mat, cv.COLOR_BGR2RGB)
        self.push_img(img_mat)

    def push_img_gray(self, img_mat):
        img_mat = cv.cvtColor(img_mat, cv.COLOR_GRAY2RGB)
        self.push_img(img_mat)

    def show_img(self):
        # load image in open cv and then use the mat data to show the image in self.img_panel
        img = cv.imread('/Users/henryshaw/Desktop/Projects/ee-capstone-bee-mite-detect/image_data/bee-image-1.jpg', cv.IMREAD_COLOR_RGB)
        bmp = wx.Bitmap.FromBuffer(img.shape[1], img.shape[0], img)
        self.img_panel.SetBitmap(bmp)
        self.frame.Layout()
        self.frame.Update()


# tests
if __name__ == "__main__":
    # sample images
    img = cv.imread('image_data/bee-image-1.jpg', cv.IMREAD_COLOR_BGR)

    class Handler(WorkspaceEventHandler):
        def process(self, _):
            print("processing")
            self.workspace.push_img_bgr(img)

            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            self.workspace.push_img_gray(gray)
            

    workspace = Workspace(title="test", event_handler=Handler())
    workspace.reg_slider_input("SomeParam", "Some Param", 0, 1000, 100, 1)
    workspace.run()