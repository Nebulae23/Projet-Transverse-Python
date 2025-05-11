"""
Magic Survivor - Configuration and settings

This module contains all the configuration settings for the game, including
screen dimensions, color definitions, file paths, and other constants.
"""

import os
import pygame

# Game title
GAME_TITLE = "Magic Survivor"

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
FPS = 60

# Color definitions
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
BRIGHT_BLUE = (0, 170, 255)
BRIGHT_GREEN = (0, 220, 0)

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Asset directories
FONT_DIR = os.path.join(ASSETS_DIR, 'fonts')
SOUND_DIR = os.path.join(ASSETS_DIR, 'sounds')
SPRITE_DIR = os.path.join(ASSETS_DIR, 'sprites')
EFFECTS_DIR = os.path.join(SOUND_DIR, 'effects')
MUSIC_DIR = os.path.join(SOUND_DIR, 'music')

# Sprite directories
PLAYER_SPRITES = os.path.join(SPRITE_DIR, 'player')
ENEMY_SPRITES = os.path.join(SPRITE_DIR, 'enemies')
PROJECTILE_SPRITES = os.path.join(SPRITE_DIR, 'projectiles')
ITEM_SPRITES = os.path.join(SPRITE_DIR, 'items')
BUILDING_SPRITES = os.path.join(SPRITE_DIR, 'city_buildings')
UI_SPRITES = os.path.join(SPRITE_DIR, 'ui_elements')

# Data file paths
SPELLS_DATA = os.path.join(DATA_DIR, 'spells.json')
RELICS_DATA = os.path.join(DATA_DIR, 'relics.json')
ENEMIES_DATA = os.path.join(DATA_DIR, 'enemies.json')
WAVES_DATA = os.path.join(DATA_DIR, 'waves.json')
BUILDINGS_DATA = os.path.join(DATA_DIR, 'city_buildings.json')
PLAYER_SAVE = os.path.join(DATA_DIR, 'player_save.json')
WORLD_MAP_DATA = os.path.join(DATA_DIR, 'world_map.json')

# Game settings
DEBUG_MODE = True  # Enable/disable debug features
EDITOR_MODE = False # Enable/disable editor mode by default

# Time settings
DAY_DURATION = 60  # Seconds for daytime on world map
NIGHT_DURATION = 120 # Seconds for night combat phase (can also be wave-based)
MAX_DAYS = 30  # Maximum number of days (for game completion)

# Player settings
PLAYER_SPEED = 3.0  # Pixels per second (intended base, scaled by dt*60 in movement)
PLAYER_BASE_HP = 100.0
PLAYER_BASE_ATTACK_DAMAGE = 10
PLAYER_BASE_ATTACK_COOLDOWN = 0.5  # in seconds
PLAYER_BASE_XP = 0
PLAYER_XP_PER_LEVEL = 100
PLAYER_MAX_MANA = 100
PLAYER_MANA_REGEN = 1

# Enemy settings
ENEMY_SPAWN_INTERVAL = 1.5  # in seconds
ENEMY_BASE_POWER = 10  # Base power value for enemies
ENEMY_POWER_SCALE = 1.5  # Power scaling multiplier per day
MAX_ENEMIES = 50  # Maximum enemies in a night

# City settings
CITY_BASE_DEFENSE = 0  # Base defense without buildings
CITY_MAX_BUILDINGS = 20  # Maximum buildings in a city
CITY_GRID_SIZE = 5  # Grid size for city layout
CITY_MAX_HP = 500
CITY_WALL_THICKNESS = 20
CITY_WALL_COLOR = (100, 100, 100)

# Projectile Settings
DEFAULT_PROJECTILE_SPEED = 300 # Default speed for projectiles if not specified in spell data
DEFAULT_PROJECTILE_RANGE = 500 # Default range for projectiles if not specified in spell data

# Resource settings
STARTING_RESOURCES = {
    "wood": 100,
    "stone": 50
}
RESOURCE_PRODUCTION_INTERVAL = 60  # Resource production interval in seconds

