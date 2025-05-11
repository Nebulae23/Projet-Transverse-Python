"""
Magic Survivor - Tilemap System

This module provides a tilemap system for handling tile-based maps.
"""

import pygame
import json
import os
import random
from src import config

class Tile:
    """Class representing a single tile"""
    
    def __init__(self, x, y, tile_type, image, tile_pixel_width, tile_pixel_height, walkable=True, properties=None):
        """Initialize a tile
        
        Args:
            x (int): X position in tile coordinates
            y (int): Y position in tile coordinates
            tile_type (str): Type of tile (e.g. "grass", "water", "road")
            image (pygame.Surface): Image for the tile
            tile_pixel_width (int): The actual width of the tile image in pixels.
            tile_pixel_height (int): The actual height of the tile image in pixels.
            walkable (bool): Whether the tile can be walked on
            properties (dict): Additional properties for the tile
        """
        self.x = x
        self.y = y
        self.tile_type = tile_type
        self.image = image
        self.walkable = walkable
        self.properties = properties or {}
        
        # Set up rect for drawing and collision using actual image dimensions
        self.rect = pygame.Rect(x * tile_pixel_width, y * tile_pixel_height, 
                               tile_pixel_width, tile_pixel_height)
    
    def render(self, screen, camera=None):
        """Render the tile
        
        Args:
            screen (pygame.Surface): Screen to render to
            camera (Camera): Camera for scrolling
        """
        draw_rect = self.rect.copy()
        
        # Apply camera offset if provided
        if camera:
            draw_rect = camera.apply_rect(self.rect)
        
        # Only draw if on screen
        if (draw_rect.right > 0 and draw_rect.left < config.SCREEN_WIDTH and
            draw_rect.bottom > 0 and draw_rect.top < config.SCREEN_HEIGHT):
            screen.blit(self.image, draw_rect)
    
    def get_center_position(self):
        """Get the center position of the tile in world coordinates
        
        Returns:
            tuple: Center position (x, y)
        """
        return (self.rect.centerx, self.rect.centery)


