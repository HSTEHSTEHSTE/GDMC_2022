# GDMC 2022 Submission - Henry Li

Welcome to Henry Li's GDMC 2022 submission!

## Overview

Our settlement generation procedure simulates the process in which a group of human players would settle a new area in Minecraft. We aim to capture the early settlement process, where players build rudimentary shelters with the appropriate amount of stylistic decorations (specifically, in the style of village houses) while more importantly satisfying the utility requirements of early shelters (equipped with bed(s), chests, crafting tables and furnaces). As the settlement progresses, more ambitious buildings may be added to the settlement, including enchantment tables and simple iron farms. Most of our settlement buildings are constructed out of simple building materials which would be available in the inventory of any player who's been spending enough time in their Minecraft world.

## Reading the map

The build area is a 256 $\times$ 256 $\times$ 256 array that is very inefficient to read. This issue is amplified by the long response time of the HTTP interface mod which this submission depends on. As such, we have to rely on Minecraft's in-house chunk information in order to get a decent representation of the map.

We use the in-house "motion blocking no leaves" height map as the basis for our height map. As buildings and roads are added, the height map is adjusted accordingly. We also make use of a sea map which affects our building and road location choices. The sea map is calculated by comparing the "motion blocking no leaves" height map with the height map with the "ocean floor" height map.

We attempted to produce a corrected version of the height map which would account for non-geographic features such as logs, generated structures, among other things. Unfortunately, the overhead of such a procedure would be prohibitive.

## Choice of starting location

The first player to jump into the map constructs a "starter house", a simple hut from simple materials that provides shelter for the first player. In our imaginary scenario, the first player in the group teleports to a new location. They subsequently seek to build the starter house at the most common altitude level in the area, in order to facilitate further construction. The process of choosing the starting location is very haphazard, as any Minecraft player would attest to.

## Choice of subsequent building locations

Subsequent buildings are constructed on plots of land that are in relative proximity to existing buildings while also being at similar altitudes. We achieve this by performing a breadth (distance)-first search, starting from existing buildings. The distance is a combination of horizontal distance and height gradient. We thus locate points on the map that are close to existing buildings (while not being too close as to induce claustrophobia), while also not being too much of a hike to reach.

Based on the chosen point, we look at all the possible plots which would contain said point. The plots are chosen to minimise terraforming - excessive modifications to the landscape. This process is performed efficiently using convolution.

Performing a breadth-first search on the entire map is computationally expensive. As such, we perform early stopping in order to save time. This occasionally results in the failure to find a point that satisfy the requirements, resulting in the early stopping threshold increasing. We selected threshold values which are a reasonable trade-off between success rate and performance, while also increasing our threshold slowly during settlement generation to account for the increasing difficulty in location appropriate plots of land as the number of buildings increase.

## Choice of subsequent buildings

Beyond the starter house/hut, the vast majority of the subsequent buildings are small, 1-story houses that have just enough space to satisfy the utility requirements. Occasionally larger buildings would be generated, with more living quarters and space for communal activity (larger chests as well as villager job tables). On most occasions a grand diorite iron farm would be generated, the culmination of the group's activity in the area. The iron farm can only be generated once. On rare occasions an additional starter hut might be generated.

## Construction of buildings

We observe that in GDPC the efficiency of geometric or list-based construction functions are the same as that of placing blocks individually. As such, we save our building blueprints in dictionary format (as block_key, point_list pairs) and read them during run time.

## Road network

We aim to simulate the spontaneous nature of road building which typical player-built road systems exhibit. Each time a building is added to a settlement, a new road is constructed to connect it with either anther building or the existing road network. The road follows the shortest path that our breadth-first search produced during selection of building location. We use linear programming to ensure that roads doesn't have a height gradient more than 1 at any adjacent blocks under most circumstances (a problematic scenario which would prevent roads from being walkable) while also minimising the amount of terraforming needed.

Roads are kept one block above any body of water whenever possible, so that the waterway would still be navigable. We place a small penalty on roads that cross over water.

## Run instructions

Run main.py to generate a settlement. main.py does not take any command line parameters; instead, important parameters can be found at the top of main.py and the user is invited to tune those parameters to their liking.

### Dependencies

main.py requires a running instance of JAVA-edition Minecraft with the target Minecraft open in-game. The Minecraft client should be of version 1.16.5 and should have the [Minecraft HTTP Interface mod](https://github.com/nilsgawlik/gdmc_http_interface) version 0.4.2 installed. main.py is dependent on the [Generative Design Python Client](https://github.com/nilsgawlik/gdmc_http_client_python), version 5.0. Notable 3rd party dependencies are Numpy and Scipy (for convolution operations and linear optimisation).
