import pygame
from src import config

class PointOfInterest:
    """Represents a Point of Interest on the world map."""

    def __init__(self, poi_id, poi_type, tile_x, tile_y, initial_surface, minimap_icon_surface, definition, game_manager, saved_state=None):
        self.poi_id = poi_id
        self.poi_type = poi_type
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.game_manager = game_manager # For accessing DataHandler (loot tables) and Player

        self.definition = definition # From config.POI_DEFINITIONS[poi_type]
        
        self.current_surface = initial_surface
        self.minimap_icon_surface = minimap_icon_surface

        # Attempt to get dimensions from surface, fallback to config or default
        if self.current_surface:
            sprite_width = self.current_surface.get_width()
            sprite_height = self.current_surface.get_height()
        elif config.POI_SPRITE_DIMENSIONS.get(self.poi_type):
            sprite_width, sprite_height = config.POI_SPRITE_DIMENSIONS[self.poi_type]
        else:
            sprite_width, sprite_height = (config.TILE_SIZE_MAP_DISPLAY, config.TILE_SIZE_MAP_DISPLAY) # Default size

        # Position in pixels (center of the tile for now, can be offset by definition)
        self.world_x = (tile_x * config.TILE_SIZE_MAP_DISPLAY) + (config.TILE_SIZE_MAP_DISPLAY / 2)
        self.world_y = (tile_y * config.TILE_SIZE_MAP_DISPLAY) + (config.TILE_SIZE_MAP_DISPLAY / 2)
        
        # Offset from definition, if any (e.g. for larger sprites to sit correctly on a tile)
        self.offset_x = self.definition.get("offset_x", 0)
        self.offset_y = self.definition.get("offset_y", -(sprite_height - config.TILE_SIZE_MAP_DISPLAY) / 2 if sprite_height > config.TILE_SIZE_MAP_DISPLAY else 0)


        self.rect = pygame.Rect(
            self.world_x - sprite_width / 2 + self.offset_x,
            self.world_y - sprite_height / 2 + self.offset_y,
            sprite_width,
            sprite_height
        )

        # State variables
        self.is_looted = False
        self.is_triggered = False # For one-time non-loot events like encounters
        self.cooldown_timer = 0.0 # Seconds
        self.current_sprite_key = self.definition.get("base_sprite_key", self.poi_type)

        if saved_state:
            self.from_dict(saved_state)
        
        self._update_surface_if_needed() # In case saved_state changed the sprite key

    def _update_surface_if_needed(self):
        """Updates self.current_surface if self.current_sprite_key indicates a different sprite."""
        # This assumes poi_surfaces in DataHandler might store multiple sprites per POI type eventually,
        # e.g., {"shrine": surface1, "shrine_looted": surface2}
        # For now, POI_SPRITE_PATHS in config points to one sprite per key.
        new_surface = self.game_manager.data_handler.poi_surfaces.get(self.current_sprite_key)
        if new_surface and new_surface != self.current_surface:
            self.current_surface = new_surface
            # Update rect if dimensions changed, though ideally sprites for different states are same size
            # For simplicity, we'll assume they are for now or that definition handles offsets.

    def render(self, surface, camera):
        """Render the POI on the given surface, adjusted by the camera."""
        if self.current_surface:
            surface.blit(self.current_surface, camera.apply_rect(self.rect))
        else: # Fallback rendering if no surface
            fallback_rect = camera.apply_rect(self.rect)
            pygame.draw.rect(surface, config.MISSING_POI_SPRITE_COLOR, fallback_rect)
            pygame.draw.rect(surface, config.WHITE, fallback_rect, 1)


    def get_render_sort_key(self):
        """Returns the y-coordinate of the bottom of the sprite, for depth sorting."""
        return self.rect.bottom

    def get_interaction_prompt(self):
        """Returns the interaction prompt text based on current state."""
        if self.cooldown_timer > 0:
            return f"{self.definition.get('display_name', self.poi_type)} (Cooldown: {int(self.cooldown_timer)}s)"
        if self.definition.get("one_time_interaction", False) and (self.is_looted or self.is_triggered):
            return f"{self.definition.get('display_name', self.poi_type)} (Already Investigated)"
        return self.definition.get("interaction_prompt", "Press E to interact")

    def interact(self, player, current_time_seconds):
        """Handles player interaction with the POI.
        Returns a dictionary describing the result of the interaction or None.
        """
        if self.cooldown_timer > 0:
            print(f"POI {self.poi_id} is on cooldown.")
            return None
        
        if self.definition.get("one_time_interaction", False) and (self.is_looted or self.is_triggered):
            print(f"POI {self.poi_id} is a one-time interaction and has already been used.")
            return None

        interaction_results = {"poi_id": self.poi_id, "type": "poi_interaction", "details": {}}
        action_taken = False

        # Grant XP
        xp_reward = self.definition.get("xp_reward", 0)
        if xp_reward > 0:
            player.gain_xp(xp_reward)
            interaction_results["details"]["xp_gained"] = xp_reward
            print(f"Player gained {xp_reward} XP from {self.poi_id}.")
            action_taken = True

        # Grant Loot
        loot_table_id = self.definition.get("loot_table_id")
        if loot_table_id:
            # TODO: Implement loot table processing in DataHandler or a new LootManager
            # For now, placeholder:
            print(f"TODO: Grant loot from table '{loot_table_id}' for POI {self.poi_id}.")
            # Example: self.game_manager.loot_manager.grant_loot(player, loot_table_id)
            # For now, let's simulate finding some gold.
            found_gold = self.game_manager.data_handler.get_loot_from_table(loot_table_id, "resources", "gold")
            if found_gold: # Assuming get_loot_from_table returns actual amount
                 player.add_resource("gold", found_gold)
                 interaction_results["details"]["resources_gained"] = {"gold": found_gold}

            self.is_looted = True # Mark as looted if it provides loot
            action_taken = True
            
            looted_sprite_key = self.definition.get("looted_sprite_key")
            if looted_sprite_key:
                self.current_sprite_key = looted_sprite_key
                self._update_surface_if_needed()


        # Trigger Encounter
        encounter_id = self.definition.get("linked_encounter_id")
        if encounter_id:
            print(f"TODO: Trigger encounter '{encounter_id}' for POI {self.poi_id}.")
            interaction_results["details"]["trigger_encounter"] = encounter_id
            # WorldMapState will need to handle this by perhaps pushing a combat state
            self.is_triggered = True # Mark as triggered if it starts an encounter
            action_taken = True

        # Set cooldown if applicable (even for one-time, to prevent immediate re-prompt)
        cooldown_duration = 0
        if self.definition.get("one_time_interaction", False):
            cooldown_duration = float('inf') # Effectively infinite for one-time
        elif "entry_cooldown" in self.definition: # For re-enterable (e.g. monster den)
            cooldown_duration = self.definition["entry_cooldown"]
        elif "explore_cooldown" in self.definition: # For re-lootable (e.g. ruin)
             cooldown_duration = self.definition["explore_cooldown"]
        
        if cooldown_duration > 0 :
            self.cooldown_timer = cooldown_duration


        if action_taken:
            self.game_manager.mark_world_map_pois_dirty()
            return interaction_results
        else:
            # If no action was taken but cooldown was set (e.g. one-time already used but setting inf cooldown)
            if cooldown_duration > 0:
                 self.game_manager.mark_world_map_pois_dirty()
            print(f"No specific action defined for POI type {self.poi_type} or already used.")
            return None


    def update(self, dt, player, game_manager):
        """Update cooldown timers or other time-based logic."""
        # player and game_manager arguments added to match call signature in WorldMapState
        # but are not used in the current POI update logic. Can be used for future features.
        if self.cooldown_timer > 0 and self.cooldown_timer != float('inf'):
            self.cooldown_timer -= dt
            if self.cooldown_timer < 0:
                self.cooldown_timer = 0
                print(f"POI {self.poi_id} cooldown finished.")
                # Potentially reset state if it's a recurring POI, e.g. reset is_looted for a ruin
                if not self.definition.get("one_time_interaction", False) and \
                   ("explore_cooldown" in self.definition or "entry_cooldown" in self.definition): # Check either cooldown type
                    self.is_looted = False 
                    self.is_triggered = False # Also reset triggered state for recurring encounters
                    self.current_sprite_key = self.definition.get("base_sprite_key", self.poi_type)
                    self._update_surface_if_needed()
                    self.game_manager.mark_world_map_pois_dirty()


    def to_dict(self):
        """Return a dictionary representing the POI's current savable state."""
        return {
            "poi_id": self.poi_id, # Though ID might be implicit from list index or key in world_map.json
            "type": self.poi_type, # Redundant if world_map.json stores by type, but good for verification
            "tile_x": self.tile_x, # Redundant but good for verification
            "tile_y": self.tile_y, # Redundant
            "is_looted": self.is_looted,
            "is_triggered": self.is_triggered,
            "cooldown_timer": self.cooldown_timer,
            "current_sprite_key": self.current_sprite_key # If sprite can change based on state
        }

    def from_dict(self, data):
        """Restore the POI's state from a dictionary."""
        self.is_looted = data.get("is_looted", False)
        self.is_triggered = data.get("is_triggered", False)
        self.cooldown_timer = data.get("cooldown_timer", 0.0)
        self.current_sprite_key = data.get("current_sprite_key", self.definition.get("base_sprite_key", self.poi_type))
        # Initial surface update will be handled after full init if sprite key changed

        self._update_surface_if_needed() # In case saved_state changed the sprite key

        # Update rect if dimensions changed, though ideally sprites for different states are same size
        # For simplicity, we'll assume they are for now or that definition handles offsets.
        if self.current_surface:
            sprite_width = self.current_surface.get_width()
            sprite_height = self.current_surface.get_height()
        elif config.POI_SPRITE_DIMENSIONS.get(self.poi_type):
            sprite_width, sprite_height = config.POI_SPRITE_DIMENSIONS[self.poi_type]
        else:
            sprite_width, sprite_height = (config.TILE_SIZE_MAP_DISPLAY, config.TILE_SIZE_MAP_DISPLAY) # Default size

        # Position in pixels (center of the tile for now, can be offset by definition)
        self.world_x = (self.tile_x * config.TILE_SIZE_MAP_DISPLAY) + (config.TILE_SIZE_MAP_DISPLAY / 2)
        self.world_y = (self.tile_y * config.TILE_SIZE_MAP_DISPLAY) + (config.TILE_SIZE_MAP_DISPLAY / 2)
        
        # Offset from definition, if any (e.g. for larger sprites to sit correctly on a tile)
        self.offset_x = self.definition.get("offset_x", 0)
        self.offset_y = self.definition.get("offset_y", -(sprite_height - config.TILE_SIZE_MAP_DISPLAY) / 2 if sprite_height > config.TILE_SIZE_MAP_DISPLAY else 0)


        self.rect = pygame.Rect(
            self.world_x - sprite_width / 2 + self.offset_x,
            self.world_y - sprite_height / 2 + self.offset_y,
            sprite_width,
            sprite_height
        ) 