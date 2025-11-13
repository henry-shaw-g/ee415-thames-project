import math
from enum import Enum
from collections import namedtuple
import shapely
from shapely.geometry import MultiPolygon
from counting.contour import Contour
from counting.contours import Contours
import numpy as np


def _get_bbox_dimension_cells(cells_dim, cell_size, contour):
    bx, by = contour.bounding_box_x, contour.bounding_box_y
    bw, bh = contour.bounding_box_w, contour.bounding_box_h

    # i denotes row (y), j denotes column (x)
    cell_i0 = min(cells_dim[1] - 1, max(0, math.floor(by / cell_size)))
    cell_i1 = min(cells_dim[1] - 1, max(0, math.floor((by + bh) / cell_size)))
    cell_j0 = min(cells_dim[0] - 1, max(0, math.floor(bx / cell_size)))
    cell_j1 = min(cells_dim[0] - 1, max(0, math.floor((bx + bw) / cell_size)))

    return (cell_j0, cell_j1), (cell_i0, cell_i1)

def _init_grid(image_w, image_h, GRID_SIZE):
    cells_wide = math.ceil(image_w / GRID_SIZE)
    cells_high = math.ceil(image_h/ GRID_SIZE)
    grid = [[[] for j in range(0, cells_wide)] for i in range(0, cells_high)]
    return grid, (cells_wide, cells_high)

def _populate_grid(grid, grid_dims, grid_size, contours):
    for contour in contours:
        _append_to_grid(grid, grid_dims, grid_size, contour)

def _append_to_grid(grid, grid_dims, grid_size, contour):
    cells_x, cells_y = _get_bbox_dimension_cells((grid_dims[0], grid_dims[1]), grid_size, contour)
    for i in range(cells_y[0], cells_y[1] + 1):
        for j in range(cells_x[0], cells_x[1] + 1):
            grid[i][j].append(contour)

def _convert_polygon_to_contour_format(polygon):
    exterior_coords = np.array(polygon.exterior.coords).reshape((-1, 1, 2)).astype(np.int32)
    return exterior_coords


