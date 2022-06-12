import random
import numpy as np
import heapq
from gdpc import geometry as GEO
from scipy.signal import convolve2d
from scipy.optimize import linprog
from blueprints import house, lookup_table
from gdpc import direct_interface as di


def get_geography_map(world_slice, STARTX, STARTZ):
    sea_map = (world_slice.heightmaps['OCEAN_FLOOR'] == world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES']).astype(int)
    # 0: land, 1: sea

    # true_height_map = np.zeros(sea_map.shape)
    # for x_index in range(0, true_height_map.shape[0]):
    #     print(x_index)
    #     for z_index in range(0, true_height_map.shape[1]):
    #         print(z_index)
    #         for y_index in range(world_slice.heightmaps['MOTION_BLOCKING_NO_LEAVES'][x_index, z_index] - 1, -1, -1):
    #             block_index = di.getBlock(x_index + STARTX, y_index, z_index + STARTZ)
                
    #             for foundation_category in lookup_table['landscape_foundations']:
    #                 if block_index in lookup_table['landscape_foundations'][foundation_category]:
    #                     true_height_map[x_index, z_index] = y_index + 1
    #                     break

    return sea_map


def pick_starting_location(height_map, sea_map, STARTX, STARTZ, ENDX, ENDZ, height_common):
    pick_location_success = False
    while not pick_location_success:
        x_start = random.randint(STARTX, ENDX)
        z_start = random.randint(STARTZ, ENDZ)
        
        if sea_map[x_start - STARTX, z_start - STARTZ] == 1 and height_common - height_map[x_start - STARTX, z_start - STARTZ] < 3:
            pick_location_success = True
            y_start = height_map[x_start - STARTX, z_start - STARTZ]
    print('Start location: ', x_start, y_start, z_start)
    return x_start, y_start, z_start


def clear_plot(house_area, house_level, STARTY, ENDY):
    # GEO.placeVolume(house_area[0, 0], house_level, house_area[1, 0], house_area[0, 1], house_level + 20, house_area[1, 1], blocks = 'air')
    GEO.placeVolume(house_area[0, 0], house_level - 3, house_area[1, 0], house_area[0, 1], house_level - 1, house_area[1, 1], blocks = 'cobblestone')


def build_road(STARTX, STARTZ, ENDX, ENDZ, distance_score_paths, next_building_location, height_map, house_areas_map, roads):
    # print(distance_score_paths[next_building_location])
    # for point in distance_score_paths[next_building_location]:
    #     print(house_areas_map[point[0] - STARTX, point[1] - STARTZ])
    # input()


    # linear system: minimise terraforming, subject to height gradient less than 2
    # number of variables: equal to lenght of path - 2 (start and finish not counted, used as linear constraint instead)
    # approximate into integer linear system by rounding

    # min sum_1^{k - 1}{t_k}
    objective = np.concatenate([np.ones([len(distance_score_paths[next_building_location])]), np.zeros([len(distance_score_paths[next_building_location])])])
    # objective = np.concatenate([np.zeros([len(distance_score_paths[next_building_location])]), np.zeros([len(distance_score_paths[next_building_location])])])

    constraint_equations = []
    constraint_values = []
    for point_index, point in enumerate(distance_score_paths[next_building_location]):
        # convert t (absolute difference) into x (true height)
        ## -t <= x - h
        constraint_equation_0 = np.zeros([2 * len(distance_score_paths[next_building_location])])
        constraint_equation_0[point_index] = -1
        constraint_equation_0[point_index + len(distance_score_paths[next_building_location])] = -1
        constraint_value_0 = -height_map[point[0] - STARTX, point[1] - STARTZ]
        constraint_equations.append(constraint_equation_0)
        constraint_values.append(constraint_value_0)

        ## -t <= h - x
        constraint_equation_1 = np.zeros([2 * len(distance_score_paths[next_building_location])])
        constraint_equation_1[point_index] = -1
        constraint_equation_1[point_index + len(distance_score_paths[next_building_location])] = 1
        constraint_value_1 = height_map[point[0] - STARTX, point[1] - STARTZ]
        constraint_equations.append(constraint_equation_1)
        constraint_values.append(constraint_value_1)

        if house_areas_map[point[0] - STARTX, point[1] - STARTZ] > 0:
            objective[point_index] = 0

            # road must be at building height
            ## x <= h
            constraint_equation_house_0 = np.zeros([2 * len(distance_score_paths[next_building_location])])
            constraint_equation_house_0[point_index + len(distance_score_paths[next_building_location])] = 1
            constraint_value_house_0 = height_map[point[0] - STARTX, point[1] - STARTZ]
            constraint_equations.append(constraint_equation_house_0)
            constraint_values.append(constraint_value_house_0)

            ## -x <= -h
            constraint_equation_house_1 = np.zeros([2 * len(distance_score_paths[next_building_location])])
            constraint_equation_house_1[point_index + len(distance_score_paths[next_building_location])] = -1
            constraint_value_house_1 = -height_map[point[0] - STARTX, point[1] - STARTZ]
            constraint_equations.append(constraint_equation_house_1)
            constraint_values.append(constraint_value_house_1)

        # ensure height gradient is less than 1
        if point_index > 0:
            # if house_areas_map[point[0] - STARTX, point[1] - STARTZ] > 0 or house_areas_map[distance_score_paths[next_building_location][point_index - 1][0] - STARTX, distance_score_paths[next_building_location][point_index - 1][1] - STARTZ] > 0:
            if point_index > 0:
                ## x_i - x_{i - 1} <= 1
                constraint_equation_2 = np.zeros([2 * len(distance_score_paths[next_building_location])])
                constraint_equation_2[point_index + len(distance_score_paths[next_building_location])] = 1
                constraint_equation_2[point_index + len(distance_score_paths[next_building_location]) - 1] = -1
                constraint_value_2 = 1
                constraint_equations.append(constraint_equation_2)
                constraint_values.append(constraint_value_2)

                ## x_{i - 1} - x_i <= 1
                constraint_equation_3 = np.zeros([2 * len(distance_score_paths[next_building_location])])
                constraint_equation_3[point_index + len(distance_score_paths[next_building_location])] = -1
                constraint_equation_3[point_index + len(distance_score_paths[next_building_location]) - 1] = 1
                constraint_value_3 = 1
                constraint_equations.append(constraint_equation_3)
                constraint_values.append(constraint_value_3)

    # for constraint_index, constraint_equation in enumerate(constraint_equations):
    #     print(constraint_equation)
    #     print(constraint_values[constraint_index])

    road_heights = np.rint(linprog(objective, A_ub = constraint_equations, b_ub = constraint_values).x[len(distance_score_paths[next_building_location]):])
    # print(road_heights)
    # input()

    for point_index, point in enumerate(distance_score_paths[next_building_location]):
        if house_areas_map[point[0] - STARTX, point[1] - STARTZ] == 0:
            road_level = int(road_heights[point_index])
            GEO.placeVolume(point[0], road_level - 1, point[1], point[0], road_level - 1, point[1], blocks = 'cobblestone')
            GEO.placeVolume(point[0], road_level, point[1], point[0], road_level + 4, point[1], blocks = 'air')
            roads.append(point)
            height_map[point[0] - STARTX, point[1] - STARTZ] = road_level
        adjacent_road_points = get_adjacent_points(point[0], point[1], STARTX, STARTZ, ENDX, ENDZ)
        for adjacent_road_point in adjacent_road_points:
            if house_areas_map[adjacent_road_point[0] - STARTX, adjacent_road_point[1] - STARTZ] == 0:
                road_level = int(road_heights[point_index])
                GEO.placeVolume(adjacent_road_point[0], road_level - 1, adjacent_road_point[1], adjacent_road_point[0], road_level - 1, adjacent_road_point[1], blocks = 'cobblestone')
                GEO.placeVolume(adjacent_road_point[0], road_level, adjacent_road_point[1], adjacent_road_point[0], road_level + 4, adjacent_road_point[1], blocks = 'air')
                roads.append(adjacent_road_point)
                height_map[adjacent_road_point[0] - STARTX, adjacent_road_point[1] - STARTZ] = road_level

    return roads, height_map


def pick_plot(house_size, height_map, house_areas_map, STARTX, STARTZ, ENDX, ENDZ, x_start, y_start, z_start):
    convolution_array = np.ones(house_size)
    look_area = np.array([[max(STARTX, min(x_start - house_size[0] + 1, ENDX - house_size[0] + 1)), min(ENDX, max(x_start + house_size[0] - 1, STARTX + house_size[0] - 1))], [max(STARTZ, min(z_start - house_size[1] + 1, ENDZ - house_size[1] + 1)), min(ENDZ, max(z_start + house_size[1] - 1, STARTZ + house_size[1] - 1))]])
    look_area_height_map = height_map[(look_area[0, 0] - STARTX):(look_area[0, 1] - STARTX + 1), (look_area[1, 0] - STARTZ):(look_area[1, 1] - STARTZ + 1)]
    look_area_house_map = house_areas_map[(look_area[0, 0] - STARTX):(look_area[0, 1] - STARTX + 1), (look_area[1, 0] - STARTZ):(look_area[1, 1] - STARTZ + 1)]
    look_area_height_map_gradient = np.abs(look_area_height_map - y_start) + look_area_house_map * 10000

    try:
        look_area_height_map_convolved = convolve2d(look_area_height_map_gradient, convolution_array, mode = 'valid')
    except:
        print(look_area_height_map_gradient)
        print(convolution_array)

    convolved_index = np.unravel_index(np.argmin(look_area_height_map_convolved), look_area_height_map_convolved.shape)
    house_area = np.array([[look_area[0, 0] + convolved_index[0], look_area[0, 0] + convolved_index[0] + house_size[0] - 1], [look_area[1, 0] + convolved_index[1], look_area[1, 0] + convolved_index[1] + house_size[1] - 1]])
    print(x_start, y_start, z_start)
    print(look_area)
    print('house area: ', house_area)
    house_level = y_start

    return house_area, house_level


def get_adjacent_points(point_x, point_z, STARTX, STARTZ, ENDX, ENDZ):
    adjacent_point_list = []
    if point_x > STARTX:
        adjacent_point_list.append([point_x - 1, point_z])
    if point_x < ENDX:
        adjacent_point_list.append([point_x + 1, point_z])
    if point_z > STARTZ:
        adjacent_point_list.append([point_x, point_z - 1])
    if point_z < ENDZ:
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


def get_distance_score_map(sea_map, surface_map, house_areas, roads, STARTX, STARTZ, ENDX, ENDZ, seafaring_cost = 5, base_edge_cost = 1, edge_weight = 1):
    ## score map
    score_map = np.full(sea_map.shape, fill_value = -1)

    ### get edge costs
    #### get sea edge costs
    sea_edge_0 = (np.absolute(sea_map[1:] - sea_map[:-1]) == 1).astype(int)
    sea_edge_1 = (np.absolute(sea_map[:, 1:] - sea_map[:, :-1]) == 1).astype(int)

    surface_edge_0 = np.absolute(surface_map[1:] - surface_map[:-1]) + sea_edge_0 * seafaring_cost
    surface_edge_1 = np.absolute(surface_map[:, 1:] - surface_map[:, :-1]) + sea_edge_1 * seafaring_cost

    edge_costs = [surface_edge_0, surface_edge_1]
    ### run dijkstra
    paths = {}
    #### initialise point stack
    point_stack = []
    for house_area in house_areas:
        score_map[house_area[0, 0] - STARTX:house_area[0, 1] - STARTX + 1, house_area[1, 0] - STARTZ:house_area[1, 1] - STARTZ + 1] = 0
        #!! assumption: all buildings are rectangular
        for x_house in range(house_area[0, 0], house_area[0, 1] + 1):
            if x_house == house_area[0, 0] or x_house == house_area[0, 1]:
                for z_house in range(house_area[1, 0], house_area[1, 1] + 1):
                    point_stack.append((0, x_house, z_house, [(x_house, z_house)]))
            else:
                point_stack.append((0, x_house, house_area[1, 0], [(x_house, house_area[1, 0])]))
                point_stack.append((0, x_house, house_area[1, 1], [(x_house, house_area[1, 1])]))
    for road_point in roads:
        score_map[road_point[0] - STARTX, road_point[1] - STARTZ] = 0
        point_stack.append((0, road_point[0], road_point[1], [(road_point[0], road_point[1])]))
    heapq.heapify(point_stack)
    #### pop from point stack
    while len(point_stack) > 0:
        next_point = heapq.heappop(point_stack)
        adjacent_point_list = np.asarray(get_adjacent_points(next_point[1], next_point[2], STARTX, STARTZ, ENDX, ENDZ))
        adjacent_point_differential = adjacent_point_list - np.array([next_point[1], next_point[2]])
        for adjacent_point_index, adjacent_point in enumerate(adjacent_point_list):
            new_cost = get_path_cost(next_point[1] - STARTX, next_point[2] - STARTZ, adjacent_point_differential[adjacent_point_index], edge_costs) * edge_weight + base_edge_cost + next_point[0]
            
            if score_map[adjacent_point[0] - STARTX, adjacent_point[1] - STARTZ] == -1 or score_map[adjacent_point[0] - STARTX, adjacent_point[1] - STARTZ] > new_cost:
                old_point = (score_map[adjacent_point[0] - STARTX, adjacent_point[1] - STARTZ], adjacent_point[0], adjacent_point[1], next_point[3])
                new_point = (new_cost, adjacent_point[0], adjacent_point[1], next_point[3] + [(adjacent_point[0], adjacent_point[1])])
                if old_point in point_stack:
                    point_stack[point_stack.index(old_point)] = new_point
                else:
                    heapq.heappush(point_stack, new_point)
                heapq.heapify(point_stack)
                score_map[adjacent_point[0] - STARTX, adjacent_point[1] - STARTZ] = new_cost
                paths[(adjacent_point[0], adjacent_point[1])] = next_point[3] + [(adjacent_point[0], adjacent_point[1])]

    return score_map, paths


def verify_build_area(house_area, house_map, STARTX, STARTZ):
    if house_map[house_area[0, 0] - STARTX, house_area[1, 0] - STARTZ] > 0 or house_map[house_area[0, 0] - STARTX, house_area[1, 1] - STARTZ] or house_map[house_area[0, 1] - STARTX, house_area[1, 0] - STARTZ] or house_map[house_area[0, 1] - STARTX, house_area[1, 1] - STARTZ]:
        return False
    else:
        return True


# orientation: [0/1, 0/1/2/3]
def build_house(house_area, house_level, orientation, house_id):
    house_object = house(house_id)
    blueprint = house_object.get_blueprint(house_area, house_level, orientation)

    for block_key in blueprint:
        point_list = blueprint[block_key]
        GEO.placeFromList(point_list, block_key)


def group_heights(height_map, sea_map):
    heights = {}
    height_lengths = {}
    for height in np.unique(height_map):
        heights[height] = np.stack(np.where(np.logical_and(height == height_map, sea_map == 0)), axis = -1)
        height_lengths[height] = len(heights[height])
    
    return heights, height_lengths