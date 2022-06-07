class house:
    def __init__(self, id):
        assert id in ids
        self.id = id
        self.blueprint = blueprints[self.id]
        self.sizes = sizes[self.id]
        self.centre_point = ((self.sizes[0] - 1) / 2, (self.sizes[1] - 1) / 2)
        self.centre_line = (self.sizes[0] - 1) / 2

    # orientation: [0/1, 0/1/2/3]
    def get_blueprint(self, house_area, house_level, orientation):
        # face positive z direction
        front = orientation[1]
        back = (orientation[1] + 2) % 4
        left = (orientation[1] - 1 + orientation[0] * 2) % 4
        right = (orientation[1] + 1 + orientation[0] * 2) % 4

        # check size fit
        assert (house_area[0, 1] - house_area[0, 0] + 1) == self.sizes[orientation[1] % 2]
        assert (house_area[1, 1] - house_area[1, 0] + 1) == self.sizes[(orientation[1] - 1) % 2]

        # move blueprint in place and spin blueprint
        blueprint = move_blueprint(self.blueprint, house_area, house_level)
        if orientation[0] == 1:
            blueprint = spin_mirror(blueprint, self.centre_line)
        if orientation[1] > 0:
            blueprint = spin_counterclockwise(blueprint, self.centre_point, orientation[1])

        return blueprint


def move_blueprint(blueprint, house_area, house_level):
    new_blueprint = {}
    for block_key in blueprint:
        point_list = []
        for point in blueprint[block_key]:
            point_list.append((point[0] + house_area[0, 0], point[1] + house_level, point[2] + house_area[1, 0]))
        new_blueprint[block_key] = point_list
    return new_blueprint


def spin_mirror(blueprint, centre_line):
    new_blueprint = {}
    for block_key in blueprint:
        point_list = []
        for point in blueprint[block_key]:
            point_list.append((centre_line * 2 - point[0], point[1], point[2]))
        new_blueprint[block_key] = point_list
    return new_blueprint


def spin_counterclockwise(blueprint, centre_point, spin_orientation):
    new_blueprint = {}
    if spin_orientation == 0:
        return blueprint
    elif spin_orientation == 1:
        for block_key in blueprint:
            point_list = []
            for point in blueprint[block_key]:
                point_list.append((centre_point[1] * 2 - point[2], point[1], point[0]))
            new_blueprint[block_key] = point_list
    elif spin_orientation == 2:
        for block_key in blueprint:
            point_list = []
            for point in blueprint[block_key]:
                point_list.append((centre_point[0] * 2 - point[0], point[1], centre_point[1] * 2 - point[2]))
            new_blueprint[block_key] = point_list
    elif spin_orientation == 3:
        for block_key in blueprint:
            point_list = []
            for point in blueprint[block_key]:
                point_list.append((point[2], point[1], centre_point[0] * 2 - point[0]))
            new_blueprint[block_key] = point_list
    return new_blueprint


ids = ['starter_dirt']

