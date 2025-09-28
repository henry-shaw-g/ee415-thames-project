'''
class: AlgorithmOutput
    Pretty much just to specify and hold all outputs of algorithm.
'''
class AlgorithmOutput():
    def __init__(self):
        self.bee_count = 0
        self.output_image = None    # bgr3 array
        self.contours = []          # list of contours found in the image, needs to identify clumps

    '''
    fn: set
    inputs: dict with keys "bee_count", "output_image", "contours"
    '''
    def set(self, dict):
        self.bee_count = dict.get("bee_count", 0)
        self.output_image = dict.get("output_image", None)
        self.contours = dict.get("contours", [])
    
