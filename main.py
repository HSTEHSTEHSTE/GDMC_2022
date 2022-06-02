import numpy as np
import time
from utils import clear_plot, pick_starting_location, pick_plot, get_distance_score_map, verify_build_area, build_road, build_house
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
house_areas = []
roads = []
house_areas_map = np.zeros(sea_map.shape)


# pick starting position
x_start, y_start, z_start = pick_starting_location(height_map, sea_map, STARTX, STARTZ, ENDX, ENDZ)
# build starter house
house_size = (9, 9)
## locate starter plot
house_area, house_level = pick_plot(house_size, height_map, house_areas_map, STARTX, STARTZ, ENDX, ENDZ, x_start, y_start, z_start)
## clear plot
clear_plot(house_area, house_level, STARTY, ENDY)
## build house
build_house(house_area, house_level, [0, 0], 'starter_dirt')
## update maps
sea_map[house_area[0, 0] - STARTX:house_area[0, 1] + 1 - STARTX, house_area[1, 0] - STARTZ:house_area[1, 1] + 1 - STARTZ] = 1
height_map[house_area[0, 0] - STARTX:house_area[0, 1] + 1 - STARTX, house_area[1, 0] - STARTZ:house_area[1, 1] + 1 - STARTZ] = house_level
surface_map[house_area[0, 0] - STARTX:house_area[0, 1] + 1 - STARTX, house_area[1, 0] - STARTZ:house_area[1, 1] + 1 - STARTZ] = house_level
house_areas_map[house_area[0, 0] - STARTX:house_area[0, 1] + 1 - STARTX, house_area[1, 0] - STARTZ:house_area[1, 1] + 1 - STARTZ] = 1
## display elapsed time
time_starter_house = time.time()
print("Starter house built: ", time_starter_house - time_start)


# build settlement
house_areas.append(house_area)
sea_build_cost = 100
## iterate over settlement number
for i in range(3):
    flat_distance_score_map, _ = get_distance_score_map(sea_map, np.zeros(surface_map.shape), house_areas, [], STARTX, STARTZ, ENDX, ENDZ, seafaring_cost = 0)
    distance_score_map, distance_score_paths = get_distance_score_map(sea_map, surface_map, house_areas, roads, STARTX, STARTZ, ENDX, ENDZ)
    build_limits = np.where(flat_distance_score_map >= 15, distance_score_map, 9999)
    build_score_map = build_limits + sea_build_cost * (np.ones(sea_map.shape) - sea_map)

    next_building_location = np.unravel_index(build_limits.argmin(), build_score_map.shape)
    next_building_location = (next_building_location[0] + STARTX, next_building_location[1] + STARTZ)

    house_size = (9, 9)

    ### locate plot
    house_area, house_level = pick_plot(house_size, height_map, house_areas_map, STARTX, STARTZ, ENDX, ENDZ, next_building_location[0], height_map[next_building_location[0] - STARTX, next_building_location[1] - STARTZ], next_building_location[1])

    if not verify_build_area(house_area, house_areas_map, STARTX, STARTZ):
        print("House area not verified!")

    ### clear plot
    clear_plot(house_area, house_level, STARTY, ENDY)
    house_areas.append(house_area)

    ### build house
    build_house(house_area, house_level, [0, 0], 'starter_dirt')

    ### update maps

    sea_map[house_area[0, 0] - STARTX:house_area[0, 1] + 1 - STARTX, house_area[1, 0] - STARTZ:house_area[1, 1] + 1 - STARTZ] = 1
    height_map[house_area[0, 0] - STARTX:house_area[0, 1] + 1 - STARTX, house_area[1, 0] - STARTZ:house_area[1, 1] + 1 - STARTZ] = house_level
    surface_map[house_area[0, 0] - STARTX:house_area[0, 1] + 1 - STARTX, house_area[1, 0] - STARTZ:house_area[1, 1] + 1 - STARTZ] = house_level
    house_areas_map[house_area[0, 0] - STARTX:house_area[0, 1] + 1 - STARTX, house_area[1, 0] - STARTZ:house_area[1, 1] + 1 - STARTZ] = 1

    ### build roads

    for point in distance_score_paths[next_building_location]:
        if house_areas_map[point[0] - STARTX, point[1] - STARTZ] == 0:
            road_level = height_map[point[0] - STARTX, point[1] - STARTZ]
            build_road(point, road_level, STARTY, ENDY)
            roads.append(point)

    ### display elapsed time
    time_house = time.time()
    print("House ", i, " built: ", time_house - time_start)
