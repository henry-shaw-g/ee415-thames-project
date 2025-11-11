'''
module: contour_merge.py
    Merges duplicate bee contour detections from multiple sources and records voting agreement for each detection.
    Current rules:
        1. CNN bee proposals are only considered if they are also a single bee detection from conventional algorithm OR
        if they are within a contour.
'''
import math
from enum import Enum
import cv2 as cv
from matplotlib.pyplot import grid
from counting.contour import Contour
import numpy as np
import shapely
from shapely.geometry import MultiPolygon

GRID_SIZE = 64 # 64 pixels / grid cell

def _get_bbox_dimension_cells(cells_dim, cell_size, contour):
    bx, by = contour.bounding_box_x, contour.bounding_box_y
    bw, bh = contour.bounding_box_w, contour.bounding_box_h

    # i denotes row (y), j denotes column (x)
    cell_i0 = min(cells_dim[1] - 1, max(0, math.floor(by / cell_size)))
    cell_i1 = min(cells_dim[1] - 1, max(0, math.floor((by + bh) / cell_size)))
    cell_j0 = min(cells_dim[0] - 1, max(0, math.floor(bx / cell_size)))
    cell_j1 = min(cells_dim[0] - 1, max(0, math.floor((bx + bw) / cell_size)))

    return (cell_j0, cell_j1), (cell_i0, cell_i1)

def _init_grid(image_w, image_h):
    cells_wide = math.ceil(image_w / GRID_SIZE)
    cells_high = math.ceil(image_h/ GRID_SIZE)
    grid = [[[] for j in range(0, cells_wide)] for i in range(0, cells_high)]
    return grid, (cells_wide, cells_high)

def _populate_grid(grid, grid_dims, contours):
    for contour in contours:
        cells_x, cells_y = _get_bbox_dimension_cells((grid_dims[0], grid_dims[1]), GRID_SIZE, contour)
        for i in range(cells_y[0], cells_y[1] + 1):
            for j in range(cells_x[0], cells_x[1] + 1):
                grid[i][j].append(contour)

class Merger:

    PolygonState = Enum('PolygonState', ['VALID', 'INVALID'])

    def __init__(self, image, contours, algorithm_settings):
        self.contours = sorted(contours, key=lambda c: c.area, reverse=True)
        self.settings = algorithm_settings
        self.grid, self.grid_dims = _init_grid(image.shape[1], image.shape[0])
        self.shapely_polygons = {}
        _populate_grid(self.grid, self.grid_dims, contours)

    def __call__(self, **kwargs):
        return self._merge(**kwargs)

    def _get_contour_polygon(self, contour):
        data = self.shapely_polygons.get(contour, None)
        if data is None:
            polygon = shapely.geometry.Polygon(contour.contour.reshape((-1, 2))).buffer(0)
            if isinstance(polygon, shapely.geometry.MultiPolygon):
               data = (self.PolygonState.INVALID, None)
            else:
               data = (self.PolygonState.VALID, polygon)
            self.shapely_polygons[contour] = data

        state, polygon = data
        return state, polygon
    
    def _set_contour_polygon(self, contour, polygon):
        self.shapely_polygons[contour] = (self.PolygonState.VALID, polygon)
    
    def _update_contours_from_polygons(self):
        for contour, (state, polygon) in self.shapely_polygons.items():
            if state == self.PolygonState.VALID and not polygon.is_empty:
                exterior_coords = np.array(polygon.exterior.coords).reshape((-1, 1, 2)).astype(np.int32)
                contour.contour = exterior_coords
                contour.area = polygon.area
                # Update other properties as needed (bounding box, fitted rectangle, etc.)
                contour.bounding_box = cv.boundingRect(contour.contour)
                contour.bounding_box_x = contour.bounding_box[0]
                contour.bounding_box_y = contour.bounding_box[1]
                contour.bounding_box_w = contour.bounding_box[2]
                contour.bounding_box_h = contour.bounding_box[3]
                contour.bounding_box_area = contour.bounding_box_w * contour.bounding_box_h
                contour.bounding_box_aspect_ratio = contour.bounding_box_w / contour.bounding_box_h if contour.bounding_box_h != 0 else 0

                contour.fitted_rotated_rect = cv.minAreaRect(contour.contour)
                contour.fitted_rect_width = contour.fitted_rotated_rect[1][0]
                contour.fitted_rect_height = contour.fitted_rotated_rect[1][1]
                contour.fitted_rect_angle = contour.fitted_rotated_rect[2]
                contour.fitted_ellipse_area = np.pi * (contour.fitted_rect_width/2) * (contour.fitted_rect_height/2)
                contour.fitted_rect_aspect_ratio = contour.fitted_rect_width / contour.fitted_rect_height if contour.fitted_rect_height != 0 else 0

    def _merge(self, split_from_clumps=True):
        for contour in self.contours:
            if contour.get_type() is not Contour.type.single_bee:
                continue
        
            # only consider contours proposed by CNN for now
            if contour.source != "cnn":
                continue

            state, _ = self._get_contour_polygon(contour)
            if state is self.PolygonState.INVALID:
                contour.set_type(Contour.type.rejected)
                continue

            cells_x, cells_y = _get_bbox_dimension_cells(self.grid_dims, GRID_SIZE, contour)
            for i in range(cells_y[0], cells_y[1] + 1):
                for j in range(cells_x[0], cells_x[1] + 1):
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
                            (in_clump, intersection) = self._check_single_in_clump(other, contour)
                            if in_clump:
                                print(f"contour id={contour.id} inside clump id={other.id} in cell (i={i},j={j}).")
                                # TODO: handle logic to reduce clump area by single bee area
                                self._split_single_from_clump(other, contour)

        self._update_contours_from_polygons()
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

        bigger_polygon_state, bigger_polygon = self._get_contour_polygon(bigger)
        smaller_polygon_state, smaller_polygon = self._get_contour_polygon(smaller)
        if bigger_polygon_state is self.PolygonState.INVALID or smaller_polygon_state is self.PolygonState.INVALID:
            return False, None, None

        intersection = bigger_polygon.intersection(smaller_polygon).area
        IOU = intersection / (bigger.area + smaller.area - intersection)
        return (IOU > self.settings["contour_merge_IOU_threshold"], IOU, intersection)

    '''
    fn: check_single_in_clump
        Check if one single bee contour is inside a clump contour.
    '''
    def _check_single_in_clump(self, clump, single):
        _, clump_polygon = self._get_contour_polygon(clump)
        _, single_polygon = self._get_contour_polygon(single)
        intersection = clump_polygon.intersection(single_polygon).area
        return (intersection / single.area >= self.settings["contour_single_in_clump_intersection_ratio"], intersection)
    
    def _split_single_from_clump(self, clump, single):
        _, clump_polygon = self._get_contour_polygon(clump)
        _, single_polygon = self._get_contour_polygon(single)
        # The difference may return a MultiPolygon if the subtraction results in disjoint regions.
        difference = clump_polygon.difference(single_polygon)                
        if isinstance(difference, shapely.geometry.MultiPolygon):
            candidates = [
                poly
                for geom in difference.geoms
                for poly in (geom.geoms if isinstance(geom, MultiPolygon) else (geom,))
            ]
        
            # # Handle MultiPolygon: for now, take the largest polygon as the new clump
            largest = max(candidates, key=lambda p: p.area)
            self._set_contour_polygon(clump, largest)
            # # Optionally, log or handle the other polygons if needed
            # raise NotImplementedError("Clump subtraction resulted in MultiPolygon; handling not implemented.")
        else:
            self._set_contour_polygon(clump, difference)