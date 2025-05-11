"""
Magic Survivor - Relic System

This module handles the relic system, including relic classes and effect application.
"""

import random
from src.data_handler import DataHandler

class Relic:
    """Class representing a relic"""
    
    def __init__(self, relic_id, relic_data):
        """Initialize a relic
        
        Args:
            relic_id (str): ID of the relic
            relic_data (dict): Relic data from DataHandler
        """
        self.id = relic_id
        self.data = relic_data
        
        # Basic properties
        self.name = relic_data.get("name", "Unknown Relic")
        self.description = relic_data.get("description", "")
        self.rarity = relic_data.get("rarity", "common")
        
        # Effects
        self.effects = relic_data.get("effects", {})
        
        # Active ability (if any)
        self.has_active = "active_ability" in relic_data
        if self.has_active:
            self.active_cooldown = relic_data.get("active_ability", {}).get("cooldown", 30.0)
            self.active_timer = 0
    
    def update(self, dt):
        """Update the relic (for active abilities)
        
        Args:
            dt (float): Time elapsed since last update in seconds
            
        Returns:
            bool: True if the active ability is ready, False otherwise
        """
        if not self.has_active:
            return False
        
        if self.active_timer > 0:
            self.active_timer -= dt
        
        return self.active_timer <= 0
    
    def use_active_ability(self):
        """Use the relic's active ability
        
        Returns:
            dict or None: Effect data if successful, None otherwise
        """
        if not self.has_active or self.active_timer > 0:
            return None
        
        # Reset the cooldown timer
        self.active_timer = self.active_cooldown
        
        # Return the effect data
        return self.data.get("active_ability", {}).get("effect", {})
    
    def get_stat_effects(self):
        """Get the stat effects of the relic
        
        Returns:
            dict: Dictionary of stat effects
        """
        return self.effects
    
    def get_display_info(self):
        """Get display information for the relic
        
        Returns:
            dict: Dictionary of display information
        """
        info = {
            "name": self.name,
            "description": self.description,
            "rarity": self.rarity,
            "effects": self.effects,
            "has_active": self.has_active
        }
        
        if self.has_active:
            info.update({
                "active_cooldown": self.active_cooldown,
                "active_ready": self.active_timer <= 0
            })
        
        return info


class RelicManager:
    """Manages relics for the player"""
    
    def __init__(self):
        """Initialize the relic manager"""
        self.relics = {}  # Dict of {relic_id: Relic}
        self.relic_data = DataHandler.load_relics()
    
    def load_player_relics(self, player_data):
        """Load relics from player data
        
        Args:
            player_data (dict): Player data from DayNightManager
        """
        self.relics = {}
        for relic_id in player_data.get("relics", []):
            if relic_id in self.relic_data:
                self.relics[relic_id] = Relic(relic_id, self.relic_data[relic_id])
    
    def update(self, dt):
        """Update all relics (for active abilities)
        
        Args:
            dt (float): Time elapsed since last update in seconds
            
        Returns:
            list: List of relic IDs with ready active abilities
        """
        ready_actives = []
        
        for relic_id, relic in self.relics.items():
            if relic.update(dt):
                ready_actives.append(relic_id)
        
        return ready_actives
    
    def use_active_ability(self, relic_id):
        """Use the active ability of a relic
        
        Args:
            relic_id (str): ID of the relic
            
        Returns:
            dict or None: Effect data if successful, None otherwise
        """
        if relic_id in self.relics:
            return self.relics[relic_id].use_active_ability()
        return None
    
    def get_combined_stat_effects(self):
        """Get the combined stat effects of all relics
        
        Returns:
            dict: Dictionary of combined stat effects
        """
        combined_effects = {}
        
        for relic in self.relics.values():
            effects = relic.get_stat_effects()
            for stat, value in effects.items():
                if stat in combined_effects:
                    combined_effects[stat] += value
                else:
                    combined_effects[stat] = value
        
        return combined_effects
    
    def apply_stat_effects(self, player):
        """Apply all relic stat effects to the player
        
        Args:
            player (Player): The player to apply effects to
        """
        # Reset derived stats
        player.derived_stats = {
            "movement_speed_percent": 0,
            "max_health_percent": 0,
            "spell_damage_percent": 0,
            "spell_cooldown_percent": 0,
            "xp_gain_percent": 0
        }
        
        # Apply combined effects
        combined_effects = self.get_combined_stat_effects()
        for stat, value in combined_effects.items():
            if stat in player.derived_stats:
                player.derived_stats[stat] += value
    
    def get_relic_choices(self, count=3, excluded_ids=None):
        """Get a list of random relics for the player to choose from
        
        Args:
            count (int): Number of choices to generate
            excluded_ids (list): List of relic IDs to exclude
            
        Returns:
            list: List of relic data dictionaries
        """
        if excluded_ids is None:
            excluded_ids = list(self.relics.keys())
        else:
            excluded_ids = list(excluded_ids) + list(self.relics.keys())
        
        # Filter available relics
        available_relics = {relic_id: data for relic_id, data in self.relic_data.items() 
                            if relic_id not in excluded_ids}
        
        if not available_relics:
            return []
        
        # Weight by rarity
        rarity_weights = {
            "common": 60,
            "uncommon": 30,
            "rare": 10,
            "epic": 5,
            "legendary": 1
        }
        
        weighted_choices = []
        for relic_id, data in available_relics.items():
            rarity = data.get("rarity", "common")
            weight = rarity_weights.get(rarity, 1)
            weighted_choices.extend([relic_id] * weight)
        
        # Select random relics
        if len(weighted_choices) <= count:
            selected_ids = weighted_choices
        else:
            selected_ids = random.sample(weighted_choices, count)
        
        # Remove duplicates (could happen due to weighting)
        selected_ids = list(set(selected_ids))
        
        # Get the data for each selected relic
        return [self.relic_data[relic_id] for relic_id in selected_ids]
    
    def add_relic(self, relic_id):
        """Add a relic to the player's collection
        
        Args:
            relic_id (str): ID of the relic to add
            
        Returns:
            bool: True if the relic was added, False otherwise
        """
        if relic_id in self.relic_data and relic_id not in self.relics:
            self.relics[relic_id] = Relic(relic_id, self.relic_data[relic_id])
            return True
        return False
    
    def get_relic_info(self, relic_id):
        """Get information about a relic
        
        Args:
            relic_id (str): ID of the relic
            
        Returns:
            dict or None: Relic display information, or None if relic not found
        """
        if relic_id in self.relics:
            return self.relics[relic_id].get_display_info()
        return None
    
    def get_all_relic_info(self):
        """Get information about all relics
        
        Returns:
            dict: Dictionary of {relic_id: relic_info}
        """
        return {relic_id: relic.get_display_info() for relic_id, relic in self.relics.items()} 