# World map settings
WORLD_MAP_WIDTH = 100  # Width in tiles
WORLD_MAP_HEIGHT = 100  # Height in tiles
TILE_SIZE_MAP_DISPLAY = 32  # Size of each tile in pixels for the main map view
MINIMAP_SCALE_FACTOR = 0.1  # 10% of the main map size
MINIMAP_BACKGROUND_COLOR = (50, 50, 50, 200)  # Semi-transparent dark gray
MINIMAP_BORDER_COLOR = WHITE
MINIMAP_BORDER_THICKNESS = 1
MINIMAP_PLAYER_COLOR = RED
MINIMAP_CITY_COLOR = BLUE
MINIMAP_CHUNK_SIZE = 16  # In tile units (e.g., 16x16 tiles per chunk)
MINIMAP_UNDISCOVERED_COLOR = (20, 20, 20, 255) # Very dark gray, opaque

# Tile Graphics Settings (for main map view)
TILE_SPRITE_DIMENSIONS = (32, 32) # Pixel dimensions for each tile sprite (e.g., for loading/scaling)
TILE_SPRITE_PATHS = {
    "grass": [
        "assets/sprites/tiles/grass_var1.png",
        "assets/sprites/tiles/grass_var2.png",
        "assets/sprites/tiles/grass_var3.png"
    ],
    "water": ["assets/sprites/tiles/water.png"],
    "sand": [
        "assets/sprites/tiles/sand_var1.png",
        "assets/sprites/tiles/sand_var2.png"
    ],
    "mountain": ["assets/sprites/tiles/mountain.png"],
    "forest": [
        "assets/sprites/tiles/forest_var1.png",
        "assets/sprites/tiles/forest_var2.png",
        "assets/sprites/tiles/forest_var3.png",
        "assets/sprites/tiles/forest_var4.png"
    ],
    "city_center": ["assets/sprites/tiles/city_center.png"]
}
DEFAULT_TILE_SPRITE_FALLBACK_COLOR = MAGENTA # Fallback for tile types not in TILE_SPRITE_PATHS
MISSING_TILE_SPRITE_FALLBACK_COLOR = RED # Fallback for sprites in TILE_SPRITE_PATHS but not loadable
TILE_VARIATION_NOISE_SCALE = 0.1 # Scaling factor for Perlin noise in tile variation
TILE_VARIATION_SEED = 12345 # Seed for Perlin noise generation for tile variations

# Static Prop Settings
PROP_SPRITE_DIMENSIONS = { # Example dimensions, adjust as needed
    "small_rock": (16, 16),
    "medium_rock": (24, 24),
    "bush": (32, 32),
    "dead_tree": (32, 64),
    "generic_tree_01": (64, 96), # Larger tree
    "generic_tree_02": (48, 80)  # Medium tree
}
PROP_SPRITE_PATHS = {
    "small_rock": "assets/sprites/props/small_rock.png",
    "medium_rock": "assets/sprites/props/medium_rock.png",
    "bush": "assets/sprites/props/bush.png",
    "dead_tree": "assets/sprites/props/dead_tree.png",
    "generic_tree_01": "assets/sprites/props/generic_tree_01.png",
    "generic_tree_02": "assets/sprites/props/generic_tree_02.png",
}
MISSING_PROP_SPRITE_COLOR = ORANGE # Fallback color for missing prop sprites

# Resource Node Settings
RESOURCE_NODE_SPRITE_PATHS = {
    "ore_vein_iron": "assets/sprites/nodes/ore_vein_iron.png",
    "ore_vein_iron_depleted": "assets/sprites/nodes/ore_vein_iron_depleted.png",
    "ancient_tree_wood": "assets/sprites/nodes/ancient_tree.png",
    "ancient_tree_wood_depleted": "assets/sprites/nodes/ancient_tree_wood_depleted.png"
}
# RESOURCE_NODE_SPRITE_DIMENSIONS = {} # Optional, define if specific scaling needed per node

