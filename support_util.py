from gdpc.direct_interface import getBlock, runCommand
import requests
import pprint
from requests.exceptions import ConnectionError


def get_block_with_state(x, y, z):
    """**Return the block ID from the world**."""
    url = f'http://localhost:9000/blocks?x={x}&y={y}&z={z}&includeState=true'
    try:
        response = requests.get(url).text
    except ConnectionError:
        return "minecraft:void_air"
    return response


# all boundaries inclusive
def load_as_blueprint(house_area, house_level, house_level_max):
    blueprint = {}

    for x in range(house_area[0, 0], house_area[0, 1] + 1):
        for y in range(house_level, house_level_max + 1):
            for z in range(house_area[1, 0], house_area[1, 1] + 1):
                block = get_block_with_state(x, y, z)[10:]
                
                if block != 'air[]':
                    if block in blueprint:
                        blueprint[block].append((x - house_area[0, 0], y - house_level, z - house_area[1, 0]))
                    else:
                        blueprint[block] = [(x - house_area[0, 0], y - house_level, z - house_area[1, 0])]

    pp = pprint.PrettyPrinter(depth = 4, width = 200, compact = True)
    pp.pprint(blueprint)
    return blueprint
