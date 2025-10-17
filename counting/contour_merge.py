'''
module: contour_merge.py
    Merges duplicate bee contour detections from multiple sources and records voting agreement for each detection.
    Current rules:
        1. CNN bee proposals are only considered if they are also a single bee detection from conventional algorithm OR
        if they are within a contour.
'''
import math
import cv2 as cv
from matplotlib.pyplot import grid
from counting.contour import Contour

GRID_SIZE = 64 # 64 pixels / grid cell

def _get_bbox_dimension_cells(cells_dim, cell_size, contour):
    bx, by = contour.bounding_box_x, contour.bounding_box_y
    bw, bh = contour.bounding_box_w, contour.bounding_box_h

    # i denotes row (y), j denotes column (x)
    cell_i0 = max(0, math.floor(by / cell_size))
    cell_i1 = min(cells_dim[1] - 1, math.floor((by + bh) / cell_size))
    cell_j0 = max(0, math.floor(bx / cell_size))
    cell_j1 = min(cells_dim[0] - 1, math.floor((bx + bw) / cell_size))

    return range(cell_j0, cell_j1 + 1), range(cell_i0, cell_i1 + 1)

def _init_grid(image_w, image_h):
    cells_wide = math.ceil(image_w / GRID_SIZE)
    cells_high = math.ceil(image_h/ GRID_SIZE)
    grid = [[[] for j in range(0, cells_wide)] for i in range(0, cells_high)]
    return grid, (cells_wide, cells_high)

def _populate_grid(grid, grid_dims, contours):
    for contour in contours:
        cells_x, cells_y = _get_bbox_dimension_cells((grid_dims[0], grid_dims[1]), GRID_SIZE, contour)
        for i in cells_y:
            for j in cells_x:
                grid[i][j].append(contour)

class Merger:
    def __init__(self, image, contours, algorithm_settings):
        self.contours = sorted(contours, key=lambda c: c.area, reverse=True)
        self.settings = algorithm_settings
        self.grid, self.grid_dims = _init_grid(image.shape[1], image.shape[0])
        _populate_grid(self.grid, self.grid_dims, contours)

    def __call__(self, **kwargs):
        return self._merge(**kwargs)

    def _merge(self, split_from_clumps=False):
        for contour in self.contours:
            if contour.get_type() is not Contour.type.single_bee:
                continue
        
            # only consider contours proposed by CNN for now
            if contour.source != "cnn":
                continue

            cells_y, cells_x = _get_bbox_dimension_cells(self.grid_dims, GRID_SIZE, contour)
            for i in cells_y:
                for j in cells_x:
                    for other in self.grid[i][j]:
                        if other is contour:
                            continue

                        if other.get_type() is Contour.type.single_bee:
                            (mergeable, IOU, intersection) = self._check_single_mergeable(other, contour)
                            if mergeable:
                                print(f"merged contour id={contour.id} into other id={other.id} in cell (i={i},j={j}). {IOU=}, {intersection=}")
                                contour.set_type(Contour.type.rejected)
                                break

                        elif other.get_type() is Contour.type.clump and split_from_clumps:
                            if self._check_single_in_clump(other, contour):
                                (in_clump, intersection) = self._check_cnn_inner(other, contour)
                                # TODO: handle logic to reduce clump area by single bee area
                                break
        return self.contours

    '''
    fn: check_cnn_inner
        Check if a smaller CNN contour is mostly inside a larger CNN contour.
    '''
    def _check_cnn_inner(self, bigger, smaller):
        (intersection, _) = cv.intersectConvexConvex(bigger.contour, smaller.contour)
        if intersection / smaller.area >= self.settings["cnn_merge_inner_intersection_ratio"]:
            return True
        return False
    
    '''
    fn: check_single_mergeable
        Check if two single bee contours are mergeable based on angle, distance, and size ratio.
    '''
    def _check_single_mergeable(self, bigger, smaller):
        angle1 = abs(bigger.fitted_rect_angle - smaller.fitted_rect_angle)
        angle2 = abs((bigger.fitted_rect_angle - 180) % 360 - smaller.fitted_rect_angle)
        angle_diff = min(angle1, angle2)
        if angle_diff > self.settings["contour_merge_angle_threshold"]:
            return False, None, None
        
        (intersection, _) = cv.intersectConvexConvex(bigger.contour, smaller.contour)
        IOU = intersection / (bigger.area + smaller.area - intersection)
        return (IOU > self.settings["contour_merge_IOU_threshold"], IOU, intersection)

    '''
    fn: check_single_in_clump
        Check if one single bee contour is inside a clump contour.
    '''
    def _check_single_in_clump(self, clump, single):
        (intersection, _) = cv.intersectConvexConvex(clump.contour, single.contour)
        return (intersection / single.area >= self.settings["contour_single_in_clump_intersection_ratio"], intersection)

