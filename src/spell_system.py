"""
Magic Survivor - Spell System

This module handles the spell system, including spell classes and spell management.
"""

import pygame
import math
import random
import json
from src import config
from src.data_handler import DataHandler
from src.projectile_system import Projectile
from src.game_state_base import GameState
from src.ui_manager import UIManager, Button, TextBox

class Spell:
    """Class representing a spell"""
    
    def __init__(self, spell_id, spell_data):
        """Initialize a spell
        
        Args:
            spell_id (str): ID of the spell
            spell_data (dict): Spell data from DataHandler
        """
        self.id = spell_id
        self.data = spell_data
        
        # Basic properties
        self.name = spell_data.get("name", "Unknown Spell")
        self.description = spell_data.get("description", "")
        self.level = 1
        self.is_automatic = spell_data.get("automatic", True)
        
        # Combat properties
        self.damage = spell_data.get("damage", 10)
        self.cooldown = spell_data.get("cooldown", 1.0)
        self.timer = 0
        
        # Targeting
        self.max_range = spell_data.get("max_range", 0)  # 0 means unlimited
        
        # Tracking upgrades and divergence
        self.has_diverged = False
        self.divergence_option = None  # "option_1" or "option_2" after divergence
        
        # Additional properties based on spell type
        self.radius = spell_data.get("radius", 0)  # For area spells
        self.projectile_count = spell_data.get("projectile_count", 1)  # For multi-projectile spells
        self.projectile_speed = spell_data.get("projectile_speed", 8)
        self.tick_rate = spell_data.get("tick_rate", 0.2)  # For damage-over-time spells
        self.tick_timer = 0
    
    def update(self, dt):
        """Update the spell
        
        Args:
            dt (float): Time elapsed since last update in seconds
            
        Returns:
            bool: True if the spell is ready to cast (for automatic spells), False otherwise
        """
        if self.timer > 0:
            self.timer -= dt
        
        # For spells that tick (like auras), update the tick timer
        if "tick_rate" in self.data:
            self.tick_timer -= dt
            if self.tick_timer <= 0:
                self.tick_timer = self.tick_rate
                return True
        
        return self.timer <= 0
    
    def cast(self, x, y, target_pos=None):
        """Cast the spell
        
        Args:
            x (float): Caster's x position
            y (float): Caster's y position
            target_pos (tuple, optional): Target position (x, y). Defaults to None.
            
        Returns:
            list: List of projectiles or other effects created by the spell
        """
        # Reset the cooldown timer
        self.timer = self.cooldown
        results = []
        
        # Different casting behavior based on spell type
        spell_type = self.data.get("type", "projectile")
        
        if spell_type == "projectile":
            results.extend(self._cast_projectile_spell(x, y, target_pos))
        elif spell_type == "aura":
            results.extend(self._cast_aura_spell(x, y))
        # Add more spell types here
        
        return results
    
    def _cast_projectile_spell(self, x, y, target_pos):
        """Cast a projectile-type spell
        
        Args:
            x (float): Caster's x position
            y (float): Caster's y position
            target_pos (tuple): Target position (x, y)
            
        Returns:
            list: List of projectiles created by the spell
        """
        projectiles = []
        
        # If no target, use a default direction
        if target_pos is None:
            direction = random.uniform(0, 2 * math.pi)
            target_pos = (x + math.cos(direction), y + math.sin(direction))
        
        # Calculate direction vector
        dx = target_pos[0] - x
        dy = target_pos[1] - y
        
        # Normalize
        magnitude = math.sqrt(dx * dx + dy * dy)
        if magnitude > 0:
            dx /= magnitude
            dy /= magnitude
        
        # Handle multi-projectile spells (e.g., after divergence)
        if self.projectile_count > 1:
            angle_spread = self.data.get("angle_spread", 30)
            base_angle = math.atan2(dy, dx)
            
            for i in range(self.projectile_count):
                # Calculate angle offset to spread projectiles
                if self.projectile_count > 1:
                    offset = (i / (self.projectile_count - 1) - 0.5) * math.radians(angle_spread)
                else:
                    offset = 0
                
                # Calculate new direction
                new_angle = base_angle + offset
                new_dx = math.cos(new_angle)
                new_dy = math.sin(new_angle)
                
                # Create projectile
                projectile = Projectile(x, y, new_dx, new_dy, self.damage, 
                                       speed=self.projectile_speed, 
                                       color=self.data.get("color", config.BLUE))
                projectiles.append(projectile)
        else:
            # Single projectile
            projectile = Projectile(x, y, dx, dy, self.damage, 
                                   speed=self.projectile_speed, 
                                   color=self.data.get("color", config.BLUE))
            projectiles.append(projectile)
        
        return projectiles
    
    def _cast_aura_spell(self, x, y):
        """Cast an aura-type spell
        
        Args:
            x (float): Caster's x position
            y (float): Caster's y position
            
        Returns:
            list: List of effects created by the spell
        """
        # For auras, we would typically handle the damage/effects directly
        # in the NightPhaseState update, using the spell's radius
        return []
    
    def upgrade(self):
        """Upgrade the spell to the next level
        
        Returns:
            bool: True if the upgrade was successful, False otherwise
        """
        next_level = self.level + 1
        level_key = f"level_{next_level}"
        
        # Check if divergence is available
        if self.data.get("upgrades", {}).get(level_key, {}).get("divergence", False):
            # Can't upgrade further without choosing a divergence path
            return False
        
        # Check if next level exists in the data
        if level_key in self.data.get("upgrades", {}):
            # Apply the upgrades
            upgrade_data = self.data["upgrades"][level_key]
            for key, value in upgrade_data.items():
                if key != "divergence" and hasattr(self, key):
                    setattr(self, key, value)
            
            self.level = next_level
            return True
        
        return False
    
    def can_diverge(self):
        """Check if the spell can diverge
        
        Returns:
            bool: True if the spell can diverge, False otherwise
        """
        level_key = f"level_{self.level}"
        return (not self.has_diverged and 
                level_key in self.data.get("upgrades", {}) and 
                self.data["upgrades"][level_key].get("divergence", False))
    
    def diverge(self, option):
        """Diverge the spell
        
        Args:
            option (str): Divergence option ("option_1" or "option_2")
            
        Returns:
            bool: True if the divergence was successful, False otherwise
        """
        if not self.can_diverge() or option not in ["option_1", "option_2"]:
            return False
        
        # Apply the divergence
        if option in self.data.get("divergence_options", {}):
            divergence_data = self.data["divergence_options"][option]
            
            # Update with the diverged values
            for key, value in divergence_data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            
            # Mark as diverged
            self.has_diverged = True
            self.divergence_option = option
            
            # Update the name and description
            if "name" in divergence_data:
                self.name = divergence_data["name"]
            if "description" in divergence_data:
                self.description = divergence_data["description"]
            
            return True
        
        return False
    
    def get_display_info(self):
        """Get display information for the spell
        
        Returns:
            dict: Dictionary of display information
        """
        return {
            "name": self.name,
            "description": self.description,
            "level": self.level,
            "damage": self.damage,
            "cooldown": self.cooldown,
            "has_diverged": self.has_diverged,
            "can_diverge": self.can_diverge()
        }


