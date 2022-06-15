from support_util import load_as_blueprint
from gdpc import direct_interface as di
import numpy as np


# read a house as blueprint

# ## starter_dirt
# house_area = np.asarray([[-130, -122], [95, 103]])
# house_level = 1
# house_level_max = 5

# ## starter_sandstone
# house_area = np.asarray([[114, 122], [65, 73]])
# house_level = 2
# house_level_max = 6
# house_level_base = 1

# ## 1b_0
# house_area = np.asarray([[90, 98], [-2, 6]])
# house_level = 1
# house_level_max = 10

# ## 1b_1
# house_area = np.asarray([[97, 105], [-34, -26]])
# house_level = 1
# house_level_max = 10

# ## 1b_2
# house_area = np.asarray([[101, 109], [8, 16]])
# house_level = 1
# house_level_max = 8

# ## 1b_3
# house_area = np.asarray([[-468, -462], [-9, -3]])
# house_level = 1
# house_level_max = 8

# ## 1b_4
# house_area = np.asarray([[-209, -203], [-254, -246]])
# house_level = 1
# house_level_max = 8

# ## 1b_5 GDMC 5
# house_area = np.asarray([[-3, 3], [-200, -187]])
# house_level = 1
# house_level_max = 11

# ## 1b_6 GDMC 5
# house_area = np.asarray([[39, 45], [-255, -249]])
# house_level = 1
# house_level_max = 4

# ## 1b_7 GDMC 5
# house_area = np.asarray([[25, 31], [-245, -238]])
# house_level = 1
# house_level_max = 5

# ## 1b_8 GDMC 5
# house_area = np.asarray([[-11, -3], [-244, -235]])
# house_level = 1
# house_level_max = 8

## 1b_9 GDMC 5
house_area = np.asarray([[-29, -21], [-230, -224]])
house_level = 1
house_level_max = 6

# ## 2b_0
# house_area = np.asarray([[101, 109], [-2, 6]])
# house_level = 1
# house_level_max = 10

# ## 2b_1
# house_area = np.asarray([[90, 98], [51, 65]])
# house_level = 1
# house_level_max = 7

# ## 2b_2
# house_area = np.asarray([[-432, -423], [24, 31]])
# house_level = 1
# house_level_max = 7

# ## 2b_3
# house_area = np.asarray([[-447, -438], [17, 29]])
# house_level = 1
# house_level_max = 6

# # large_0
# house_area = np.asarray([[-190, -178], [-91, -77]])
# house_level = 1
# house_level_max = 24

# # grand_0
# house_area = np.asarray([[-453, -405], [-493, -459]])
# house_level = 7
# house_level_max = 40

blueprint = load_as_blueprint(house_area, house_level, house_level_max, house_level_base = 1)

blueprint_file = open("blueprint.txt", "w")
print(blueprint, file = blueprint_file)
blueprint_file.close()
