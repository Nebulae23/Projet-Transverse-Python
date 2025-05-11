"""
Magic Survivor - City Interior

This module provides the city interior state, where the player can manage
buildings, collect resources, and upgrade their city.
"""

import pygame
import math
from src import config
from src.game_manager import GameState
from src.ui_manager import Button, TextBox, ProgressBar
from src.data_handler import DataHandler
from src.city_manager import CityManager, Building

class BuildingUI:
    """UI representation of a building"""
    
    def __init__(self, building_id, building_data, x, y, width, height):
        """Initialize the building UI
        
        Args:
            building_id (str): ID of the building
            building_data (dict): Building data
            x (int): X position on screen
            y (int): Y position on screen
            width (int): Width of the building UI
            height (int): Height of the building UI
        """
        self.building_id = building_id
        self.data = building_data
        self.rect = pygame.Rect(x, y, width, height)
        
        # Get name and level
        self.name = building_data.get("name", "Unknown Building")
        self.level = building_data.get("level", 1)
        
        # Create a button for the building
        self.button = Button(
            x=x,
            y=y,
            width=width,
            height=height,
            text=f"{self.name} (Lv{self.level})",
            color=config.GRAY,
            hover_color=(180, 180, 200),
            text_color=config.BLACK
        )
    
    def update(self, mouse_pos):
        """Update the building UI
        
        Args:
            mouse_pos (tuple): Current mouse position (x, y)
        """
        self.button.update(mouse_pos)
    
    def render(self, screen):
        """Render the building UI
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        self.button.render(screen)
    
    def is_clicked(self, event):
        """Check if the building was clicked
        
        Args:
            event (pygame.event.Event): Mouse event
            
        Returns:
            bool: True if clicked, False otherwise
        """
        return self.button.is_clicked(event)


class BuildingDetailsPanel:
    """Panel showing details and actions for a building"""
    
    def __init__(self, x, y, width, height):
        """Initialize the building details panel
        
        Args:
            x (int): X position on screen
            y (int): Y position on screen
            width (int): Width of the panel
            height (int): Height of the panel
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.building = None
        
        # Background
        self.bg = TextBox(
            x=x,
            y=y,
            width=width,
            height=height,
            background_color=(100, 100, 120),
            border_color=config.BLACK
        )
        
        # Title
        self.title = TextBox(
            x=x,
            y=y,
            width=width,
            height=30,
            text="Building Details",
            text_color=config.WHITE,
            background_color=(50, 50, 70),
            border_color=config.BLACK,
            alignment="center"
        )
        
        # Description
        self.description = TextBox(
            x=x + 10,
            y=y + 40,
            width=width - 20,
            height=60,
            text="Select a building to see details",
            text_color=config.WHITE,
            alignment="left"
        )
        
        # Level and stats
        self.stats = TextBox(
            x=x + 10,
            y=y + 110,
            width=width - 20,
            height=100,
            text="",
            text_color=config.WHITE,
            alignment="left"
        )
        
        # Upgrade button (initially inactive)
        self.upgrade_button = Button(
            x=x + width // 2 - 75,
            y=y + height - 50,
            width=150,
            height=40,
            text="Upgrade",
            color=config.GREEN,
            hover_color=(150, 255, 150),
            text_color=config.BLACK
        )
        self.upgrade_button.is_active = False
    
    def set_building(self, building, city_manager, resources):
        """Set the building to display and update UI
        
        Args:
            building (Building): Building to display
            city_manager (CityManager): City manager reference
            resources (dict): Current resources
        """
        self.building = building
        
        if building:
            # Update title
            self.title.set_text(f"{building.name} (Level {building.level})")
            
            # Update description
            self.description.set_text(building.description)
            
            # Update stats
            stats_text = "Production:\n"
            for resource, amount in building.production.items():
                stats_text += f"  {resource.capitalize()}: {amount}/min\n"
            
            stats_text += "\nBonuses:\n"
            for bonus, value in building.bonuses.items():
                if "_percent" in bonus:
                    stats_text += f"  {bonus.replace('_', ' ').capitalize()}: {value}%\n"
                else:
                    stats_text += f"  {bonus.replace('_', ' ').capitalize()}: {value}\n"
            
            self.stats.set_text(stats_text)
            
            # Update upgrade button
            upgrade_cost = building.get_upgrade_cost()
            if upgrade_cost:
                # Check if player has enough resources
                can_upgrade = True
                for resource, amount in upgrade_cost.items():
                    if resources.get(resource, 0) < amount:
                        can_upgrade = False
                        break
                
                self.upgrade_button.is_active = can_upgrade
                
                # Update button text with cost
                cost_text = " ".join(f"{resource}:{amount}" for resource, amount in upgrade_cost.items())
                self.upgrade_button.text = f"Upgrade ({cost_text})"
            else:
                self.upgrade_button.is_active = False
                self.upgrade_button.text = "Max Level"
        else:
            # Reset to default
            self.title.set_text("Building Details")
            self.description.set_text("Select a building to see details")
            self.stats.set_text("")
            self.upgrade_button.is_active = False
            self.upgrade_button.text = "Upgrade"
    
    def update(self, mouse_pos):
        """Update the panel
        
        Args:
            mouse_pos (tuple): Current mouse position (x, y)
        """
        self.upgrade_button.update(mouse_pos)
    
    def render(self, screen):
        """Render the panel
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        self.bg.render(screen)
        self.title.render(screen)
        self.description.render(screen)
        self.stats.render(screen)
        self.upgrade_button.render(screen)
    
    def handle_upgrade_click(self, event, city_manager, resources):
        """Handle clicks on the upgrade button
        
        Args:
            event (pygame.event.Event): Mouse event
            city_manager (CityManager): City manager reference
            resources (dict): Current resources
            
        Returns:
            tuple: (success, updated_resources, resource_changes) if upgrade was attempted
                  None if no upgrade was attempted
        """
        if self.building and self.upgrade_button.is_active and self.upgrade_button.is_clicked(event):
            return city_manager.upgrade(self.building.id, resources)
        return None


class BuildingPlacementUI:
    """UI for placing new buildings"""
    
    def __init__(self, x, y, width, height):
        """Initialize the building placement UI
        
        Args:
            x (int): X position on screen
            y (int): Y position on screen
            width (int): Width of the UI
            height (int): Height of the UI
        """
        self.rect = pygame.Rect(x, y, width, height)
        
        # Background
        self.bg = TextBox(
            x=x,
            y=y,
            width=width,
            height=height,
            background_color=(100, 100, 120),
            border_color=config.BLACK
        )
        
        # Title
        self.title = TextBox(
            x=x,
            y=y,
            width=width,
            height=30,
            text="Build New Structure",
            text_color=config.WHITE,
            background_color=(50, 50, 70),
            border_color=config.BLACK,
            alignment="center"
        )
        
        # Available buildings (will be populated later)
        self.available_buildings = []
        self.building_buttons = []
    
    def set_available_buildings(self, building_data, city_manager, resources):
        """Set the available buildings and create buttons
        
        Args:
            building_data (dict): Building data (from DataHandler)
            city_manager (CityManager): City manager reference
            resources (dict): Current resources
        """
        self.available_buildings = []
        self.building_buttons = []
        
        available_ids = city_manager.get_available_buildings()
        button_y = self.rect.y + 40
        
        for building_id in available_ids:
            if building_id in building_data:
                data = building_data[building_id]
                
                # Check if player has enough resources
                can_build = True
                base_cost = data.get("base_cost", {})
                for resource, amount in base_cost.items():
                    if resources.get(resource, 0) < amount:
                        can_build = False
                        break
                
                # Create button
                cost_text = " ".join(f"{resource}:{amount}" for resource, amount in base_cost.items())
                button = Button(
                    x=self.rect.x + 10,
                    y=button_y,
                    width=self.rect.width - 20,
                    height=40,
                    text=f"{data.get('name', building_id)} ({cost_text})",
                    color=config.GRAY if can_build else (100, 100, 100),
                    hover_color=(180, 180, 200) if can_build else (100, 100, 100),
                    text_color=config.BLACK
                )
                button.is_active = can_build
                
                self.building_buttons.append((building_id, button))
                button_y += 50
    
    def update(self, mouse_pos):
        """Update the UI
        
        Args:
            mouse_pos (tuple): Current mouse position (x, y)
        """
        for _, button in self.building_buttons:
            button.update(mouse_pos)
    
    def render(self, screen):
        """Render the UI
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        self.bg.render(screen)
        self.title.render(screen)
        
        for _, button in self.building_buttons:
            button.render(screen)
    
    def handle_button_clicks(self, event, city_manager, resources):
        """Handle clicks on building buttons
        
        Args:
            event (pygame.event.Event): Mouse event
            city_manager (CityManager): City manager reference
            resources (dict): Current resources
            
        Returns:
            tuple: (success, updated_resources, resource_changes, building_id) if build was attempted
                  None if no build was attempted
        """
        for building_id, button in self.building_buttons:
            if button.is_active and button.is_clicked(event):
                success, updated_resources, resource_changes = city_manager.build(building_id, resources)
                return (success, updated_resources, resource_changes, building_id)
        return None