class SpellManager:
    """Manages spells for the player"""
    
    def __init__(self):
        """Initialize the spell manager"""
        self.spells = {}  # Dict of {spell_id: Spell}
        self.spell_data = DataHandler.load_spells()
        
        # Tracking active spell effects
        self.active_projectiles = []
        self.active_auras = []
    
    def load_player_spells(self, player_data):
        """Load spells from player data
        
        Args:
            player_data (dict): Player data from DayNightManager
        """
        self.spells = {}
        for spell_id in player_data.get("spells", []):
            if spell_id in self.spell_data:
                self.spells[spell_id] = Spell(spell_id, self.spell_data[spell_id])
    
    def update(self, dt, player_x, player_y, enemies):
        """Update spells and cast automatic spells
        
        Args:
            dt (float): Time elapsed since last update in seconds
            player_x (float): Player's x position
            player_y (float): Player's y position
            enemies (pygame.sprite.Group): Group of enemies
            
        Returns:
            list: List of new projectiles created by automatic spells
        """
        new_projectiles = []
        
        # Update all spells
        for spell_id, spell in self.spells.items():
            if spell.is_automatic and spell.update(dt):
                # Find a target for the spell (closest enemy)
                target_pos = self._find_target(player_x, player_y, enemies)
                
                # Cast the spell
                cast_results = spell.cast(player_x, player_y, target_pos)
                new_projectiles.extend(cast_results)
        
        return new_projectiles
    
    def cast_spell(self, spell_id, player_x, player_y, target_pos):
        """Cast a specific spell
        
        Args:
            spell_id (str): ID of the spell to cast
            player_x (float): Player's x position
            player_y (float): Player's y position
            target_pos (tuple): Target position (x, y)
            
        Returns:
            list: List of projectiles or other effects created by the spell
        """
        if spell_id in self.spells and not self.spells[spell_id].is_automatic:
            if self.spells[spell_id].update(0):  # Check if ready
                return self.spells[spell_id].cast(player_x, player_y, target_pos)
        
        return []
    
    def _find_target(self, player_x, player_y, enemies):
        """Find a target for a spell (closest enemy)
        
        Args:
            player_x (float): Player's x position
            player_y (float): Player's y position
            enemies (pygame.sprite.Group): Group of enemies
            
        Returns:
            tuple or None: Target position (x, y), or None if no valid target
        """
        closest_enemy = None
        closest_distance = float('inf')
        
        for enemy in enemies:
            dx = enemy.rect.centerx - player_x
            dy = enemy.rect.centery - player_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < closest_distance:
                closest_distance = distance
                closest_enemy = enemy
        
        if closest_enemy:
            return (closest_enemy.rect.centerx, closest_enemy.rect.centery)
        else:
            # Random direction if no enemies
            angle = random.uniform(0, 2 * math.pi)
            return (player_x + math.cos(angle) * 100, player_y + math.sin(angle) * 100)
    
    def upgrade_spell(self, spell_id):
        """Upgrade a spell
        
        Args:
            spell_id (str): ID of the spell to upgrade
            
        Returns:
            bool: True if the upgrade was successful, False otherwise
        """
        if spell_id in self.spells:
            return self.spells[spell_id].upgrade()
        return False
    
    def diverge_spell(self, spell_id, option):
        """Diverge a spell
        
        Args:
            spell_id (str): ID of the spell to diverge
            option (str): Divergence option ("option_1" or "option_2")
            
        Returns:
            bool: True if the divergence was successful, False otherwise
        """
        if spell_id in self.spells:
            return self.spells[spell_id].diverge(option)
        return False
    
    def get_spell_info(self, spell_id):
        """Get information about a spell
        
        Args:
            spell_id (str): ID of the spell
            
        Returns:
            dict or None: Spell display information, or None if spell not found
        """
        if spell_id in self.spells:
            return self.spells[spell_id].get_display_info()
        return None
    
    def get_all_spell_info(self):
        """Get information about all spells
        
        Returns:
            dict: Dictionary of {spell_id: spell_info}
        """
        return {spell_id: spell.get_display_info() for spell_id, spell in self.spells.items()}
    
    def add_new_spell(self, spell_id):
        """Add a new spell to the player's spells
        
        Args:
            spell_id (str): ID of the spell to add
            
        Returns:
            bool: True if the spell was added, False otherwise
        """
        if spell_id in self.spell_data and spell_id not in self.spells:
            self.spells[spell_id] = Spell(spell_id, self.spell_data[spell_id])
            return True
        return False
    
    def fuse_spells(self, spell_id1, spell_id2, fusion_rules):
        """Fuse two spells together
        
        Args:
            spell_id1 (str): ID of the first spell
            spell_id2 (str): ID of the second spell
            fusion_rules (dict): Rules for fusion from DataHandler
            
        Returns:
            str or None: ID of the resulting spell, or None if fusion failed
        """
        # Ensure both spells exist
        if spell_id1 not in self.spells or spell_id2 not in self.spells:
            return None
        
        # Check if this fusion is defined in the rules
        fusion_key = f"{spell_id1}_{spell_id2}"
        reverse_fusion_key = f"{spell_id2}_{spell_id1}"
        
        result_spell_id = None
        if fusion_key in fusion_rules:
            result_spell_id = fusion_rules[fusion_key]
        elif reverse_fusion_key in fusion_rules:
            result_spell_id = fusion_rules[reverse_fusion_key]
        
        if result_spell_id and result_spell_id in self.spell_data:
            # Remove the second spell
            del self.spells[spell_id2]
            
            # Replace the first spell with the fusion result
            self.spells[spell_id1] = Spell(result_spell_id, self.spell_data[result_spell_id])
            
            return result_spell_id
        
        return None 

