import pygame
from src import config

class StaticProp:
    """Represents a static visual prop on the world map."""
    def __init__(self, prop_type, tile_x, tile_y, surface, offset_x=0, offset_y=0, layer=0):
        """Initialize a static prop.

        Args:
            prop_type (str): The type of the prop (e.g., 'small_rock').
            tile_x (int): The X coordinate of the tile the prop is anchored to.
            tile_y (int): The Y coordinate of the tile the prop is anchored to.
            surface (pygame.Surface): The pre-loaded image/surface for this prop.
            offset_x (int, optional): Pixel offset from the anchor tile's top-left. Defaults to 0.
            offset_y (int, optional): Pixel offset from the anchor tile's top-left. Defaults to 0.
            layer (int, optional): Rendering layer (for potential future use). Defaults to 0.
        """
        self.prop_type = prop_type
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.surface = surface
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.layer = layer # Store layer for potential future sorting or effects

        if self.surface:
            self.width = self.surface.get_width()
            self.height = self.surface.get_height()
        else:
            # Fallback dimensions if surface is None (e.g. failed to load)
            # This might happen if _load_prop_sprites stores None instead of a fallback surface
            # Or, use dimensions from config if available
            fallback_dims = config.PROP_SPRITE_DIMENSIONS.get(prop_type, (config.TILE_SIZE_MAP_DISPLAY, config.TILE_SIZE_MAP_DISPLAY))
            self.width = fallback_dims[0]
            self.height = fallback_dims[1]
            print(f"Warning: StaticProp '{prop_type}' initialized without a valid surface. Using fallback dimensions: {self.width}x{self.height}")

        # Calculate the prop's world position based on anchor tile and offsets
        # This is the top-left of the prop itself in world pixel coordinates
        self.world_x = (self.tile_x * config.TILE_SIZE_MAP_DISPLAY) + self.offset_x
        self.world_y = (self.tile_y * config.TILE_SIZE_MAP_DISPLAY) + self.offset_y

        # Create a rect for the prop in world coordinates, useful for culling or interaction
        self.rect = pygame.Rect(self.world_x, self.world_y, self.width, self.height)

    def render(self, screen, camera):
        """Render the prop if it has a surface and is on screen.

        Args:
            screen (pygame.Surface): The screen to draw on.
            camera (Camera): The game camera for applying transformations.
        """
        if not self.surface:
            # If there's no surface (e.g., sprite failed to load and no fallback was made in DataHandler),
            # we could draw a placeholder or skip. For now, skip.
            # A fallback colored rectangle could be drawn here if desired, 
            # using self.width, self.height and MISSING_PROP_SPRITE_COLOR.
            return

        # Apply camera to the prop's world rect to get screen coordinates
        screen_rect = camera.apply_rect(self.rect)

        # Basic culling: only draw if visible on screen
        if screen_rect.colliderect(screen.get_rect()):
            screen.blit(self.surface, screen_rect.topleft)

    def get_render_sort_key(self):
        """Get a key for depth sorting. Lower Y means further back (rendered first usually).
           Objects further down (higher Y) or with a higher layer value render on top.
           Sorting by the bottom edge of the prop.
        """
        # Sort primarily by the bottom Y coordinate of the prop in the world
        # A secondary sort key (like X or original index) can be added for tie-breaking if needed
        return self.world_y + self.height # Sort by bottom edge
        # Alternative: return (self.layer, self.world_y + self.height) for layer-based sorting primarily 