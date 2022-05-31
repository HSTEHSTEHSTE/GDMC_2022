import random
import numpy as np
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
    GEO.placeVolume(house_area[0, 0], house_level, house_area[1, 0], house_area[0, 1], ENDY - 1, house_area[1, 1], blocks = 'air')
    GEO.placeVolume(house_area[0, 0], STARTY, house_area[1, 0], house_area[0, 1], house_level - 1, house_area[1, 1], blocks = 'dirt', replace = ['minecraft:air', 'minecraft:water', 'minecraft:lava'])


def pick_plot(house_size, height_map, STARTX, STARTZ, x_start, y_start, z_start):
    convolution_array = np.ones(house_size)
    look_area = np.array([[max(STARTX, x_start - house_size[0] + 1), min(STARTX + height_map.shape[0], x_start + house_size[0] - 1 + 1)], [max(STARTZ, z_start - house_size[1] + 1), min(STARTZ + height_map.shape[1], z_start + house_size[1] - 1 + 1)]])
    look_area_height_map = height_map[(look_area[0, 0] - STARTX):(look_area[0, 1] - STARTX), (look_area[1, 0] - STARTZ):(look_area[1, 1] - STARTZ)]
    look_area_height_map_gradient = look_area_height_map - y_start
    print(look_area_height_map_gradient.shape)
    look_area_height_map_convolved = convolve2d(np.abs(look_area_height_map_gradient), convolution_array, mode = 'valid')

    convolved_index = np.unravel_index(np.argmin(look_area_height_map_convolved), look_area_height_map_convolved.shape)
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