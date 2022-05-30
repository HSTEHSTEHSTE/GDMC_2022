import random
import numpy as np
from scipy.signal import convolve2d
from gdpc import interface as INTF
from gdpc import worldLoader as WL

STARTX, STARTY, STARTZ, ENDX, ENDY, ENDZ = INTF.requestPlayerArea(dx = 256, dz = 256)


WORLDSLICE = WL.WorldSlice(STARTX, STARTZ, ENDX + 1, ENDZ + 1)
height_map = WORLDSLICE.heightmaps['OCEAN_FLOOR']

def get_geography_map(world_slice):
    sea_map = (world_slice.heightmaps['OCEAN_FLOOR'] == world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES']).astype(int)
    return sea_map

sea_map = get_geography_map(WORLDSLICE)


# pick starting position
pick_location_success = False
while not pick_location_success:
    x_start = random.randint(STARTX, ENDX)
    z_start = random.randint(STARTZ, ENDZ)
    
    if sea_map[x_start + 1, z_start + 1] < 1:
        pick_location_success = True
        y_start = height_map[x_start + 1, z_start + 1]
print('Start location: ', x_start, y_start, z_start)


# build starter house
house_size = (9, 9)
## clear starter plot
x_look_size = house_size[0] * 2 - 1
z_look_size = house_size[1] * 2 - 1
convolution_array = np.ones(house_size)
look_area = np.array([[max(1, x_start - house_size[0] + 1 + 1), min(height_map.shape[0], x_start + house_size[0] - 1 + 1 + 1)], [max(1, z_start - house_size[1] + 1 + 1), min(height_map.shape[1], z_start + house_size[1] - 1 + 1 + 1)]])
look_area_height_map = height_map[look_area[0, 0]:look_area[0, 1], look_area[1, 0]:look_area[1, 1]]
look_area = look_area - 1
# print(max(1, x_start - house_size[0] + 1 + 1), min(height_map.shape[0], x_start + house_size[0] - 1 + 1 + 1), max(1, z_start - house_size[1] + 1 + 1), min(height_map.shape[1], z_start + house_size[1] - 1 + 1 + 1))
# print(look_area_height_map)
look_area_height_map_gradient = look_area_height_map - y_start
print(look_area_height_map_gradient)
look_area_height_map_convolved = convolve2d(np.abs(look_area_height_map_gradient), convolution_array, mode = 'valid')
print(look_area_height_map_convolved)

convolved_index = np.unravel_index(np.argmin(look_area_height_map_convolved), look_area_height_map_convolved.shape)
house_area = np.array([[look_area[0, 0] + convolved_index[0], look_area[0, 0] + convolved_index[0] + house_size[0] - 1], [look_area[1, 0] + convolved_index[1], look_area[1, 0] + convolved_index[1] + house_size[1] - 1]])
print(house_area)
## build house
