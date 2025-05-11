"""
Magic Survivor - World Map

This module provides the world map state for the game, representing the 
overworld where the player can explore and access the city.
"""

import pygame
import math
import random
import os
import typing
from src import config
from src.game_state_base import GameState
from src.camera import Camera
from src.tilemap import TileMap
from src.player_character import Player
from src.data_handler import DataHandler
from src.enemy_system import EnemyManager
from src.ui_manager import Button, TextBox, ProgressBar
from src.projectile_system import ProjectileManager
from src.static_prop import StaticProp
from src.resource_node import ResourceNode
from src.global_ui_manager import GlobalUIManager
from src.point_of_interest import PointOfInterest

if typing.TYPE_CHECKING:
    from src.game_manager import GameManager
    from src.city_interior import CityInteriorState
    from src.night_phase import NightPhaseState

class CityLocation:
    """Class representing the city on the world map"""
    
    def __init__(self, x, y, size=5):
        """Initialize the city location
        
        Args:
            x (int): X position in tile coordinates
            y (int): Y position in tile coordinates
            size (int): Size of the city in tiles (diameter in tiles)
        """
        self.x = x # Tile X of top-left corner of city area
        self.y = y # Tile Y of top-left corner of city area
        self.size = size # City diameter in tiles
        self.center_x = x + size // 2 # Center tile X
        self.center_y = y + size // 2 # Center tile Y
        
        # Use config.TILE_SIZE_MAP_DISPLAY for pixel calculations
        current_tile_size = config.TILE_SIZE_MAP_DISPLAY
        
        # Create the city bounding rect (in pixel coordinates)
        self.rect = pygame.Rect(
            x * current_tile_size, 
            y * current_tile_size, 
            size * current_tile_size, 
            size * current_tile_size
        )
        
        # Entry point: Center of the city (in tile coordinates)
        self.entry_point = (self.center_x, self.center_y) # MODIFIED
        
        # Entry distance: Covers the city's rect + wall thickness
        self.entry_distance = (self.rect.width / 2) + config.CITY_WALL_THICKNESS + 50 # MODIFIED: Increased by 50 pixels
    
    def is_player_in_range(self, player_x, player_y):
        """Check if the player is in range to enter the city
        
        Args:
            player_x (float): Player's x position in pixel coordinates
            player_y (float): Player's y position in pixel coordinates
            
        Returns:
            bool: True if in range, False otherwise
        """
        # Convert entry_point (tile coords) to pixel coordinates
        entry_pixel_x = self.entry_point[0] * config.TILE_SIZE_MAP_DISPLAY
        entry_pixel_y = self.entry_point[1] * config.TILE_SIZE_MAP_DISPLAY
        
        # Calculate distance
        dx = player_x - entry_pixel_x
        dy = player_y - entry_pixel_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        return distance <= self.entry_distance
    
    def render(self, screen, camera=None):
        """Render the city
        
        Args:
            screen (pygame.Surface): Screen to render to
            camera (Camera): Camera for scrolling
        """
        # Draw city outline
        rect_to_draw = self.rect.copy() # Use self.rect which is in world pixels
        if camera:
            rect_to_draw = camera.apply_rect(rect_to_draw)
        
        pygame.draw.rect(screen, (150, 150, 200), rect_to_draw) # City base color
        pygame.draw.rect(screen, (100, 100, 150), rect_to_draw, 3) # City border
        
        # Draw some building shapes for visual representation (camera applied)
        for i in range(3):
            building_width = rect_to_draw.width // 5
            building_height = rect_to_draw.height // 3
            building_rect = pygame.Rect(
                rect_to_draw.x + rect_to_draw.width // 4 * i + 10,
                rect_to_draw.y + 10,
                building_width,
                building_height
            )
            pygame.draw.rect(screen, (120, 100, 80), building_rect)
            pygame.draw.rect(screen, (80, 60, 40), building_rect, 2)
        
        # Draw entry point visual cue (was previously using hardcoded 32 for tile size)
        # This visual cue is less important if entry is entire city area, but can be kept or removed.
        # For now, let's keep it, centered on the new entry_point (city center in tiles).
        entry_pixel_x_vis = self.entry_point[0] * config.TILE_SIZE_MAP_DISPLAY
        entry_pixel_y_vis = self.entry_point[1] * config.TILE_SIZE_MAP_DISPLAY
        
        if camera:
            entry_pixel_x_vis, entry_pixel_y_vis = camera.apply_point(entry_pixel_x_vis, entry_pixel_y_vis)
        
        pygame.draw.circle(screen, (200, 200, 50), (entry_pixel_x_vis, entry_pixel_y_vis), 8)
        pygame.draw.circle(screen, (150, 150, 0), (entry_pixel_x_vis, entry_pixel_y_vis), 8, 2)

        renderable_objects = []
        
        # Add static props
        renderable_objects.extend(self.static_props_list)
        
        # Add resource nodes
        renderable_objects.extend(self.resource_nodes_list)
        
        # Add points of interest
        renderable_objects.extend(self.points_of_interest_list) # ADDED
        
        # Add player
        if self.player: # Ensure player exists
            renderable_objects.append(self.player)
            
        # Add enemies during nighttime
        if not self.is_day and self.enemy_manager:
            # Convert pygame sprite group to a list of enemy objects for rendering
            active_enemies = self.enemy_manager.get_enemies().sprites()
            renderable_objects.extend(active_enemies)

        # Sort objects by their Y-coordinate (bottom of sprite for pseudo-3D effect)
        # Requires each object to have a get_render_sort_key() method
        try:
            renderable_objects.sort(key=lambda obj: obj.get_render_sort_key())
        except AttributeError as e:
            print(f"Warning: An object in renderable_objects is missing get_render_sort_key method: {e}")
            # Fallback: render unsorted or handle error
        
        # Render sorted objects
        for obj in renderable_objects:
            try:
                obj.render(screen, self.camera) # CHANGED: display_surface to screen
            except AttributeError as e:
                print(f"Warning: An object in renderable_objects is missing render method or has incompatible signature: {e}")
            except Exception as e:
                print(f"Error rendering object {obj}: {e}")

        # Projectiles - typically rendered on top or based on their own logic
        self.projectile_manager.render(screen, self.camera) # CHANGED: display_surface to screen
                
        # Day/Night cycle overlay (optional, if you have one)
        # Example: self.day_night_cycle.render(screen) # COMMENTED: Also changed to screen if used
        
        # UI elements (on top of everything)
        # Draw time remaining
        time_str = self.get_time_remaining_str()
        time_text = self.font_small.render(time_str, True, config.WHITE)
        screen.blit(time_text, (10, 10))
        
        # Draw day number
        day_text = self.font_small.render(f"Day: {self.player_data['day']}", True, config.WHITE)
        screen.blit(day_text, (config.SCREEN_WIDTH - day_text.get_width() - 10, 10))

        # Draw player XP bar at bottom
        if self.player:
            xp_bar_width = config.SCREEN_WIDTH - 40
            xp_bar_height = 20
            xp_bar_x = 20
            xp_bar_y = config.SCREEN_HEIGHT - xp_bar_height - 10
            
            # Calculate current XP for level
            current_level_xp = self.player.calculate_xp_for_level(self.player.level)
            prev_level_xp = self.player.calculate_xp_for_level(self.player.level - 1) if self.player.level > 1 else 0
            
            xp_in_current_level = self.player.xp - prev_level_xp
            xp_needed_for_level = current_level_xp - prev_level_xp
            
            xp_ratio = 0
            if xp_needed_for_level > 0:
                xp_ratio = min(1, xp_in_current_level / xp_needed_for_level)

            # Background
            pygame.draw.rect(screen, config.DARK_GRAY, (xp_bar_x, xp_bar_y, xp_bar_width, xp_bar_height))
            # Foreground (XP fill)
            pygame.draw.rect(screen, config.YELLOW, (xp_bar_x, xp_bar_y, xp_bar_width * xp_ratio, xp_bar_height))
            # Border
            pygame.draw.rect(screen, config.WHITE, (xp_bar_x, xp_bar_y, xp_bar_width, xp_bar_height), 2)

            xp_text_str = f"XP: {self.player.xp} / {current_level_xp} (Lvl {self.player.level})"
            xp_label = self.font_small.render(xp_text_str, True, config.WHITE)
            screen.blit(xp_label, (xp_bar_x + (xp_bar_width - xp_label.get_width()) // 2, xp_bar_y + (xp_bar_height - xp_label.get_height()) // 2))
        
        # City entry prompt
        if self.show_entry_prompt:
            self.entry_prompt.render(screen) # Render directly to screen as it's UI
            
        # Interaction Prompt (for POIs and Resource Nodes)
        if self.show_interaction_prompt and self.active_interaction_target: # ADDED
            self.interaction_prompt_box.render(screen) # ADDED
        
        # Minimap
        if self.minimap_visible:
            minimap_rect = pygame.Rect(config.SCREEN_WIDTH - self.minimap_width - 10, 30, self.minimap_width, self.minimap_height)
            pygame.draw.rect(screen, config.DARK_GRAY, minimap_rect) 
            pygame.draw.rect(screen, config.WHITE, minimap_rect, 2)  
            screen.blit(self.minimap_surface, minimap_rect.topleft)
        
        # --- Draw City HP Bar if Night ---
        if not self.is_day: # ADDED rendering for city HP at night
            hp_bar_width = 200
            hp_bar_height = 20
            hp_bar_x = (config.SCREEN_WIDTH - hp_bar_width) // 2
            hp_bar_y = 10 # At the top of the screen
            
            current_hp_ratio = 0
            if self.game_manager.city_max_hp > 0 :
                 current_hp_ratio = max(0, self.game_manager.city_current_hp / self.game_manager.city_max_hp)

            pygame.draw.rect(screen, config.DARK_GRAY, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
            pygame.draw.rect(screen, config.RED, (hp_bar_x, hp_bar_y, hp_bar_width * current_hp_ratio, hp_bar_height))
            pygame.draw.rect(screen, config.WHITE, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height), 2)
            
            hp_text_str = f"City HP: {int(self.game_manager.city_current_hp)}/{self.game_manager.city_max_hp}"
            hp_label = self.font_small.render(hp_text_str, True, config.WHITE)
            text_rect = hp_label.get_rect(center=(hp_bar_x + hp_bar_width / 2, hp_bar_y + hp_bar_height / 2))
            screen.blit(hp_label, text_rect)
        # --- END ---

        self.game_manager.global_ui_manager.render(screen)
            
        # Flip the display (done in game_manager.run)
        # pygame.display.flip() # Usually handled by the main game loop

    def get_wall_rects(self): # ADDED METHOD
        """
        Returns a dictionary of pygame.Rect objects representing the city's outer walls.
        Keys are "top", "bottom", "left", "right".
        Rects are in world coordinates.
        """
        wall_thickness = config.CITY_WALL_THICKNESS
        # Main city footprint rect is self.rect

        # Top wall: Starts at self.rect.top, extends for wall_thickness
        top_wall = pygame.Rect(
            self.rect.left - wall_thickness, # Extend to include corners
            self.rect.top - wall_thickness,
            self.rect.width + (2 * wall_thickness),
            wall_thickness
        )
        # Bottom wall: Starts at self.rect.bottom - wall_thickness
        bottom_wall = pygame.Rect(
            self.rect.left - wall_thickness,
            self.rect.bottom, # Starts at the bottom edge of the city area
            self.rect.width + (2 * wall_thickness),
            wall_thickness
        )
        # Left wall: Starts at self.rect.left, extends for wall_thickness
        # Height should not include the top/bottom walls' thickness to avoid double corners,
        # but for simplicity and clear visual, let them overlap slightly for now.
        # Or, adjust height: self.rect.height (city area)
        left_wall = pygame.Rect(
            self.rect.left - wall_thickness,
            self.rect.top, # Starts at the top of the city area
            wall_thickness,
            self.rect.height
        )
        # Right wall: Starts at self.rect.right - wall_thickness
        right_wall = pygame.Rect(
            self.rect.right, # Starts at the right edge of the city area
            self.rect.top,
            wall_thickness,
            self.rect.height
        )
        
        return {
            "top": top_wall,
            "bottom": bottom_wall,
            "left": left_wall,
            "right": right_wall
        }


class WorldMapState(GameState):
    """World map state"""
    
    def __init__(self, game_manager: 'GameManager', load_saved=False):
        """Initialize the world map state
        
        Args:
            game_manager (GameManager): Reference to the game manager
            load_saved (bool): Whether to load saved game data
        """
        super().__init__(game_manager)
        
        # Initialize fonts (example for font_small)
        self.font_small = pygame.font.Font(None, 24) # ADDED
        self.minimap_visible = True # ADDED

        # Load player save data
        self.player_data = DataHandler.load_player_save() if load_saved else {
            "level": 1,
            "xp": 0,
            "city_buildings": {},
            "spells": ["basic_projectile"],
            "relics": [],
            "day": 1,
            "position": {"x": None, "y": None},  # Will be set during setup
            "visited_map_chunks": [], # ADDED: ensure this key exists
            "resources": config.STARTING_RESOURCES.copy() # Ensure it has resources
        }
        if "resources" not in self.player_data: # Ensure loaded saves also have resources
            self.player_data["resources"] = config.STARTING_RESOURCES.copy()
        
        # Set up map
        self.setup_map()
        
        # Create camera
        self.camera = Camera(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        
        # Create player
        player_x = self.player_data["position"]["x"]
        player_y = self.player_data["position"]["y"]
        
        if player_x is None or player_y is None:
            # Position player outside the south wall of city by default (rather than at entry point)
            south_wall_y = self.city.rect.bottom + config.CITY_WALL_THICKNESS + 50 # 50px extra buffer
            player_x = self.city.rect.centerx # Centered horizontally with city
            player_y = south_wall_y
            
            # Update player data
            self.player_data["position"]["x"] = player_x
            self.player_data["position"]["y"] = player_y
        
        self.player = Player(player_x, player_y, self.game_manager)
        
        # Set camera to follow player
        self.camera.set_target(self.player)
        
        # Set camera bounds to map size
        self.camera.set_bounds(0, 0, self.map.pixel_width, self.map.pixel_height)
        
        # Enemy system for nighttime
        self.enemy_manager = EnemyManager()
        # Projectile manager for player attacks on world map
        self.projectile_manager = ProjectileManager(self.game_manager)
        
        # Time of day
        self.is_day = True
        self.day_timer = config.DAY_DURATION
        self.time_scale = 1.0  # For speeding up time if needed
        
        # UI elements for city entrance
        self.entry_prompt = TextBox(
            x=config.SCREEN_WIDTH // 2 - 100,
            y=config.SCREEN_HEIGHT - 100,
            width=200,
            height=50,
            text="Press E to enter city", # Default text
            text_color=config.WHITE,
            background_color=(0, 0, 0, 150),
            border_color=config.WHITE,
            alignment="center"
        )
        self.show_entry_prompt = False

        # UI Element for POI/Resource Node Interaction Prompts
        self.interaction_prompt_box = TextBox(
            x=config.SCREEN_WIDTH // 2 - 150, # Centered
            y=config.SCREEN_HEIGHT - 150,   # Above city entry prompt
            width=300,
            height=40,
            text="", # Will be set dynamically
            font_size=20,
            text_color=config.WHITE,
            background_color=(0, 0, 0, 180), # Slightly more opaque
            border_color=config.LIGHT_GRAY,
            alignment="center"
        )
        self.show_interaction_prompt = False
        self.active_interaction_target = None # Can be a ResourceNode or PointOfInterest
        
        # Minimap related attributes
        self.visited_map_chunks = set()
        self.last_player_chunk_coords = None
        self.static_props_list = []
        self.resource_nodes_list = []
        self.points_of_interest_list = [] # ADDED

        # Setup mini-map (will now use visited_map_chunks)
        self.setup_minimap(load_saved)
        self._setup_props()
        self._setup_resource_nodes()
        self._setup_points_of_interest() # ADDED
        
        # Set up city walls
        self.city_wall_rects = self.city.get_wall_rects() # ADDED: Initialize wall rects
    
    def setup_map(self):
        """Set up the world map"""
        # Create a new tilemap, passing the data_handler for sprite access
        self.map = TileMap(
            config.WORLD_MAP_WIDTH, 
            config.WORLD_MAP_HEIGHT, 
            config.TILE_SIZE_MAP_DISPLAY, # Use display tile size for map logic
            data_handler=self.game_manager.data_handler
        )
        
        # Generate simple colored tiles for testing (acts as fallback if sprites fail)
        # These colors are primarily for the minimap now, or if sprites are missing.
        self.map.generate_simple_tileset({
            "grass": config.GREEN, # Example: Use colors from config for consistency
            "water": config.BLUE,
            "mountain": config.GRAY, # Example: (100,100,100) might be DARK_GRAY
            "forest": (34, 139, 34), # Forest Green
            "sand": config.YELLOW, # Example: (244, 164, 96) Sandy Brown
            "road": config.DARK_GRAY, # Example
            "city_center": config.PURPLE # Example for city base tile if distinct
        })
        
        # Generate a random map using tile type strings defined in config.TILE_SPRITE_PATHS
        # self.world_data in DataHandler should be populated with these tile types.
        # TileMap.set_tile will then use DataHandler to get the correct sprite variation.
        self.map.generate_random_map(
            default_tile="grass", 
            feature_tiles={
                "water": 0.3, # Define prevalence of features
                "forest": 0.3,
                "mountain": 0.2,
                "sand": 0.1
            }, 
            feature_probability=0.15 # Overall chance of a non-default tile
        )
        
        # Ensure the center area is clear for the city and make it "city_center" if defined
        city_tile_radius = 2 # How many tiles around the city center are part of it
        city_center_x = self.map.width // 2
        city_center_y = self.map.height // 2

        city_base_tile = "grass" # Fallback tile under city structures
        if "city_center" in config.TILE_SPRITE_PATHS:
             city_base_tile = "city_center" # Use a specific tile if defined

        for r in range(city_center_y - city_tile_radius, city_center_y + city_tile_radius + 1):
            for c in range(city_center_x - city_tile_radius, city_center_x + city_tile_radius + 1):
                if 0 <= c < self.map.width and 0 <= r < self.map.height:
                    self.map.set_tile(c, r, city_base_tile, walkable=True) # City area is walkable
        
        # Create the city object (visual representation, entry points etc.)
        # The CityLocation class itself might need updates if its visual rendering relied on old tile sizes.
        # For now, its internal rect calculation used a hardcoded 32, which matches TILE_SIZE_MAP_DISPLAY.
        self.city = CityLocation(
            city_center_x - city_tile_radius, 
            city_center_y - city_tile_radius, 
            size=city_tile_radius * 2 + 1
        )
        
        # Example: Ensure player starts on a valid tile, potentially city entrance
        # (This logic is already in __init__, re-check if needed after map generation)
    
    def _setup_props(self):
        """Set up static props on the map."""
        self.static_props_list = []
        # Example: Load props from world_map.json (data_handler should provide this)
        if self.game_manager.data_handler and self.game_manager.data_handler.raw_world_map_json:
            prop_definitions = self.game_manager.data_handler.raw_world_map_json.get("static_props", [])
            # print(f"Found {len(prop_definitions)} static prop definitions in world_map.json")

            for prop_def in prop_definitions:
                prop_type = prop_def["type"]
                tile_x = prop_def["tile_x"]
                tile_y = prop_def["tile_y"]
                offset_x = prop_def.get("offset_x", 0) # Default to 0 if not specified
                offset_y = prop_def.get("offset_y", 0) # Default to 0 if not specified
                layer = prop_def.get("layer", 1) # Default layer
                
                surface = self.game_manager.data_handler.prop_surfaces.get(prop_type)
                if surface:
                    new_prop = StaticProp(
                        prop_type=prop_type,
                        tile_x=tile_x,
                        tile_y=tile_y,
                        surface=surface,
                        offset_x=offset_x,
                        offset_y=offset_y,
                        layer=layer
                    )
                    self.static_props_list.append(new_prop)
                else:
                    print(f"Warning: Surface not found for prop type '{prop_type}'. Prop at ({tile_x},{tile_y}) will not be rendered.")
        
        # Sort props by their y-coordinate for correct draw order (optional, but good for depth)
        # This initial sort might be redundant if we re-sort all renderable objects in the render loop
        # self.static_props_list.sort(key=lambda prop: prop.rect.bottom)
        # print(f"Loaded {len(self.static_props_list)} static props.")

    def _setup_resource_nodes(self):
        """Set up resource nodes on the map."""
        self.resource_nodes_list = []
        if not (self.game_manager.data_handler and self.game_manager.data_handler.raw_world_map_json):
            print("Warning: DataHandler or raw_world_map_json not available for setting up resource nodes.")
            return

        node_definitions = self.game_manager.data_handler.raw_world_map_json.get("resource_nodes", [])
        # print(f"Found {len(node_definitions)} resource node definitions in world_map.json")

        for node_def in node_definitions:
            node_type = node_def.get("type")
            tile_x = node_def.get("tile_x")
            tile_y = node_def.get("tile_y")
            node_id = node_def.get("id", f"node_{tile_x}_{tile_y}_{node_type}")

            if node_type is None or tile_x is None or tile_y is None:
                print(f"Warning: Skipping resource node due to missing type, tile_x, or tile_y: {node_def}")
                continue

            node_config_data = config.RESOURCE_NODE_TYPES.get(node_type)
            if not node_config_data:
                print(f"Warning: Config data not found for resource node type '{node_type}'. Skipping node: {node_id}")
                continue

            initial_surface = self.game_manager.data_handler.resource_node_surfaces.get(node_type)
            if not initial_surface:
                print(f"Warning: Initial surface not found for resource node type '{node_type}'. Node {node_id} might not render correctly.")
                # Create a fallback surface or skip? For now, ResourceNode init might handle it or use a placeholder.

            depleted_surface = None
            depleted_sprite_suffix = node_config_data.get("depleted_sprite_suffix", "")
            if depleted_sprite_suffix:
                depleted_sprite_key = node_type + depleted_sprite_suffix
                depleted_surface = self.game_manager.data_handler.resource_node_surfaces.get(depleted_sprite_key)
                if not depleted_surface:
                    print(f"Warning: Depleted surface not found for key '{depleted_sprite_key}' (node type '{node_type}').")
            
            saved_node_state = node_def.get("saved_state") # Will be None if not in JSON

            try:
                new_node = ResourceNode(
                    node_id=node_id,
                    node_type=node_type,
                    tile_x=tile_x,
                    tile_y=tile_y,
                    initial_surface=initial_surface, # Pass even if None, ResourceNode might have fallbacks
                    depleted_surface=depleted_surface,
                    saved_state=saved_node_state
                )
                self.resource_nodes_list.append(new_node)
            except Exception as e:
                print(f"Error creating ResourceNode instance for {node_id} ({node_type}): {e}")

        # print(f"Loaded {len(self.resource_nodes_list)} resource nodes.")
    
    def _setup_points_of_interest(self): # ADDED METHOD
        """Set up points of interest on the map."""
        self.points_of_interest_list = []
        if not (self.game_manager.data_handler and self.game_manager.data_handler.raw_world_map_json):
            print("Warning: DataHandler or raw_world_map_json not available for setting up Points of Interest.")
            return

        poi_definitions = self.game_manager.data_handler.raw_world_map_json.get("points_of_interest", [])
        # print(f"Found {len(poi_definitions)} POI definitions in world_map.json")

        for poi_def in poi_definitions:
            poi_id = poi_def.get("id")
            poi_type = poi_def.get("type")
            tile_x = poi_def.get("tile_x")
            tile_y = poi_def.get("tile_y")
            saved_state = poi_def.get("saved_state") 

            if poi_id is None or poi_type is None or tile_x is None or tile_y is None:
                print(f"Warning: Skipping POI due to missing id, type, tile_x, or tile_y: {poi_def}")
                continue

            # Get POI definition from config
            definition = config.POI_DEFINITIONS.get(poi_type)
            if not definition:
                print(f"Warning: POI definition not found in config.POI_DEFINITIONS for type '{poi_type}'. Skipping POI: {poi_id}")
                continue

            # Get surfaces from DataHandler
            initial_surface = self.game_manager.data_handler.poi_surfaces.get(poi_type)
            minimap_icon_surface = self.game_manager.data_handler.poi_minimap_icons.get(poi_type)

            if not initial_surface:
                print(f"Warning: Initial surface not found for POI type '{poi_type}' in DataHandler. POI {poi_id} might use fallback.")
                # PointOfInterest class has fallback drawing if surface is None

            # Note: minimap_icon_surface can be None, PointOfInterest might handle it or minimap drawing logic.
            # In DataHandler._load_poi_sprites, a fallback minimap icon is created if the specified one is missing.

            try:
                new_poi = PointOfInterest(
                    poi_id=poi_id,
                    poi_type=poi_type,
                    tile_x=tile_x,
                    tile_y=tile_y,
                    initial_surface=initial_surface,         # ADDED
                    minimap_icon_surface=minimap_icon_surface, # ADDED
                    definition=definition,                   # ADDED
                    game_manager=self.game_manager,
                    saved_state=saved_state 
                )
                self.points_of_interest_list.append(new_poi)
            except Exception as e:
                print(f"Error creating PointOfInterest instance for {poi_id} ({poi_type}): {e}")
        
        # print(f"Loaded {len(self.points_of_interest_list)} Points of Interest.")
    
    def setup_minimap(self, load_saved):
        """Set up the mini-map"""
        # Scale the tilemap down to a mini-map size
        self.minimap_scale = 0.1
        self.minimap_width = int(self.map.pixel_width * self.minimap_scale)
        self.minimap_height = int(self.map.pixel_height * self.minimap_scale)
        
        # Create a surface for the mini-map background
        self.minimap_surface = pygame.Surface((self.minimap_width, self.minimap_height))
        self.minimap_surface.fill(config.MINIMAP_UNDISCOVERED_COLOR) # Fill with undiscovered color

        # If loading saved game, reveal already visited chunks
        if load_saved: # Assuming load_saved is a parameter of __init__ and available here
            saved_chunks_data = self.player_data.get("visited_map_chunks", [])
            self.visited_map_chunks = {tuple(chunk_coords) for chunk_coords in saved_chunks_data}
            for chunk_coords in self.visited_map_chunks:
                self._reveal_minimap_chunk(chunk_coords) # Assumes this method exists
        
        # Always draw city on minimap after terrain (respecting visited chunks)
        self._update_static_elements_on_minimap() # ADDED: Call to draw city and POIs

    def _get_chunk_coords_from_tile_coords(self, tile_x, tile_y):
        chunk_x = tile_x // config.MINIMAP_CHUNK_SIZE
        chunk_y = tile_y // config.MINIMAP_CHUNK_SIZE
        return (chunk_x, chunk_y)

    def _reveal_minimap_chunk(self, chunk_coords):
        """Render a specific chunk of the map onto the minimap_surface using simple colors."""
        chunk_tile_x = chunk_coords[0] * config.MINIMAP_CHUNK_SIZE
        chunk_tile_y = chunk_coords[1] * config.MINIMAP_CHUNK_SIZE

        # Define colors for minimap tiles (ensure these types match your world generation)
        MINIMAP_TILE_COLORS = {
            "grass": (50, 150, 50),  # Darker green for minimap
            "water": (50, 50, 150),  # Darker blue
            "mountain": (100, 100, 100), # Gray
            "forest": (30, 100, 30),   # Darker forest green
            "sand": (180, 180, 120), # Sandy color
            "road": (80, 80, 80),     # Dark gray for roads
            "city_center": (150, 50, 150), # Distinct city color on minimap
            "default": (70, 70, 70) # Fallback color for unknown tiles on minimap
        }

        for y_offset in range(config.MINIMAP_CHUNK_SIZE):
            for x_offset in range(config.MINIMAP_CHUNK_SIZE):
                tile_x = chunk_tile_x + x_offset
                tile_y = chunk_tile_y + y_offset

                if 0 <= tile_x < self.map.width and 0 <= tile_y < self.map.height:
                    map_tile_obj = self.map.get_tile(tile_x, tile_y)
                    tile_type = map_tile_obj.tile_type if map_tile_obj else "default"
                    
                    color = MINIMAP_TILE_COLORS.get(tile_type, MINIMAP_TILE_COLORS["default"])
                    
                    # Calculate position and size on the minimap surface
                    mini_x = int(tile_x * self.map.tile_size * self.minimap_scale)
                    mini_y = int(tile_y * self.map.tile_size * self.minimap_scale)
                    mini_tile_w = int(self.map.tile_size * self.minimap_scale)
                    mini_tile_h = int(self.map.tile_size * self.minimap_scale)
                    
                    # Ensure minimap tiles are at least 1x1 pixel
                    mini_tile_w = max(1, mini_tile_w)
                    mini_tile_h = max(1, mini_tile_h)

                    pygame.draw.rect(self.minimap_surface, color, (mini_x, mini_y, mini_tile_w, mini_tile_h))
        
        # After revealing terrain, redraw city on top if it's in a visited chunk (or always)
        self._update_static_elements_on_minimap() # ADDED: Update city and POIs

    def _draw_city_on_minimap(self):
        # Calculate city's bounding box in chunk coordinates
        city_start_chunk_x, city_start_chunk_y = self._get_chunk_coords_from_tile_coords(self.city.x, self.city.y)
        city_end_tile_x = self.city.x + self.city.size -1
        city_end_tile_y = self.city.y + self.city.size -1
        city_end_chunk_x, city_end_chunk_y = self._get_chunk_coords_from_tile_coords(city_end_tile_x, city_end_tile_y)

        city_is_partially_visible = False
        for r_chunk_x in range(city_start_chunk_x, city_end_chunk_x + 1):
            for r_chunk_y in range(city_start_chunk_y, city_end_chunk_y + 1):
                if (r_chunk_x, r_chunk_y) in self.visited_map_chunks:
                    city_is_partially_visible = True
                    break
            if city_is_partially_visible: 
                break
        
        if city_is_partially_visible:
            city_rect_minimap = pygame.Rect(
                int(self.city.x * self.map.tile_size * self.minimap_scale),
                int(self.city.y * self.map.tile_size * self.minimap_scale),
                int(self.city.size * self.map.tile_size * self.minimap_scale),
                int(self.city.size * self.map.tile_size * self.minimap_scale)
            )
            pygame.draw.rect(self.minimap_surface, (200, 200, 50), city_rect_minimap) # Yellow city icon

    def _update_static_elements_on_minimap(self): # ADDED METHOD
        """Draws static elements like the city and revealed POIs on the minimap."""
        # 1. Draw the city
        self._draw_city_on_minimap()

        # 2. Draw POI icons for visited chunks
        for poi in self.points_of_interest_list:
            if not poi.minimap_icon_surface:
                continue # No icon to draw

            poi_chunk_coords = self._get_chunk_coords_from_tile_coords(poi.tile_x, poi.tile_y)
            
            if poi_chunk_coords in self.visited_map_chunks:
                # Calculate base position on minimap (top-left of the POI's tile on minimap)
                mini_tile_x = int(poi.tile_x * self.map.tile_size * self.minimap_scale)
                mini_tile_y = int(poi.tile_y * self.map.tile_size * self.minimap_scale)
                
                icon_width = poi.minimap_icon_surface.get_width()
                icon_height = poi.minimap_icon_surface.get_height()

                # Center the icon on its tile representation on the minimap
                # A minimap tile is roughly (self.map.tile_size * self.minimap_scale) wide/high
                minimap_tile_display_size_w = max(1, int(self.map.tile_size * self.minimap_scale))
                minimap_tile_display_size_h = max(1, int(self.map.tile_size * self.minimap_scale))

                draw_x = mini_tile_x + (minimap_tile_display_size_w - icon_width) // 2
                draw_y = mini_tile_y + (minimap_tile_display_size_h - icon_height) // 2
                
                self.minimap_surface.blit(poi.minimap_icon_surface, (draw_x, draw_y))

    def handle_events(self, events):
        """Handle pygame events
        
        Args:
            events (list): List of pygame events
        """
        for event in events:
            if event.type == pygame.QUIT:
                self.game_manager.quit_game()
                return # Exit early if quitting
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Import PauseState locally to avoid circular import at module level
                    from src.game_manager import PauseState 
                    self.game_manager.push_state(PauseState(self.game_manager, self)) # Pass current state
                elif event.key == pygame.K_e and self.show_entry_prompt and self.is_day:
                    # 'E' key now only for entering city interior during the day
                    self.enter_city_interior()
                elif event.key == pygame.K_m:
                    # Toggle mini-map size
                    self.toggle_minimap()
                elif event.key == pygame.K_t:
                    # Speed up time (debug feature)
                    self.time_scale = 10.0 if self.time_scale == 1.0 else 1.0
                # Test keybinds for different spells
                elif event.key == pygame.K_1: # Cast Basic Homing Projectile
                    projectile = self.player.cast_spell("basic_projectile", *self.camera.reverse_apply_point(*pygame.mouse.get_pos()))
                    if projectile:
                        self.projectile_manager.add_projectile(projectile)
                elif event.key == pygame.K_2: # Cast Orbiting Blades
                    projectile = self.player.cast_spell("orbiting_blades", *self.camera.reverse_apply_point(*pygame.mouse.get_pos()))
                    if projectile:
                        self.projectile_manager.add_projectile(projectile)
                elif event.key == pygame.K_3: # Cast Fireball (Straight)
                    projectile = self.player.cast_spell("fireball", *self.camera.reverse_apply_point(*pygame.mouse.get_pos()))
                    if projectile:
                        self.projectile_manager.add_projectile(projectile)
                elif event.key == pygame.K_4: # Cast Wave Pulse (Sine Wave)
                    projectile = self.player.cast_spell("wave_pulse", *self.camera.reverse_apply_point(*pygame.mouse.get_pos()))
                    if projectile:
                        self.projectile_manager.add_projectile(projectile)
                elif event.key == pygame.K_5: # Cast Returning Disk (Boomerang)
                    projectile = self.player.cast_spell("returning_disk", *self.camera.reverse_apply_point(*pygame.mouse.get_pos()))
                    if projectile:
                        self.projectile_manager.add_projectile(projectile)
                elif event.key == pygame.K_6: # Cast Chain Spark
                    projectile = self.player.cast_spell("chain_spark", *self.camera.reverse_apply_point(*pygame.mouse.get_pos()))
                    if projectile:
                        self.projectile_manager.add_projectile(projectile)
                elif event.key == pygame.K_7: # Cast Piercing Bolt
                    projectile = self.player.cast_spell("piercing_bolt", *self.camera.reverse_apply_point(*pygame.mouse.get_pos()))
                    if projectile:
                        self.projectile_manager.add_projectile(projectile)
                elif event.key == pygame.K_8: # Cast Meteor Shard (Ground AOE)
                    projectile = self.player.cast_spell("meteor_shard", *self.camera.reverse_apply_point(*pygame.mouse.get_pos()))
                    if projectile:
                        self.projectile_manager.add_projectile(projectile)
                elif event.key == pygame.K_9: # Cast Forking Bolt
                    projectile = self.player.cast_spell("forking_bolt", *self.camera.reverse_apply_point(*pygame.mouse.get_pos()))
                    if projectile:
                        self.projectile_manager.add_projectile(projectile)
                elif event.key == pygame.K_0: # Cast Spiral Blast
                    projectile = self.player.cast_spell("spiral_blast", *self.camera.reverse_apply_point(*pygame.mouse.get_pos()))
                    if projectile:
                        self.projectile_manager.add_projectile(projectile)
                elif event.key == pygame.K_g: # Cast Growing Orb
                    projectile = self.player.cast_spell("growing_orb_spell", *self.camera.reverse_apply_point(*pygame.mouse.get_pos()))
                    if projectile:
                        self.projectile_manager.add_projectile(projectile)
                elif event.key == config.KEY_INTERACT: # ADDED: Interaction key
                    current_time_seconds = pygame.time.get_ticks() / 1000.0
                    
                    interaction_performed = False
                    # Priority to active_interaction_target if already set (e.g. by proximity update)
                    if self.active_interaction_target:
                        if isinstance(self.active_interaction_target, ResourceNode):
                            node = self.active_interaction_target
                            if node.can_harvest(current_time_seconds):
                                harvest_result = node.harvest(current_time_seconds)
                                if harvest_result:
                                    self.game_manager.player.add_resource(
                                        harvest_result["resource_type"],
                                        harvest_result["amount"]
                                    )
                                    if hasattr(self.game_manager, 'mark_world_map_dirty'):
                                        self.game_manager.mark_world_map_dirty()
                                    print(f"Harvested {harvest_result['amount']} {harvest_result['resource_type']} from {node.node_id}")
                                    interaction_performed = True
                            # else:
                                # print(f"Node {node.node_id} ({node.get_interaction_prompt()}) cannot be harvested now.")
                        
                        elif isinstance(self.active_interaction_target, PointOfInterest):
                            poi = self.active_interaction_target
                            # Assuming POI.interact handles its own logic and feedback
                            poi.interact(self.player, self.game_manager) 
                            interaction_performed = True 
                            # POI interaction might need to set world_map_dirty if state changes
                            # This should be handled within POI.interact or GameManger via callback

                    # Fallback to iterating if no active target or if specific logic requires it
                    # This part is mostly superseded by the active_interaction_target logic in update()
                    if not interaction_performed:
                        # Check Resource Nodes first
                        for node in self.resource_nodes_list:
                            player_pos = pygame.math.Vector2(self.player.rect.center)
                            node_pos = pygame.math.Vector2(node.rect.center)
                            distance = player_pos.distance_to(node_pos)

                            if distance <= config.INTERACTION_DISTANCE_THRESHOLD:
                                if node.can_harvest(current_time_seconds):
                                    harvest_result = node.harvest(current_time_seconds)
                                    if harvest_result:
                                        self.game_manager.player.add_resource(
                                            harvest_result["resource_type"],
                                            harvest_result["amount"]
                                        )
                                        if hasattr(self.game_manager, 'mark_world_map_dirty'):
                                            self.game_manager.mark_world_map_dirty()
                                        print(f"Harvested {harvest_result['amount']} {harvest_result['resource_type']} from {node.node_id}")
                                        interaction_performed = True
                                        break 
                                # else:
                                    # print(f"Node {node.node_id} ({node.get_interaction_prompt()}) cannot be harvested now.")
                                # break # Interact with one node at a time if in range

                        # Then Check POIs if no resource node was interacted with
                        if not interaction_performed:
                            for poi in self.points_of_interest_list:
                                player_pos = pygame.math.Vector2(self.player.rect.center)
                                # Assuming POI has a rect similar to ResourceNode for interaction distance
                                if hasattr(poi, 'rect'):
                                    poi_center_pos = pygame.math.Vector2(poi.rect.center)
                                    distance = player_pos.distance_to(poi_center_pos)
                                    if distance <= config.INTERACTION_DISTANCE_THRESHOLD:
                                        poi.interact(self.player, self.game_manager)
                                        interaction_performed = True
                                        # Mark map dirty if POI interaction changes savable state
                                        # This might be handled by the POI's interact method or a callback
                                        break # Interact with one POI at a time
                                else: # Fallback if POI doesn't have a rect, use tile position
                                    poi_pixel_x = poi.tile_x * self.map.tile_size + self.map.tile_size / 2
                                    poi_pixel_y = poi.tile_y * self.map.tile_size + self.map.tile_size / 2
                                    poi_center_pos = pygame.math.Vector2(poi_pixel_x, poi_pixel_y)
                                    distance = player_pos.distance_to(poi_center_pos)
                                    if distance <= config.INTERACTION_DISTANCE_THRESHOLD: # A slightly larger threshold might be needed if checking tile center
                                        poi.interact(self.player, self.game_manager)
                                        interaction_performed = True
                                        break


            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    # Attack with basic projectile
                    mouse_pos = pygame.mouse.get_pos()
                    # Convert screen coordinates to world coordinates for target_pos
                    world_pos = self.camera.reverse_apply_point(*mouse_pos)
                    
                    # Check if player is clicked (for interaction, not attack here)
                    if self.player.rect.collidepoint(world_pos):
                        print("Player clicked on world map") # Placeholder for interaction
                        # Potentially open player menu or stats
                    else:
                        # If not clicking player, could be map movement or other interaction
                        # For now, let's assume a click on the map might be a target for an action
                        # if an action is pending. If basic attack is intended on map, it needs context.
                        # The error occurs here, so we are addressing this call:
                        projectile = self.player.handle_basic_attack(*world_pos) # Unpack tuple
                        if projectile:
                            # This part needs to be thought out: projectiles on world map?
                            # Adding to a projectile manager specific to world map if exists,
                            # or deciding if shooting is allowed here.
                            # For now, let's assume there isn't a projectile manager on world map
                            # or that this call was perhaps unintended for actual shooting.
                            print(f"Projectile created on world map: {projectile}")
                            self.projectile_manager.add_projectile(projectile) # Ensure projectile is added
                            # self.world_projectile_manager.add_projectile(projectile) # Example
    
    def update(self, dt):
        """Update the world map
        
        Args:
            dt (float): Time elapsed since last update in seconds
        """
        super().update(dt)
        
        # Scale time if needed
        dt_scaled = dt * self.time_scale
        
        # Update player
        keys_pressed = pygame.key.get_pressed()
        self.player.update(dt, keys_pressed)
        
        # Update enemies at night - added with wall collision and city damage callback
        if not self.is_day and self.enemy_manager:
            # Get a callback for enemy damaging the city
            damage_city_callback = self.damage_city_on_world_map
            # Get wall collision rects for enemies to attack
            wall_rects = self.city_wall_rects
            # Update enemy manager with player position, wall rects, and damage callback
            
            # Track enemy count before update
            enemy_count_before = len(self.enemy_manager.get_enemies())
            
            self.enemy_manager.update(dt, self.player.rect.center, wall_rects, damage_city_callback)
            
            # Only print if enemy count has changed
            enemy_count_after = len(self.enemy_manager.get_enemies())
            if enemy_count_before != enemy_count_after:
                print(f"Enemy count changed: {enemy_count_before} → {enemy_count_after}")
        
        # Update projectiles
        # Pass enemies list, which might be empty if it's day or no enemies on map
        self.projectile_manager.update(dt, self.enemy_manager.get_enemies())
        
        # Update resource nodes (e.g., for cooldowns)
        current_time_seconds = pygame.time.get_ticks() / 1000.0
        for node in self.resource_nodes_list:
            node.update(dt, current_time_seconds)

        # Update Points of Interest
        for poi in self.points_of_interest_list: # ADDED
            poi.update(dt, self.player, self.game_manager) # ADDED

        # Handle collision with map boundaries
        self.handle_collision()
        
        # Check if player is in range to enter city & update prompt text
        self.show_entry_prompt = self.city.is_player_in_range(self.player.x, self.player.y)
        if self.show_entry_prompt:
            if self.is_day:
                self.entry_prompt.set_text("Press E to enter city")
            else:
                self.entry_prompt.set_text("Press E to defend city!") # MODIFIED prompt for night
        
        # Update camera
        self.camera.update(dt)
        
        # Update active interaction target and prompt
        self.active_interaction_target = None
        closest_interaction_distance_sq = (config.INTERACTION_DISTANCE_THRESHOLD + 1)**2 # slightly more than threshold

        # Check Resource Nodes
        for node in self.resource_nodes_list:
            player_pos_sq = pygame.math.Vector2(self.player.rect.centerx, self.player.rect.centery)
            node_pos_sq = pygame.math.Vector2(node.rect.centerx, node.rect.centery)
            distance_sq = player_pos_sq.distance_squared_to(node_pos_sq)

            if distance_sq < closest_interaction_distance_sq:
                closest_interaction_distance_sq = distance_sq
                self.active_interaction_target = node
        
        # Check Points of Interest (override resource node if POI is closer or equally close)
        for poi in self.points_of_interest_list:
            player_pos_sq = pygame.math.Vector2(self.player.rect.centerx, self.player.rect.centery)
            if hasattr(poi, 'rect'): # Prefer rect if available
                 poi_center_pos_sq = pygame.math.Vector2(poi.rect.centerx, poi.rect.centery)
            else: # Fallback to tile center
                poi_pixel_x = poi.tile_x * self.map.tile_size + self.map.tile_size / 2
                poi_pixel_y = poi.tile_y * self.map.tile_size + self.map.tile_size / 2
                poi_center_pos_sq = pygame.math.Vector2(poi_pixel_x, poi_pixel_y)

            distance_sq = player_pos_sq.distance_squared_to(poi_center_pos_sq)
            
            # POIs might take precedence or have different interaction radius logic later
            # For now, just find the closest of any interactable
            if distance_sq < closest_interaction_distance_sq:
                closest_interaction_distance_sq = distance_sq
                self.active_interaction_target = poi

        if self.active_interaction_target and closest_interaction_distance_sq <= config.INTERACTION_DISTANCE_THRESHOLD**2:
            prompt_text = self.active_interaction_target.get_interaction_prompt()
            self.interaction_prompt_box.set_text(prompt_text if prompt_text else "Interact")
            self.show_interaction_prompt = True
        else:
            self.active_interaction_target = None
            self.show_interaction_prompt = False
        
        # Player chunk tracking for minimap
        player_tile_x = int(self.player.x / self.map.tile_size)
        player_tile_y = int(self.player.y / self.map.tile_size)
        current_chunk_coords = self._get_chunk_coords_from_tile_coords(player_tile_x, player_tile_y)

        if current_chunk_coords != self.last_player_chunk_coords:
            self.last_player_chunk_coords = current_chunk_coords
            if current_chunk_coords not in self.visited_map_chunks:
                self.visited_map_chunks.add(current_chunk_coords)
                self._reveal_minimap_chunk(current_chunk_coords)
                # City is redrawn inside _reveal_minimap_chunk if it overlaps, 
                # or consistently in setup_minimap based on all visited chunks.

        # Update day/night cycle
        if self.is_day:
            self.day_timer -= dt_scaled
            if self.day_timer <= 0:
                self.transition_to_night()
        else:
            # Update enemies during night
            self.enemy_manager.update(dt, (self.player.x, self.player.y), self.city_wall_rects, self.damage_city_on_world_map) # MODIFIED: Pass actual walls and callback
            
            if self.enemy_manager.is_night_complete(): # This check might need adjustment if night doesn't end based on enemy count on world map
                self.transition_to_day()
        
        # Save player position
        self.player_data["position"]["x"] = self.player.x
        self.player_data["position"]["y"] = self.player.y
    
    def handle_collision(self):
        """Handle collision with map boundaries and obstacles"""
        # Get the tile at the player's position
        player_tile_x = int(self.player.x / self.map.tile_size)
        player_tile_y = int(self.player.y / self.map.tile_size)
        
        # Check if tile is walkable
        if not self.map.is_walkable(player_tile_x, player_tile_y):
            # Move the player back to the previous position
            # For simplicity, just nudge in the opposite direction of movement
            # A better solution would use collision response
            if self.player.rect.centerx != int(self.player.x) or self.player.rect.centery != int(self.player.y):
                dx = self.player.rect.centerx - int(self.player.x)
                dy = self.player.rect.centery - int(self.player.y)
                
                self.player.x += dx * 2
                self.player.y += dy * 2
                
                self.player.rect.centerx = int(self.player.x)
                self.player.rect.centery = int(self.player.y)
        
        # ADDED: Handle city wall collision (one-way walls)
        if self.city_wall_rects and self.is_day:
            player_rect = self.player.rect.copy()
            
            # Check if player is completely inside the city area (not including walls)
            # We check the corners to be more strict, ensuring player is fully inside
            city_inner_rect = self.city.rect.copy()
            player_inside_city = city_inner_rect.contains(player_rect)
            
            # Get the player's movement direction
            move_dx = self.player.dx
            move_dy = self.player.dy
            
            # If player isn't moving, we need a fallback for situations where they're stuck in a wall
            if move_dx == 0 and move_dy == 0:
                # Get center coordinates for reference
                city_center_x, city_center_y = city_inner_rect.center
                player_center_x, player_center_y = player_rect.center
                
                # Calculate vector from city center to player to determine outward direction
                center_to_player_x = player_center_x - city_center_x
                center_to_player_y = player_center_y - city_center_y
                
                # Avoid zero values
                if abs(center_to_player_x) < 0.1: center_to_player_x = 0.1
                if abs(center_to_player_y) < 0.1: center_to_player_y = 0.1
                
                # Normalize
                magnitude = math.sqrt(center_to_player_x**2 + center_to_player_y**2)
                if magnitude > 0:
                    move_dx = center_to_player_x / magnitude
                    move_dy = center_to_player_y / magnitude
            
            for wall_key, wall_rect in self.city_wall_rects.items():
                if player_rect.colliderect(wall_rect):
                    # If player is outside the city or on the wall's edge
                    if not player_inside_city:
                        # Push player away from wall (outward)
                        if wall_key == "top": 
                            self.player.y = wall_rect.top - player_rect.height/2 - 1
                        elif wall_key == "bottom": 
                            self.player.y = wall_rect.bottom + player_rect.height/2 + 1
                        elif wall_key == "left": 
                            self.player.x = wall_rect.left - player_rect.width/2 - 1
                        elif wall_key == "right": 
                            self.player.x = wall_rect.right + player_rect.width/2 + 1
                    # If player is inside the city or we can't determine, push them toward their movement direction
                    else:
                        # Determine the exit direction based on movement and wall
                        if wall_key == "top" and move_dy < 0:  # Moving upward
                            self.player.y = wall_rect.top - player_rect.height/2 - 1
                        elif wall_key == "bottom" and move_dy > 0:  # Moving downward
                            self.player.y = wall_rect.bottom + player_rect.height/2 + 1
                        elif wall_key == "left" and move_dx < 0:  # Moving leftward
                            self.player.x = wall_rect.left - player_rect.width/2 - 1
                        elif wall_key == "right" and move_dx > 0:  # Moving rightward
                            self.player.x = wall_rect.right + player_rect.width/2 + 1
                        # If stuck in a wall with no clear direction, force them outside
                        else:
                            # Find nearest edge of the wall and push out
                            if abs(player_rect.centery - wall_rect.top) <= abs(player_rect.centery - wall_rect.bottom):
                                self.player.y = wall_rect.top - player_rect.height/2 - 1 # Push up through top
                            else:
                                self.player.y = wall_rect.bottom + player_rect.height/2 + 1 # Push down through bottom
                        
                    # Update the player's rect to match the new position
                    self.player.rect.centerx = int(self.player.x)
                    self.player.rect.centery = int(self.player.y)
            
        # Keep player within map boundaries
        if self.player.x < 0:
            self.player.x = 0
            self.player.rect.centerx = int(self.player.x)
        elif self.player.x > self.map.pixel_width:
            self.player.x = self.map.pixel_width
            self.player.rect.centerx = int(self.player.x)
        
        if self.player.y < 0:
            self.player.y = 0
            self.player.rect.centery = int(self.player.y)
        elif self.player.y > self.map.pixel_height:
            self.player.y = self.map.pixel_height
            self.player.rect.centery = int(self.player.y)
    
    def damage_city_on_world_map(self, amount): # ADDED METHOD
        """Callback for when an enemy damages the city walls on the world map."""
        if self.game_manager.city_current_hp > 0:
            self.game_manager.city_current_hp -= amount
            print(f"City walls on world map damaged by {amount} HP! Current HP: {self.game_manager.city_current_hp}")
            if self.game_manager.city_current_hp <= 0:
                self.game_manager.city_current_hp = 0
                print("City has fallen on the world map!")
                # self.game_manager.game_over() # Assuming GameManager has a game_over method
                # For now, just print. Game over logic can be centralized in GameManager.
    
    def enter_city_interior(self): # RENAMED from enter_city
        """Enter the city (transition to city interior state) - only during the day."""
        if self.is_day:
            from src.city_interior import CityInteriorState
            # Pass player_data which might be updated (e.g. resources from world map)
            self.game_manager.push_state(CityInteriorState(self.game_manager, self.player_data))
        else:
            print("Cannot enter city interior at night.")

    def start_city_defense(self): # ADDED METHOD
        """Transition to the NightPhaseState to defend the city."""
        print("Starting city defense! Transitioning to NightPhaseState.")
        from src.night_phase import NightPhaseState
        # Ensure player_data is current before transitioning
        self.player_data["position"]["x"] = self.player.x
        self.player_data["position"]["y"] = self.player.y
        # MODIFIED: Pass player_data (dict) and current day number
        self.game_manager.change_state(NightPhaseState(self.game_manager, self.player_data, self.player_data["day"]))

    def transition_to_night(self):
        """Transition from day to night phase"""
        self.is_day = False
        self.day_timer = 0 # Ensure timer is zeroed
        print("WorldMapState: Transitioning to Night.")
        # self.game_manager.notify_night_has_fallen() # REMOVED - WorldMapState manages its own transition to night behavior
        
        print(f"WorldMapState: Starting enemy manager for day {self.player_data['day']}.")
        self.enemy_manager.start_night(self.player_data["day"]) # UNCOMMENTED/ENSURED
    
    def transition_to_day(self):
        """Transition from night to day phase"""
        self.is_day = True
        self.day_timer = config.DAY_DURATION
        print("WorldMapState: Transitioning to Day.")
        self.game_manager.notify_day_has_broken() # ADDED notification
        
        # Increment day counter
        self.player_data["day"] += 1
        
        # Save player progress after each night
        # Consider if saving here is always appropriate or if GameManager should handle it.
        # DataHandler.save_player_data(self.player_data) # Moved to GameManager.save_all_game_data for consistency
    
    def toggle_minimap(self):
        """Toggle between small and large mini-map"""
        # TODO: Implement mini-map size toggling
        pass
    
    def render(self, screen):
        """Render the world map
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        screen.fill(config.BLACK)
        self.map.render(screen, self.camera)
        
        # --- Draw City Walls --- # MODIFIED: Condition changed
        if self.city_wall_rects: # Render if wall_rects exist (removed 'not self.is_day')
            for wall_key, wall_rect in self.city_wall_rects.items():
                pygame.draw.rect(screen, config.CITY_WALL_COLOR, self.camera.apply_rect(wall_rect))
        # --- END ---

        renderable_objects = []
        
        # Add static props
        renderable_objects.extend(self.static_props_list)
        
        # Add resource nodes
        renderable_objects.extend(self.resource_nodes_list)
        
        # Add points of interest
        renderable_objects.extend(self.points_of_interest_list) # ADDED
        
        # Add player
        if self.player: # Ensure player exists
            renderable_objects.append(self.player)
            
        # Add enemies during nighttime
        if not self.is_day and self.enemy_manager:
            # Convert pygame sprite group to a list of enemy objects for rendering
            active_enemies = self.enemy_manager.get_enemies().sprites()
            renderable_objects.extend(active_enemies)

        # Sort objects by their Y-coordinate (bottom of sprite for pseudo-3D effect)
        # Requires each object to have a get_render_sort_key() method
        try:
            renderable_objects.sort(key=lambda obj: obj.get_render_sort_key())
        except AttributeError as e:
            print(f"Warning: An object in renderable_objects is missing get_render_sort_key method: {e}")
            # Fallback: render unsorted or handle error
        
        # Render sorted objects
        for obj in renderable_objects:
            try:
                obj.render(screen, self.camera) # CHANGED: display_surface to screen
            except AttributeError as e:
                print(f"Warning: An object in renderable_objects is missing render method or has incompatible signature: {e}")
            except Exception as e:
                print(f"Error rendering object {obj}: {e}")

        # Projectiles - typically rendered on top or based on their own logic
        self.projectile_manager.render(screen, self.camera) # CHANGED: display_surface to screen
                
        # Day/Night cycle overlay (optional, if you have one)
        # Example: self.day_night_cycle.render(screen) # COMMENTED: Also changed to screen if used
        
        # UI elements (on top of everything)
        # Draw time remaining
        time_str = self.get_time_remaining_str()
        time_text = self.font_small.render(time_str, True, config.WHITE)
        screen.blit(time_text, (10, 10))
        
        # Draw day number
        day_text = self.font_small.render(f"Day: {self.player_data['day']}", True, config.WHITE)
        screen.blit(day_text, (config.SCREEN_WIDTH - day_text.get_width() - 10, 10))

        # Draw player XP bar at bottom
        if self.player:
            xp_bar_width = config.SCREEN_WIDTH - 40
            xp_bar_height = 20
            xp_bar_x = 20
            xp_bar_y = config.SCREEN_HEIGHT - xp_bar_height - 10
            
            # Calculate current XP for level
            current_level_xp = self.player.calculate_xp_for_level(self.player.level)
            prev_level_xp = self.player.calculate_xp_for_level(self.player.level - 1) if self.player.level > 1 else 0
            
            xp_in_current_level = self.player.xp - prev_level_xp
            xp_needed_for_level = current_level_xp - prev_level_xp
            
            xp_ratio = 0
            if xp_needed_for_level > 0:
                xp_ratio = min(1, xp_in_current_level / xp_needed_for_level)

            # Background
            pygame.draw.rect(screen, config.DARK_GRAY, (xp_bar_x, xp_bar_y, xp_bar_width, xp_bar_height))
            # Foreground (XP fill)
            pygame.draw.rect(screen, config.YELLOW, (xp_bar_x, xp_bar_y, xp_bar_width * xp_ratio, xp_bar_height))
            # Border
            pygame.draw.rect(screen, config.WHITE, (xp_bar_x, xp_bar_y, xp_bar_width, xp_bar_height), 2)

            xp_text_str = f"XP: {self.player.xp} / {current_level_xp} (Lvl {self.player.level})"
            xp_label = self.font_small.render(xp_text_str, True, config.WHITE)
            screen.blit(xp_label, (xp_bar_x + (xp_bar_width - xp_label.get_width()) // 2, xp_bar_y + (xp_bar_height - xp_label.get_height()) // 2))
        
        # City entry prompt
        if self.show_entry_prompt:
            self.entry_prompt.render(screen) # Render directly to screen as it's UI
            
        # Interaction Prompt (for POIs and Resource Nodes)
        if self.show_interaction_prompt and self.active_interaction_target: # ADDED
            self.interaction_prompt_box.render(screen) # ADDED
        
        # Minimap
        if self.minimap_visible:
            minimap_rect = pygame.Rect(config.SCREEN_WIDTH - self.minimap_width - 10, 30, self.minimap_width, self.minimap_height)
            pygame.draw.rect(screen, config.DARK_GRAY, minimap_rect) 
            pygame.draw.rect(screen, config.WHITE, minimap_rect, 2)  
            screen.blit(self.minimap_surface, minimap_rect.topleft)
        
        # --- Draw City HP Bar if Night ---
        if not self.is_day: # ADDED rendering for city HP at night
            hp_bar_width = 200
            hp_bar_height = 20
            hp_bar_x = (config.SCREEN_WIDTH - hp_bar_width) // 2
            hp_bar_y = 10 # At the top of the screen
            
            current_hp_ratio = 0
            if self.game_manager.city_max_hp > 0 :
                 current_hp_ratio = max(0, self.game_manager.city_current_hp / self.game_manager.city_max_hp)

            pygame.draw.rect(screen, config.DARK_GRAY, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
            pygame.draw.rect(screen, config.RED, (hp_bar_x, hp_bar_y, hp_bar_width * current_hp_ratio, hp_bar_height))
            pygame.draw.rect(screen, config.WHITE, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height), 2)
            
            hp_text_str = f"City HP: {int(self.game_manager.city_current_hp)}/{self.game_manager.city_max_hp}"
            hp_label = self.font_small.render(hp_text_str, True, config.WHITE)
            text_rect = hp_label.get_rect(center=(hp_bar_x + hp_bar_width / 2, hp_bar_y + hp_bar_height / 2))
            screen.blit(hp_label, text_rect)
        # --- END ---

        self.game_manager.global_ui_manager.render(screen)
            
        # Flip the display (done in game_manager.run)
        # pygame.display.flip() # Usually handled by the main game loop

    def get_time_remaining_str(self):
        """Get a string representation of the time remaining in the day
        
        Returns:
            str: Time remaining in MM:SS format
        """
        minutes = int(self.day_timer // 60)
        seconds = int(self.day_timer % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def enter(self):
        """Called when entering the world map state"""
        super().enter()
    
    def exit(self):
        """Called when exiting the world map state"""
        # Prepare visited_map_chunks for saving
        self.player_data["visited_map_chunks"] = [list(chunk_coords) for chunk_coords in self.visited_map_chunks]
        # Save player data (which now includes the chunks)
        DataHandler.save_player_data(self.player_data)
    
    def resume(self):
        """Called when the world map state is resumed"""
        pass
    
    def pause(self):
        """Called when the world map state is paused"""
        pass

    def get_current_resource_node_data_for_saving(self): # ADDED METHOD
        """Gathers current state of all resource nodes for saving."""
        node_data_list = []
        for node_instance in self.resource_nodes_list:
            node_data_list.append({
                "id": node_instance.node_id, 
                "type": node_instance.node_type, 
                "tile_x": node_instance.tile_x, 
                "tile_y": node_instance.tile_y, 
                "saved_state": node_instance.to_dict()
            })
        return node_data_list

    def get_current_poi_data_for_saving(self): # ADDED METHOD
        """Gathers current state of all Points of Interest for saving."""
        poi_data_list = []
        for poi_instance in self.points_of_interest_list:
            poi_data_list.append({
                "id": poi_instance.poi_id, 
                "type": poi_instance.poi_type, 
                "tile_x": poi_instance.tile_x, 
                "tile_y": poi_instance.tile_y, 
                "saved_state": poi_instance.to_dict() # Assumes to_dict() returns all necessary save data
            })
        return poi_data_list 