class TileMap:
    """Class representing a tilemap"""
    
    def __init__(self, width, height, tile_size=32, data_handler=None):
        """Initialize a tilemap
        
        Args:
            width (int): Width of the map in tiles
            height (int): Height of the map in tiles
            tile_size (int): Size of each tile in pixels
            data_handler (DataHandler, optional): Reference to the data handler for sprites.
        """
        self.width = width
        self.height = height
        self.tile_size = tile_size
        self.data_handler = data_handler
        self.tiles = {}  # Dict of {(x, y): Tile}
        self.tile_images = {}  # Dict of {tile_type: pygame.Surface}
        self.collision_tiles = []  # List of non-walkable tiles for collision detection
        
        # Size in pixels
        self.pixel_width = width * tile_size
        self.pixel_height = height * tile_size
    
    def load_tileset(self, tileset_image, tile_types, tile_size=32):
        """Load a tileset image and cut it into individual tiles
        
        Args:
            tileset_image (str): Path to the tileset image
            tile_types (list): List of tile types corresponding to the tileset
            tile_size (int): Size of each tile in pixels
        """
        try:
            tileset = pygame.image.load(tileset_image).convert_alpha()
            
            # Get the dimensions of the tileset
            tileset_width = tileset.get_width() // tile_size
            tileset_height = tileset.get_height() // tile_size
            
            # Cut the tileset into individual tiles
            for y in range(tileset_height):
                for x in range(tileset_width):
                    # Get the tile from the tileset
                    rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
                    tile_image = tileset.subsurface(rect)
                    
                    # Get the tile type
                    index = y * tileset_width + x
                    if index < len(tile_types):
                        self.tile_images[tile_types[index]] = tile_image
        
        except pygame.error as e:
            print(f"Error loading tileset: {e}")
    
    def generate_simple_tileset(self, colors):
        """Generate a simple tileset from colors for testing
        
        Args:
            colors (dict): Dictionary of {tile_type: (r, g, b)} colors
        """
        for tile_type, color in colors.items():
            # Create a colored square
            image = pygame.Surface((self.tile_size, self.tile_size))
            image.fill(color)
            
            # Add a grid line for visual clarity
            pygame.draw.rect(image, (0, 0, 0), (0, 0, self.tile_size, self.tile_size), 1)
            
            # Store the image
            self.tile_images[tile_type] = image
    
    def set_tile(self, x, y, tile_type, walkable=True, properties=None):
        """Set a tile at the given position
        
        Args:
            x (int): X position in tile coordinates
            y (int): Y position in tile coordinates
            tile_type (str): Type of tile
            walkable (bool): Whether the tile can be walked on
            properties (dict): Additional properties for the tile
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            return # Out of bounds

        image_to_use = None

        if (self.data_handler and 
            hasattr(self.data_handler, 'tile_surfaces') and self.data_handler.tile_surfaces and 
            hasattr(self.data_handler, 'tile_variation_map') and self.data_handler.tile_variation_map):
            
            # Ensure map dimensions match variation map dimensions if possible
            # This is a sanity check; ideally, they are always in sync.
            if y < len(self.data_handler.tile_variation_map) and x < len(self.data_handler.tile_variation_map[y]):
                variation_index = self.data_handler.tile_variation_map[y][x]
                if tile_type in self.data_handler.tile_surfaces and self.data_handler.tile_surfaces[tile_type]:
                    surface_list = self.data_handler.tile_surfaces[tile_type]
                    if 0 <= variation_index < len(surface_list):
                        image_to_use = surface_list[variation_index]
                    elif surface_list: # Fallback to first variation if index is bad
                        image_to_use = surface_list[0]
                        # print(f"Debug: Bad variation index {variation_index} for {tile_type} at ({x},{y}). Using first variation.")
                    # else: print(f"Debug: Empty surface list for {tile_type} at ({x},{y}) despite variation map.")
                # else: print(f"Debug: Tile type {tile_type} not in data_handler.tile_surfaces at ({x},{y}).")
            # else: print(f"Debug: Coords ({x},{y}) out of bounds for tile_variation_map.")
        # else: print("Debug: DataHandler or its sprite/variation maps not available for set_tile.")

        # Fallback to self.tile_images (e.g., from generate_simple_tileset)
        if image_to_use is None:
            if tile_type in self.tile_images:
                image_to_use = self.tile_images[tile_type]
                # print(f"Debug: Using pre-generated image for {tile_type} at ({x},{y}) from self.tile_images.")
            else:
                # Ultimate fallback: create a magenta square
                print(f"Warning: No sprite or pre-generated image for tile_type '{tile_type}' at ({x},{y}). Using default fallback color.")
                image_to_use = pygame.Surface((self.tile_size, self.tile_size))
                image_to_use.fill(config.DEFAULT_TILE_SPRITE_FALLBACK_COLOR)
                # For visual debugging of this state, add a border or pattern
                pygame.draw.line(image_to_use, config.BLACK, (0,0), (self.tile_size, self.tile_size), 1)
                pygame.draw.line(image_to_use, config.BLACK, (0,self.tile_size), (self.tile_size, 0), 1)
        
        if image_to_use:
            # Create the tile
            # Ensure the tile_size used for Tile's rect matches the actual image dimensions
            # which should be config.TILE_SPRITE_DIMENSIONS if loaded from data_handler
            # or self.tile_size if from generate_simple_tileset or fallback.
            actual_tile_w, actual_tile_h = image_to_use.get_size()
            tile = Tile(x, y, tile_type, image_to_use, actual_tile_w, actual_tile_h, walkable, properties)
            
            # Store the tile
            self.tiles[(x, y)] = tile
            
            # Add to collision tiles if not walkable
            if not walkable:
                self.collision_tiles.append(tile)
        # else: print(f"Error: Could not determine image for tile {tile_type} at ({x},{y}). Tile not set.")
    
    def get_tile(self, x, y):
        """Get the tile at the given position
        
        Args:
            x (int): X position in tile coordinates
            y (int): Y position in tile coordinates
            
        Returns:
            Tile or None: The tile at the given position, or None if no tile
        """
        return self.tiles.get((x, y))
    
    def get_tile_at_pixel(self, pixel_x, pixel_y):
        """Get the tile at the given pixel position
        
        Args:
            pixel_x (int): X position in pixels
            pixel_y (int): Y position in pixels
            
        Returns:
            Tile or None: The tile at the given position, or None if no tile
        """
        # Convert pixel coordinates to tile coordinates
        tile_x = pixel_x // self.tile_size
        tile_y = pixel_y // self.tile_size
        
        return self.get_tile(tile_x, tile_y)
    
    def render(self, screen, camera=None):
        """Render the tilemap
        
        Args:
            screen (pygame.Surface): Screen to render to
            camera (Camera): Camera for scrolling
        """
        # Get the visible area in tile coordinates
        if camera:
            start_x = max(0, camera.rect.left // self.tile_size)
            start_y = max(0, camera.rect.top // self.tile_size)
            end_x = min(self.width, (camera.rect.right // self.tile_size) + 1)
            end_y = min(self.height, (camera.rect.bottom // self.tile_size) + 1)
        else:
            start_x, start_y = 0, 0
            end_x, end_y = self.width, self.height
        
        # Render only the visible tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = self.get_tile(x, y)
                if tile:
                    tile.render(screen, camera)
    
    def is_walkable(self, x, y):
        """Check if the given position is walkable
        
        Args:
            x (int): X position in tile coordinates
            y (int): Y position in tile coordinates
            
        Returns:
            bool: True if walkable, False otherwise
        """
        tile = self.get_tile(x, y)
        return tile is not None and tile.walkable
    
    def is_walkable_pixel(self, pixel_x, pixel_y):
        """Check if the given pixel position is walkable
        
        Args:
            pixel_x (int): X position in pixels
            pixel_y (int): Y position in pixels
            
        Returns:
            bool: True if walkable, False otherwise
        """
        tile = self.get_tile_at_pixel(pixel_x, pixel_y)
        return tile is not None and tile.walkable
    
    def get_path(self, start_x, start_y, end_x, end_y):
        """Get a path from start to end (simple implementation)
        
        Args:
            start_x (int): Start X position in tile coordinates
            start_y (int): Start Y position in tile coordinates
            end_x (int): End X position in tile coordinates
            end_y (int): End Y position in tile coordinates
            
        Returns:
            list: List of (x, y) positions forming a path
        """
        # This is a very simple direct path - a real implementation would use A*
        path = []
        
        # Get the direction
        dx = 1 if end_x > start_x else -1 if end_x < start_x else 0
        dy = 1 if end_y > start_y else -1 if end_y < start_y else 0
        
        # Start at the beginning
        x, y = start_x, start_y
        
        # Add steps until we reach the end
        while x != end_x or y != end_y:
            # Try to move in both directions if possible
            if x != end_x and self.is_walkable(x + dx, y):
                x += dx
            elif y != end_y and self.is_walkable(x, y + dy):
                y += dy
            else:
                # We're stuck, try a diagonal
                if x != end_x and y != end_y and self.is_walkable(x + dx, y + dy):
                    x += dx
                    y += dy
                else:
                    # No path
                    break
            
            path.append((x, y))
        
        return path
    
    def generate_random_map(self, default_tile="grass", feature_tiles=None, feature_probability=0.1):
        """Generate a random map
        
        Args:
            default_tile (str): Default tile type
            feature_tiles (dict): Dictionary of {tile_type: probability} feature tiles
            feature_probability (float): Overall probability of a feature tile
        """
        feature_tiles = feature_tiles or {
            "water": 0.5,
            "mountain": 0.5
        }
        
        # Fill the map with the default tile
        for y in range(self.height):
            for x in range(self.width):
                self.set_tile(x, y, default_tile, True)
        
        # Add feature tiles
        for y in range(self.height):
            for x in range(self.width):
                if random.random() < feature_probability:
                    # Choose a feature tile
                    feature_type = random.choices(
                        list(feature_tiles.keys()),
                        weights=list(feature_tiles.values()),
                        k=1
                    )[0]
                    
                    # Set the tile
                    walkable = feature_type != "mountain"  # Example: mountains aren't walkable
                    self.set_tile(x, y, feature_type, walkable)
    
    def save_to_file(self, filename):
        """Save the tilemap to a file
        
        Args:
            filename (str): Path to save the file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            map_data = {
                "width": self.width,
                "height": self.height,
                "tile_size": self.tile_size,
                "tiles": []
            }
            
            # Convert tiles to a serializable format
            for (x, y), tile in self.tiles.items():
                map_data["tiles"].append({
                    "x": x,
                    "y": y,
                    "type": tile.tile_type,
                    "walkable": tile.walkable,
                    "properties": tile.properties
                })
            
            # Save to file
            with open(filename, "w") as f:
                json.dump(map_data, f, indent=4)
            
            return True
        
        except Exception as e:
            print(f"Error saving tilemap: {e}")
            return False
    
    def load_from_file(self, filename):
        """Load the tilemap from a file
        
        Args:
            filename (str): Path to the file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Load from file
            with open(filename, "r") as f:
                map_data = json.load(f)
            
            # Set the map properties
            self.width = map_data["width"]
            self.height = map_data["height"]
            self.tile_size = map_data["tile_size"]
            self.pixel_width = self.width * self.tile_size
            self.pixel_height = self.height * self.tile_size
            
            # Clear existing tiles
            self.tiles = {}
            self.collision_tiles = []
            
            # Load the tiles
            for tile_data in map_data["tiles"]:
                self.set_tile(
                    tile_data["x"],
                    tile_data["y"],
                    tile_data["type"],
                    tile_data["walkable"],
                    tile_data.get("properties", {})
                )
            
            return True
        
        except Exception as e:
            print(f"Error loading tilemap: {e}")
            return False 