class ResourceDisplay:
    """UI for displaying resources"""
    
    def __init__(self, x, y, width, height):
        """Initialize the resource display
        
        Args:
            x (int): X position on screen
            y (int): Y position on screen
            width (int): Width of the display
            height (int): Height of the display
        """
        self.rect = pygame.Rect(x, y, width, height)
        
        # Background
        self.bg = TextBox(
            x=x,
            y=y,
            width=width,
            height=height,
            background_color=(50, 50, 70, 200),  # Semi-transparent
            border_color=config.BLACK
        )
        
        # Resources text
        self.resources_text = TextBox(
            x=x + 10,
            y=y + 5,
            width=width - 20,
            height=height - 10,
            text="Resources:",
            text_color=config.WHITE,
            alignment="left"
        )
    
    def update(self, resources, production_rates):
        """Update the resource display
        
        Args:
            resources (dict): Current resources
            production_rates (dict): Current production rates
        """
        # Build the text
        text = "Resources:\n"
        for resource, amount in sorted(resources.items()):
            # Get production rate
            rate = production_rates.get(resource, 0)
            rate_text = f"+{rate}/min" if rate > 0 else ""
            
            text += f"{resource.capitalize()}: {amount} {rate_text}\n"
        
        self.resources_text.set_text(text)
    
    def render(self, screen):
        """Render the display
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        self.bg.render(screen)
        self.resources_text.render(screen)


class CityInteriorState(GameState):
    """City interior state"""
    
    def __init__(self, game_manager, player_data):
        """Initialize the city interior state
        
        Args:
            game_manager (GameManager): Reference to the game manager
            player_data (dict): Player data
        """
        super().__init__(game_manager)
        self.player_data = player_data
        
        # City manager
        self.city_manager = CityManager()
        self.city_manager.load_player_buildings(player_data)
        
        # Resources
        self.resources = player_data.get("resources", {
            "wood": 100,
            "stone": 100
        })
        
        # Building data
        self.building_data = DataHandler.load_buildings()
        
        # Set up grid layout for buildings
        self.grid_size = 80  # Size of each grid cell
        self.grid_rows = 5
        self.grid_cols = 7
        self.grid_start_x = (config.SCREEN_WIDTH - self.grid_cols * self.grid_size) // 2
        self.grid_start_y = 100
        
        # Building UI elements
        self.building_uis = {}  # Dict of {building_id: BuildingUI}
        self.setup_building_uis()
        
        # Current selected building
        self.selected_building = None
        
        # Building details panel
        self.details_panel = BuildingDetailsPanel(
            x=config.SCREEN_WIDTH - 320,
            y=100,
            width=300,
            height=300
        )
        
        # Building placement UI
        self.placement_ui = BuildingPlacementUI(
            x=config.SCREEN_WIDTH - 320,
            y=420,
            width=300,
            height=250
        )
        self.placement_ui.set_available_buildings(self.building_data, self.city_manager, self.resources)
        
        # Resource display
        self.resource_display = ResourceDisplay(
            x=20,
            y=20,
            width=300,
            height=150
        )
        self.resource_display.update(self.resources, self.city_manager.production_rates)
        
        # Exit button
        self.exit_button = Button(
            x=config.SCREEN_WIDTH - 120,
            y=20,
            width=100,
            height=40,
            text="Exit City",
            color=config.RED,
            hover_color=(255, 150, 150),
            text_color=config.WHITE
        )
    
    def setup_building_uis(self):
        """Set up UI elements for all buildings"""
        self.building_uis = {}
        
        # Create a UI element for each building in the city
        grid_positions = {}  # Keep track of used grid positions
        
        for building_id, building in self.city_manager.buildings.items():
            # Find an available grid position
            row, col = 0, 0
            while (row, col) in grid_positions.values():
                col += 1
                if col >= self.grid_cols:
                    col = 0
                    row += 1
            
            # Calculate position
            x = self.grid_start_x + col * self.grid_size
            y = self.grid_start_y + row * self.grid_size
            
            # Create building UI
            building_ui = BuildingUI(
                building_id=building_id,
                building_data=building.get_display_info(),
                x=x,
                y=y,
                width=self.grid_size - 10,
                height=self.grid_size - 10
            )
            
            self.building_uis[building_id] = building_ui
            grid_positions[building_id] = (row, col)
    
    def handle_events(self, events):
        """Handle pygame events
        
        Args:
            events (list): List of pygame events
        """
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Exit the city
                    self.exit_city()
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check if exit button was clicked
                if self.exit_button.is_clicked(event):
                    self.exit_city()
                
                # Check if a building was clicked
                building_clicked = False
                for building_id, building_ui in self.building_uis.items():
                    if building_ui.is_clicked(event):
                        self.select_building(building_id)
                        building_clicked = True
                        break
                
                if not building_clicked:
                    # Check if upgrade button was clicked
                    upgrade_result = self.details_panel.handle_upgrade_click(event, self.city_manager, self.resources)
                    if upgrade_result:
                        success, updated_resources, resource_changes = upgrade_result
                        if success:
                            self.resources = updated_resources
                            
                            # Update UI elements
                            self.setup_building_uis()
                            if self.selected_building:
                                self.select_building(self.selected_building)
                            
                            # Update placement UI
                            self.placement_ui.set_available_buildings(
                                self.building_data, self.city_manager, self.resources
                            )
                    
                    # Check if build button was clicked
                    build_result = self.placement_ui.handle_button_clicks(event, self.city_manager, self.resources)
                    if build_result:
                        success, updated_resources, resource_changes, building_id = build_result
                        if success:
                            self.resources = updated_resources
                            
                            # Update UI elements
                            self.setup_building_uis()
                            
                            # Update placement UI
                            self.placement_ui.set_available_buildings(
                                self.building_data, self.city_manager, self.resources
                            )
    
    def select_building(self, building_id):
        """Select a building and update UI
        
        Args:
            building_id (str): ID of the building to select
        """
        self.selected_building = building_id
        
        # Update details panel
        building = self.city_manager.buildings.get(building_id)
        if building:
            self.details_panel.set_building(building, self.city_manager, self.resources)
    
    def update(self, dt):
        """Update the city interior
        
        Args:
            dt (float): Time elapsed since last update in seconds
        """
        super().update(dt)
        
        # Update city and resource production
        updated_resources = self.city_manager.update(dt, self.resources)
        if updated_resources != self.resources:
            self.resources = updated_resources
            
            # Store resources in player data
            self.player_data["resources"] = self.resources
            
            # Update UI
            self.resource_display.update(self.resources, self.city_manager.production_rates)
            
            # Update details panel if a building is selected
            if self.selected_building:
                building = self.city_manager.buildings.get(self.selected_building)
                if building:
                    self.details_panel.set_building(building, self.city_manager, self.resources)
            
            # Update placement UI
            self.placement_ui.set_available_buildings(self.building_data, self.city_manager, self.resources)
        
        # Update UI elements
        mouse_pos = pygame.mouse.get_pos()
        
        for building_ui in self.building_uis.values():
            building_ui.update(mouse_pos)
        
        self.details_panel.update(mouse_pos)
        self.placement_ui.update(mouse_pos)
        self.exit_button.update(mouse_pos)
    
    def render(self, screen):
        """Render the city interior
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        # Fill the screen with a background color
        screen.fill((100, 100, 150))
        
        # Draw a city layout background
        self.render_city_layout(screen)
        
        # Render buildings
        for building_ui in self.building_uis.values():
            building_ui.render(screen)
        
        # Render UI panels
        self.details_panel.render(screen)
        self.placement_ui.render(screen)
        self.resource_display.render(screen)
        self.exit_button.render(screen)
        
        # Render transition effects
        self.render_transition(screen)
    
    def render_city_layout(self, screen):
        """Render the city layout background
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        # Draw a grid for building placement
        for row in range(self.grid_rows):
            for col in range(self.grid_cols):
                x = self.grid_start_x + col * self.grid_size
                y = self.grid_start_y + row * self.grid_size
                
                rect = pygame.Rect(x, y, self.grid_size, self.grid_size)
                pygame.draw.rect(screen, (120, 120, 170), rect, 1)
    
    def exit_city(self):
        """Exit the city and return to the world map"""
        # Save player data
        self.player_data["city_buildings"] = {
            building_id: building.level for building_id, building in self.city_manager.buildings.items()
        }
        self.player_data["resources"] = self.resources
        DataHandler.save_player_data(self.player_data)
        
        # Pop this state to return to the world map
        self.game_manager.pop_state()
    
    def enter(self):
        """Called when entering the city interior state"""
        super().enter()
    
    def exit(self):
        """Called when exiting the city interior state"""
        # Save player data
        self.player_data["city_buildings"] = {
            building_id: building.level for building_id, building in self.city_manager.buildings.items()
        }
        self.player_data["resources"] = self.resources
        DataHandler.save_player_data(self.player_data)
    
    def resume(self):
        """Called when the city interior state is resumed"""
        pass
    
    def pause(self):
        """Called when the city interior state is paused"""
        pass 