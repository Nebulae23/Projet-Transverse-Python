import pygame
import random
from src import config

class ResourceNode:
    """Represents an interactive resource node on the world map."""
    def __init__(self, node_id, node_type, tile_x, tile_y, initial_surface, depleted_surface=None, saved_state=None):
        """Initialize a resource node.

        Args:
            node_id (str): A unique identifier for this node instance.
            node_type (str): The type of the resource node (e.g., 'ore_vein_iron').
            tile_x (int): The X coordinate of the tile the node is anchored to.
            tile_y (int): The Y coordinate of the tile the node is anchored to.
            initial_surface (pygame.Surface): The pre-loaded image for the node.
            depleted_surface (pygame.Surface, optional): Surface for when node is depleted.
            saved_state (dict, optional): Saved state data to restore from.
        """
        self.node_id = node_id
        self.node_type = node_type
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.config_data = config.RESOURCE_NODE_TYPES.get(node_type)
        if not self.config_data:
            print(f"Error: ResourceNode type '{node_type}' not found in config.RESOURCE_NODE_TYPES. Node {node_id} may not function.")
            # Fallback defaults to prevent crashes, actual behavior will be limited
            self.config_data = {
                "display_name": "Unknown Node", "resource_type": "unknown", "yield_min": 0, 
                "yield_max": 0, "durability": 0, "cooldown": 9999, 
                "interaction_prompt": "Unknown Node", "depleted_sprite_suffix": ""
            }

        self.initial_surface = initial_surface
        self.depleted_surface = depleted_surface
        self.current_surface = self.initial_surface

        # World position and rect (based on tile_x, tile_y and assuming TILE_SIZE_MAP_DISPLAY for now)
        # Offset might be needed if sprite is not anchored at top-left of tile
        self.x = self.tile_x * config.TILE_SIZE_MAP_DISPLAY
        self.y = self.tile_y * config.TILE_SIZE_MAP_DISPLAY
        sprite_width = self.current_surface.get_width() if self.current_surface else config.TILE_SIZE_MAP_DISPLAY
        sprite_height = self.current_surface.get_height() if self.current_surface else config.TILE_SIZE_MAP_DISPLAY
        self.rect = pygame.Rect(self.x, self.y, sprite_width, sprite_height)

        # State variables - load from saved_state or use defaults from config
        if saved_state:
            self.current_durability = saved_state.get("current_durability", self.config_data["durability"])
            self.is_depleted = saved_state.get("is_depleted", False)
            self.last_harvest_time = saved_state.get("last_harvest_time", 0)
        else:
            self.current_durability = self.config_data["durability"]
            self.is_depleted = False
            self.last_harvest_time = 0
        
        if self.is_depleted and self.depleted_surface:
            self.current_surface = self.depleted_surface
        elif self.is_depleted and not self.depleted_surface:
             # If depleted but no depleted sprite, might keep initial or become invisible (current_surface=None)
             # For now, keep initial if no depleted sprite exists, or could set self.current_surface = None
             pass 

    def get_interaction_prompt(self):
        """Get the interaction prompt text."""
        if self.is_depleted:
            return f"{self.config_data['display_name']} (Depleted)"
        return self.config_data.get("interaction_prompt", "Interact")

    def can_harvest(self, current_game_time):
        """Check if the node can be harvested."""
        if self.is_depleted or self.current_durability <= 0:
            return False
        
        cooldown_duration = self.config_data.get("cooldown", 60)
        if current_game_time - self.last_harvest_time < cooldown_duration:
            # print(f"Node {self.node_id} on cooldown. Time left: {cooldown_duration - (current_game_time - self.last_harvest_time):.1f}s")
            return False
        return True

    def harvest(self, current_game_time):
        """Perform the harvest action on the node."""
        if not self.can_harvest(current_game_time):
            return None

        yield_amount = random.randint(self.config_data["yield_min"], self.config_data["yield_max"])
        self.current_durability -= 1
        self.last_harvest_time = current_game_time # pygame.time.get_ticks() / 1000.0 for seconds

        if self.current_durability <= 0:
            self.is_depleted = True
            if self.depleted_surface:
                self.current_surface = self.depleted_surface
            print(f"Node {self.node_id} ({self.config_data['display_name']}) depleted.")
        
        print(f"Harvested {yield_amount} {self.config_data['resource_type']} from {self.node_id}.")
        return {"resource_type": self.config_data["resource_type"], "amount": yield_amount}

    def render(self, screen, camera):
        """Render the resource node."""
        if not self.current_surface:
            return
        
        # The rect for collision/interaction is based on tile position.
        # For rendering, we might want to offset based on sprite size relative to tile size.
        # Assuming sprite is anchored at top-left of its tile for now.
        screen_pos_rect = camera.apply_rect(self.rect)
        screen.blit(self.current_surface, screen_pos_rect)

    def get_render_sort_key(self):
        """Return a sort key for rendering (e.g., Y-coordinate of bottom of sprite)."""
        return self.rect.bottom # Simple Y-sort based on top-left origin

    def to_dict(self):
        """Convert node state to a dictionary for saving."""
        return {
            "current_durability": self.current_durability,
            "is_depleted": self.is_depleted,
            "last_harvest_time": self.last_harvest_time
        }

    @classmethod
    def from_dict(cls, node_id, node_type, tile_x, tile_y, saved_state_dict, initial_surface, depleted_surface=None):
        """Create a ResourceNode instance from a saved state dictionary."""
        # Config data is fetched internally by __init__ based on node_type
        return cls(node_id, node_type, tile_x, tile_y, initial_surface, depleted_surface, saved_state=saved_state_dict) 