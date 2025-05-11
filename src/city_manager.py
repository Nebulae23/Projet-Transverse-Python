"""
Magic Survivor - City Manager

This module handles the city management system, including buildings and resource production.
"""

from src.data_handler import DataHandler

class Building:
    """Class representing a building in the city"""
    
    def __init__(self, building_id, building_data, level=1):
        """Initialize a building
        
        Args:
            building_id (str): ID of the building
            building_data (dict): Building data from DataHandler
            level (int): Initial level of the building (default: 1)
        """
        self.id = building_id
        self.data = building_data
        self.level = level
        
        # Basic properties
        self.name = building_data.get("name", "Unknown Building")
        self.description = building_data.get("description", "")
        self.category = building_data.get("category", "production")
        
        # Production and bonuses
        self.production = self._get_level_data("production", {})
        self.bonuses = self._get_level_data("bonuses", {})
        
        # Defenses (for defense buildings)
        self.defense_stats = self._get_level_data("defense_stats", {})
    
    def _get_level_data(self, key, default_value):
        """Get data for the current level
        
        Args:
            key (str): Key to look up in the level data
            default_value: Default value if not found
            
        Returns:
            any: The value from the level data, or default_value
        """
        level_str = str(self.level)
        if level_str in self.data.get("levels", {}):
            return self.data["levels"][level_str].get(key, default_value)
        return default_value
    
    def get_upgrade_cost(self):
        """Get the cost to upgrade this building to the next level
        
        Returns:
            dict or None: Dictionary of {resource: amount} needed, or None if max level
        """
        next_level = self.level + 1
        next_level_str = str(next_level)
        
        if next_level_str in self.data.get("levels", {}):
            return self.data["levels"][next_level_str].get("cost", {})
        
        return None  # Can't upgrade further
    
    def upgrade(self):
        """Upgrade the building to the next level
        
        Returns:
            bool: True if successful, False if at max level
        """
        if self.get_upgrade_cost() is None:
            return False
        
        self.level += 1
        
        # Update properties
        self.production = self._get_level_data("production", {})
        self.bonuses = self._get_level_data("bonuses", {})
        self.defense_stats = self._get_level_data("defense_stats", {})
        
        return True
    
    def get_production(self):
        """Get the current production of this building
        
        Returns:
            dict: Dictionary of {resource: amount_per_minute}
        """
        return self.production
    
    def get_bonuses(self):
        """Get the current bonuses from this building
        
        Returns:
            dict: Dictionary of {bonus_type: value}
        """
        return self.bonuses
    
    def get_defense_stats(self):
        """Get the defense stats for this building
        
        Returns:
            dict: Dictionary of defense stats (e.g. damage, range, etc.)
        """
        return self.defense_stats
    
    def get_display_info(self):
        """Get display information for the building
        
        Returns:
            dict: Dictionary of display information
        """
        info = {
            "name": self.name,
            "description": self.description,
            "level": self.level,
            "category": self.category,
            "production": self.production,
            "bonuses": self.bonuses,
            "upgrade_cost": self.get_upgrade_cost()
        }
        
        # Add defense stats if this is a defense building
        if self.category == "defense":
            info["defense_stats"] = self.defense_stats
        
        return info


