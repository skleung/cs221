from enum import Enum
from collections import Counter

VICTORY_POINTS_TO_WIN = 10
SETTLEMENT_VICTORY_POINTS = 1
CITY_VICTORY_POINTS = SETTLEMENT_VICTORY_POINTS + 1

NUM_INITIAL_SETTLEMENTS = 2
TOTAL_NUM_AGENTS = 10
CUTOFF_TURNS = 600

VERBOSE = False

DEFAULT_PLAYER_ARRAY = [7,0]

ACTIONS = Enum(["SETTLE", "CITY", "ROAD"])

ResourceTypes = Enum(["BRICK", "WOOL", "ORE", "GRAIN", "LUMBER" ,"NOTHING"])

# Resource costs of a Road, a Settlement, and a City
ROAD_COST = Counter({ResourceTypes.BRICK: 1, ResourceTypes.LUMBER: 1})
SETTLEMENT_COST = Counter({ResourceTypes.LUMBER: 1, ResourceTypes.BRICK: 1, ResourceTypes.WOOL: 1, ResourceTypes.GRAIN: 1})
CITY_COST = Counter({ResourceTypes.GRAIN: 2, ResourceTypes.ORE: 3})

# A dictionary from resource type (enum, above) to string representation
# so we can print out the resource type easily
ResourceDict = {ResourceTypes.GRAIN:"G", ResourceTypes.WOOL:"W", ResourceTypes.ORE:"O", ResourceTypes.LUMBER:"L", ResourceTypes.BRICK:"B", ResourceTypes.NOTHING:"N"}
NUM_PLAYERS = 2
NUM_ITERATIONS = 4
DEPTH = 3

# Types of Agents
AGENT = Enum(["PLAYER_AGENT", "DICE_AGENT"])

# Set debug mode on or off
DEBUG = True