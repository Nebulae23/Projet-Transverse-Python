"""
Magic Survivor - Data Handler

This module handles loading and saving of game data from JSON files.
"""

import json
import os
from src import config
import pygame
import noise

class DataHandler:
    """Handles loading and saving of game data"""
    
    def __init__(self):
        self.spells = {}
        self.relics = {}
        self.enemies = {}
        self.waves = {}
        self.buildings = {}
        self.world_data = {} # For storing loaded world map tile data (the grid itself)
        self.tile_surfaces = {} # Will store lists of Pygame surfaces per tile type
        self.tile_variation_map = None # Will store variation indices for each map tile
        self.prop_surfaces = {} # Will store surfaces for static props
        self.raw_world_map_json = {} # To store the full loaded world_map.json for props etc.
        self.resource_node_surfaces = {} # ADDED
        self.poi_surfaces = {} # ADDED: Stores loaded pygame.Surface for POI main sprites
        self.poi_minimap_icons = {} # ADDED: Stores loaded pygame.Surface for POI minimap icons

    @staticmethod
    def _encode_row_rle(row_list):
        """Encode a single row of tile data using Run-Length Encoding."""
        if not row_list:
            return []
        
        encoded_row = []
        current_tile_type = row_list[0]
        count = 1
        for i in range(1, len(row_list)):
            if row_list[i] == current_tile_type:
                count += 1
            else:
                encoded_row.append({"tile": current_tile_type, "count": count})
                current_tile_type = row_list[i]
                count = 1
        encoded_row.append({"tile": current_tile_type, "count": count}) # Append the last run
        return encoded_row

    @staticmethod
    def _decode_row_rle(rle_row_list):
        """Decode a single RLE row back into a plain list of tile types."""
        decoded_row = []
        for item in rle_row_list:
            decoded_row.extend([item["tile"]] * item["count"])
        return decoded_row

    @staticmethod
    def load_json(file_path):
        """Load data from a JSON file
        
        Args:
            file_path (str): Path to the JSON file
            
        Returns:
            dict: The loaded data, or an empty dict if the file doesn't exist
        """
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    return json.load(file)
            else:
                print(f"Warning: File not found: {file_path}")
                return {}
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return {}
    
    @staticmethod
    def save_json(data, file_path):
        """Save data to a JSON file
        
        Args:
            data (dict): The data to save
            file_path (str): Path to the JSON file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)
            return True
        except Exception as e:
            print(f"Error saving to {file_path}: {e}")
            return False
    
    @classmethod
    def load_spells(cls):
        """Load spell data
        
        Returns:
            dict: Spell data
        """
        return cls.load_json(config.SPELLS_DATA)
    
    @classmethod
    def load_relics(cls):
        """Load relic data
        
        Returns:
            dict: Relic data
        """
        return cls.load_json(config.RELICS_DATA)
    
    @classmethod
    def load_enemies(cls):
        """Load enemy data
        
        Returns:
            dict: Enemy data
        """
        return cls.load_json(config.ENEMIES_DATA)
    
    @classmethod
    def load_waves(cls):
        """Load wave data
        
        Returns:
            dict: Wave data
        """
        return cls.load_json(config.WAVES_DATA)
    
    @classmethod
    def load_buildings(cls):
        """Load building data
        
        Returns:
            dict: Building data
        """
        return cls.load_json(config.BUILDINGS_DATA)
    
    @classmethod
    def load_world_map(cls):
        """Load world map data
        
        Returns:
            dict: World map data, or default values if no map exists
        """
        map_data = cls.load_json(config.WORLD_MAP_DATA)
        if not map_data:
            # Return default world map data if no file exists
            return {
                "width": config.WORLD_MAP_WIDTH,
                "height": config.WORLD_MAP_HEIGHT,
                "tile_size": config.TILE_SIZE,
                "cities": [
                    {
                        "name": "Main City",
                        "position": {
                            "x": config.WORLD_MAP_WIDTH // 2,
                            "y": config.WORLD_MAP_HEIGHT // 2
                        },
                        "size": 5
                    }
                ],
                "points_of_interest": []
            }
        return map_data
    
    @classmethod
    def save_world_map(cls, map_data):
        """Save world map data
        
        Args:
            map_data (dict): World map data to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        return cls.save_json(map_data, config.WORLD_MAP_DATA)
    
    @classmethod
    def load_player_save(cls):
        """Load player save data
        
        Returns:
            dict: Player save data, or default values if no save exists
        """
        save_data = cls.load_json(config.PLAYER_SAVE)
        if not save_data:
            # Return default player data if no save exists
            return {
                "level": 1,
                "xp": 0,
                "city_buildings": {},
                "spells": ["basic_projectile"],  # Start with just the basic attack
                "relics": [],
                "day": 1,
                "resources": config.STARTING_RESOURCES,
                "position": {"x": None, "y": None},  # Will be set at game start
                "stats": {
                    "max_health": config.PLAYER_BASE_HP,
                    "damage": config.PLAYER_BASE_ATTACK_DAMAGE,
                    "speed": config.PLAYER_SPEED
                }
            }
        return save_data
    
    @classmethod
    def save_player_data(cls, player_data):
        """Save player data
        
        Args:
            player_data (dict): Player data to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        return cls.save_json(player_data, config.PLAYER_SAVE)
    
    def load_all_data(self):
        """Load all core game data definitions."""
        self.spells = self.load_json(config.SPELLS_DATA)
        self.relics = self.load_json(config.RELICS_DATA)
        self.enemies = self.load_json(config.ENEMIES_DATA)
        self.waves = self.load_json(config.WAVES_DATA)
        self.buildings = self.load_json(config.BUILDINGS_DATA)
        
        self.raw_world_map_json = self.load_json(config.WORLD_MAP_DATA)
        self.world_data = [] # Initialize world_data

        if self.raw_world_map_json and "tiles" in self.raw_world_map_json:
            tile_data_format = self.raw_world_map_json.get("tile_data_format")
            if tile_data_format == "list_of_lists_rle":
                print("Decoding RLE tile data...")
                decoded_world_data = []
                for rle_row in self.raw_world_map_json["tiles"]:
                    plain_row = DataHandler._decode_row_rle(rle_row) # Explicitly call static method
                    decoded_world_data.append(plain_row)
                self.world_data = decoded_world_data
                print(f"Decoded RLE map: {len(self.world_data)} rows, {len(self.world_data[0]) if self.world_data else 0} cols")
            elif tile_data_format == "list_of_lists_tile_types": # Handle old format explicitly
                print("Loading plain list_of_lists_tile_types tile data...")
                self.world_data = self.raw_world_map_json["tiles"]
            else: # Fallback for very old format or missing format - assume plain list if possible
                print(f"Warning: Unknown or missing tile_data_format ('{tile_data_format}'). Assuming plain list if possible.")
                if isinstance(self.raw_world_map_json["tiles"], list) and \
                   all(isinstance(row, list) for row in self.raw_world_map_json["tiles"]):
                    self.world_data = self.raw_world_map_json["tiles"]
                else:
                    print("Error: Could not interpret tile data from world_map.json. World data will be empty.")
                    self.world_data = [] # Ensure it's empty if unparseable
        
        elif not self.raw_world_map_json: 
             # This case means world_map.json was missing entirely.
             # create_default_files should have made one, so load_json *should* have found it.
             # If it's still missing, _create_default_world_data_internal might be a last resort
             # for internal representation, but the JSON on disk needs to be addressed.
             print("Warning: raw_world_map_json is empty. Attempting to create default internal world data.")
             self._create_default_world_data_internal()

        self._load_tile_sprites()
        self._load_prop_sprites()
        self._load_resource_node_sprites() # ADDED
        self._load_poi_sprites() # ADDED CALL
        
        if self.world_data and isinstance(self.world_data, list) and len(self.world_data) > 0:
            world_height = len(self.world_data)
            world_width = len(self.world_data[0]) if world_height > 0 else 0
            if world_width > 0:
                self._generate_tile_variation_map(world_width, world_height)
            else:
                print("Warning: World data is empty or malformed, cannot generate tile variation map.")
        else:
            print("Warning: World data not available or not in expected list format after loading, cannot generate tile variation map.")

        # Keep returning a dictionary for compatibility if anything still uses the old static return
        all_data = {
            "spells": self.spells,
            "relics": self.relics,
            "enemies": self.enemies,
            "waves": self.waves,
            "buildings": self.buildings,
        }
        return all_data

    def _load_tile_sprites(self):
        """Load tile sprites and their variations."""
        print("Loading tile sprites...")
        self.tile_surfaces = {} # Ensure it's reset
        for tile_type, sprite_paths in config.TILE_SPRITE_PATHS.items():
            self.tile_surfaces[tile_type] = []
            for sprite_path_str in sprite_paths:
                # Construct full path using ASSETS_DIR if sprite_path_str is relative inside assets
                # Assuming TILE_SPRITE_PATHS stores paths relative to project root like "assets/sprites/tiles/grass.png"
                full_sprite_path = os.path.join(config.BASE_DIR, sprite_path_str) # Corrected path construction

                if not os.path.exists(full_sprite_path):
                    # Try with ASSETS_DIR if BASE_DIR failed (e.g. if path was "sprites/tiles/grass.png")
                    alt_path = os.path.join(config.ASSETS_DIR, sprite_path_str.replace("assets/", "", 1))
                    if os.path.exists(alt_path):
                        full_sprite_path = alt_path
                    else:
                        print(f"Warning: Sprite file not found: {sprite_path_str} (checked {full_sprite_path} and {alt_path}). Skipping for tile type {tile_type}.")
                        continue
                
                try:
                    image = pygame.image.load(full_sprite_path).convert_alpha()
                    scaled_image = pygame.transform.scale(image, config.TILE_SPRITE_DIMENSIONS)
                    self.tile_surfaces[tile_type].append(scaled_image)
                    print(f"Loaded and scaled sprite: {full_sprite_path} for {tile_type}")
                except pygame.error as e:
                    print(f"Error loading sprite {full_sprite_path} for tile type {tile_type}: {e}. Skipping.")
                except FileNotFoundError: # Should be caught by os.path.exists, but as a safeguard
                    print(f"Warning: Sprite file not found (secondary check): {full_sprite_path}. Skipping for tile type {tile_type}.")

            if not self.tile_surfaces[tile_type]:
                print(f"Warning: No sprites successfully loaded for tile type '{tile_type}'. It will use fallback colors.")
        print(f"Tile surfaces loaded: { {k: len(v) for k, v in self.tile_surfaces.items()} }")

    def _load_prop_sprites(self):
        """Load prop sprites."""
        print("Loading prop sprites...")
        self.prop_surfaces = {} # Ensure it's reset
        for prop_type, sprite_path_str in config.PROP_SPRITE_PATHS.items():
            full_sprite_path = os.path.join(config.BASE_DIR, sprite_path_str)

            if not os.path.exists(full_sprite_path):
                alt_path = os.path.join(config.ASSETS_DIR, sprite_path_str.replace("assets/", "", 1))
                if os.path.exists(alt_path):
                    full_sprite_path = alt_path
                else:
                    print(f"Warning: Prop sprite file not found: {sprite_path_str} (checked {full_sprite_path} and {alt_path}). Using fallback for {prop_type}.")
                    # Create a fallback colored surface
                    dims = config.PROP_SPRITE_DIMENSIONS.get(prop_type, (config.TILE_SIZE_MAP_DISPLAY, config.TILE_SIZE_MAP_DISPLAY))
                    fallback_surface = pygame.Surface(dims)
                    fallback_surface.fill(config.MISSING_PROP_SPRITE_COLOR)
                    pygame.draw.rect(fallback_surface, config.BLACK, fallback_surface.get_rect(), 1) # Border
                    self.prop_surfaces[prop_type] = fallback_surface
                    continue
            
            try:
                image = pygame.image.load(full_sprite_path).convert_alpha()
                # Optional: Scale if dimensions in config are different from image file
                # target_dims = config.PROP_SPRITE_DIMENSIONS.get(prop_type)
                # if target_dims and image.get_size() != target_dims:
                #     image = pygame.transform.scale(image, target_dims)
                self.prop_surfaces[prop_type] = image
                # print(f"Loaded prop sprite: {full_sprite_path} for {prop_type}")
            except pygame.error as e:
                print(f"Error loading prop sprite {full_sprite_path} for {prop_type}: {e}. Using fallback.")
                dims = config.PROP_SPRITE_DIMENSIONS.get(prop_type, (config.TILE_SIZE_MAP_DISPLAY, config.TILE_SIZE_MAP_DISPLAY))
                fallback_surface = pygame.Surface(dims)
                fallback_surface.fill(config.MISSING_PROP_SPRITE_COLOR)
                pygame.draw.rect(fallback_surface, config.BLACK, fallback_surface.get_rect(), 1)
                self.prop_surfaces[prop_type] = fallback_surface
            except FileNotFoundError:
                print(f"Warning: Prop sprite file not found (FNF): {full_sprite_path}. Using fallback for {prop_type}.")
                dims = config.PROP_SPRITE_DIMENSIONS.get(prop_type, (config.TILE_SIZE_MAP_DISPLAY, config.TILE_SIZE_MAP_DISPLAY))
                fallback_surface = pygame.Surface(dims)
                fallback_surface.fill(config.MISSING_PROP_SPRITE_COLOR)
                pygame.draw.rect(fallback_surface, config.BLACK, fallback_surface.get_rect(), 1)
                self.prop_surfaces[prop_type] = fallback_surface

        prop_surface_summary = {k: "Surface" if v else "None" for k, v in self.prop_surfaces.items()}
        print(f"Prop surfaces loaded: {prop_surface_summary}")

    def _load_resource_node_sprites(self):
        """Load resource node sprites (normal and depleted)."""
        print("Loading resource node sprites...")
        self.resource_node_surfaces = {} # Ensure it's reset
        for node_type_key, sprite_path_str in config.RESOURCE_NODE_SPRITE_PATHS.items():
            full_sprite_path = os.path.join(config.BASE_DIR, sprite_path_str)
            if not os.path.exists(full_sprite_path):
                alt_path = os.path.join(config.ASSETS_DIR, sprite_path_str.replace("assets/", "", 1))
                if os.path.exists(alt_path):
                    full_sprite_path = alt_path
                else:
                    print(f"Warning: Node sprite file not found: {sprite_path_str} (checked {full_sprite_path} and {alt_path}). Using fallback for {node_type_key}.")
                    # Create a fallback colored surface
                    # Dimensions could be TILE_SIZE_MAP_DISPLAY or from a new RESOURCE_NODE_SPRITE_DIMENSIONS in config
                    dims = getattr(config, 'RESOURCE_NODE_SPRITE_DIMENSIONS', {}).get(node_type_key, (config.TILE_SIZE_MAP_DISPLAY, config.TILE_SIZE_MAP_DISPLAY))
                    fallback_surface = pygame.Surface(dims)
                    fallback_surface.fill(config.MISSING_NODE_SPRITE_COLOR)
                    pygame.draw.rect(fallback_surface, config.BLACK, fallback_surface.get_rect(), 1) # Border
                    self.resource_node_surfaces[node_type_key] = fallback_surface
                    continue
            try:
                image = pygame.image.load(full_sprite_path).convert_alpha()
                # Optional: Scale if dimensions in config are different from image file
                # target_dims = getattr(config, 'RESOURCE_NODE_SPRITE_DIMENSIONS', {}).get(node_type_key)
                # if target_dims and image.get_size() != target_dims:
                #     image = pygame.transform.scale(image, target_dims)
                self.resource_node_surfaces[node_type_key] = image
            except pygame.error as e:
                print(f"Error loading node sprite {full_sprite_path} for {node_type_key}: {e}. Using fallback.")
                dims = getattr(config, 'RESOURCE_NODE_SPRITE_DIMENSIONS', {}).get(node_type_key, (config.TILE_SIZE_MAP_DISPLAY, config.TILE_SIZE_MAP_DISPLAY))
                fallback_surface = pygame.Surface(dims)
                fallback_surface.fill(config.MISSING_NODE_SPRITE_COLOR)
                pygame.draw.rect(fallback_surface, config.BLACK, fallback_surface.get_rect(), 1)
                self.resource_node_surfaces[node_type_key] = fallback_surface
        node_surface_summary = {k: "Surface" if v else "None" for k, v in self.resource_node_surfaces.items()}
        print(f"Resource node surfaces loaded: {node_surface_summary}")

    def _load_poi_sprites(self):
        """Load POI sprites and their minimap icons."""
        print("Loading POI sprites...")
        loaded_count = 0
        missing_count = 0

        # Load main POI sprites
        for poi_type, sprite_path_or_list in config.POI_SPRITE_PATHS.items():
            paths_to_try = [sprite_path_or_list] if isinstance(sprite_path_or_list, str) else sprite_path_or_list
            
            loaded_successfully_for_type = False
            for idx, sprite_path in enumerate(paths_to_try):
                full_path_abs = os.path.join(config.BASE_DIR, sprite_path)
                full_path_rel = sprite_path # Relative to workspace for clarity in logs
                
                target_dimensions = config.POI_SPRITE_DIMENSIONS.get(poi_type) # Can be None

                try:
                    # Try loading from absolute path first, then relative (common in some setups)
                    if os.path.exists(full_path_abs):
                        surface = self._load_image_scaled(full_path_abs, target_dimensions)
                    elif os.path.exists(full_path_rel): # Check relative to CWD if absolute fails
                        surface = self._load_image_scaled(full_path_rel, target_dimensions)
                    else:
                        raise FileNotFoundError(f"Sprite file not found at {full_path_abs} or {full_path_rel}")

                    # Store the first successfully loaded sprite for a given POI type
                    # More complex POIs might have multiple sprites (idle, active, etc.)
                    # For now, POI_SPRITE_PATHS points to the primary/base sprite.
                    if poi_type not in self.poi_surfaces: # Only load one per poi_type for now
                         self.poi_surfaces[poi_type] = surface
                         loaded_successfully_for_type = True
                         loaded_count +=1
                         break # Loaded one for this type
                except (pygame.error, FileNotFoundError) as e:
                    print(f"Warning: POI sprite file not found or error loading: {sprite_path} (checked {full_path_abs} and {full_path_rel}). {e}. Skipping for POI type {poi_type}.")
            
            if not loaded_successfully_for_type:
                missing_count += 1
                print(f"Warning: No sprites successfully loaded for POI type '{poi_type}'. It may use a fallback color if rendered directly or rely on PointOfInterest class for handling.")
                # Create a fallback surface if none loaded for this poi_type
                fallback_dims = target_dimensions if target_dimensions else (32,32) # Default fallback size
                surface = pygame.Surface(fallback_dims, pygame.SRCALPHA)
                surface.fill(config.MISSING_POI_SPRITE_COLOR)
                pygame.draw.rect(surface, config.WHITE, surface.get_rect(), 1) # Border
                self.poi_surfaces[poi_type] = surface


        # Load POI minimap icons
        print("Loading POI minimap icons...")
        for poi_type, definition in config.POI_DEFINITIONS.items():
            icon_path = definition.get("world_map_icon_path")
            if icon_path:
                full_path_abs = os.path.join(config.BASE_DIR, icon_path)
                full_path_rel = icon_path
                
                # Minimap icons are usually small, direct load without scaling unless specified
                # For now, let's assume they are pre-sized correctly.
                try:
                    if os.path.exists(full_path_abs):
                        icon_surface = self._load_image_scaled(full_path_abs, target_dimensions=None) # No specific scaling for now
                    elif os.path.exists(full_path_rel):
                        icon_surface = self._load_image_scaled(full_path_rel, target_dimensions=None)
                    else:
                         raise FileNotFoundError(f"Minimap icon file not found at {full_path_abs} or {full_path_rel}")
                    self.poi_minimap_icons[poi_type] = icon_surface
                except (pygame.error, FileNotFoundError) as e:
                    print(f"Warning: Minimap icon not found for POI '{poi_type}' at {icon_path}. {e}. A fallback might be used.")
                    # Create a small fallback icon
                    fallback_icon = pygame.Surface((8, 8), pygame.SRCALPHA)
                    fallback_icon.fill(config.MISSING_POI_SPRITE_COLOR) # Use same fallback color for now
                    self.poi_minimap_icons[poi_type] = fallback_icon
            else:
                 print(f"Note: No minimap icon path specified for POI type '{poi_type}'.")
                 fallback_icon = pygame.Surface((8, 8), pygame.SRCALPHA)
                 fallback_icon.fill(config.GRAY) # Default gray if no path
                 self.poi_minimap_icons[poi_type] = fallback_icon


        print(f"POI sprites loaded: {loaded_count} (main), Missing/Fallback: {missing_count} (main).")
        print(f"POI minimap icons loaded/created: {len(self.poi_minimap_icons)}.")

    def _generate_tile_variation_map(self, world_width, world_height):
        """Generate a map of tile variations using Perlin noise."""
        print(f"Generating tile variation map for {world_width}x{world_height} world...")
        self.tile_variation_map = [[0 for _ in range(world_width)] for _ in range(world_height)] # Initialize with 0

        for r in range(world_height):
            for c in range(world_width):
                # Assuming self.world_data[r][c] stores the tile_type string or an object with a 'type' attribute
                tile_info = self.world_data[r][c]
                current_tile_type = ""
                if isinstance(tile_info, str):
                    current_tile_type = tile_info
                elif isinstance(tile_info, dict) and "type" in tile_info: # If world_data stores dicts per tile
                    current_tile_type = tile_info["type"]
                else:
                    # Fallback or error for unknown world_data structure for this tile
                    # print(f"Warning: Unknown tile data structure at ({r},{c}): {tile_info}. Using default variation.")
                    self.tile_variation_map[r][c] = 0 # Default to first variation or handle as error
                    continue

                if current_tile_type in self.tile_surfaces and self.tile_surfaces[current_tile_type]:
                    num_variations = len(self.tile_surfaces[current_tile_type])
                    if num_variations > 1:
                        # Ensure TILE_VARIATION_SEED is an int. Pygame's noise functions might prefer float or int.
                        # The `noise` library's pnoise2 'base' is the seed.
                        noise_seed = int(config.TILE_VARIATION_SEED)

                        noise_val = noise.pnoise2(
                            c * config.TILE_VARIATION_NOISE_SCALE,
                            r * config.TILE_VARIATION_NOISE_SCALE,
                            octaves=1, # Keep simple for now
                            persistence=0.5,
                            lacunarity=2.0,
                            repeatx=world_width * config.TILE_VARIATION_NOISE_SCALE, # Consider noise domain for repeat
                            repeaty=world_height * config.TILE_VARIATION_NOISE_SCALE,
                            base=noise_seed
                        )
                        # pnoise2 returns values in [-1, 1] (approx). Normalize to [0, 1]
                        normalized_noise = (noise_val + 1) / 2.0
                        variation_index = int(normalized_noise * num_variations) % num_variations
                        self.tile_variation_map[r][c] = variation_index
                    else:
                        self.tile_variation_map[r][c] = 0 # Only one variation, so index is 0
                else:
                    self.tile_variation_map[r][c] = -1 # Mark for fallback color (no sprites for this type)
        print("Tile variation map generated.")
        # For debugging: print a snippet of the map
        # for i in range(min(5, world_height)):
        # print(self.tile_variation_map[i][:min(5, world_width)])
        
    def _create_default_world_data_internal(self):
        """
        Creates a default world data grid and populates self.world_data.
        This is a placeholder and should align with how create_default_files structures world_map.json.
        """
        print("Creating default internal world data...")
        width = config.WORLD_MAP_WIDTH
        height = config.WORLD_MAP_HEIGHT
        default_tile = "grass" # Or some other default from your TILE_SPRITE_PATHS

        self.world_data = [[default_tile for _ in range(width)] for _ in range(height)]
        
        # Example: Place a city center tile
        # This needs to match the structure expected by _generate_tile_variation_map
        # and how world_map.json is structured if it contains tile data directly.
        # If world_map.json only stores city positions and points of interest,
        # then the actual tile grid might be generated elsewhere or procedurally.
        # For now, assume a simple grid of tile type strings.
        # city_x = width // 2
        # city_y = height // 2
        # if "city_center" in config.TILE_SPRITE_PATHS:
        #     if 0 <= city_y < height and 0 <= city_x < width:
        #         self.world_data[city_y][city_x] = "city_center"
        print("Default internal world data created.")

    @classmethod
    def create_default_files(cls):
        """Create default data files if they don't exist
        
        This is useful for a fresh installation or to reset the game.
        """
        # Default spell data
        if not os.path.exists(config.SPELLS_DATA):
            default_spells = {
                "basic_projectile": {
                    "name": "Basic Bolt",
                    "description": "Fires a simple magical bolt.",
                    "type": "PROJECTILE", 
                    "damage": 10,
                    "cooldown": 0.5, 
                    "range": 300, 
                    "speed": 250, 
                    "projectile_sprite": "default_projectile.png", 
                    "trajectory_properties": {"type": "HOMING", "homing_strength": 0.1, "radius": 6, "color": [255, 165, 0]}, # Orange, Homing
                    "upgrades": {}
                },
                "fireball": {
                    "name": "Fireball",
                    "description": "Launches a fiery explosion.",
                    "type": "PROJECTILE_AOE", 
                    "damage": 25,
                    "cooldown": 2.0,
                    "range": 400,
                    "speed": 200,
                    "aoe_radius": 50,
                    "projectile_sprite": "fireball.png",
                    "trajectory_properties": {"type": "STRAIGHT", "radius": 8, "color": [255, 0, 0]}, # Red, Straight
                    "upgrades": {}
                },
                "orbiting_blades": {
                    "name": "Orbiting Blades",
                    "description": "Summons magical blades that orbit the caster.",
                    "type": "PROJECTILE",
                    "damage": 5,
                    "cooldown": 15.0,
                    "range": 0,
                    "speed": 0,
                    "projectile_sprite": "default_orbiter.png",
                    "trajectory_properties": {
                        "type": "ORBITING", 
                        "orbit_radius": 80, 
                        "angular_speed": 3, # Radians per second
                        "duration": 10, # Seconds
                        "radius": 7, 
                        "color": [100, 180, 255] # Light blue
                    },
                    "upgrades": {}
                },
                "wave_pulse": {
                    "name": "Wave Pulse",
                    "description": "Fires a pulse that travels in a sine wave.",
                    "type": "PROJECTILE",
                    "damage": 12,
                    "cooldown": 0.8,
                    "range": 350,
                    "speed": 200, # Speed along the central path
                    "projectile_sprite": "default_wave_pulse.png",
                    "trajectory_properties": {
                        "type": "SINE_WAVE", 
                        "amplitude": 30,
                        "frequency": 5,
                        "radius": 5,
                        "color": [0, 255, 255] # Cyan
                    },
                    "upgrades": {}
                },
                "returning_disk": {
                    "name": "Returning Disk",
                    "description": "Throws a disk that returns to the caster.",
                    "type": "PROJECTILE",
                    "damage": 15,
                    "cooldown": 1.2,
                    "range": 250, # Outward travel distance
                    "speed": 300,
                    "projectile_sprite": "default_disk.png",
                    "trajectory_properties": {
                        "type": "BOOMERANG",
                        "radius": 10,     
                        "color": [128, 0, 128] # Purple
                    },
                    "upgrades": {}
                },
                "chain_spark": {
                    "name": "Chain Spark",
                    "description": "A spark that jumps between enemies.",
                    "type": "PROJECTILE",
                    "damage": 8,
                    "cooldown": 1.0,
                    "range": 300,
                    "speed": 350,
                    "projectile_sprite": "default_spark.png",
                    "trajectory_properties": {
                        "type": "CHAIN",
                        "max_chains": 3,
                        "chain_radius": 150,
                        "radius": 4,      
                        "color": [255, 255, 0] # Yellow
                    },
                    "upgrades": {}
                },
                "piercing_bolt": {
                    "name": "Piercing Bolt",
                    "description": "A bolt that pierces through multiple enemies.",
                    "type": "PROJECTILE",
                    "damage": 12,
                    "cooldown": 0.7,
                    "range": 400,
                    "speed": 300,
                    "projectile_sprite": "default_piercing.png",
                    "trajectory_properties": {
                        "type": "PIERCING",
                        "pierce_count": 3,
                        "radius": 5,      
                        "color": [200, 200, 200] # Light Gray
                    },
                    "upgrades": {}
                },
                "meteor_shard": {
                    "name": "Meteor Shard",
                    "description": "Calls down a shard that explodes at the target location after a delay.",
                    "type": "PROJECTILE",
                    "damage": 0,
                    "cooldown": 2.5,
                    "range": 1000,
                    "speed": 0,
                    "projectile_sprite": "default_marker.png",
                    "trajectory_properties": {
                        "type": "GROUND_AOE",
                        "travel_speed": 500,
                        "aoe_radius": 80,
                        "aoe_damage": 30,
                        "aoe_duration": 0.2,
                        "delay_after_arrival": 0.3,
                        "marker_radius": 6,      
                        "marker_color": [255, 120, 0],
                        "aoe_visual_color": [255, 60, 0, 180]
                    },
                    "upgrades": {}
                },
                "spiral_blast": {
                    "name": "Spiral Blast",
                    "description": "Launches a spiraling energy blast.",
                    "type": "PROJECTILE", 
                    "damage": 7, 
                    "cooldown": 1.0,
                    "range": 0,
                    "speed": 0,
                    "projectile_sprite": "default_spiral.png", 
                    "trajectory_properties": {
                        "type": "SPIRAL",
                        "expansion_speed": 40,
                        "rotation_speed": 720,
                        "base_travel_speed": 150,
                        "duration": 1.5,
                        "initial_radius": 5,
                        "radius": 5,
                        "color": [200, 0, 255]
                    },
                    "upgrades": {}
                },
                "forking_bolt": {
                    "name": "Forking Bolt",
                    "description": "A bolt that splits into smaller fragments.",
                    "type": "PROJECTILE", 
                    "damage": 10,
                    "cooldown": 1.5,
                    "range": 150,
                    "speed": 250, 
                    "projectile_sprite": "default_forker.png", 
                    "trajectory_properties": {
                        "type": "FORKING",
                        "fork_condition_type": "DISTANCE",
                        "fork_condition_value": 150,
                        "fork_count": 3,               
                        "fork_angle_spread": 45,
                        "child_spell_id": "seeking_fragment",
                        "radius": 6,      
                        "color": [0, 255, 0]
                    },
                    "upgrades": {}
                },
                "seeking_fragment": {
                    "name": "Seeking Fragment",
                    "description": "A small, homing fragment.",
                    "type": "PROJECTILE",
                    "damage": 5,
                    "cooldown": 0, # Not directly castable
                    "range": 200,
                    "speed": 300,
                    "projectile_sprite": "default_fragment.png",
                    "trajectory_properties": {
                        "type": "HOMING",
                        "homing_strength": 0.2,
                        "duration": 2.0,
                        "radius": 3,
                        "color": [100, 255, 100] 
                    },
                    "upgrades": {}
                },
                "growing_orb_spell": {
                    "name": "Growing Orb",
                    "description": "An orb that expands as it travels.",
                    "type": "PROJECTILE",
                    "damage": 15,
                    "cooldown": 2.0,
                    "range": 500,
                    "speed": 100,
                    "projectile_sprite": "default_growing_orb.png",
                    "trajectory_properties": {
                        "type": "GROWING_ORB",
                        "initial_radius": 5,
                        "max_radius": 50,
                        "growth_rate": 20,
                        "growth_duration": 2.5,
                        "color": [173, 216, 230]
                    },
                    "upgrades": {}
                }
            }
            cls.save_json(default_spells, config.SPELLS_DATA)
            print(f"Created default {config.SPELLS_DATA}")

        # Default relic data
        if not os.path.exists(config.RELICS_DATA):
            default_relics = {
                "strength_tome_1": {
                    "name": "Tome of Strength I",
                    "description": "Slightly increases attack damage.",
                    "effects": {"spell_damage_percent": 5}
                }
                # Add other default relics here if any were previously defined and correct
            }
            cls.save_json(default_relics, config.RELICS_DATA)
            print(f"Created default {config.RELICS_DATA}")

        # Default enemy data
        if not os.path.exists(config.ENEMIES_DATA):
            default_enemies = {
                "goblin_grunt": {
                    "name": "Goblin Grunt",
                    "hp": 20,
                    "damage": 5,
                    "speed": 1.5,
                    "xp_value": 10,
                    "sprite": "goblin_grunt.png"
                }
                # Add other default enemies here if any
            }
            cls.save_json(default_enemies, config.ENEMIES_DATA)
            print(f"Created default {config.ENEMIES_DATA}")

        # Default wave data
        if not os.path.exists(config.WAVES_DATA):
            default_waves = {
                "day_1": {
                    "waves": [
                        {"enemy_type": "goblin_grunt", "count": 5, "interval": 2.0},
                        {"enemy_type": "goblin_grunt", "count": 8, "interval": 1.5, "delay": 5.0}
                    ]
                }
                # Add other default day waves here if any
            }
            cls.save_json(default_waves, config.WAVES_DATA)
            print(f"Created default {config.WAVES_DATA}")

        # Default building data
        if not os.path.exists(config.BUILDINGS_DATA):
            default_buildings = {
                "basic_wall": {
                    "name": "Basic Wall",
                    "cost": {"wood": 50},
                    "hp_bonus": 100,
                    "description": "A simple wooden wall segment."
                }
                # Add other default buildings here if any
            }
            cls.save_json(default_buildings, config.BUILDINGS_DATA)
            print(f"Created default {config.BUILDINGS_DATA}")
            
        # world_map.json
        if not os.path.exists(config.WORLD_MAP_DATA):
            default_row_plain = ["grass" for _ in range(config.WORLD_MAP_WIDTH)]
            default_row_rle = cls._encode_row_rle(default_row_plain)
            
            # Define some default POIs if POI types are available in config
            default_pois = []
            if "abandoned_shrine" in config.POI_DEFINITIONS:
                default_pois.append({
                    "id": "default_shrine_1",
                    "type": "abandoned_shrine",
                    "tile_x": 20,
                    "tile_y": 20,
                    "saved_state": None # Will be initialized by POI class
                })
            if "monster_den" in config.POI_DEFINITIONS:
                default_pois.append({
                    "id": "default_den_1",
                    "type": "monster_den",
                    "tile_x": 80,
                    "tile_y": 80,
                    "saved_state": None # Will be initialized by POI class
                })
            if "ancient_ruin" in config.POI_DEFINITIONS: # Add a ruin too if defined
                default_pois.append({
                    "id": "default_ruin_1",
                    "type": "ancient_ruin",
                    "tile_x": 20,
                    "tile_y": 80, # Different location
                    "saved_state": None
                })


            default_world_map = {
                "width": config.WORLD_MAP_WIDTH,
                "height": config.WORLD_MAP_HEIGHT,
                "tile_data_format": "list_of_lists_rle",
                "generated_by": "DataHandler.create_default_files",
                "generation_timestamp": "timestamp_placeholder", 
                "static_props": [], 
                "resource_nodes": [],
                "points_of_interest": default_pois, # MODIFIED: Use the generated list
                "tiles": [default_row_rle for _ in range(config.WORLD_MAP_HEIGHT)]
            }
            cls.save_json(default_world_map, config.WORLD_MAP_DATA)
            print(f"Created default {config.WORLD_MAP_DATA} with RLE format")
            
        print("Default file check complete.")

    def _ensure_config_import(self, file_path):
        # Check if config is imported, if not, add it.
        # This is a simple check and might need to be more robust.
        with open(file_path, 'r+') as f:
            content = f.read()
            if "from src import config" not in content and "import config" not in content :
                f.seek(0, 0)
                # Look for the first import or the beginning of the file
                lines = content.split('\n')
                import_added = False
                new_lines = []
                for line in lines:
                    if line.startswith("import ") or line.startswith("from "):
                        new_lines.append("from src import config")
                        new_lines.append(line)
                        import_added = True
                        break
                    new_lines.append(line)
                
                if not import_added: # Prepend if no imports found
                    f.write("from src import config\n" + content)
                else: # Reconstruct if import was added mid-file
                    idx = lines.index(new_lines[new_lines.index("from src import config")+1])
                    final_content = "\n".join(lines[:idx]) + "\nfrom src import config\n" + "\n".join(lines[idx:])
                    f.seek(0)
                    f.write(final_content)
                    f.truncate()

    def update_and_save_world_map_nodes(self, list_of_node_data_to_save): # WILL NEED REFACTORING
        """Updates the resource node states in raw_world_map_json and saves the file."""
        # This method needs to be generalized to update not just nodes, 
        # but any dynamic element on the world map, like POIs.
        # For now, it will only handle nodes as per its current design.
        # A new method or a refactor will be part of Phase 2.
        if not self.raw_world_map_json:
            print("Warning: DataHandler.update_and_save_world_map_nodes: raw_world_map_json not loaded. Attempting to load.")
            self.raw_world_map_json = DataHandler.load_json(config.WORLD_MAP_DATA)
            if not self.raw_world_map_json : # If still not loaded (e.g. file missing and not regenerated yet)
                print("Error: raw_world_map_json still not loaded after attempt. Cannot save node states.")
                return

        # Ensure 'resource_nodes' key exists
        if "resource_nodes" not in self.raw_world_map_json:
            self.raw_world_map_json["resource_nodes"] = []
            print("Warning: 'resource_nodes' key was missing in raw_world_map_json. Initialized as empty list.")

        
        # Create a dictionary of new node data by ID for quick lookup
        new_node_data_map = {node_data["id"]: node_data for node_data in list_of_node_data_to_save}

        # Update existing nodes or add new ones
        found_ids = set()
        for i, existing_node_def in enumerate(self.raw_world_map_json["resource_nodes"]):
            node_id = existing_node_def.get("id")
            if node_id in new_node_data_map:
                self.raw_world_map_json["resource_nodes"][i] = new_node_data_map[node_id]
                found_ids.add(node_id)
        
        # Add any new nodes that weren't in the original list
        for node_id, node_data in new_node_data_map.items():
            if node_id not in found_ids:
                self.raw_world_map_json["resource_nodes"].append(node_data)
                print(f"Added new node {node_id} to world_map.json during save.")

        try:
            DataHandler.save_json(self.raw_world_map_json, config.WORLD_MAP_DATA)
            # print(f"World map node states saved to {config.WORLD_MAP_DATA}")
        except Exception as e:
            print(f"Error saving world map node states to {config.WORLD_MAP_DATA}: {e}")

    def update_and_save_world_map_pois(self, list_of_poi_data_to_save): # ADDED METHOD
        """Updates the Point of Interest states in raw_world_map_json and saves the file."""
        if not self.raw_world_map_json:
            print("Warning: DataHandler.update_and_save_world_map_pois: raw_world_map_json not loaded. Attempting to load.")
            self.raw_world_map_json = DataHandler.load_json(config.WORLD_MAP_DATA)
            if not self.raw_world_map_json:
                print("Error: raw_world_map_json still not loaded after attempt. Cannot save POI states.")
                return

        if "points_of_interest" not in self.raw_world_map_json:
            self.raw_world_map_json["points_of_interest"] = []
            print("Warning: 'points_of_interest' key was missing in raw_world_map_json. Initialized as empty list.")

        new_poi_data_map = {poi_data["id"]: poi_data for poi_data in list_of_poi_data_to_save}
        found_ids = set()

        # Update existing POIs or add new ones
        # Need to iterate over a copy if modifying the list during iteration, or use indices
        updated_pois_list = []
        existing_pois = self.raw_world_map_json.get("points_of_interest", [])

        for existing_poi_def in existing_pois:
            poi_id = existing_poi_def.get("id")
            if poi_id in new_poi_data_map:
                # Update with new data (which includes full definition + saved_state)
                updated_pois_list.append(new_poi_data_map[poi_id])
                found_ids.add(poi_id)
            else:
                # Keep existing POI if not in the new data (should not happen if list_of_poi_data_to_save is comprehensive)
                updated_pois_list.append(existing_poi_def) 

        # Add any new POIs that weren't in the original list 
        # (e.g. if a POI was procedurally generated and now needs saving)
        for poi_id, poi_data in new_poi_data_map.items():
            if poi_id not in found_ids:
                updated_pois_list.append(poi_data)
                print(f"Added new POI {poi_id} to world_map.json during save.")
        
        self.raw_world_map_json["points_of_interest"] = updated_pois_list

        try:
            # Use the static save_json method, consistent with other save operations.
            # The first argument should be the data to save, the second is the file path.
            # An earlier version of update_and_save_world_map_nodes had this reversed.
            DataHandler.save_json(self.raw_world_map_json, config.WORLD_MAP_DATA) 
            # print(f"World map POI states saved to {config.WORLD_MAP_DATA}")
        except Exception as e:
            print(f"Error saving world map POI states to {config.WORLD_MAP_DATA}: {e}")

    # Method to be refactored/created in Phase 2 for generic world map element saving:
    # def update_and_save_world_map_dynamic_elements(self, dynamic_elements_data):
    #     pass
        
# Example usage (typically in GameManager or specific game states)
# data_handler = DataHandler()
# data_handler.load_all_data()
# player_progress = data_handler.load_player_save()
# data_handler.save_player_data(player_progress)

