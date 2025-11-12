from os import path
import counting.algorithm as algorithm
import counting.cnn_detect as cnn_detect
from utils.file_system import get_project_dir
from user_interface.frontend_display import FrontendDisplay

def main():
    weights_path = path.join(get_project_dir(), "data/bee_detect_yolov11seg.pt")
    cnn_detect.load(cnn_detect.YoloV11SegCNN, path_to_weights = weights_path)

    settings_path = path.join(get_project_dir(), "counting/default_settings.json")
    algorithm.USE_CNN_BEE_DETECTION = True

    display = FrontendDisplay()
    display.mainloop()


if __name__ == "__main__":
    main()
    