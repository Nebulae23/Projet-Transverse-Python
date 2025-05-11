"""
Magic Survivor - Game Manager

This module manages the overall game state and transitions between states.
"""

import pygame
from src import config
from src.global_ui_manager import GlobalUIManager
from src.data_handler import DataHandler
from src.ui_manager import Button, TextBox
from src.projectile_system import ProjectileManager
from src.world_map import WorldMapState
from src.game_state_base import GameState
# Import CityInteriorState for type checking in notify_night_has_fallen
import typing
if typing.TYPE_CHECKING:
    from src.city_interior import CityInteriorState

class MainMenuState(GameState):
    """Main menu state"""
    
    def __init__(self, game_manager):
        """Initialize the main menu state
        
        Args:
            game_manager (GameManager): Reference to the game manager
        """
        super().__init__(game_manager)
        # Font will be properly set in enter() when Pygame is initialized
        self.font = None
        self.title_text = "MAGIC SURVIVOR"
        self.menu_options = ["New Game", "Load Game", "Quit"]
        self.selected_option = 0
        
        # If debug mode is enabled, add Editor option
        if config.DEBUG_MODE:
            self.menu_options.insert(2, "Editors")
    
    def handle_events(self, events):
        """Handle pygame events
        
        Args:
            events (list): List of pygame events
        """
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                elif event.key == pygame.K_RETURN:
                    self._select_option()
    
    def _select_option(self):
        """Handle selection of a menu option"""
        selected = self.menu_options[self.selected_option]
        
        if selected == "New Game":
            # Start new game - transition to WorldMapState
            from src.world_map import WorldMapState
            self.game_manager.change_state(WorldMapState(self.game_manager))
        elif selected == "Load Game":
            # Load saved game - for now, same as New Game but with saved data
            from src.world_map import WorldMapState
            self.game_manager.change_state(WorldMapState(self.game_manager, load_saved=True))
        elif selected == "Editors" and config.DEBUG_MODE:
            # Open editor menu
            from src.editor.editor_main import EditorMenuState
            self.game_manager.change_state(EditorMenuState(self.game_manager))
        elif selected == "Quit":
            self.game_manager.quit_game()
    
    def update(self, dt):
        """Update the main menu
        
        Args:
            dt (float): Time elapsed since last update in seconds
        """
        super().update(dt)
    
    def render(self, screen):
        """Render the main menu
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        # Fill the screen with black
        screen.fill(config.BLACK)
        
        # Render title
        title_surface = self.font.render(self.title_text, True, config.WHITE)
        title_rect = title_surface.get_rect(center=(config.SCREEN_WIDTH // 2, 100))
        screen.blit(title_surface, title_rect)
        
        # Render menu options
        for i, option in enumerate(self.menu_options):
            color = config.YELLOW if i == self.selected_option else config.WHITE
            option_surface = self.font.render(option, True, color)
            option_rect = option_surface.get_rect(center=(config.SCREEN_WIDTH // 2, 250 + i * 50))
            screen.blit(option_surface, option_rect)
        
        # Render transition effects
        self.render_transition(screen)
    
    def enter(self):
        """Called when entering the main menu state"""
        super().enter()
        # Initialize the font - do this here to ensure pygame is already initialized
        self.font = pygame.font.Font(None, 36)
    
    def exit(self):
        """Called when exiting the main menu state"""
        pass


class PauseState(GameState):
    """Pause menu state"""
    
    def __init__(self, game_manager, previous_state):
        """Initialize the pause state
        
        Args:
            game_manager (GameManager): Reference to the game manager
            previous_state (GameState): State to return to when unpausing
        """
        super().__init__(game_manager)
        self.previous_state = previous_state
        self.font = None
        self.title_text = "PAUSED"
        self.menu_options = ["Resume", "Save Game", "Main Menu", "Quit"]
        self.selected_option = 0
        self.is_transparent = True  # Render the state below this one
    
    def handle_events(self, events):
        """Handle pygame events
        
        Args:
            events (list): List of pygame events
        """
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Return to previous state
                    self.game_manager.pop_state()
                elif event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                elif event.key == pygame.K_RETURN:
                    self._select_option()
    
    def _select_option(self):
        """Handle selection of a menu option"""
        selected = self.menu_options[self.selected_option]
        
        if selected == "Resume":
            # Return to previous state
            self.game_manager.pop_state()
        elif selected == "Save Game":
            # Save game and return to previous state
            self.game_manager.save_all_game_data()
            self.game_manager.pop_state()
        elif selected == "Main Menu":
            # Return to main menu
            self.game_manager.clear_states()
            self.game_manager.push_state(MainMenuState(self.game_manager))
        elif selected == "Quit":
            self.game_manager.quit_game()
    
    def update(self, dt):
        """Update the pause menu
        
        Args:
            dt (float): Time elapsed since last update in seconds
        """
        super().update(dt)
    
    def render(self, screen):
        """Render the pause menu
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        # Create a semi-transparent overlay
        overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Black with alpha
        screen.blit(overlay, (0, 0))
        
        # Render pause menu
        title_surface = self.font.render(self.title_text, True, config.WHITE)
        title_rect = title_surface.get_rect(center=(config.SCREEN_WIDTH // 2, 100))
        screen.blit(title_surface, title_rect)
        
        # Render menu options
        for i, option in enumerate(self.menu_options):
            color = config.YELLOW if i == self.selected_option else config.WHITE
            option_surface = self.font.render(option, True, color)
            option_rect = option_surface.get_rect(center=(config.SCREEN_WIDTH // 2, 250 + i * 50))
            screen.blit(option_surface, option_rect)
        
        # Render transition effects
        self.render_transition(screen)
    
    def enter(self):
        """Called when entering the pause state"""
        super().enter()
        self.font = pygame.font.Font(None, 36)
    
    def exit(self):
        """Called when exiting the pause state"""
        pass


class GameManager:
    """Manages the game loop, states, and core systems."""
    
    def __init__(self):
        """Initialize the game manager"""
        pygame.init()
        pygame.mixer.init() # Initialize the mixer for sound
        
        # Initialize DataHandler and load all game data first
        self.data_handler = DataHandler()
        self.game_data = self.data_handler.load_all_data() # Loads data into data_handler instance and returns a dict
        # self.world_data_grid = self.data_handler.world_data # Direct access to the tile grid
        # self.tile_surfaces = self.data_handler.tile_surfaces # Direct access to loaded tile images
        # self.tile_variation_map = self.data_handler.tile_variation_map # Direct access to variation map

        self.screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption(config.GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.state_stack = []
        self.global_ui_manager = GlobalUIManager(self) # Pass game_manager reference

        # Initialize ProjectileManager here so it's available globally via game_manager
        self.projectile_manager = ProjectileManager(self) # Pass game_manager reference

        # City HP - Initialize after DataHandler potentially loads save data that might include this
        self.city_max_hp = config.CITY_MAX_HP
        # Try to load current city HP from player save data if available
        # This assumes player_save.json might store city_current_hp
        # player_save_data = self.data_handler.load_player_save() # REMOVE - Redundant and uses instance for classmethod
        player_save_data_static = DataHandler.load_player_save()
        self.city_current_hp = player_save_data_static.get("city_current_hp", config.CITY_MAX_HP)

        self.world_map_is_dirty = False # ADDED: Flag for pending world map save
        self.world_map_pois_dirty = False # ADDED: Flag for POI saving

        # Initial game state
        if config.EDITOR_MODE:
            from src.editor.editor_main import EditorMenuState
            self.push_state(EditorMenuState(self))
        else:
            self.push_state(MainMenuState(self))
            
        # Debug: Print loaded tile surfaces info
        if hasattr(self.data_handler, 'tile_surfaces') and self.data_handler.tile_surfaces:
            print("GameManager: Tile surfaces loaded in DataHandler:")
            for tile_type, surfaces in self.data_handler.tile_surfaces.items():
                print(f"  {tile_type}: {len(surfaces)} variations")
        else:
            print("GameManager: Tile surfaces not found or empty in DataHandler.")

        if hasattr(self.data_handler, 'tile_variation_map') and self.data_handler.tile_variation_map:
            print(f"GameManager: Tile variation map generated ({len(self.data_handler.tile_variation_map)}x{len(self.data_handler.tile_variation_map[0]) if self.data_handler.tile_variation_map else 0})")
        else:
            print("GameManager: Tile variation map not found or empty.")
    
    def push_state(self, new_state):
        """Push a new state onto the stack
        
        Args:
            new_state (GameState): New game state
        """
        # Pause current state if there is one
        if self.state_stack:
            self.state_stack[-1].pause()
        
        # Push the new state
        self.state_stack.append(new_state)
        new_state.enter()
    
    def pop_state(self):
        """Pop the current state off the stack"""
        if self.state_stack:
            old_state = self.state_stack.pop()
            if isinstance(old_state, WorldMapState) and self.world_map_is_dirty:
                print("WorldMapState popped and is dirty, attempting to save node states...")
                node_states_to_save = old_state.get_current_resource_node_data_for_saving()
                if self.data_handler.update_and_save_world_map_nodes(node_states_to_save):
                    self.world_map_is_dirty = False
                    print("Node states saved successfully on pop_state.")
                else:
                    print("Error saving node states on pop_state.")
            old_state.exit()
            
            # Resume the previous state if there is one
            if self.state_stack:
                self.state_stack[-1].resume()
    
    def change_state(self, new_state):
        """Change the current state (pop current state and push new state)
        
        Args:
            new_state (GameState): New game state
        """
        if self.state_stack:
            old_state = self.state_stack[-1]

            if isinstance(old_state, WorldMapState) and self.world_map_is_dirty:
                print("WorldMapState is being changed (exiting) and is dirty, attempting to save node states...")
                node_states_to_save = old_state.get_current_resource_node_data_for_saving()
                if self.data_handler.update_and_save_world_map_nodes(node_states_to_save):
                    self.world_map_is_dirty = False
                    print("Node states saved successfully before changing state.")
                else:
                    print("Error saving node states before changing state.")

            # Now proceed to pop and exit the old state
            self.state_stack.pop()
            old_state.exit()
        
        self.state_stack.append(new_state)
        new_state.enter()
    
    def clear_states(self):
        """Clear all states from the stack"""
        while self.state_stack:
            old_state = self.state_stack.pop()
            old_state.exit()
    
    def handle_events(self):
        """Handle pygame events"""
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                self.quit_game()
        
        # Handle UI events
        ui_clicked = self.global_ui_manager.update(pygame.mouse.get_pos(), events)
        self._handle_ui_clicks(ui_clicked)
        
        # Handle current state events
        if self.state_stack:
            self.state_stack[-1].handle_events(events)
    
    def _handle_ui_clicks(self, clicked):
        """Handle UI element clicks
        
        Args:
            clicked (dict): Dictionary of {element_id: True} for elements that were clicked
        """
        # Handle character UI button
        if "character_button" in clicked:
            self._toggle_character_panel()
        
        # Handle equipment UI button
        if "equipment_button" in clicked:
            self._toggle_equipment_panel()
        
        # Handle abilities UI button
        if "abilities_button" in clicked:
            self._toggle_abilities_panel()
        
        # Handle close buttons on panels
        for element_id in clicked:
            if element_id.endswith("_close"):
                panel_id = element_id[:-6]  # Remove "_close"
                self.global_ui_manager.remove_panel(panel_id)
                self.global_ui_manager.hide_modal()
    
    def _toggle_character_panel(self):
        """Toggle the character panel"""
        panel_id = "panel_character"
        if self.global_ui_manager.get_element(f"{panel_id}_bg", self.global_ui_manager.LAYER_OVERLAY):
            # Panel exists, remove it
            self.global_ui_manager.remove_panel(panel_id)
            self.global_ui_manager.hide_modal()
        else:
            # Create character panel
            self.global_ui_manager.create_panel(
                "Character",
                x=config.SCREEN_WIDTH // 2 - 200,
                y=config.SCREEN_HEIGHT // 2 - 250,
                width=400,
                height=500
            )
            
            # TODO: Add character stats to panel
            
            # Show as modal
            self.global_ui_manager.show_modal(self.global_ui_manager.LAYER_OVERLAY)
    
    def _toggle_equipment_panel(self):
        """Toggle the equipment panel"""
        panel_id = "panel_equipment"
        if self.global_ui_manager.get_element(f"{panel_id}_bg", self.global_ui_manager.LAYER_OVERLAY):
            # Panel exists, remove it
            self.global_ui_manager.remove_panel(panel_id)
            self.global_ui_manager.hide_modal()
        else:
            # Create equipment panel
            self.global_ui_manager.create_panel(
                "Equipment",
                x=config.SCREEN_WIDTH // 2 - 200,
                y=config.SCREEN_HEIGHT // 2 - 250,
                width=400,
                height=500
            )
            
            # TODO: Add equipment slots to panel
            
            # Show as modal
            self.global_ui_manager.show_modal(self.global_ui_manager.LAYER_OVERLAY)
    
    def _toggle_abilities_panel(self):
        """Toggle the abilities panel"""
        panel_id = "panel_abilities"
        if self.global_ui_manager.get_element(f"{panel_id}_bg", self.global_ui_manager.LAYER_OVERLAY):
            # Panel exists, remove it
            self.global_ui_manager.remove_panel(panel_id)
            self.global_ui_manager.hide_modal()
        else:
            # Create abilities panel
            self.global_ui_manager.create_panel(
                "Abilities",
                x=config.SCREEN_WIDTH // 2 - 200,
                y=config.SCREEN_HEIGHT // 2 - 250,
                width=400,
                height=500
            )
            
            # Get current state to access player data
            current_state = None
            if self.state_stack:
                current_state = self.state_stack[-1]
            
            # Try to get player data from current state
            player_data = None
            if hasattr(current_state, 'player_data'):
                player_data = current_state.player_data
            elif hasattr(current_state, 'player'):
                player_data = current_state.player.get_save_data() if hasattr(current_state.player, 'get_save_data') else None
            
            # If we have player data, show spells
            if player_data and 'spells' in player_data:
                # Load spell data
                spell_data = DataHandler.load_spells()
                
                # Add title for spells section
                self.global_ui_manager.add_element(
                    f"{panel_id}_spells_title",
                    TextBox(
                        x=config.SCREEN_WIDTH // 2 - 180,
                        y=config.SCREEN_HEIGHT // 2 - 210,
                        width=360,
                        height=30,
                        text="Spells/Abilities",
                        text_color=config.WHITE,
                        background_color=(50, 50, 70),
                        alignment="center"
                    ),
                    self.global_ui_manager.LAYER_OVERLAY
                )
                
                # Add each spell
                for i, spell_id in enumerate(player_data['spells']):
                    if spell_id in spell_data:
                        spell = spell_data[spell_id]
                        
                        # Background box
                        self.global_ui_manager.add_element(
                            f"{panel_id}_spell_{i}_bg",
                            TextBox(
                                x=config.SCREEN_WIDTH // 2 - 180,
                                y=config.SCREEN_HEIGHT // 2 - 170 + i * 90,
                                width=360,
                                height=80,
                                background_color=(80, 80, 100),
                                border_color=config.BLACK
                            ),
                            self.global_ui_manager.LAYER_OVERLAY
                        )
                        
                        # Spell name
                        self.global_ui_manager.add_element(
                            f"{panel_id}_spell_{i}_name",
                            TextBox(
                                x=config.SCREEN_WIDTH // 2 - 175,
                                y=config.SCREEN_HEIGHT // 2 - 170 + i * 90,
                                width=350,
                                height=25,
                                text=spell.get('name', 'Unknown Spell'),
                                text_color=config.YELLOW,
                                alignment="left"
                            ),
                            self.global_ui_manager.LAYER_OVERLAY
                        )
                        
                        # Spell description
                        self.global_ui_manager.add_element(
                            f"{panel_id}_spell_{i}_desc",
                            TextBox(
                                x=config.SCREEN_WIDTH // 2 - 175,
                                y=config.SCREEN_HEIGHT // 2 - 145 + i * 90,
                                width=350,
                                height=50,
                                text=spell.get('description', 'No description available.'),
                                text_color=config.WHITE,
                                font_size=16,
                                alignment="left"
                            ),
                            self.global_ui_manager.LAYER_OVERLAY
                        )
            else:
                # Show message if no spells found
                self.global_ui_manager.add_element(
                    f"{panel_id}_no_spells",
                    TextBox(
                        x=config.SCREEN_WIDTH // 2 - 180,
                        y=config.SCREEN_HEIGHT // 2 - 100,
                        width=360,
                        height=30,
                        text="No abilities found.",
                        text_color=config.WHITE,
                        alignment="center"
                    ),
                    self.global_ui_manager.LAYER_OVERLAY
                )
            
            # Show as modal
            self.global_ui_manager.show_modal(self.global_ui_manager.LAYER_OVERLAY)
    
    def update(self):
        """Update the game state"""
        dt = self.clock.get_time() / 1000.0  # Convert to seconds
        
        # Update state stack
        if self.state_stack:
            self.state_stack[-1].update(dt)
    
    def render(self):
        """Render the current game state"""
        # Find the first non-transparent state from the top
        first_solid_index = len(self.state_stack) - 1
        while first_solid_index >= 0 and self.state_stack[first_solid_index].is_transparent:
            first_solid_index -= 1
        
        # Render states from the first solid state to the top
        if first_solid_index >= 0:
            for i in range(first_solid_index, len(self.state_stack)):
                if i == first_solid_index or self.state_stack[i].is_transparent:
                    self.state_stack[i].render(self.screen)
        
        # Render UI on top
        self.global_ui_manager.render(self.screen)
        
        # Flip the display
        pygame.display.flip()
    
    def run(self):
        """Run the main game loop"""
        self.running = True
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(config.FPS)
        
        # Quit pygame when loop ends
        pygame.quit()
    
    def quit_game(self):
        """Quit the game"""
        # Save game data before quitting
        self.save_all_game_data()
        
        self.running = False
        pygame.quit()
        # Consider sys.exit() if pygame.quit() doesn't always terminate cleanly
        # import sys
        # sys.exit()

    def notify_night_has_fallen(self): # ADDED METHOD
        """Called by a game state (e.g., WorldMapState) when night begins."""
        print("GameManager: Night has fallen.")
        # Check if current state is CityInteriorState and pop it (expel player)
        if self.current_state and isinstance(self.current_state, typing.cast(typing.Any, __import__('src.city_interior', fromlist=['CityInteriorState'])).CityInteriorState): # Use cast and dynamic import for runtime check
            print("Player is in City Interior as night falls. Expelling to previous state (World Map).")
            self.pop_state()
            # Potentially, directly go to NightPhaseState if that's the desired flow
            # For now, popping to WorldMapState which will then handle NightPhase transition via 'E' key or automatically.

    def notify_day_has_broken(self): # ADDED METHOD
        """Called by a game state (e.g., WorldMapState) when day begins."""
        print("GameManager: Day has broken.")
        # Future logic for daybreak events could go here.
        pass

    def mark_world_map_dirty(self): # ADDED METHOD
        """Marks the world map (nodes) as dirty, needing a save."""
        self.world_map_is_dirty = True
        print("GameManager: World map nodes marked as dirty.") # Debug

    def mark_world_map_pois_dirty(self): # ADDED METHOD
        """Marks the world map POIs as dirty, needing a save."""
        self.world_map_pois_dirty = True
        print("GameManager: World map POIs marked as dirty.") # Debug

    def save_all_game_data(self): # ADDED METHOD
        """Saves all relevant game data."""
        print("GameManager: Attempting to save all game data...")
        current_active_state = self.current_state

        # 1. Save Player Data (primary responsibility of states managing player_data dict)
        player_data_to_save = None
        # Prioritize player_data from the current active state
        if hasattr(current_active_state, 'player_data') and current_active_state.player_data is not None:
            player_data_to_save = current_active_state.player_data
            # Ensure player position is updated from player object if current state has one
            if hasattr(current_active_state, 'player') and current_active_state.player is not None:
                player_data_to_save["position"] = {"x": current_active_state.player.x, "y": current_active_state.player.y}
            
            # Special handling for visited_map_chunks in WorldMapState to ensure correct format
            if isinstance(current_active_state, WorldMapState):
                if hasattr(current_active_state, 'visited_map_chunks') and isinstance(current_active_state.visited_map_chunks, set):
                    player_data_to_save["visited_map_chunks"] = [list(chunk) for chunk in current_active_state.visited_map_chunks]
                else: # If it's already a list (e.g. loaded from save)
                    player_data_to_save["visited_map_chunks"] = getattr(current_active_state, 'visited_map_chunks', [])
        #
        # If player_data was found, save it along with city HP
        if player_data_to_save is not None:
            player_data_to_save["city_current_hp"] = self.city_current_hp
            DataHandler.save_player_data(player_data_to_save)
            print("GameManager: Player data and City HP saved.")
        else:
            print("GameManager Warning: No player_data found in current state or game manager to save.")

        # 2. Save World Map Elements (Nodes and POIs)
        # This relies on dirty flags and current state being WorldMapState
        if isinstance(current_active_state, WorldMapState):
            if self.world_map_is_dirty:
                node_data = current_active_state.get_current_resource_node_data_for_saving()
                self.data_handler.update_and_save_world_map_nodes(node_data)
                self.world_map_is_dirty = False
                print("GameManager: World map resource node data saved.")
            
            if self.world_map_pois_dirty:
                poi_data = current_active_state.get_current_poi_data_for_saving()
                self.data_handler.update_and_save_world_map_pois(poi_data)
                self.world_map_pois_dirty = False
                print("GameManager: World map POI data saved.")
        elif self.world_map_is_dirty or self.world_map_pois_dirty:
            print("GameManager Warning: World map elements (nodes/POIs) are marked dirty, but current state is not WorldMapState. These elements were NOT saved.")

        print("GameManager: Save all game data process finished.")

    @property
    def current_state(self):
        """Get the current state"""
        if self.state_stack:
            return self.state_stack[-1]
        else:
            return None 