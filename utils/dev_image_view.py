# SHOW_IMAGE_OPENCV_ENABLED = True
SHOW_IMAGE_MATPLOTLIB_ENABLED = True # turn this off for deployment

class ShowImageBackend:
    @staticmethod
    def show_image(image_bgr):
        pass

# if SHOW_IMAGE_OPENCV_ENABLED:
import cv2 as cv
class ShowImageOpenCV(ShowImageBackend):
    @staticmethod
    def show_image(image_bgr):
        cv.imshow("Image", image_bgr)
        cv.waitKey(0)
        cv.destroyAllWindows()

if SHOW_IMAGE_MATPLOTLIB_ENABLED:
    from matplotlib import pyplot as plt
    class ShowImageMatplotlib(ShowImageBackend):
        @staticmethod
        def show_image(image_bgr):
            image_rgb = image_bgr[:, :, ::-1]  # Convert BGR to RGB
            plt.imshow(image_rgb)
            plt.axis('off')  # Hide axis
            plt.show()

_global_backend = ShowImageOpenCV

def set_backend(backend):
    global _global_backend
    _global_backend = backend

def show_image(image, backend=None):
    backend = backend or _global_backend
    backend.show_image(image)
