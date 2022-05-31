import random
import numpy as np
import heapq
from gdpc import geometry as GEO
from scipy.signal import convolve2d


def pick_starting_location(height_map, sea_map, STARTX, STARTZ, ENDX, ENDZ):
    pick_location_success = False
    while not pick_location_success:
        x_start = random.randint(STARTX, ENDX)
        z_start = random.randint(STARTZ, ENDZ)
        
        if sea_map[x_start - STARTX, z_start - STARTZ] == 1:
            pick_location_success = True
            y_start = height_map[x_start - STARTX, z_start - STARTZ]
    print('Start location: ', x_start, y_start, z_start)
    return x_start, y_start, z_start


def clear_plot(house_area, house_level, STARTY, ENDY):
    GEO.placeVolume(house_area[0, 0], house_level, house_area[1, 0], house_area[0, 1], 150, house_area[1, 1], blocks = 'air')
    GEO.placeVolume(house_area[0, 0], STARTY, house_area[1, 0], house_area[0, 1], house_level - 1, house_area[1, 1], blocks = 'dirt', replace = ['minecraft:air', 'minecraft:water', 'minecraft:lava'])


def pick_plot(house_size, height_map, house_areas_map, STARTX, STARTZ, x_start, y_start, z_start):
    convolution_array = np.ones(house_size)
    look_area = np.array([[max(STARTX, x_start - house_size[0] + 1), min(STARTX + height_map.shape[0], x_start + house_size[0] - 1 + 1)], [max(STARTZ, z_start - house_size[1] + 1), min(STARTZ + height_map.shape[1], z_start + house_size[1] - 1 + 1)]])
    look_area_height_map = height_map[(look_area[0, 0] - STARTX):(look_area[0, 1] - STARTX), (look_area[1, 0] - STARTZ):(look_area[1, 1] - STARTZ)]
    look_area_house_map = house_areas_map[(look_area[0, 0] - STARTX):(look_area[0, 1] - STARTX), (look_area[1, 0] - STARTZ):(look_area[1, 1] - STARTZ)]
    look_area_height_map_gradient = np.abs(look_area_height_map - y_start)
    look_area_height_map_convolved = convolve2d(look_area_height_map_gradient, convolution_array, mode = 'valid')

    convolved_index = np.unravel_index(np.argmin(look_area_height_map_convolved), look_area_height_map_convolved.shape)
    print(look_area_height_map_gradient, look_area_height_map_convolved, convolved_index)
    house_area = np.array([[look_area[0, 0] + convolved_index[0], look_area[0, 0] + convolved_index[0] + house_size[0] - 1], [look_area[1, 0] + convolved_index[1], look_area[1, 0] + convolved_index[1] + house_size[1] - 1]])
    print('house area: ', house_area)
    house_level = y_start

    return house_area, house_level


def get_adjacent_points(point_x, point_z, STARTX, STARTZ, ENDX, ENDZ):
    adjacent_point_list = []
    if point_x > STARTX:
        adjacent_point_list.append([point_x - 1, point_z])
    if point_x <= ENDX:
        adjacent_point_list.append([point_x + 1, point_z])
    if point_z > STARTZ:
        adjacent_point_list.append([point_x, point_z - 1])
    if point_z <= ENDZ:
        adjacent_point_list.append([point_x, point_z + 1])
    return adjacent_point_list


def get_path_cost(point_x, point_z, differential, edge_costs):
    if differential[0] != 0:
        if differential[0] == 1:
            return edge_costs[0][point_x, point_z]
        else:
            return edge_costs[0][point_x - 1, point_z]
    else:
        if differential[1] == 1:
            return edge_costs[1][point_x, point_z]
        else:
            return edge_costs[1][point_x, point_z - 1]


def get_distance_socre_map(sea_map, surface_map, house_areas, STARTX, STARTZ, ENDX, ENDZ):
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
    for house_area in house_areas:
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

    return score_map