# x, y, z
blueprints = {
    # 'starter_dirt': {
    #     'dirt[]': [(1, 0, 1), (1, 0, 2), (1, 0, 3), (1, 0, 4), (1, 0, 5), (1, 0, 6), (1, 0, 7), (1, 1, 1), (1, 1, 2), (1, 1, 6), (1, 1, 7), (1, 2, 1), (1, 2, 2), (1, 2, 3), (1, 2, 4), (1, 2, 5), (1, 2, 6),
    #         (1, 2, 7), (1, 3, 1), (1, 3, 2), (1, 3, 3), (1, 3, 4), (1, 3, 5), (1, 3, 6), (1, 3, 7), (2, 0, 7), (2, 1, 7), (2, 2, 1), (2, 2, 7), (2, 3, 1), (2, 3, 2), (2, 3, 3), (2, 3, 4), (2, 3, 5),
    #         (2, 3, 6), (2, 3, 7), (3, 0, 1), (3, 0, 7), (3, 1, 1), (3, 1, 7), (3, 2, 1), (3, 2, 7), (3, 3, 1), (3, 3, 2), (3, 3, 3), (3, 3, 4), (3, 3, 5), (3, 3, 6), (3, 3, 7), (4, 0, 1), (4, 0, 7),
    #         (4, 1, 7), (4, 2, 1), (4, 2, 7), (4, 3, 1), (4, 3, 2), (4, 3, 3), (4, 3, 4), (4, 3, 5), (4, 3, 6), (4, 3, 7), (5, 0, 1), (5, 0, 7), (5, 1, 7), (5, 2, 1), (5, 2, 7), (5, 3, 1), (5, 3, 2),
    #         (5, 3, 3), (5, 3, 4), (5, 3, 5), (5, 3, 6), (5, 3, 7), (6, 0, 1), (6, 0, 7), (6, 1, 1), (6, 1, 7), (6, 2, 1), (6, 2, 7), (6, 3, 1), (6, 3, 2), (6, 3, 3), (6, 3, 4), (6, 3, 5), (6, 3, 6),
    #         (6, 3, 7), (7, 0, 1), (7, 0, 2), (7, 0, 3), (7, 0, 4), (7, 0, 5), (7, 0, 6), (7, 0, 7), (7, 1, 1), (7, 1, 2), (7, 1, 6), (7, 1, 7), (7, 2, 1), (7, 2, 2), (7, 2, 3), (7, 2, 4), (7, 2, 5),
    #         (7, 2, 6), (7, 2, 7), (7, 3, 1), (7, 3, 2), (7, 3, 3), (7, 3, 4), (7, 3, 5), (7, 3, 6), (7, 3, 7)],
    #     'glass_pane[east=false,north=true,south=true,waterlogged=false,west=false]': [(1, 1, 3), (1, 1, 4), (1, 1, 5), (7, 1, 3), (7, 1, 4), (7, 1, 5)],
    #     'glass_pane[east=true,north=false,south=false,waterlogged=false,west=true]': [(4, 1, 1), (5, 1, 1)],
    #     'oak_door[facing=north,half=lower,hinge=left,open=true,powered=false]': [(2, 0, 1)],
    #     'oak_door[facing=north,half=upper,hinge=left,open=true,powered=false]': [(2, 1, 1)],
    #     'torch[]': [(4, 4, 4)],
    #     'wall_torch[facing=north]': [(4, 1, 6)],
    #     'white_bed[facing=south,occupied=false,part=foot]': [(5, 0, 4)],
    #     'white_bed[facing=south,occupied=false,part=head]': [(5, 0, 5)]
    # }
    'starter_dirt': {
        'dirt[]': [(1, 0, 1), (1, 0, 2), (1, 0, 3), (1, 0, 4), (1, 0, 5), (1, 0, 6), (1, 0, 7), (1, 1, 1), (1, 1, 2), (1, 1, 6), (1, 1, 7), (1, 2, 1), (1, 2, 2), (1, 2, 3), (1, 2, 4), (1, 2, 5), (1, 2, 6),
            (1, 2, 7), (1, 3, 1), (1, 3, 2), (1, 3, 3), (1, 3, 4), (1, 3, 5), (1, 3, 6), (1, 3, 7), (2, 0, 7), (2, 1, 7), (2, 2, 1), (2, 2, 7), (2, 3, 1), (2, 3, 2), (2, 3, 3), (2, 3, 4), (2, 3, 5),
            (2, 3, 6), (2, 3, 7), (3, 0, 1), (3, 0, 7), (3, 1, 1), (3, 1, 7), (3, 2, 1), (3, 2, 7), (3, 3, 1), (3, 3, 2), (3, 3, 3), (3, 3, 4), (3, 3, 5), (3, 3, 6), (3, 3, 7), (4, 0, 1), (4, 0, 7),
            (4, 1, 7), (4, 2, 1), (4, 2, 7), (4, 3, 1), (4, 3, 2), (4, 3, 3), (4, 3, 4), (4, 3, 5), (4, 3, 6), (4, 3, 7), (5, 0, 1), (5, 0, 7), (5, 1, 7), (5, 2, 1), (5, 2, 7), (5, 3, 1), (5, 3, 2),
            (5, 3, 3), (5, 3, 4), (5, 3, 5), (5, 3, 6), (5, 3, 7), (6, 0, 1), (6, 0, 7), (6, 1, 1), (6, 1, 7), (6, 2, 1), (6, 2, 7), (6, 3, 1), (6, 3, 2), (6, 3, 3), (6, 3, 4), (6, 3, 5), (6, 3, 6),
            (6, 3, 7), (7, 0, 1), (7, 0, 2), (7, 0, 3), (7, 0, 4), (7, 0, 5), (7, 0, 6), (7, 0, 7), (7, 1, 1), (7, 1, 2), (7, 1, 6), (7, 1, 7), (7, 2, 1), (7, 2, 2), (7, 2, 3), (7, 2, 4), (7, 2, 5),
            (7, 2, 6), (7, 2, 7), (7, 3, 1), (7, 3, 2), (7, 3, 3), (7, 3, 4), (7, 3, 5), (7, 3, 6), (7, 3, 7)],
        'glass_pane[]': [(1, 1, 3), (1, 1, 4), (1, 1, 5), (7, 1, 3), (7, 1, 4), (7, 1, 5), (4, 1, 1), (5, 1, 1)],
        'oak_door[facing=north,half=lower,hinge=left,open=true,powered=false]': [(2, 0, 1)],
        'oak_door[facing=north,half=upper,hinge=left,open=true,powered=false]': [(2, 1, 1)],
        'torch[]': [(4, 4, 4)],
        'wall_torch[facing=north]': [(4, 1, 6)],
        'white_bed[facing=south,occupied=false,part=foot]': [(5, 0, 4)],
        'white_bed[facing=south,occupied=false,part=head]': [(5, 0, 5)]
    }
}

# x, z, y
sizes = {
    'starter_dirt': (9, 9, 5)
}



# lookup
lookup_table = {
    'landscape_foundations': {
        # all natural occurring stone, not including cobblestone
        'stone': ['minecraft:stone', 'minecraft_diorite', 'minecraft_andesite', 'minecraft_bedrock', 'minecraft:bone_block', 'minecraft:end_stone', 'minecraft:granite', 'minecraft:infested_cobblestone'],
        'ore': ['minecraft:coal_ore', 'minecraft:diamond_ore', 'minecraft:emerald_ore', 'minecraft:gold_ore', 'minecraft:iron_ore', 'minecraft:lapis_ore', 'minecraft:mossy_cobblestone'],
        'dirt': ['minecraft:coarse_dirt', 'minecraft:dirt', 'minecraft:farmland', 'minecraft:grass_block', 'minecraft:grass_path', 'minecraft:gravel', 'minecraft:mycelium', 'minecraft:sand', 'minecraft:sandstone'],
        'ice': ['minecraft:blue_ice', 'minecraft:frosted_ice', 'minecraft:ice', 'minecraft:packed_ice']
    }
}