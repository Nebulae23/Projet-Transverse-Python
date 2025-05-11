"""
Magic Survivor - Day/Night Manager

This module manages the day/night cycle and transitions between phases.
"""

import pygame
from src import config
from src.game_manager import GameState, PauseState
from src.data_handler import DataHandler

class DayNightManager:
    """Manages the day/night cycle"""
    
    def __init__(self, load_saved=False):
        """Initialize the day/night manager
        
        Args:
            load_saved (bool): Whether to load saved game data
        """
        # Load player save data
        self.player_data = DataHandler.load_player_save() if load_saved else {
            "level": 1,
            "xp": 0,
            "city_buildings": {},
            "spells": ["basic_projectile"],
            "relics": [],
            "day": 1
        }
        
        # Current day/night
        self.current_day = self.player_data["day"]
        self.is_day = True
        
        # Day timer
        self.day_timer = config.DAY_DURATION  # 10 minutes in seconds
        
        # Current resources
        self.resources = self.player_data.get("resources", {
            "wood": 100,
            "stone": 100,
            "iron": 0,
            "steel": 0,
            "knowledge": 0,
            "scrolls": 0
        })
    
    def update(self, dt):
        """Update the day/night cycle
        
        Args:
            dt (float): Time elapsed since last update in seconds
        
        Returns:
            bool: True if phase has changed, False otherwise
        """
        if self.is_day:
            self.day_timer -= dt
            if self.day_timer <= 0:
                self.transition_to_night()
                return True
        
        return False
    
    def transition_to_night(self):
        """Transition from day to night phase"""
        self.is_day = False
        # The actual transition will be handled by the game state
    
    def transition_to_day(self):
        """Transition from night to day phase"""
        self.is_day = True
        self.current_day += 1
        self.player_data["day"] = self.current_day
        self.day_timer = config.DAY_DURATION
        
        # Save player progress after each night
        DataHandler.save_player_data(self.player_data)
    
    def get_time_remaining_str(self):
        """Get a string representation of the time remaining in the day
        
        Returns:
            str: Time remaining in MM:SS format
        """
        minutes = int(self.day_timer // 60)
        seconds = int(self.day_timer % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_resources(self):
        """Get current resources
        
        Returns:
            dict: Current resources
        """
        return self.resources
    
    def update_resources(self, resource_changes):
        """Update resources
        
        Args:
            resource_changes (dict): Changes to resources (can be positive or negative)
        
        Returns:
            bool: True if successful, False if not enough resources
        """
        # Check if enough resources for negative changes
        for resource, change in resource_changes.items():
            if change < 0:
                current = self.resources.get(resource, 0)
                if current < abs(change):
                    return False
        
        # Apply changes
        for resource, change in resource_changes.items():
            current = self.resources.get(resource, 0)
            self.resources[resource] = current + change
        
        # Update player data
        self.player_data["resources"] = self.resources
        return True


class DayPhaseState(GameState):
    """Day phase game state"""
    
    def __init__(self, game_manager, load_saved=False):
        """Initialize the day phase state
        
        Args:
            game_manager (GameManager): Reference to the game manager
            load_saved (bool): Whether to load a saved game
        """
        super().__init__(game_manager)
        self.day_night_manager = DayNightManager(load_saved)
        self.font = None
        self.title_font = None
        self.resource_font = None
        
        # UI state
        self.current_screen = "city"  # "city" or "spellbook"
        self.selected_building = None
    
    def handle_events(self, events):
        """Handle pygame events
        
        Args:
            events (list): List of pygame events
        """
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Pause the game
                    self.game_manager.change_state(PauseState(self.game_manager, self))
                elif event.key == pygame.K_SPACE:
                    # Skip day and go directly to night by notifying GameManager
                    print("DayPhaseState: Spacebar pressed. Notifying GameManager night has fallen.")
                    self.game_manager.notify_night_has_fallen()
                elif event.key == pygame.K_1:
                    # Switch to city view
                    self.current_screen = "city"
                elif event.key == pygame.K_2:
                    # Switch to spellbook
                    self.current_screen = "spellbook"
                # Add more key handlers as needed
    
    def update(self, dt):
        """Update the day phase
        
        Args:
            dt (float): Time elapsed since last update in seconds
        """
        # Update day/night manager
        if self.day_night_manager.update(dt):
            # Phase has changed to night
            print("DayPhaseState: Day timer expired. Notifying GameManager night has fallen.")
            self.game_manager.notify_night_has_fallen()
    
    def render(self, screen):
        """Render the day phase
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        # Fill the screen with a "day" color
        screen.fill((135, 206, 235))  # Sky blue for day
        
        # Render day timer
        time_str = self.day_night_manager.get_time_remaining_str()
        time_surface = self.font.render(f"Day {self.day_night_manager.current_day} - {time_str}", True, config.BLACK)
        screen.blit(time_surface, (20, 20))
        
        # Render current screen
        if self.current_screen == "city":
            self._render_city_screen(screen)
        elif self.current_screen == "spellbook":
            self._render_spellbook_screen(screen)
        
        # Render resources bar
        self._render_resources_bar(screen)
        
        # Render UI navigation help
        help_surface = self.font.render("Press [1] for City, [2] for Spellbook, [Space] to skip to night", True, config.BLACK)
        screen.blit(help_surface, (20, config.SCREEN_HEIGHT - 30))
    
    def _render_city_screen(self, screen):
        """Render the city management screen
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        # Title
        title_surface = self.title_font.render("City Management", True, config.BLACK)
        screen.blit(title_surface, (config.SCREEN_WIDTH // 2 - title_surface.get_width() // 2, 60))
        
        # For now, just render placeholders for buildings
        # This would be replaced with actual building rendering and UI
        buildings = ["Forge", "Arcane Library"]
        for i, building in enumerate(buildings):
            # Simple rectangle to represent building
            building_rect = pygame.Rect(100, 120 + i * 100, 200, 80)
            pygame.draw.rect(screen, config.GRAY, building_rect)
            pygame.draw.rect(screen, config.BLACK, building_rect, 2)
            
            # Building name
            building_surface = self.font.render(building, True, config.BLACK)
            screen.blit(building_surface, (building_rect.centerx - building_surface.get_width() // 2,
                                           building_rect.centery - building_surface.get_height() // 2))
    
    def _render_spellbook_screen(self, screen):
        """Render the spellbook screen
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        # Title
        title_surface = self.title_font.render("Spellbook", True, config.BLACK)
        screen.blit(title_surface, (config.SCREEN_WIDTH // 2 - title_surface.get_width() // 2, 60))
        
        # Load spell data
        spells_data = DataHandler.load_spells()
        player_spells = self.day_night_manager.player_data["spells"]
        
        # For now, just render placeholders for spells
        # This would be replaced with actual spell rendering and UI
        for i, spell_id in enumerate(player_spells):
            if spell_id in spells_data:
                spell = spells_data[spell_id]
                # Simple rectangle to represent spell
                spell_rect = pygame.Rect(100, 120 + i * 100, 200, 80)
                pygame.draw.rect(screen, config.BLUE, spell_rect)
                pygame.draw.rect(screen, config.BLACK, spell_rect, 2)
                
                # Spell name
                spell_surface = self.font.render(spell["name"], True, config.WHITE)
                screen.blit(spell_surface, (spell_rect.centerx - spell_surface.get_width() // 2,
                                           spell_rect.centery - spell_surface.get_height() // 2))
    
    def _render_resources_bar(self, screen):
        """Render the resources bar
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        resources = self.day_night_manager.get_resources()
        
        # Background
        resource_bar_rect = pygame.Rect(0, 50, config.SCREEN_WIDTH, 30)
        pygame.draw.rect(screen, config.GRAY, resource_bar_rect)
        
        # Resource text
        x_pos = 20
        for resource, amount in resources.items():
            resource_text = f"{resource.capitalize()}: {amount}"
            resource_surface = self.resource_font.render(resource_text, True, config.BLACK)
            screen.blit(resource_surface, (x_pos, 55))
            x_pos += resource_surface.get_width() + 20
    
    def enter(self):
        """Called when entering the day phase state"""
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 48)
        self.resource_font = pygame.font.Font(None, 24)
    
    def exit(self):
        """Called when exiting the day phase state"""
        pass


class NightPhaseState(GameState):
    """Night phase game state - Placeholder for now
    
    This will be defined fully in night_phase.py
    """
    
    def __init__(self, game_manager, day_night_manager):
        """Initialize the night phase state
        
        Args:
            game_manager (GameManager): Reference to the game manager
            day_night_manager (DayNightManager): Reference to the day/night manager
        """
        super().__init__(game_manager)
        self.day_night_manager = day_night_manager
        # Just a placeholder - will be properly implemented in night_phase.py 