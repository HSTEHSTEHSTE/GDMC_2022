import numpy as np
import time
from utils import clear_plot, pick_starting_location, pick_plot, get_distance_score_map, verify_build_area, build_road, build_house, get_geography_map, group_heights, choose_house_type
from gdpc import interface as INTF
from gdpc import worldLoader as WL
from blueprints import sizes, categories
import random


## Parameters
build_area_size_x = 256
build_area_size_z = 256
time_limit = 300 #seconds
house_weights = {
    'small': 7,
    'large': 3,
    'starter': .5,
    'grand': 3
}
house_type_limits = {
    'grand': 1
}


time_start = time.time()
STARTX, STARTY, STARTZ, ENDX, ENDY, ENDZ = INTF.requestPlayerArea(dx = build_area_size_x, dz = build_area_size_z)
print("Build area: ", STARTX, STARTY, STARTZ, ENDX, ENDY, ENDZ)

WORLDSLICE = WL.WorldSlice(STARTX, STARTZ, ENDX, ENDZ)

height_map = np.minimum(WORLDSLICE.heightmaps['OCEAN_FLOOR'], WORLDSLICE.heightmaps['MOTION_BLOCKING_NO_LEAVES'])
surface_map = WORLDSLICE.heightmaps['MOTION_BLOCKING_NO_LEAVES']
sea_map = get_geography_map(WORLDSLICE, STARTX, STARTZ)
heights, height_lengths = group_heights(height_map, sea_map)
height_common = max(height_lengths, key = height_lengths.get)
height_map = WORLDSLICE.heightmaps['MOTION_BLOCKING_NO_LEAVES']

time_read_map = time.time()
print("Map read: ", time_read_map - time_start)
house_areas = []
roads = []
house_areas_map = np.zeros(sea_map.shape)
house_type_counter = {}

# pick starting position
x_start, y_start, z_start = pick_starting_location(height_map, sea_map, STARTX, STARTZ, ENDX, ENDZ, height_common)
# build starter house
## choose house
starter_house_id = random.choice(categories['starter'])
house_size = (sizes[starter_house_id][0], sizes[starter_house_id][1])
## locate starter plot
house_area, house_level = pick_plot(house_size, height_map, house_areas_map, sea_map, STARTX, STARTZ, ENDX, ENDZ, x_start, y_start, z_start)
## clear plot
clear_plot(house_area, house_level, STARTY, ENDY)
## build house
build_house(house_area, house_level, [0, 0], starter_house_id)
## update maps
sea_map[house_area[0, 0] - STARTX:house_area[0, 1] + 1 - STARTX, house_area[1, 0] - STARTZ:house_area[1, 1] + 1 - STARTZ] = 1
height_map[house_area[0, 0] - STARTX:house_area[0, 1] + 1 - STARTX, house_area[1, 0] - STARTZ:house_area[1, 1] + 1 - STARTZ] = house_level
surface_map[house_area[0, 0] - STARTX:house_area[0, 1] + 1 - STARTX, house_area[1, 0] - STARTZ:house_area[1, 1] + 1 - STARTZ] = house_level
house_areas_map[house_area[0, 0] - STARTX:house_area[0, 1] + 1 - STARTX, house_area[1, 0] - STARTZ:house_area[1, 1] + 1 - STARTZ] = 1
## display elapsed time
time_house = time.time()
print("Starter house built: ", time_house - time_start)


# build settlement
house_areas.append(house_area)
sea_build_cost = 20000
## iterate over settlement number
# for i in range(3):
i = 0
while (time_house - time_start) < time_limit:
    i += 1

    ### choose house type
    house_type = choose_house_type(house_weights)[0]
    # house_type = 'grand'
    if house_type in house_type_limits:
        if house_type not in house_type_counter:
            house_type_counter[house_type] = 1
        else:
            house_type_counter[house_type] += 1
        if house_type_counter[house_type] >= house_type_limits[house_type]:
            house_weights[house_type] = 0

    house_id = random.choice(categories[house_type])
    house_size = (sizes[house_id][0], sizes[house_id][1])
    # house_size = (sizes['grand_0'][0], sizes['grand_0'][1])

    ### locate house position
    flat_distance_score_map, _ = get_distance_score_map(sea_map, np.zeros(surface_map.shape), house_areas, [], STARTX, STARTZ, ENDX, ENDZ, seafaring_cost = 0)
    distance_score_map, distance_score_paths = get_distance_score_map(sea_map, surface_map, house_areas, roads, STARTX, STARTZ, ENDX, ENDZ)
    build_limits = np.where(flat_distance_score_map >= np.amax(np.asarray(house_size) * 2), distance_score_map, 9999999)
    build_score_map = build_limits + sea_build_cost * (np.ones(sea_map.shape) - sea_map) + abs(height_map - height_common) * 3

    next_building_location = np.unravel_index(build_score_map.argmin(), build_score_map.shape)
    next_building_location = (next_building_location[0] + STARTX, next_building_location[1] + STARTZ)

    ### locate plot
    house_area, house_level = pick_plot(house_size, height_map, house_areas_map, sea_map, STARTX, STARTZ, ENDX, ENDZ, next_building_location[0], height_map[next_building_location[0] - STARTX, next_building_location[1] - STARTZ], next_building_location[1], house_type = house_type)

    if not verify_build_area(house_area, house_areas_map, STARTX, STARTZ):
        print("House area not verified!")

    ### clear plot
    clear_plot(house_area, house_level, STARTY, ENDY)
    house_areas.append(house_area)

    ### build house
    build_house(house_area, house_level, [0, 0], house_id)
    # build_house(house_area, house_level, [0, 0], 'grand_0')

    ### update maps
    sea_map[house_area[0, 0] - STARTX:house_area[0, 1] + 1 - STARTX, house_area[1, 0] - STARTZ:house_area[1, 1] + 1 - STARTZ] = 1
    height_map[house_area[0, 0] - STARTX:house_area[0, 1] + 1 - STARTX, house_area[1, 0] - STARTZ:house_area[1, 1] + 1 - STARTZ] = house_level
    surface_map[house_area[0, 0] - STARTX:house_area[0, 1] + 1 - STARTX, house_area[1, 0] - STARTZ:house_area[1, 1] + 1 - STARTZ] = house_level
    house_areas_map[house_area[0, 0] - STARTX:house_area[0, 1] + 1 - STARTX, house_area[1, 0] - STARTZ:house_area[1, 1] + 1 - STARTZ] = 1

    ### build roads
    roads, height_map, house_areas_map = build_road(STARTX, STARTZ, ENDX, ENDZ, distance_score_paths, next_building_location, height_map, house_areas_map, roads)

    ### display elapsed time
    time_house = time.time()
    print("House ", i, "built: ", time_house - time_start)
