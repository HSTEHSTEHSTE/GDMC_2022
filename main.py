import random
import numpy as np
from scipy.signal import convolve2d
from gdpc import interface as INTF
from gdpc import worldLoader as WL
from gdpc import geometry as GEO

STARTX, STARTY, STARTZ, ENDX, ENDY, ENDZ = INTF.requestPlayerArea(dx = 128, dz = 128)
print("Build area: ", STARTX, STARTY, STARTZ, ENDX, ENDY, ENDZ)

WORLDSLICE = WL.WorldSlice(STARTX, STARTZ, ENDX + 1, ENDZ + 1)
def get_geography_map(world_slice):
    sea_map = (world_slice.heightmaps['OCEAN_FLOOR'] == world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES']).astype(int)
    return sea_map

height_map = np.minimum(WORLDSLICE.heightmaps['OCEAN_FLOOR'], WORLDSLICE.heightmaps['MOTION_BLOCKING_NO_LEAVES'])

sea_map = get_geography_map(WORLDSLICE)


# pick starting position
pick_location_success = False
while not pick_location_success:
    x_start = random.randint(STARTX, ENDX)
    z_start = random.randint(STARTZ, ENDZ)
    
    if sea_map[x_start + 1 - STARTX, z_start + 1 - STARTZ] == 1:
        pick_location_success = True
        y_start = height_map[x_start + 1 - STARTX, z_start + 1 - STARTZ]
print('Start location: ', x_start, y_start, z_start)


# build starter house
house_size = (9, 9)
## locate starter plot
x_look_size = house_size[0] * 2 - 1
z_look_size = house_size[1] * 2 - 1
convolution_array = np.ones(house_size)
look_area = np.array([[max(STARTX, x_start - house_size[0] + 1 + 1), min(STARTX + height_map.shape[0], x_start + house_size[0] - 1 + 1 + 1)], [max(STARTZ, z_start - house_size[1] + 1 + 1), min(STARTZ + height_map.shape[1], z_start + house_size[1] - 1 + 1 + 1)]])
look_area_height_map = height_map[(look_area[0, 0] - STARTX):(look_area[0, 1] - STARTX), (look_area[1, 0] - STARTZ):(look_area[1, 1] - STARTZ)]
look_area = look_area - 1
look_area_height_map_gradient = look_area_height_map - y_start
print(look_area_height_map_gradient.shape)
look_area_height_map_convolved = convolve2d(np.abs(look_area_height_map_gradient), convolution_array, mode = 'valid')

convolved_index = np.unravel_index(np.argmin(look_area_height_map_convolved), look_area_height_map_convolved.shape)
house_area = np.array([[look_area[0, 0] + convolved_index[0], look_area[0, 0] + convolved_index[0] + house_size[0] - 1], [look_area[1, 0] + convolved_index[1], look_area[1, 0] + convolved_index[1] + house_size[1] - 1]])
print('house area: ', house_area)
house_level = y_start
## clear plot
GEO.placeVolume(house_area[0, 0] + 1, house_level, house_area[1, 0] + 1, house_area[0, 1], ENDY - 1, house_area[1, 1], blocks = 'air')
GEO.placeVolume(house_area[0, 0] + 1, STARTY, house_area[1, 0] + 1, house_area[0, 1], house_level - 1, house_area[1, 1], blocks = 'dirt', replace = ['minecraft:air', 'minecraft:water', 'minecraft:lava'])
## build house