class LevelUpState(GameState):
    """State for handling level up spell selection UI"""
    
    def __init__(self, game_manager, player, level):
        """Initialize level up state
        
        Args:
            game_manager (GameManager): Reference to the game manager
            player (Player): Reference to the player
            level (int): New player level
        """
        print(f"LevelUpState.__init__: Creating with level={level}, player={player}")
        
        try:
            super().__init__(game_manager)
            print("LevelUpState.__init__: Called super().__init__()")
            
            self.player = player
            self.level = level
            self.ui_manager = UIManager()
            print("LevelUpState.__init__: Created UIManager")
            
            self.available_spells = []
            self.spell_choices = []
            
            # Load all spells data
            print("LevelUpState.__init__: Loading spell data")
            self.all_spells_data = DataHandler.load_spells()
            print(f"LevelUpState.__init__: Loaded {len(self.all_spells_data)} spells")
            
            # Setup UI
            print("LevelUpState.__init__: Setting up UI")
            self.setup_ui()
            print("LevelUpState.__init__: UI setup complete")
            
            # Generate spell choices - either upgrades to existing spells or new spells
            print("LevelUpState.__init__: Generating spell choices")
            self._generate_spell_choices()
            print(f"LevelUpState.__init__: Generated {len(self.spell_choices)} spell choices")
            
            print("LevelUpState.__init__: Initialization complete")
        except Exception as e:
            print(f"LevelUpState.__init__: Error during initialization: {e}")
            import traceback
            traceback.print_exc()
    
    def setup_ui(self):
        """Setup the level up UI"""
        from src import config
        
        # Title
        title_x = config.SCREEN_WIDTH // 2 - 200
        title_y = 50
        title_width = 400
        title_height = 50
        
        self.ui_manager.add_element("level_up_title", TextBox(
            x=title_x,
            y=title_y,
            width=title_width,
            height=title_height,
            text=f"Level Up! - Level {self.level}",
            font_size=36,
            text_color=config.WHITE,
            background_color=config.DARK_GRAY
        ))
        
        # Subtitle
        subtitle_y = title_y + title_height + 20
        
        self.ui_manager.add_element("level_up_subtitle", TextBox(
            x=title_x,
            y=subtitle_y,
            width=title_width,
            height=30,
            text="Choose a spell or upgrade:",
            font_size=24,
            text_color=config.WHITE,
            background_color=None
        ))
    
    def _generate_spell_choices(self):
        """Generate spell choices for the level up UI"""
        # First, check if the player has existing spells that can be upgraded
        upgradable_spells = []
        new_spell_options = []
        
        print(f"LevelUpState._generate_spell_choices: Starting spell choices generation")
        
        # Make sure we always have 3 choices
        self.spell_choices = []
        
        if self.player:
            print(f"LevelUpState._generate_spell_choices: Player has {len(self.player.spells)} spells")
            # Check current spells for upgrades
            for spell_id in self.player.spells:
                spell_data = self.all_spells_data.get(spell_id)
                if spell_data:
                    # Check if this spell has an upgrade for the current level
                    next_level = 2  # Assuming spell starts at level 1
                    if hasattr(self.player, 'spell_levels'):
                        next_level = self.player.spell_levels.get(spell_id, 1) + 1
                    
                    level_key = f"level_{next_level}"
                    
                    # Debug output for spell upgrades
                    print(f"LevelUpState._generate_spell_choices: Checking upgrades for {spell_id}, next_level={next_level}")
                    print(f"LevelUpState._generate_spell_choices: Upgrades available: {spell_data.get('upgrades', {}).keys()}")
                    
                    if level_key in spell_data.get("upgrades", {}):
                        # This spell can be upgraded
                        upgradable_spells.append({
                            "id": spell_id,
                            "name": spell_data.get("name", "Unknown Spell"),
                            "description": spell_data.get("description", ""),
                            "upgrade_level": next_level,
                            "type": "upgrade"
                        })
            
            # Now add some new spell options
            # Filter to spells the player doesn't have yet
            for spell_id, spell_data in self.all_spells_data.items():
                if spell_id not in self.player.spells:
                    new_spell_options.append({
                        "id": spell_id,
                        "name": spell_data.get("name", "Unknown Spell"),
                        "description": spell_data.get("description", ""),
                        "type": "new"
                    })
        
        print(f"LevelUpState._generate_spell_choices: Found {len(upgradable_spells)} upgradable spells and {len(new_spell_options)} new spells")
        
        # Combine and limit choices
        if upgradable_spells:
            # Prioritize upgrades
            self.spell_choices = upgradable_spells[:2]  # Maximum 2 upgrade options
        
        # Fill remaining slots with new spells
        remaining_slots = 3 - len(self.spell_choices)
        if remaining_slots > 0 and new_spell_options:
            import random
            # Randomly select from available new spells
            random_new_spells = random.sample(new_spell_options, min(remaining_slots, len(new_spell_options)))
            self.spell_choices.extend(random_new_spells)
        
        # If we still don't have 3 choices, add filler options
        while len(self.spell_choices) < 3:
            # Add a basic health upgrade as filler
            self.spell_choices.append({
                "id": "health_boost",
                "name": "Health Boost",
                "description": "Increase your maximum health by 20 points.",
                "type": "new"
            })
        
        print(f"LevelUpState._generate_spell_choices: Final spell choices: {len(self.spell_choices)}")
        for i, choice in enumerate(self.spell_choices):
            print(f"  Choice {i+1}: {choice['name']} ({choice['type']})")
        
        # Now create UI elements for each choice
        self._create_spell_choice_ui()
    
    def _create_spell_choice_ui(self):
        """Create UI elements for spell choices"""
        from src import config
        
        # Position calculations
        button_width = 300
        button_height = 150
        button_spacing = 40
        start_y = 150
        
        print(f"LevelUpState._create_spell_choice_ui: Creating UI for {len(self.spell_choices)} choices")
        
        # Always use the layout for 3 buttons to ensure consistent spacing
        # Three buttons side by side
        total_width = 3 * button_width + 2 * button_spacing
        start_x = config.SCREEN_WIDTH // 2 - total_width // 2
        positions = [
            (start_x, start_y),
            (start_x + button_width + button_spacing, start_y),
            (start_x + 2 * (button_width + button_spacing), start_y)
        ]
        
        # Create buttons for each spell choice
        for i, choice in enumerate(self.spell_choices):
            if i < len(positions):
                x, y = positions[i]
                
                print(f"LevelUpState._create_spell_choice_ui: Creating UI for choice {i+1}: {choice['name']}")
                
                # Box background with vibrant border
                border_color = config.BRIGHT_BLUE if choice["type"] == "new" else config.BRIGHT_GREEN
                
                # Create background with contrasting colors
                self.ui_manager.add_element(f"spell_choice_bg_{i}", TextBox(
                    x=x,
                    y=y,
                    width=button_width,
                    height=button_height,
                    background_color=config.GRAY,  # Lighter background for better contrast
                    border_color=border_color
                ))
                
                # Spell name with bright color
                spell_type_text = "New Spell!" if choice["type"] == "new" else f"Upgrade (Level {choice.get('upgrade_level', 1)})"
                title_color = config.BRIGHT_BLUE if choice["type"] == "new" else config.BRIGHT_GREEN
                
                self.ui_manager.add_element(f"spell_choice_name_{i}", TextBox(
                    x=x,
                    y=y + 10,
                    width=button_width,
                    height=30,
                    text=f"{choice['name']} - {spell_type_text}",
                    font_size=20,
                    text_color=title_color,
                    background_color=None
                ))
                
                # Spell description
                self.ui_manager.add_element(f"spell_choice_desc_{i}", TextBox(
                    x=x + 10,
                    y=y + 50,
                    width=button_width - 20,
                    height=60,
                    text=choice["description"],
                    font_size=16,
                    text_color=config.BLACK,  # Change text color to black for better visibility on gray
                    background_color=None
                ))
                
                # Add a "Click to select" text at the bottom
                self.ui_manager.add_element(f"spell_choice_hint_{i}", TextBox(
                    x=x + 10,
                    y=y + button_height - 30,
                    width=button_width - 20,
                    height=20,
                    text="Click to select",
                    font_size=16,
                    text_color=config.RED,  # Make the hint text bright red for better visibility
                    background_color=None
                ))
                
                # Button overlay (for clicking) - make hover effect more noticeable
                self.ui_manager.add_element(f"spell_choice_button_{i}", Button(
                    x=x,
                    y=y,
                    width=button_width,
                    height=button_height,
                    text="",
                    color=(0, 0, 0, 0),  # Transparent
                    hover_color=(255, 255, 255, 130),  # More visible hover effect
                    on_click_data=i  # Store the choice index
                ))
    
    def handle_events(self, events):
        """Handle events
        
        Args:
            events (list): List of pygame events
        """
        # Handle mouse position
        mouse_pos = pygame.mouse.get_pos()
        
        # Process events for UI elements
        for event in events:
            # Handle mouse click events directly
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
                # Check if any spell choice button was clicked
                for i in range(len(self.spell_choices)):
                    button_id = f"spell_choice_button_{i}"
                    if button_id in self.ui_manager.elements:
                        button = self.ui_manager.elements[button_id]
                        if button.rect.collidepoint(mouse_pos):
                            self._select_spell(self.spell_choices[i])
                            return
            
            # Check for escape key to cancel
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # Default to first choice if player presses escape
                if self.spell_choices:
                    self._select_spell(self.spell_choices[0])
                else:
                    # Nothing to choose from, just return to previous state
                    self.game_manager.pop_state()
        
        # Pass events to UI manager as a backup
        clicked_elements = self.ui_manager.update(mouse_pos, events, 0.016)
        
        # Handle spell choice clicks from UI manager (if the direct check above missed anything)
        for element_id, click_data in clicked_elements.items():
            if element_id.startswith("spell_choice_button_") and isinstance(click_data, int):
                choice_index = click_data
                if 0 <= choice_index < len(self.spell_choices):
                    self._select_spell(self.spell_choices[choice_index])
                    return
    
    def _select_spell(self, spell_choice):
        """Handle spell selection
        
        Args:
            spell_choice (dict): The selected spell choice
        """
        print(f"Selected spell: {spell_choice['name']} ({spell_choice['id']})")
        
        if self.player:
            spell_id = spell_choice["id"]
            
            # Special handling for health boost
            if spell_id == "health_boost":
                print("Applying health boost...")
                # Increase max HP
                self.player.max_hp += 20
                self.player.current_hp += 20  # Also heal the player
                print(f"Player max HP increased to {self.player.max_hp}")
            elif spell_choice["type"] == "upgrade":
                # Upgrade existing spell
                print(f"Upgrading spell: {spell_id} to level {spell_choice['upgrade_level']}")
                # Track the levels in a dictionary attribute
                if not hasattr(self.player, 'spell_levels'):
                    self.player.spell_levels = {}
                
                # Set to the new level
                self.player.spell_levels[spell_id] = spell_choice["upgrade_level"]
                
            elif spell_choice["type"] == "new":
                # Add new spell
                print(f"Adding new spell: {spell_id}")
                self.player.equip_spell(spell_id)
                # Initialize level to 1
                if not hasattr(self.player, 'spell_levels'):
                    self.player.spell_levels = {}
                self.player.spell_levels[spell_id] = 1
        
        # Return to previous state
        self.game_manager.pop_state()
    
    def update(self, dt):
        """Update the level up state
        
        Args:
            dt (float): Time elapsed since last update in seconds
        """
        # No active updates needed
        pass
    
    def render(self, screen):
        """Render the level up state
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        # First, darken the previous state more significantly
        dark_overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        dark_overlay.fill((0, 0, 0, 220))  # More opaque black overlay (less transparent)
        screen.blit(dark_overlay, (0, 0))
        
        # Now render UI elements
        self.ui_manager.render(screen)
    
    def enter(self):
        """Called when entering this state"""
        print("LevelUpState.enter: Entering state")
        super().enter()
        print("LevelUpState.enter: State entered, transition started")
    
    def exit(self):
        """Called when exiting this state"""
        print("LevelUpState.exit: Exiting state")
        super().exit()
        print("LevelUpState.exit: State exited") 