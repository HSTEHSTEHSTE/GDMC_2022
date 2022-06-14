# GDMC 2022 Submission - Henry Li

Welcome to Henry Li's GDMC 2022 submission!

## Overview

Our settlement generation procedure simulates the process in which a group of human players would settle a new area in Minecraft. We aim to capture the early settlment process, where players build rudimentary shelters with the appropriate amount of stylistic decorations (specifically, in the style of village houses) while more importantly satisfying the utility requirements of early shelters (equiped with bed(s), chests, crafting tables and furnaces). As the settlement progresses, more ambitious buildings may be added to the settlement, including enchantment tables and simple iron farms. Most of our settlement buildings are constructed out of simple building materials which would be available in the inventory of any player who's been spending enough time in their Minecraft world.

## Choice of location

The first player to jump into the map constructs a "starter house", a simple hut from simple materials that provides shelter for the first player. Subsequent buildings are clustered around the starter house, seeking plots of land that are in relative proximity to existing buildings while also being at similar altitudes. The plots are also chosen to minimise terraforming - excessive modifications to the landscape.

## Choice of subsequent buildings

Beyond the starter house/hut, the vast majority of the subsequent buildings are small, 1-story houses that have just enough space to satisfy the utility requirements. Occasionally larger buildings would be generated, with more living quarters and space for communal activity (larger chests as well as villager job tables). On most occasions a grand diorite iron farm would be generated, the culmination of the group's activity in the area. The iron farm can only be generated once.

## Road network

We aim to simulate the spontaneous nature of road building which typical player-built road systems exhibit. Each time a building is added to a settlement, a new road is constructed to connect it with either anther building or the existing road network. A linear programming system ensures that the road doesn't have a height gradient more than 1 at any adjacent blocks under most circumstances (a problematic scenario which would prevent the roads from being walkable) while also minimising the amount of terraforming needed.