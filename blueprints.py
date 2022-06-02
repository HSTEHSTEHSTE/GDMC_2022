class house:
    def __init__(self, id):
        assert id in ids
        self.id = id
        self.blueprint = blueprints[self.id]
        self.sizes = sizes[self.id]
        self.centre_point = ((self.sizes[0] - 1) / 2, (self.sizes[1] - 1) / 2)
        self.centre_line = (self.sizes[0] - 1) / 2

    # orientation: [0/1, 0/1/2/3]
    def get_blueprint(self, house_area, orientation):
        # face positive z direction
        front = orientation[1]
        back = (orientation[1] + 2) % 4
        left = (orientation[1] - 1 + orientation[0] * 2) % 4
        right = (orientation[1] + 1 + orientation[0] * 2) % 4

        # check size fit
        assert (house_area[0, 1] - house_area[0, 0] + 1) == self.sizes[orientation[1] % 2]
        assert (house_area[1, 1] - house_area[1, 0] + 1) == self.sizes[(orientation[1] - 1) % 2]

        # spin blueprint
        blueprint = self.blueprint       
        if orientation[0] == 1:
            blueprint = spin_mirror(blueprint, self.centre_line)
        if orientation[1] > 0:
            blueprint = spin_counterclockwise(blueprint, self.centre_point, orientation[1])

        return blueprint


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
    'starter_dirt': {
        'dirt': [(1, 0, 1), (2, 0, 1), (3, 0, 1), (4, 0, 1), (5, 0, 1), (6, 0, 1), (7, 0, 1), (1, 1, 1), (2, 1, 1), (3, 1, 1), (4, 1, 1), (5, 1, 1), (6, 1, 1), (7, 0, 2), (7, 0, 3), (7, 0, 4), (7, 0, 5), (7, 0, 6), (7, 0, 7), (7, 1, 2), (7, 1, 3), (7, 1, 4), (7, 1, 5), (7, 1, 6), (7, 1, 7), (1, 0, 7), (2, 0, 7), (3, 0, 7), (4, 0, 7), (5, 0, 7), (6, 0, 7), (1, 1, 7), (2, 1, 7), (3, 1, 7), (4, 1, 7), (5, 1, 7), (6, 1, 7), (1, 0, 3), (1, 0, 4), (1, 0, 5), (1, 0, 6), (1, 1, 3), (1, 1, 4), (1, 1, 5), (1, 1, 6)],
        'wooden_door': [(1, 0, 2), (1, 1, 2)]
    }
}

# x, z, y
sizes = {
    'starter_dirt': (9, 9, 5)
}