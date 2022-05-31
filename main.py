import numpy as np
import time
import heapq
from utils import clear_plot, pick_starting_location, pick_plot, get_adjacent_points, get_path_cost
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
## score map
score_map = np.full(sea_map.shape, fill_value = -1)
seafaring_cost = 5
base_edge_cost = 1

### get edge costs
#### get sea edge costs
sea_edge_0 = (np.absolute(sea_map[1:] - sea_map[:-1]) == 1).astype(int)
sea_edge_1 = (np.absolute(sea_map[:, 1:] - sea_map[:, :-1]) == 1).astype(int)

surface_edge_0 = np.absolute(surface_map[1:] - surface_map[:-1]) + sea_edge_0 * seafaring_cost
surface_edge_1 = np.absolute(surface_map[:, 1:] - surface_map[:, :-1]) + sea_edge_1 * seafaring_cost

edge_costs = [surface_edge_0, surface_edge_1]
### run dijkstra
score_map[house_area[0, 0] - STARTX + 1: house_area[0, 1] - STARTX + 1, house_area[1, 0] - STARTZ + 1: house_area[1, 1] - STARTZ + 1] = 0
#!! assumption: all buildings are rectangular
#### initialise point stack
point_stack = []
for x_house in range(house_area[0, 0], house_area[0, 1] + 1):
    if x_house == house_area[0, 0] or x_house == house_area[0, 1]:
        for y_house in range(house_area[1, 0], house_area[1, 1] + 1):
            point_stack.append((0, x_house, y_house))
    else:
        point_stack.append((0, x_house, house_area[1, 0]))
        point_stack.append((0, x_house, house_area[1, 1]))
heapq.heapify(point_stack)
#### pop from point stack
while len(point_stack) > 0:
    next_point = heapq.heappop(point_stack)
    adjacent_point_list = np.asarray(get_adjacent_points(next_point[1], next_point[2], STARTX, STARTZ, ENDX, ENDZ))
    adjacent_point_differential = adjacent_point_list - np.array([next_point[1], next_point[2]])
    for adjacent_point_index, adjacent_point in enumerate(adjacent_point_list):
        new_cost = get_path_cost(next_point[1] - STARTX, next_point[2] - STARTZ, adjacent_point_differential[adjacent_point_index], edge_costs) + base_edge_cost + next_point[0]
        
        if score_map[adjacent_point[0] - STARTX, adjacent_point[1] - STARTZ] == -1 or score_map[adjacent_point[0] - STARTX, adjacent_point[1] - STARTZ] > new_cost:
            old_point = (score_map[adjacent_point[0] - STARTX, adjacent_point[1] - STARTZ], adjacent_point[0], adjacent_point[1])
            new_point = (new_cost, adjacent_point[0], adjacent_point[1])
            if old_point in point_stack:
                point_stack[point_stack.index(old_point)] = new_point
            else:
                heapq.heappush(point_stack, new_point)
            heapq.heapify(point_stack)
            score_map[adjacent_point[0] - STARTX, adjacent_point[1] - STARTZ] = new_cost