RESOURCE_NODE_TYPES = {
    "ore_vein_iron": {
        "display_name": "Iron Vein",
        "resource_type": "iron",
        "yield_min": 10,
        "yield_max": 25,
        "durability": 3,
        "cooldown": 60, # Seconds before it can be harvested again (if not depleted)
        "interaction_prompt": "Press E to mine Iron",
        "depleted_sprite_suffix": "_depleted" # Used by DataHandler to find the right sprite key
    },
    "ancient_tree_wood": {
        "display_name": "Ancient Tree",
        "resource_type": "wood",
        "yield_min": 20,
        "yield_max": 50,
        "durability": 1, 
        "cooldown": 300, 
        "interaction_prompt": "Press E to chop Wood",
        "depleted_sprite_suffix": "_depleted"
    }
}
MISSING_NODE_SPRITE_COLOR = (128, 0, 128) # Purple fallback for missing node sprites

# --- Points of Interest (POI) Settings ---
POI_SPRITE_PATHS = {
    "abandoned_shrine": "assets/sprites/pois/shrine_placeholder.png", # Placeholder path
    "monster_den": "assets/sprites/pois/den_placeholder.png",       # Placeholder path
    "ancient_ruin": "assets/sprites/pois/ruin_placeholder.png"      # Placeholder path
}

POI_SPRITE_DIMENSIONS = { # Example dimensions, adjust as needed
    "abandoned_shrine": (32, 48),
    "monster_den": (48, 48),
    "ancient_ruin": (64, 64)
}

MISSING_POI_SPRITE_COLOR = (255, 105, 180) # Hot pink fallback

POI_DEFINITIONS = {
    "abandoned_shrine": {
        "display_name": "Abandoned Shrine",
        "interaction_prompt": "Press E to investigate",
        "base_sprite_key": "abandoned_shrine", # Assumes key in POI_SPRITE_PATHS
        # "looted_sprite_key": "abandoned_shrine_looted", # Example for state change
        "loot_table_id": "shrine_common_loot", 
        "xp_reward": 50,
        "one_time_interaction": True,
        "world_map_icon_path": "assets/sprites/ui_elements/minimap_icons/shrine_icon.png" # Placeholder
    },
    "monster_den": {
        "display_name": "Monster Den",
        "interaction_prompt": "Press E to enter",
        "base_sprite_key": "monster_den",
        "entry_cooldown": 300, 
        "linked_encounter_id": "den_encounter_1", 
        "world_map_icon_path": "assets/sprites/ui_elements/minimap_icons/den_icon.png" # Placeholder
    },
    "ancient_ruin": {
        "display_name": "Ancient Ruin",
        "interaction_prompt": "Press E to explore",
        "base_sprite_key": "ancient_ruin",
        "loot_table_id": "ruin_rare_loot",
        "xp_reward": 100,
        "one_time_interaction": False, # Example: could be repeatable with cooldown
        "explore_cooldown": 600,
        "world_map_icon_path": "assets/sprites/ui_elements/minimap_icons/ruin_icon.png" # Placeholder
    }
}

# --- Editor Settings ---
FONT_NAME = "Arial"
FONT_SIZE_STANDARD = 24
FONT_SIZE_LARGE = 32
FONT_SIZE_SMALL = 18
MESSAGE_DURATION = 3  # seconds
DEFAULT_TEXT_COLOR = WHITE
TEXT_INPUT_BG_COLOR = GRAY
TEXT_INPUT_BORDER_COLOR = DARK_GRAY
TEXT_INPUT_WIDTH = 300
TEXT_INPUT_HEIGHT = 40
TEXT_CURSOR_COLOR = WHITE
TEXT_CURSOR_BLINK_RATE = 500  # milliseconds
PREDEFINED_UPGRADE_PROPERTIES = [
    "damage_multiplier", "cooldown_reduction", "projectile_speed",
    "area_of_effect", "duration", "pierce_count", "chain_count",
    "homing_strength", "orbit_radius", "orbit_speed", "wave_amplitude",
    "wave_frequency", "health_bonus", "mana_bonus", "movement_speed_bonus"
]

# Day/Night Cycle
DAY_DURATION = 60  # seconds

# --- Interaction ---
INTERACTION_DISTANCE_THRESHOLD = 48 # Approx 1.5 tiles (32 * 1.5)
KEY_INTERACT = pygame.K_f 