class CityManager:
    """Manages the city, including buildings and resource production"""
    
    # Building categories
    CATEGORY_PRODUCTION = "production"  # Resource production buildings
    CATEGORY_DEFENSE = "defense"        # Defense buildings
    CATEGORY_UTILITY = "utility"        # Utility buildings (bonuses, etc.)
    CATEGORY_SPECIAL = "special"        # Special buildings (plot advancement, etc.)
    
    def __init__(self):
        """Initialize the city manager"""
        self.buildings = {}  # Dict of {building_id: Building}
        self.building_data = DataHandler.load_buildings()
        
        # Resource production and accumulation
        self.production_rates = {}  # Resources per minute
        self.accumulated_resources = {}  # Fractional resources accumulated since last update
        
        # Defense stats
        self.total_defense_power = 0
        self.defense_buildings = []  # List of defense building IDs
        
        # Production time modifiers
        self.production_time_modifier = 1.0  # Multiplier for production speed
    
    def load_player_buildings(self, player_data):
        """Load buildings from player data
        
        Args:
            player_data (dict): Player data
        """
        self.buildings = {}
        
        # Load existing buildings
        for building_id, level in player_data.get("city_buildings", {}).items():
            if building_id in self.building_data:
                self.buildings[building_id] = Building(building_id, self.building_data[building_id], level)
        
        # Update stats
        self._update_production_rates()
        self._update_defense_stats()
    
    def _update_production_rates(self):
        """Update the production rates based on current buildings"""
        self.production_rates = {}
        
        # Apply base production rates
        for building in self.buildings.values():
            production = building.get_production()
            for resource, amount in production.items():
                if resource in self.production_rates:
                    self.production_rates[resource] += amount
                else:
                    self.production_rates[resource] = amount
        
        # Apply production bonuses
        total_production_bonus = 0
        for building in self.buildings.values():
            bonuses = building.get_bonuses()
            if "production_speed_percent" in bonuses:
                total_production_bonus += bonuses["production_speed_percent"]
        
        # Apply the production bonus
        if total_production_bonus != 0:
            self.production_time_modifier = 1.0 + (total_production_bonus / 100.0)
            for resource in self.production_rates:
                self.production_rates[resource] *= self.production_time_modifier
    
    def _update_defense_stats(self):
        """Update defense stats based on current buildings"""
        self.total_defense_power = 0
        self.defense_buildings = []
        
        # Get all defense buildings
        for building_id, building in self.buildings.items():
            if building.category == self.CATEGORY_DEFENSE:
                self.defense_buildings.append(building_id)
                
                # Add defense power
                defense_stats = building.get_defense_stats()
                if "power" in defense_stats:
                    self.total_defense_power += defense_stats["power"]
    
    def update(self, dt, resources):
        """Update resource production
        
        Args:
            dt (float): Time elapsed since last update in seconds
            resources (dict): Current resources
            
        Returns:
            dict: Updated resources
        """
        # Initialize accumulated resources for new resource types
        for resource in self.production_rates:
            if resource not in self.accumulated_resources:
                self.accumulated_resources[resource] = 0
        
        # Update accumulated resources (convert from per-minute to per-second)
        for resource, rate in self.production_rates.items():
            amount_per_second = rate / 60
            self.accumulated_resources[resource] += amount_per_second * dt
        
        # Add whole number of resources to the player's total
        updated_resources = resources.copy()
        for resource, accumulated in self.accumulated_resources.items():
            whole_amount = int(accumulated)
            if whole_amount > 0:
                self.accumulated_resources[resource] -= whole_amount
                if resource in updated_resources:
                    updated_resources[resource] += whole_amount
                else:
                    updated_resources[resource] = whole_amount
        
        return updated_resources
    
    def can_build(self, building_id, resources):
        """Check if a building can be built
        
        Args:
            building_id (str): ID of the building to build
            resources (dict): Current resources
            
        Returns:
            bool: True if the building can be built, False otherwise
        """
        # Check if the building exists in data
        if building_id not in self.building_data:
            return False
        
        # Check if already built
        if building_id in self.buildings:
            return False
        
        # Check if enough resources
        base_cost = self.building_data[building_id].get("base_cost", {})
        for resource, amount in base_cost.items():
            if resources.get(resource, 0) < amount:
                return False
        
        # Check if prerequisites are met
        prerequisites = self.building_data[building_id].get("prerequisites", {})
        
        # Check required buildings
        if "required_buildings" in prerequisites:
            for req_building in prerequisites["required_buildings"]:
                if req_building not in self.buildings:
                    return False
        
        # Check required levels
        if "required_levels" in prerequisites:
            for req_building, req_level in prerequisites["required_levels"].items():
                if req_building not in self.buildings or self.buildings[req_building].level < req_level:
                    return False
        
        return True
    
    def can_upgrade(self, building_id, resources):
        """Check if a building can be upgraded
        
        Args:
            building_id (str): ID of the building to upgrade
            resources (dict): Current resources
            
        Returns:
            bool: True if the building can be upgraded, False otherwise
        """
        # Check if the building is built
        if building_id not in self.buildings:
            return False
        
        # Get upgrade cost
        upgrade_cost = self.buildings[building_id].get_upgrade_cost()
        if upgrade_cost is None:
            return False  # Max level
        
        # Check if enough resources
        for resource, amount in upgrade_cost.items():
            if resources.get(resource, 0) < amount:
                return False
        
        # Check if upgrade prerequisites are met
        building_data = self.building_data[building_id]
        next_level = self.buildings[building_id].level + 1
        level_str = str(next_level)
        
        if level_str in building_data.get("levels", {}):
            prerequisites = building_data["levels"][level_str].get("prerequisites", {})
            
            # Check required buildings
            if "required_buildings" in prerequisites:
                for req_building in prerequisites["required_buildings"]:
                    if req_building not in self.buildings:
                        return False
            
            # Check required levels
            if "required_levels" in prerequisites:
                for req_building, req_level in prerequisites["required_levels"].items():
                    if req_building not in self.buildings or self.buildings[req_building].level < req_level:
                        return False
        
        return True
    
    def build(self, building_id, resources):
        """Build a new building
        
        Args:
            building_id (str): ID of the building to build
            resources (dict): Current resources
            
        Returns:
            tuple: (success, updated_resources, resource_changes)
        """
        if not self.can_build(building_id, resources):
            return False, resources, {}
        
        # Calculate resource changes
        resource_changes = {}
        base_cost = self.building_data[building_id].get("base_cost", {})
        for resource, amount in base_cost.items():
            resource_changes[resource] = -amount
        
        # Update resources
        updated_resources = resources.copy()
        for resource, change in resource_changes.items():
            if resource in updated_resources:
                updated_resources[resource] += change
            else:
                updated_resources[resource] = change
        
        # Create the building
        self.buildings[building_id] = Building(building_id, self.building_data[building_id])
        
        # Update stats
        self._update_production_rates()
        self._update_defense_stats()
        
        return True, updated_resources, resource_changes
    
    def upgrade(self, building_id, resources):
        """Upgrade a building
        
        Args:
            building_id (str): ID of the building to upgrade
            resources (dict): Current resources
            
        Returns:
            tuple: (success, updated_resources, resource_changes)
        """
        if not self.can_upgrade(building_id, resources):
            return False, resources, {}
        
        # Get upgrade cost
        upgrade_cost = self.buildings[building_id].get_upgrade_cost()
        
        # Calculate resource changes
        resource_changes = {}
        for resource, amount in upgrade_cost.items():
            resource_changes[resource] = -amount
        
        # Update resources
        updated_resources = resources.copy()
        for resource, change in resource_changes.items():
            if resource in updated_resources:
                updated_resources[resource] += change
            else:
                updated_resources[resource] = change
        
        # Upgrade the building
        self.buildings[building_id].upgrade()
        
        # Update stats
        self._update_production_rates()
        self._update_defense_stats()
        
        return True, updated_resources, resource_changes
    
    def get_available_buildings(self):
        """Get a list of buildings that can be built
        
        Returns:
            list: List of building IDs
        """
        available = []
        
        for building_id in self.building_data:
            if building_id not in self.buildings:
                # Check prerequisites
                prerequisites = self.building_data[building_id].get("prerequisites", {})
                meets_prereqs = True
                
                # Check required buildings
                if "required_buildings" in prerequisites:
                    for req_building in prerequisites["required_buildings"]:
                        if req_building not in self.buildings:
                            meets_prereqs = False
                            break
                
                # Check required levels
                if meets_prereqs and "required_levels" in prerequisites:
                    for req_building, req_level in prerequisites["required_levels"].items():
                        if req_building not in self.buildings or self.buildings[req_building].level < req_level:
                            meets_prereqs = False
                            break
                
                if meets_prereqs:
                    available.append(building_id)
        
        return available
    
    def get_buildings_by_category(self, category):
        """Get all buildings of a specific category
        
        Args:
            category (str): Building category
            
        Returns:
            dict: Dictionary of {building_id: Building} for the category
        """
        return {bid: building for bid, building in self.buildings.items() 
                if building.category == category}
    
    def get_all_building_info(self):
        """Get information about all buildings
        
        Returns:
            dict: Dictionary of {building_id: building_info}
        """
        built = {building_id: building.get_display_info() 
                for building_id, building in self.buildings.items()}
        
        available = {}
        for building_id in self.get_available_buildings():
            data = self.building_data[building_id]
            available[building_id] = {
                "name": data.get("name", "Unknown Building"),
                "description": data.get("description", ""),
                "category": data.get("category", "production"),
                "base_cost": data.get("base_cost", {})
            }
        
        return {"built": built, "available": available}
    
    def get_combined_bonuses(self):
        """Get the combined bonuses from all buildings
        
        Returns:
            dict: Dictionary of {bonus_type: value}
        """
        combined_bonuses = {}
        
        for building in self.buildings.values():
            bonuses = building.get_bonuses()
            for bonus_type, value in bonuses.items():
                if bonus_type in combined_bonuses:
                    combined_bonuses[bonus_type] += value
                else:
                    combined_bonuses[bonus_type] = value
        
        return combined_bonuses
    
    def get_production_info(self):
        """Get information about current production
        
        Returns:
            dict: Dictionary with production information
        """
        return {
            "rates": self.production_rates,
            "accumulated": self.accumulated_resources,
            "time_modifier": self.production_time_modifier
        }
    
    def get_defense_info(self):
        """Get information about city defenses
        
        Returns:
            dict: Dictionary with defense information
        """
        defense_buildings_info = []
        
        for building_id in self.defense_buildings:
            building = self.buildings[building_id]
            defense_buildings_info.append({
                "id": building_id,
                "name": building.name,
                "level": building.level,
                "stats": building.get_defense_stats()
            })
        
        return {
            "total_power": self.total_defense_power,
            "buildings": defense_buildings_info
        }
    
    def handle_night_defense(self, enemy_power):
        """Handle night defense calculations
        
        Args:
            enemy_power (float): Total enemy power attacking the city
            
        Returns:
            tuple: (city_survived, damage_to_player_percent, damage_to_enemies_percent)
        """
        # Compare defense power to enemy power
        power_ratio = self.total_defense_power / max(1, enemy_power)
        
        # Determine if city survived
        city_survived = power_ratio >= 0.75
        
        # Calculate damage percentages (how much damage player/enemies avoided)
        damage_to_player_percent = max(0, min(100, (1 - power_ratio) * 100))
        damage_to_enemies_percent = max(0, min(100, power_ratio * 100))
        
        return (city_survived, damage_to_player_percent, damage_to_enemies_percent) 