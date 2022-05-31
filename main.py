import numpy as np
import time
from utils import clear_plot, pick_starting_location, pick_plot, get_distance_socre_map
from gdpc import interface as INTF
from gdpc import worldLoader as WL

time_start = time.time()
STARTX, STARTY, STARTZ, ENDX, ENDY, ENDZ = INTF.requestPlayerArea(dx = 128, dz = 128)
print("Build area: ", STARTX, STARTY, STARTZ, ENDX, ENDY, ENDZ)

WORLDSLICE = WL.WorldSlice(STARTX, STARTZ, ENDX + 1, ENDZ + 1)
def get_geography_map(world_slice):
    sea_map = (world_slice.heightmaps['OCEAN_FLOOR'] == world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES']).astype(int)
    # 1: land, 0: sea
    return sea_map

height_map = np.minimum(WORLDSLICE.heightmaps['OCEAN_FLOOR'], WORLDSLICE.heightmaps['MOTION_BLOCKING_NO_LEAVES'])
surface_map = WORLDSLICE.heightmaps['MOTION_BLOCKING_NO_LEAVES']

sea_map = get_geography_map(WORLDSLICE)


# pick starting position
x_start, y_start, z_start = pick_starting_location(height_map, sea_map, STARTX, STARTZ, ENDX, ENDZ)
# build starter house
house_size = (9, 9)
## locate starter plot
house_area, house_level = pick_plot(house_size, height_map, STARTX, STARTZ, x_start, y_start, z_start)
## clear plot
clear_plot(house_area, house_level, STARTY, ENDY)
## build house

## display elapsed time
time_starter_house = time.time()
print("Starter house build: ", time_starter_house - time_start)


# build settlement
get_distance_socre_map(sea_map, surface_map, house_area, STARTX, STARTZ, ENDX, ENDZ)