class CNNContours(Contours):
    grid_size = 64
    PolygonState = Enum('PolygonState', ['VALID', 'INVALID'])
    ContourPolygon = namedtuple('ContourPolygon', ['polygon', 'state', 'synced', 'contour'])    

    def __init__(self, image_thresholded, original_image, settings, *, prior_contours, cnn_contour_list):
        super().__init__(image_thresholded, original_image, settings)
        self.image_shape = original_image.shape[0:2]
        self.polygons = {}
        self.grid, self.grid_dims = _init_grid(self.image_shape[1], self.image_shape[0], self.grid_size)
        self.copy_single_bee_statistics(prior_contours)
        self.contours = prior_contours.contours.copy()  # TODO: address that we are probably breaking heirachy information here
        self.contours.extend(cnn_contour_list)

    def merge_cnn_contours(self):
        _populate_grid(self.grid, self.grid_dims, self.grid_size, self.contours)

        for contour in self.contours:
            if not ((contour.get_type() == Contour.type.single_bee or contour.get_type() == Contour.type.unprocessed) and contour.source == "cnn"):
                continue
            self._merge_contour(contour)

        # revise contour data for any modified clump polygons
        # self._update_contours_from_polygons()
        # clean polygon list
        self.polygons.clear()

    def _merge_contour(self, contour):
        

        state, polygon = self._get_contour_polygon(contour)
        if state == self.PolygonState.INVALID:
            contour.set_type(Contour.type.rejected)
            return

        cells_x, cells_y = _get_bbox_dimension_cells(self.grid_dims, self.grid_size, contour)
        for i in range(cells_y[0], cells_y[1] + 1):
            for j in range(cells_x[0], cells_x[1] + 1):
                for other in self.grid[i][j]:
                    if other is contour:
                        continue
                    
                    if other.get_type() == Contour.type.single_bee:
                        in_single, iou, intersection = self._is_single_in_single(contour, other)
                        if in_single:
                            contour.set_type(Contour.type.rejected)
                            return

    '''
    func: _is_single_in_clump
        Determine if a single bee contour is inside a clump contour.
    '''
    def _is_single_in_clump(self, single_contour, clump_contour):
        _, clump_polygon = self._get_contour_polygon(clump_contour)
        _, single_polygon = self._get_contour_polygon(single_contour)
        single_area = single_polygon.area
        intersection = clump_polygon.intersection(single_polygon).area
        return (intersection / single_area >= self.settings["contour_single_in_clump_intersection_ratio"], intersection)

    '''
    func:   _is_single_in_single
        Determine if a single bee contour can be merged into another single bee contour.
    '''
    def _is_single_in_single(self, contour1, contour2):
        angle1 = abs(contour1.fitted_rect_angle - contour2.fitted_rect_angle)
        angle2 = abs((contour1.fitted_rect_angle - 180) % 360 - contour2.fitted_rect_angle)
        angle_diff = min(angle1, angle2)
        if angle_diff > self.settings["contour_merge_angle_threshold"]:
            return False, None, None

        state1, polygon1 = self._get_contour_polygon(contour1)
        state2, polygon2 = self._get_contour_polygon(contour2)
        if state1 is self.PolygonState.INVALID or state2 is self.PolygonState.INVALID:
            return False, None, None

        intersection = polygon1.intersection(polygon2).area
        IO1 = intersection / (polygon1.area)
        return (IO1 > self.settings["contour_merge_IO1_threshold"], IO1, intersection)

    '''
    func: _split_from_clump
        CURRENTLY NOT USED
    '''
    def _split_from_clump(self, single_contour, clump_contour):
        # assume all polygons are valid at this point
        _, clump_polygon = self._get_contour_polygon(clump_contour)
        _, single_polygon = self._get_contour_polygon(single_contour)
        difference = clump_polygon.difference(single_polygon)                
        if isinstance(difference, shapely.geometry.MultiPolygon):
            candidates = []
            for geom in difference.geoms:
                if isinstance(geom, MultiPolygon):
                    for poly in geom.geoms:
                        candidates.append(poly)
                else:
                    candidates.append(geom)
        
            iter = candidates.__iter__()

            first = next(iter, None)
            if first is None:
                raise ValueError("No valid polygons found after difference operation")
            self._set_contour_polygon(clump_contour, first, desync=True)
            clump_contour.source = "clump_split"
            print("split clump many out",clump_contour.id)

            for poly in iter:
                new_contour = Contour(
                    contour = _convert_polygon_to_contour_format(poly),
                    source = "clump_split"
                )
                new_contour.set_type(Contour.type.clump)
                self.contours.append(new_contour)
                _append_to_grid(self.grid, self.grid_dims, self.grid_size, new_contour)
                self._set_contour_polygon(new_contour, poly, desync=False)
        else:
            print("split clump 1 out", clump_contour.id)
            self._set_contour_polygon(clump_contour, difference, desync=True)

    def _get_contour_polygon(self, contour):
        data = self.polygons.get(contour, None)
        if data is None:
            polygon = shapely.geometry.Polygon(contour.contour.reshape((-1, 2))).buffer(0)
            if isinstance(polygon, shapely.geometry.MultiPolygon):
               data = self.ContourPolygon(polygon=None, state=self.PolygonState.INVALID, synced=True, contour=contour)
            else:
               data = self.ContourPolygon(polygon=polygon, state=self.PolygonState.VALID, synced=True, contour=contour)
            self.polygons[contour] = data

        state, polygon = data.state, data.polygon
        return state, polygon

    def _set_contour_polygon(self, contour, polygon, desync=True):
        if isinstance(polygon, shapely.geometry.MultiPolygon):
            raise ValueError("Cannot set contour polygon to MultiPolygon")
        self.polygons[contour.id] = self.ContourPolygon(polygon=polygon, state=self.PolygonState.VALID, synced=not desync, contour=contour)


    def _update_contours_from_polygons(self):
        for data in self.polygons.values():
            contour, state, polygon, synced = data.contour, data.state, data.polygon, data.synced
            # if contour.source == "clump_split" and state == self.PolygonState.VALID and not polygon.is_empty:
            # if not synced and state == self.PolygonState.VALID and not polygon.is_empty:
            if state == self.PolygonState.VALID and not polygon.is_empty:
                exterior_coords = _convert_polygon_to_contour_format(polygon)
                contour.set_contour_data(exterior_coords)