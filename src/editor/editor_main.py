"""
Magic Survivor - Editor

This module provides a basic editor for game content, accessible in debug mode.
"""

import pygame
import json # Import json for parsing trajectory_params
from src import config
from src.game_manager import GameState
from src.ui_manager import UIManager, Button, TextBox, InputBox
from src.data_handler import DataHandler

class EditorMenuState(GameState):
    """Editor menu state"""
    
    def __init__(self, game_manager):
        """Initialize the editor menu state
        
        Args:
            game_manager (GameManager): Reference to the game manager
        """
        super().__init__(game_manager)
        self.ui_manager = UIManager()
        self.font = None
        self.current_events = []
        self.last_clicked_elements = {}
        self.title_text = "GAME CONTENT EDITOR"
        
        # Editor options
        self.editor_options = [
            "Spell Editor",
            "Relic Editor",
            "Enemy Editor",
            "Wave Editor",
            "Building Editor",
            "Back to Main Menu"
        ]
    
    def handle_events(self, events):
        """Handle pygame events
        
        Args:
            events (list): List of pygame events
        """
        self.current_events = events
        # UI update and click processing moved to update() method
    
    def update(self, dt):
        """Update the editor menu
        
        Args:
            dt (float): Time elapsed since last update in seconds
        """
        self.last_clicked_elements = self.ui_manager.update(pygame.mouse.get_pos(), self.current_events, dt)
        for button_id, was_clicked in self.last_clicked_elements.items():
            if was_clicked:
                if button_id == "back_button":
                    from src.game_manager import MainMenuState
                    self.game_manager.change_state(MainMenuState(self.game_manager))
                elif button_id == "spell_button":
                    self.game_manager.change_state(SpellEditorState(self.game_manager))
                elif button_id == "relic_button":
                    self.game_manager.change_state(RelicEditorState(self.game_manager))
                elif button_id == "enemy_button":
                    self.game_manager.change_state(EnemyEditorState(self.game_manager))
                elif button_id == "wave_button":
                    self.game_manager.change_state(WaveEditorState(self.game_manager))
                elif button_id == "building_button":
                    self.game_manager.change_state(BuildingEditorState(self.game_manager))
        self.current_events = []
    
    def render(self, screen):
        """Render the editor menu
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        # Fill the screen with a dark color
        screen.fill((50, 50, 70))
        
        # Render UI elements
        self.ui_manager.render(screen)
    
    def enter(self):
        """Called when entering the editor menu state"""
        self.font = pygame.font.Font(None, 36)
        
        # Create UI elements
        button_width = 300
        button_height = 50
        button_spacing = 20
        start_y = 150
        
        # Title
        self.ui_manager.add_element("title", TextBox(
            x=config.SCREEN_WIDTH // 2 - 250,
            y=50,
            width=500,
            height=60,
            text=self.title_text,
            font_size=48,
            text_color=config.WHITE,
            alignment="center"
        ))
        
        # Editor option buttons
        self.ui_manager.add_element("spell_button", Button(
            x=config.SCREEN_WIDTH // 2 - button_width // 2,
            y=start_y,
            width=button_width,
            height=button_height,
            text="Spell Editor",
            color=config.GRAY,
            hover_color=config.WHITE,
            text_color=config.BLACK
        ))
        
        self.ui_manager.add_element("relic_button", Button(
            x=config.SCREEN_WIDTH // 2 - button_width // 2,
            y=start_y + button_height + button_spacing,
            width=button_width,
            height=button_height,
            text="Relic Editor",
            color=config.GRAY,
            hover_color=config.WHITE,
            text_color=config.BLACK
        ))
        
        self.ui_manager.add_element("enemy_button", Button(
            x=config.SCREEN_WIDTH // 2 - button_width // 2,
            y=start_y + (button_height + button_spacing) * 2,
            width=button_width,
            height=button_height,
            text="Enemy Editor",
            color=config.GRAY,
            hover_color=config.WHITE,
            text_color=config.BLACK
        ))
        
        self.ui_manager.add_element("wave_button", Button(
            x=config.SCREEN_WIDTH // 2 - button_width // 2,
            y=start_y + (button_height + button_spacing) * 3,
            width=button_width,
            height=button_height,
            text="Wave Editor",
            color=config.GRAY,
            hover_color=config.WHITE,
            text_color=config.BLACK
        ))
        
        self.ui_manager.add_element("building_button", Button(
            x=config.SCREEN_WIDTH // 2 - button_width // 2,
            y=start_y + (button_height + button_spacing) * 4,
            width=button_width,
            height=button_height,
            text="Building Editor",
            color=config.GRAY,
            hover_color=config.WHITE,
            text_color=config.BLACK
        ))
        
        # Back button
        self.ui_manager.add_element("back_button", Button(
            x=config.SCREEN_WIDTH // 2 - button_width // 2,
            y=start_y + (button_height + button_spacing) * 5,
            width=button_width,
            height=button_height,
            text="Back to Main Menu",
            color=config.RED,
            hover_color=(255, 150, 150),
            text_color=config.WHITE
        ))
    
    def exit(self):
        """Called when exiting the editor menu state"""
        pass


class BaseEditorState(GameState):
    """Base class for editor states"""
    
    def __init__(self, game_manager, title):
        """Initialize the base editor state
        
        Args:
            game_manager (GameManager): Reference to the game manager
            title (str): Title for the editor
        """
        super().__init__(game_manager)
        self.ui_manager = UIManager()
        self.font = None
        self.title = title
        self.current_events = []
        self.last_clicked_elements = {} # To store clicks from UIManager
        
        # Data handling
        self.data_handler = DataHandler()
        self.current_item = None
        self.items_data = {}
        self.modified = False
    
    def handle_events(self, events):
        """Handle pygame events
        
        Args:
            events (list): List of pygame events
        """
        self.current_events = events
        # Actual processing of clicks is moved to the update method
    
    def handle_back_button(self):
        """Handle back button click"""
        if self.modified:
            # TODO: Show confirmation dialog
            pass
        
        # Return to editor menu
        self.game_manager.change_state(EditorMenuState(self.game_manager))
    
    def update(self, dt):
        """Update the editor
        
        Args:
            dt (float): Time elapsed since last update in seconds
        """
        self.last_clicked_elements = self.ui_manager.update(pygame.mouse.get_pos(), self.current_events, dt)
        
        for button_id, was_clicked in self.last_clicked_elements.items():
            if was_clicked:
                if button_id == "back_button":
                    self.handle_back_button()
                elif button_id == "save_button":
                    self.save_data()
                # Specific editor buttons will be handled by the subclass's update method
                # by checking self.last_clicked_elements.
        
        self.current_events = []
    
    def render(self, screen):
        """Render the editor
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        # Fill the screen with a dark color
        screen.fill((50, 50, 70))
        
        # Render UI elements
        self.ui_manager.render(screen)
    
    def enter(self):
        """Called when entering the editor state"""
        self.font = pygame.font.Font(None, 36)
        
        # Create common UI elements
        # Title
        self.ui_manager.add_element("title", TextBox(
            x=config.SCREEN_WIDTH // 2 - 250,
            y=20,
            width=500,
            height=60,
            text=self.title,
            font_size=48,
            text_color=config.WHITE,
            alignment="center"
        ))
        
        # Back button
        self.ui_manager.add_element("back_button", Button(
            x=50,
            y=config.SCREEN_HEIGHT - 70,
            width=150,
            height=50,
            text="Back",
            color=config.RED,
            hover_color=(255, 150, 150),
            text_color=config.WHITE
        ))
        
        # Save button
        self.ui_manager.add_element("save_button", Button(
            x=config.SCREEN_WIDTH - 200,
            y=config.SCREEN_HEIGHT - 70,
            width=150,
            height=50,
            text="Save",
            color=config.GREEN,
            hover_color=(150, 255, 150),
            text_color=config.BLACK
        ))
        
        # Load data
        self.load_data()
        
        # Create editor-specific UI
        self.create_editor_ui()
    
    def exit(self):
        """Called when exiting the editor state"""
        pass
    
    def load_data(self):
        """Load data from the appropriate file - to be implemented in subclasses"""
        pass
    
    def save_data(self):
        """Save data to the appropriate file - to be implemented in subclasses"""
        pass
    
    def create_editor_ui(self):
        """Create editor-specific UI - to be implemented in subclasses"""
        pass


class SpellEditorState(BaseEditorState):
    """Spell editor state"""
    
    def __init__(self, game_manager):
        """Initialize the spell editor state
        
        Args:
            game_manager (GameManager): Reference to the game manager
        """
        super().__init__(game_manager, "SPELL EDITOR")
        self.spell_list = []
        self.selected_spell = None
        self.selected_spell_id = None
        self.text_inputs = {}
        self.selected_upgrade_level_key = None # For selected upgrade level
        self.upgrade_property_inputs = {} # To store InputBox instances for upgrade properties
                                          # {(level_key, prop_key): input_box_instance}
        self.upgrade_level_scroll_offset = 0
        self.max_visible_upgrade_levels = 0
        self.upgrade_level_list_rect = None # Will be defined in create_editor_ui
        self.spell_list_scroll_offset = 0
        self.max_visible_spells = 0
        self.spell_list_rect = None # For mouse wheel detection

        # For spell detail inputs
        self.detail_text_inputs = {} # name, description, mana_cost, cooldown, damage, etc.
        self.selected_spell_id = None
        self.selected_spell_data = {} # Holds a copy of the spell data for editing
        
        # For upgrade level list (master panel)
        self.upgrade_level_keys = [] # e.g. ["level_2", "level_3", ...]
        self.selected_upgrade_level_key = None # e.g. "level_2"
        self.upgrade_level_list_scroll_offset = 0
        self.max_visible_upgrade_levels = 10 # Will be calculated
        self.upgrade_level_list_rect = None

        # For upgrade properties of a selected level (detail panel)
        self.upgrade_property_inputs = {} # Stores InputBox instances for current level's props
        self.current_upgrade_level_data_copy = {} # Copy of selected upgrade level data

        # NEW: Trajectory inputs
        self.trajectory_input_id = "spell_trajectory_input"
        self.trajectory_params_input_id = "spell_trajectory_params_input"
    
    def load_data(self):
        """Load spell data"""
        self.items_data = self.data_handler.load_spells()
        self.spell_list = list(self.items_data.keys())
    
    def save_data(self):
        """Save spell data"""
        print(f"[DEBUG] save_data: Attempting to save. self.items_data to be saved: {self.items_data}")
        success = self.data_handler.save_json(self.items_data, config.SPELLS_DATA)
        print(f"[DEBUG] save_data: Save operation success: {success}")
        if not success:
            print(f"[DEBUG] save_data: Data that failed to save: {self.items_data}")
        if success:
            self.modified = False
            # Show success message
            self.ui_manager.add_element("save_message", TextBox(
                x=config.SCREEN_WIDTH // 2 - 100,
                y=config.SCREEN_HEIGHT - 50,
                width=200,
                height=30,
                text="Spells saved successfully!",
                text_color=config.GREEN,
                alignment="center"
            ))
    
    def create_editor_ui(self):
        """Create spell editor UI"""
        # Left panel - spell list
        list_width = 250
        list_height = 400
        list_x = 50
        list_y = 100
        
        self.ui_manager.add_element("spell_list_bg", TextBox(
            x=list_x,
            y=list_y,
            width=list_width,
            height=list_height,
            background_color=(100, 100, 120),
            border_color=config.BLACK
        ))
        
        self.ui_manager.add_element("spell_list_title", TextBox(
            x=list_x,
            y=list_y - 30,
            width=list_width,
            height=30,
            text="Spells",
            text_color=config.WHITE,
            alignment="center"
        ))
        
        # Create spell list buttons
        button_height = 30
        for i, spell_id in enumerate(self.spell_list):
            spell_name = self.items_data[spell_id].get("name", spell_id)
            self.ui_manager.add_element(f"spell_button_{i}", Button(
                x=list_x + 5,
                y=list_y + 5 + i * (button_height + 5),
                width=list_width - 10,
                height=button_height,
                text=spell_name,
                color=config.GRAY,
                hover_color=config.WHITE,
                text_color=config.BLACK
            ))
        
        # Right panel - spell details
        detail_width = 700
        detail_height = 500
        detail_x = list_x + list_width + 50
        detail_y = 100
        
        self.ui_manager.add_element("spell_details_bg", TextBox(
            x=detail_x,
            y=detail_y,
            width=detail_width,
            height=detail_height,
            background_color=(100, 100, 120),
            border_color=config.BLACK
        ))
        
        self.ui_manager.add_element("spell_details_title", TextBox(
            x=detail_x,
            y=detail_y - 30,
            width=detail_width,
            height=30,
            text="Spell Details",
            text_color=config.WHITE,
            alignment="center"
        ))
        
        # Add spell detail fields
        field_x = detail_x + 20
        field_y_start_main_props = detail_y + 20
        field_width = 300
        field_height = 30
        field_spacing = 40
        
        fields = [
            ("name", "Name:"),
            ("description", "Description:"),
            ("damage", "Damage:"),
            ("cooldown", "Cooldown:"),
            ("projectile_speed", "Projectile Speed:"),
            ("radius", "Radius (if applicable):"),
            ("tick_rate", "Tick Rate (if applicable):"),
        ]
        
        for i, (field_id, field_label) in enumerate(fields):
            # Label
            self.ui_manager.add_element(f"spell_field_label_{field_id}", TextBox(
                x=field_x,
                y=field_y_start_main_props + i * field_spacing,
                width=150,
                height=field_height,
                text=field_label,
                text_color=config.WHITE,
                alignment="left"
            ))
            
            # Input box
            self.ui_manager.add_element(f"spell_field_input_{field_id}", InputBox(
                x=field_x + 160,
                y=field_y_start_main_props + i * field_spacing,
                width=field_width,
                height=field_height,
                text="",
                text_color=config.BLACK,
                background_color=config.WHITE,
                border_color=config.BLACK,
                alignment="left"
            ))
            
            # Track the input field
            self.text_inputs[field_id] = f"spell_field_input_{field_id}"
        
        # Calculate end Y of main properties to position upgrade editor below them
        end_y_of_main_props = field_y_start_main_props + len(fields) * field_spacing

        # --- Upgrade Editor Section UI --- 
        # Positioned within the lower part of "spell_details_bg"
        self.upgrade_editor_area_x = detail_x + 10 # Inside spell_details_bg padding
        self.upgrade_editor_area_y = end_y_of_main_props + 20 # Start below main props + padding
        self.upgrade_editor_area_width = detail_width - 20 # Fit within spell_details_bg with padding
        # Calculate remaining height for upgrade editor within spell_details_bg
        self.upgrade_editor_area_height = detail_y + detail_height - self.upgrade_editor_area_y - 10 # Maximize height, -10 for bottom padding

        self.ui_manager.add_element("upgrade_editor_bg", TextBox(
            x=self.upgrade_editor_area_x,
            y=self.upgrade_editor_area_y,
            width=self.upgrade_editor_area_width,
            height=self.upgrade_editor_area_height,
            background_color=(70, 70, 90), 
            border_color=config.BLACK
        ))
        
        self.ui_manager.add_element("upgrade_editor_title_text", TextBox( # Renamed to avoid ID clash if any
            x=self.upgrade_editor_area_x,
            y=self.upgrade_editor_area_y + 5, 
            width=self.upgrade_editor_area_width,
            height=20,
            text="Upgrade Levels Editor",
            text_color=config.WHITE,
            alignment="center"
        ))

        # --- Scroll Button Panel (NEW) ---
        scroll_button_panel_width = 30
        scroll_button_panel_padding = 5
        self.scroll_button_panel_x = self.upgrade_editor_area_x + scroll_button_panel_padding
        self.scroll_button_panel_y = self.upgrade_editor_area_y + 30 # Align with master_panel_y start
        self.scroll_button_panel_height = self.upgrade_editor_area_height - 35 # Match master_panel_height for levels

        self.ui_manager.add_element("uplevel_scroll_up_button", Button(
            x=self.scroll_button_panel_x,
            y=self.scroll_button_panel_y,
            width=scroll_button_panel_width,
            height=scroll_button_panel_width, # Square button
            text="^", # Up arrow or similar
            color=config.GRAY, text_color=config.BLACK
        ))

        self.ui_manager.add_element("uplevel_scroll_down_button", Button(
            x=self.scroll_button_panel_x,
            y=self.scroll_button_panel_y + self.scroll_button_panel_height - scroll_button_panel_width,
            width=scroll_button_panel_width,
            height=scroll_button_panel_width, # Square button
            text="v", # Down arrow or similar
            color=config.GRAY, text_color=config.BLACK
        ))

        # Master Panel (Levels List) - Adjusted for Scroll Button Panel
        self.master_panel_x = self.scroll_button_panel_x + scroll_button_panel_width + scroll_button_panel_padding
        self.master_panel_y = self.upgrade_editor_area_y + 30 
        self.master_panel_width = 200 - scroll_button_panel_width - scroll_button_panel_padding # Original was 200
        self.master_panel_height = self.upgrade_editor_area_height - 35
        
        # Define the actual rect for mouse wheel collision (area where level buttons are listed)
        # Exclude area taken by Add/Remove buttons at the bottom of the master panel
        add_remove_buttons_total_height = 60 # (25 for add + 25 for remove + 10 padding)
        actual_list_area_height = self.master_panel_height - add_remove_buttons_total_height 
        self.upgrade_level_list_rect = pygame.Rect(
            self.master_panel_x,
            self.master_panel_y,
            self.master_panel_width,
            actual_list_area_height 
        )
        
        # Calculate max_visible_upgrade_levels
        level_button_height = 25
        level_button_spacing = 5
        if actual_list_area_height > 0 and (level_button_height + level_button_spacing) > 0:
            self.max_visible_upgrade_levels = actual_list_area_height // (level_button_height + level_button_spacing)
        else:
            self.max_visible_upgrade_levels = 0

        self.ui_manager.add_element("add_new_level_button", Button(
            x=self.master_panel_x, # Positioned within the adjusted master panel
            y=self.master_panel_y + self.master_panel_height - 30, 
            width=self.master_panel_width - 10,
            height=25,
            text="Add New Level",
            color=config.GREEN, text_color=config.BLACK
        ))
        
        self.ui_manager.add_element("remove_selected_level_button", Button(
            x=self.master_panel_x, # Positioned within the adjusted master panel
            y=self.master_panel_y + self.master_panel_height - 60, 
            width=self.master_panel_width - 10,
            height=25,
            text="Remove Selected Level",
            color=config.RED, text_color=config.WHITE
        ))
        
        # Detail Panel (Properties) - Adjusted for Master Panel's new X
        self.detail_panel_x = self.master_panel_x + self.master_panel_width + 10
        self.detail_panel_y = self.upgrade_editor_area_y + 30 
        self.detail_panel_width = self.upgrade_editor_area_width - self.master_panel_width - 20 
        self.detail_panel_height = self.upgrade_editor_area_height - 35 # Align with master_panel_height

        self.ui_manager.add_element("upgrade_detail_panel_title_text", TextBox( # Renamed
            x=self.detail_panel_x,
            y=self.detail_panel_y, # Position title at the top of this sub-panel
            width=self.detail_panel_width,
            height=20,
            text="Edit Level: None",
            text_color=config.WHITE,
            alignment="center"
        ))

        prop_button_y_start = self.detail_panel_y + self.detail_panel_height - 30 # Bottom of detail panel
        self.ui_manager.add_element("add_damage_prop_button", Button(
            x=self.detail_panel_x + 5, y=prop_button_y_start,
            width=100, height=25, text="Add Damage", color=config.BLUE, text_color=config.WHITE
        ))
        self.ui_manager.add_element("add_cooldown_prop_button", Button(
            x=self.detail_panel_x + 110, y=prop_button_y_start,
            width=100, height=25, text="Add Cooldown", color=config.BLUE, text_color=config.WHITE
        ))
        self.ui_manager.add_element("toggle_divergence_button", Button(
            x=self.detail_panel_x + 215, y=prop_button_y_start,
            width=120, height=25, text="Toggle Divergence", color=config.BLUE, text_color=config.WHITE
        ))

        # Remove the old "upgrades_info" text box if it exists from a previous state
        if self.ui_manager.get_element("upgrades_info"):
            self.ui_manager.remove_element("upgrades_info")
        if self.ui_manager.get_element("upgrades_label"):
             self.ui_manager.remove_element("upgrades_label")

        # Apply button (to apply changes to the current spell - existing button)
        # This should be outside and below the spell_details_bg or positioned fixedly.
        # For now, ensure its Y position is below the spell_details_bg or fixed.
        # The original create_editor_ui code had it positioned relative to main spell fields.
        # Let's make its Y position fixed relative to the bottom of the screen, or below spell_details_bg.
        apply_button_y = detail_y + detail_height + 10 # Below the main spell detail area
        self.ui_manager.add_element("apply_changes_button", Button(
            x=detail_x + detail_width - 170, # Align to right within detail_x area
            y=apply_button_y, 
            width=150, height=40, text="Apply Changes",
            color=config.BLUE, hover_color=(150, 150, 255), text_color=config.WHITE
        ))
        
        # New spell and Delete spell buttons (existing)
        self.ui_manager.add_element("new_spell_button", Button(
            x=list_x, y=list_y + list_height + 10, width=list_width, height=40,
            text="New Spell", color=config.GREEN, hover_color=(150, 255, 150), text_color=config.BLACK
        ))
        self.ui_manager.add_element("delete_spell_button", Button(
            x=list_x, y=list_y + list_height + 60, width=list_width, height=40,
            text="Delete Spell", color=config.RED, hover_color=(255, 150, 150), text_color=config.WHITE
        ))
        
        self._rebuild_spell_list_ui()
    
    def _rebuild_spell_list_ui(self):
        """Clears and recreates the spell list buttons in the UI."""
        # Remove existing spell buttons (assuming IDs like "spell_button_0", "spell_button_1", etc.)
        # Collect IDs to remove to avoid modifying dict while iterating
        buttons_to_remove = [elem_id for elem_id in self.ui_manager.elements 
                             if elem_id.startswith("spell_button_")]
        for elem_id in buttons_to_remove:
            self.ui_manager.remove_element(elem_id)

        list_width = 250
        list_x = 50
        list_y = 100
        button_height = 30

        # Re-create spell list buttons
        for i, spell_id in enumerate(self.spell_list):
            spell_name = self.items_data.get(spell_id, {}).get("name", spell_id) # Safer get
            self.ui_manager.add_element(f"spell_button_{i}", Button(
                x=list_x + 5,
                y=list_y + 5 + i * (button_height + 5),
                width=list_width - 10,
                height=button_height,
                text=spell_name,
                color=config.GRAY,
                hover_color=config.WHITE,
                text_color=config.BLACK
            ))
    
    def handle_events(self, events):
        """Handle pygame events - primarily for parent state and global keys if any.
           Specific UI event handling (clicks, text input) is now in update() via UIManager.
        Args:
            events (list): List of pygame events
        """
        super().handle_events(events) # This will store events in self.current_events

        # Keyboard input for text fields is now handled by UIManager and InputBox itself.
        # The placeholder loop below is no longer needed.
        # for event in events:
        #     if event.type == pygame.KEYDOWN and self.selected_spell_id:
        #         pass

    def update(self, dt):
        """Update spell editor state"""

        # Handle mouse wheel scrolling for the upgrade level list
        if self.selected_spell and self.upgrade_level_list_rect: # Ensure rect is defined
            mouse_pos = pygame.mouse.get_pos()
            if self.upgrade_level_list_rect.collidepoint(mouse_pos):
                for event in self.current_events: # self.current_events is populated by GameState.handle_events
                    if event.type == pygame.MOUSEWHEEL:
                        if event.y > 0:  # Scroll Up
                            self.upgrade_level_scroll_offset = max(0, self.upgrade_level_scroll_offset - 1)
                        elif event.y < 0:  # Scroll Down
                            # Recalculate total_upgrade_levels and max_scroll locally for safety
                            total_upgrade_levels = len(self.selected_spell.get('upgrades', {}).keys())
                            max_scroll = total_upgrade_levels - self.max_visible_upgrade_levels
                            if max_scroll < 0: max_scroll = 0
                            self.upgrade_level_scroll_offset = min(max_scroll, self.upgrade_level_scroll_offset + 1)
                        
                        self._populate_upgrade_editor() # Refresh list and scroll button states
                        # Consume the event to prevent other uses if necessary, though UIManager might not use it.
                        # self.current_events.remove(event) # Careful if iterating and modifying
                        break # Process only one scroll event per frame for this list
        
        super().update(dt) # This calls UIManager.update and handles common buttons (Back, Save)
                        # and populates self.last_clicked_elements

        for element_id, was_clicked in self.last_clicked_elements.items():
            if was_clicked:
                if element_id.startswith("spell_button_"):
                    try:
                        index_str = element_id.split("_")[-1]
                        index = int(index_str)
                        if 0 <= index < len(self.spell_list):
                            spell_id = self.spell_list[index]
                            self.select_spell(spell_id)
                    except ValueError:
                        # Handle cases where conversion to int might fail or index is out of bounds
                        print(f"Error processing spell button click: {element_id}")
                elif element_id == "apply_changes_button":
                    self.apply_changes()
                elif element_id == "new_spell_button":
                    self.create_new_spell()
                elif element_id == "delete_spell_button":
                    self.delete_selected_spell()
                # --- Scroll Button Click Handling for Upgrade Levels ---
                elif element_id == "uplevel_scroll_up_button":
                    button_instance = self.ui_manager.get_element(element_id)
                    if self.selected_spell and button_instance and button_instance.is_active:
                        self.upgrade_level_scroll_offset = max(0, self.upgrade_level_scroll_offset - 1)
                        self._populate_upgrade_editor()
                elif element_id == "uplevel_scroll_down_button":
                    button_instance = self.ui_manager.get_element(element_id)
                    if self.selected_spell and button_instance and button_instance.is_active:
                        total_upgrade_levels = len(self.selected_spell.get('upgrades', {}).keys())
                        max_scroll = total_upgrade_levels - self.max_visible_upgrade_levels
                        if max_scroll < 0: max_scroll = 0
                        self.upgrade_level_scroll_offset = min(max_scroll, self.upgrade_level_scroll_offset + 1)
                        self._populate_upgrade_editor()
                # --- Existing Upgrade Editor Click Handling ---
                elif element_id.startswith("uplevel_button_"):
                    button_instance = self.ui_manager.get_element(element_id)
                    if button_instance and button_instance.on_click_data and "level_key" in button_instance.on_click_data:
                        self._handle_upgrade_level_select(button_instance.on_click_data["level_key"])
                elif element_id == "add_new_level_button": # Connect new button
                    self._handle_add_new_level()
                elif element_id == "remove_selected_level_button": # Connect new button
                    self._handle_remove_selected_level()
                elif element_id == "toggle_divergence_button": # Check if this is the correct new ID
                    button_instance = self.ui_manager.get_element(element_id)
                    if button_instance: # No need to check data, action is implicit by ID
                        self._handle_toggle_divergence()
                # Check for add_prop_button_<prop_name> clicks
                elif element_id.startswith("add_prop_button_"):
                    button_instance = self.ui_manager.get_element(element_id)
                    if button_instance and button_instance.on_click_data and \
                       button_instance.on_click_data.get("action") == "add_property":
                        prop_name = button_instance.on_click_data.get("property_name")
                        if prop_name:
                            # For now, new properties get a default value (e.g., 0 or ""). Adjust as needed.
                            default_val = "" if prop_name == "divergence_target" else 0
                            if prop_name == "description": default_val = "New Effect"
                            self._handle_add_property_to_level(prop_name, default_val)
                # Check for remove_prop_button_<level_key>_<prop_key> clicks
                elif element_id.startswith("remove_prop_button_"):
                    button_instance = self.ui_manager.get_element(element_id)
                    if button_instance and button_instance.on_click_data and \
                       button_instance.on_click_data.get("action") == "remove_property":
                        prop_name = button_instance.on_click_data.get("property_name")
                        if prop_name:
                            self._handle_remove_property_from_level(prop_name)
                elif element_id.startswith("uplevel_prop_divergence_toggle_"): # This might be old or need adjustment
                    button_instance = self.ui_manager.get_element(element_id)
                    if button_instance and button_instance.data:
                        level_key = button_instance.data["level_key"]
                        # prop_key = button_instance.data["prop_key"] # "divergence"
                        if self.selected_spell and level_key in self.selected_spell.get('upgrades',{}):
                            current_val = self.selected_spell['upgrades'][level_key].get("divergence", False)
                            self.selected_spell['upgrades'][level_key]["divergence"] = not current_val
                            self.modified = True
                            # Refresh only this button's text/color
                            button_instance.set_text(str(not current_val))
                            button_instance.color = config.YELLOW if not current_val else config.LIGHT_GRAY
                            # Or call self._handle_upgrade_level_select(level_key) to refresh whole detail panel for simplicity
                            self._handle_upgrade_level_select(level_key)


        # Handle input for active upgrade property InputBox instances
        # This is implicitly handled by UIManager if InputBox instances are correctly managed.
        # The values will be read in apply_changes.
                            
    def select_spell(self, spell_id):
        """Select a spell to edit
        
        Args:
            spell_id (str): ID of the spell to select
        """
        self.selected_spell_id = spell_id
        self.selected_spell = self.items_data.get(spell_id, {})
        # Debug prints removed for brevity in this edit, but were useful
        # print(f"[DEBUG] select_spell: Selected '{spell_id}'. Initial data: {self.selected_spell}")
        # print(f"[DEBUG] select_spell: ID of self.selected_spell: {id(self.selected_spell)}")
        # if spell_id in self.items_data:
        #     print(f"[DEBUG] select_spell: ID of self.items_data['{spell_id}']: {id(self.items_data[spell_id])}")
        
        # Update UI with the selected spell's data (main properties)
        for field_id in self.text_inputs:
            text_element = self.ui_manager.get_element(self.text_inputs[field_id])
            if text_element:
                value = self.selected_spell.get(field_id, "")
                if isinstance(text_element, InputBox): # Ensure it is an InputBox before setting text
                    text_element.set_text(str(value))
                elif isinstance(text_element, TextBox):
                    text_element.set_text(str(value))
        
        # Reset scroll offset for upgrade list
        self.upgrade_level_scroll_offset = 0
        
        # Old upgrade info population - REMOVED
        # upgrades_text = ""
        # if "upgrades" in self.selected_spell:
        #     for level, upgrade in self.selected_spell["upgrades"].items():
        #         upgrades_text += f"{level}:\n"
        #         for key, value in upgrade.items():
        #             upgrades_text += f"  {key}: {value}\n"
        # else:
        #     upgrades_text = "No upgrade information available."
        # 
        # upgrades_info = self.ui_manager.get_element("upgrades_info")
        # if upgrades_info and isinstance(upgrades_info, TextBox):
        #     upgrades_info.set_text(upgrades_text)
        
        # Clear and populate new upgrade editor UI
        self.selected_upgrade_level_key = None 
        self._clear_upgrade_editor_ui() 
        if self.selected_spell: 
             self._populate_upgrade_editor() 
        else: 
            detail_title = self.ui_manager.get_element("upgrade_detail_panel_title_text")
            if detail_title and isinstance(detail_title, TextBox):
                detail_title.set_text("Edit Level: None")
    
    def apply_changes(self):
        """Apply changes to the selected spell"""
        print(f"[DEBUG] apply_changes: Applying to '{self.selected_spell_id}'. Current self.selected_spell before changes: {self.selected_spell}")
        if not self.selected_spell_id or not self.selected_spell: # Added check for self.selected_spell
            return
        
        # Update the main spell properties from self.text_inputs
        for field_id in self.text_inputs:
            input_box_id = self.text_inputs[field_id]
            # Assuming self.text_inputs stores IDs of InputBox elements
            text_element = self.ui_manager.get_element(input_box_id) 
            if text_element and isinstance(text_element, InputBox): # Check if it's an InputBox
                value = text_element.text
                
                if field_id in ["damage", "cooldown", "projectile_speed", "radius", "tick_rate"]:
                    try:
                        if "." in value and value: # Check if value is not empty before float conversion
                            value = float(value)
                        elif value: # Check if value is not empty before int conversion
                            value = int(value)
                        else: # Handle empty string for numeric fields, maybe default to 0 or skip?
                            value = 0 # Or some other default, or None to remove if empty
                    except ValueError:
                        # Keep as string if conversion fails, or handle error
                        print(f"Warning: Could not convert '{value}' for field '{field_id}' to number. Kept as string or default.")
                        if field_id in ["damage", "radius", "tick_rate"]: value = 0
                        if field_id == "cooldown": value = 1.0
                        if field_id == "projectile_speed": value = 0

                self.selected_spell[field_id] = value
            elif text_element and isinstance(text_element, TextBox): # Should not happen if setup is correct
                 print(f"Warning: Expected InputBox for {field_id}, got TextBox. Value not read.")


        # Update upgrade properties from self.upgrade_property_inputs
        if 'upgrades' in self.selected_spell:
            for (level_key, prop_key), input_box_instance in self.upgrade_property_inputs.items():
                if level_key in self.selected_spell['upgrades'] and prop_key in self.selected_spell['upgrades'][level_key]:
                    if isinstance(input_box_instance, InputBox):
                        value_str = input_box_instance.text
                        # Type conversion (similar to main properties, needs to be robust)
                        # For simplicity, assume numeric for now, can be expanded
                        new_value = None
                        try:
                            if "." in value_str and value_str: new_value = float(value_str)
                            elif value_str: new_value = int(value_str)
                            else: new_value = 0 # Default for empty string
                        except ValueError:
                            print(f"Warning: Could not convert upgrade value '{value_str}' for {level_key}.{prop_key}. Kept as string or default.")
                            new_value = self.selected_spell['upgrades'][level_key][prop_key] # Keep old value on error

                        if new_value is not None: # Check if conversion was successful
                             self.selected_spell['upgrades'][level_key][prop_key] = new_value
        
        print(f"[DEBUG] apply_changes: self.selected_spell after field updates: {self.selected_spell}")
        # Update the items data with the modified spell
        self.items_data[self.selected_spell_id] = self.selected_spell
        print(f"[DEBUG] apply_changes: self.items_data['{self.selected_spell_id}'] after assignment: {self.items_data[self.selected_spell_id]}")
        print(f"[DEBUG] apply_changes: Full self.items_data before save: {self.items_data}")
        self.modified = True
        
        # Show confirmation message
        self.ui_manager.add_element("apply_message", TextBox(
            x=config.SCREEN_WIDTH // 2 - 100,
            y=config.SCREEN_HEIGHT - 80,
            width=200,
            height=30,
            text="Changes applied!",
            text_color=config.GREEN,
            alignment="center"
        ))
    
    def create_new_spell(self):
        """Create a new spell"""
        # Generate a unique ID
        base_id = "new_spell"
        spell_id = base_id
        counter = 1
        
        while spell_id in self.items_data:
            spell_id = f"{base_id}_{counter}"
            counter += 1
        
        # Create a basic spell template
        self.items_data[spell_id] = {
            "name": "New Spell",
            "description": "A new spell description.",
            "damage": 10,
            "cooldown": 1.0,
            "projectile_speed": 8,
            "type": "projectile",
            "upgrades": {
                "level_2": {"damage": 15, "cooldown": 0.9}
            }
        }
        
        # Update the spell list
        self.spell_list.append(spell_id)
        self.modified = True
        
        # Refresh the UI list and select the new spell
        self._rebuild_spell_list_ui()
        self.select_spell(spell_id)
    
    def delete_selected_spell(self):
        """Delete the selected spell"""
        if not self.selected_spell_id:
            return
        
        # Remove from items data and spell list
        if self.selected_spell_id in self.items_data:
            del self.items_data[self.selected_spell_id]
        if self.selected_spell_id in self.spell_list: # Check before removing
            self.spell_list.remove(self.selected_spell_id)
            self.modified = True
            
            # Clear selection
            current_selected_id = self.selected_spell_id
            self.selected_spell_id = None
            self.selected_spell = None
            
            # Refresh the UI list
            self._rebuild_spell_list_ui()

            # Clear the detail panel
            for field_id, input_box_id in self.text_inputs.items():
                input_box = self.ui_manager.get_element(input_box_id)
                if input_box and isinstance(input_box, InputBox):
                    input_box.set_text("") # Clear text
                elif input_box and isinstance(input_box, TextBox): # Fallback for safety if type is TextBox
                    input_box.set_text("")
            
            upgrades_info = self.ui_manager.get_element("upgrades_info")
            if upgrades_info and isinstance(upgrades_info, TextBox):
                upgrades_info.set_text("Select a spell to view and edit upgrade information.")
            
            # Deactivate any active input box from the deleted item
            if self.ui_manager.active_input_box:
                # Check if the active input box belonged to the deleted spell's details
                # This is a bit tricky without direct association. A simpler way:
                # If we just deleted a spell, it's safer to deactivate any active input box.
                self.ui_manager.active_input_box.is_active = False
                self.ui_manager.active_input_box = None

    def _clear_upgrade_editor_ui(self):
        """Clears dynamic UI elements from the upgrade editor (level buttons, property fields)."""
        # Remove level buttons
        buttons_to_remove = [elem_id for elem_id in self.ui_manager.elements
                             if elem_id.startswith("uplevel_button_")]
        for elem_id in buttons_to_remove:
            self.ui_manager.remove_element(elem_id)

        # Remove property fields (labels, input boxes, toggle buttons)
        # This needs to be more robust if IDs are not consistently prefixed
        # For now, we assume property input boxes are stored in self.upgrade_property_inputs
        for (level_key, prop_key), input_box_id_or_instance in list(self.upgrade_property_inputs.items()):
            # If storing IDs:
            if isinstance(input_box_id_or_instance, str):
                if self.ui_manager.get_element(input_box_id_or_instance):
                    self.ui_manager.remove_element(input_box_id_or_instance)
                # Also remove associated label and delete button if they follow a naming convention
                if self.ui_manager.get_element(f"uplevel_prop_label_{level_key}_{prop_key}"):
                    self.ui_manager.remove_element(f"uplevel_prop_label_{level_key}_{prop_key}")
                if self.ui_manager.get_element(f"uplevel_prop_delete_{level_key}_{prop_key}"): # For optional delete prop button
                     self.ui_manager.remove_element(f"uplevel_prop_delete_{level_key}_{prop_key}")
            # If storing instances (better for direct manipulation):
            # (This example assumes we transition to storing IDs for removal consistency here)

        self.upgrade_property_inputs.clear()
        
        detail_title = self.ui_manager.get_element("upgrade_detail_panel_title_text")
        if detail_title and isinstance(detail_title, TextBox):
            detail_title.set_text("Edit Level: None")


    def _populate_upgrade_editor(self):
        """Populates the Master Panel (upgrade level list) based on current spell's upgrades."""
        self._clear_upgrade_editor_ui() # Clear previous dynamic elements first

        if not self.selected_spell or 'upgrades' not in self.selected_spell:
            # Ensure scroll buttons are disabled if no spell or no upgrades
            scroll_up_button = self.ui_manager.get_element("uplevel_scroll_up_button")
            if scroll_up_button: scroll_up_button.is_active = False
            scroll_down_button = self.ui_manager.get_element("uplevel_scroll_down_button")
            if scroll_down_button: scroll_down_button.is_active = False
            return

        level_keys = sorted(self.selected_spell['upgrades'].keys())
        total_upgrade_levels = len(level_keys)

        # Bound check for scroll offset (critical)
        max_scroll = total_upgrade_levels - self.max_visible_upgrade_levels
        if max_scroll < 0:
            max_scroll = 0 # Handles cases with fewer items than can be shown
        self.upgrade_level_scroll_offset = max(0, min(self.upgrade_level_scroll_offset, max_scroll))

        # Determine the slice of keys to display
        visible_keys_end_index = self.upgrade_level_scroll_offset + self.max_visible_upgrade_levels
        visible_keys = level_keys[self.upgrade_level_scroll_offset : visible_keys_end_index]

        # Use self.master_panel_x, self.master_panel_y etc. defined in create_editor_ui
        button_height = 25
        button_spacing = 5
        # max_buttons_visible is now self.max_visible_upgrade_levels

        for i, level_key in enumerate(visible_keys):
            # Create button relative to the master_panel_x and master_panel_y
            self.ui_manager.add_element(f"uplevel_button_{level_key}", Button(
                x=self.master_panel_x + 5,
                y=self.master_panel_y + 5 + i * (button_height + button_spacing),
                width=self.master_panel_width - 10, # Padding within master panel
                height=button_height,
                text=str(level_key).replace("_", " ").title(),
                color=config.LIGHT_GRAY,
                hover_color=config.WHITE,
                text_color=config.BLACK,
                on_click_data={"level_key": level_key}
            ))
        
        # Update scroll button states
        scroll_up_button = self.ui_manager.get_element("uplevel_scroll_up_button")
        if scroll_up_button:
            scroll_up_button.is_active = self.upgrade_level_scroll_offset > 0
        
        scroll_down_button = self.ui_manager.get_element("uplevel_scroll_down_button")
        if scroll_down_button:
            scroll_down_button.is_active = self.upgrade_level_scroll_offset < max_scroll

    def _handle_upgrade_level_select(self, level_key):
        """Handles selection of an upgrade level to populate the Detail Panel."""
        self.selected_upgrade_level_key = level_key
        
        # Clear previous property UIs from Detail Panel
        # (More specific clearing than _clear_upgrade_editor_ui which clears levels too)
        prop_elements_to_remove = []
        for elem_id in self.ui_manager.elements:
            if elem_id.startswith(f"uplevel_prop_label_{self.selected_upgrade_level_key}_") or \
               elem_id.startswith(f"uplevel_prop_input_{self.selected_upgrade_level_key}_") or \
               elem_id.startswith(f"uplevel_prop_divergence_toggle_{self.selected_upgrade_level_key}"):
                prop_elements_to_remove.append(elem_id)
        for elem_id in prop_elements_to_remove:
            if self.ui_manager.get_element(elem_id): # Check if still exists
                 self.ui_manager.remove_element(elem_id)
        self.upgrade_property_inputs.clear()


        detail_title = self.ui_manager.get_element("upgrade_detail_panel_title_text")
        if detail_title and isinstance(detail_title, TextBox):
            detail_title.set_text(f"Edit Level: {str(level_key).replace('_', ' ').title()}")

        if not self.selected_spell or 'upgrades' not in self.selected_spell or \
           level_key not in self.selected_spell['upgrades']:
            return

        current_level_props = self.selected_spell['upgrades'][level_key]
        prop_y_start = self.detail_panel_y + 25 # Below detail title
        prop_spacing = 30
        prop_label_width = 100
        prop_input_width = self.detail_panel_width - prop_label_width - 20 # Accommodate label and padding
        
        prop_display_order = ["damage", "cooldown", "radius", "projectile_speed", "tick_rate"] # Add other common ones

        idx = 0
        # Display known properties first
        for prop_key in prop_display_order:
            if prop_key in current_level_props:
                value = current_level_props[prop_key]
                label_id = f"uplevel_prop_label_{level_key}_{prop_key}"
                input_id = f"uplevel_prop_input_{level_key}_{prop_key}"
                
                self.ui_manager.add_element(label_id, TextBox(
                    x=self.detail_panel_x + 5, y=prop_y_start + idx * prop_spacing,
                    width=prop_label_width, height=25, text=prop_key.title() + ":", 
                    text_color=config.WHITE, alignment="left"
                ))
                input_box = InputBox(
                    x=self.detail_panel_x + 5 + prop_label_width, y=prop_y_start + idx * prop_spacing,
                    width=prop_input_width, height=25, text=str(value),
                    text_color=config.BLACK, background_color=config.WHITE, border_color=config.BLACK
                )
                self.ui_manager.add_element(input_id, input_box)
                self.upgrade_property_inputs[(level_key, prop_key)] = input_box # Store instance
                idx +=1

        # Display other properties (not in known order)
        for prop_key, value in current_level_props.items():
            if prop_key in prop_display_order or prop_key == "divergence": # Already handled or will be
                continue
            
            label_id = f"uplevel_prop_label_{level_key}_{prop_key}"
            input_id = f"uplevel_prop_input_{level_key}_{prop_key}"
            self.ui_manager.add_element(label_id, TextBox(
                x=self.detail_panel_x + 5, y=prop_y_start + idx * prop_spacing,
                width=prop_label_width, height=25, text=prop_key.title() + ":", 
                text_color=config.WHITE, alignment="left"
            ))
            input_box = InputBox(
                x=self.detail_panel_x + 5 + prop_label_width, y=prop_y_start + idx * prop_spacing,
                width=prop_input_width, height=25, text=str(value),
                text_color=config.BLACK, background_color=config.WHITE, border_color=config.BLACK
            )
            self.ui_manager.add_element(input_id, input_box)
            self.upgrade_property_inputs[(level_key, prop_key)] = input_box # Store instance
            idx +=1
            
        # Handle divergence specifically as a toggle button
        if "divergence" in current_level_props:
            div_button_id = f"uplevel_prop_divergence_toggle_{level_key}"
            self.ui_manager.add_element(f"uplevel_prop_label_{level_key}_divergence", TextBox(
                 x=self.detail_panel_x + 5, y=prop_y_start + idx * prop_spacing,
                 width=prop_label_width, height=25, text="Divergence:", 
                 text_color=config.WHITE, alignment="left"
            ))
            div_button = Button(
                x=self.detail_panel_x + 5 + prop_label_width, y=prop_y_start + idx * prop_spacing,
                width=prop_input_width, height=25,
                text=str(current_level_props.get("divergence", False)), # Default to False if key somehow missing after check
                color=config.YELLOW if current_level_props.get("divergence") else config.LIGHT_GRAY,
                text_color=config.BLACK,
                on_click_data={"level_key": level_key, "prop_key": "divergence"}
            )
            self.ui_manager.add_element(div_button_id, div_button)
            # No need to add to self.upgrade_property_inputs as it's a button not an InputBox for apply_changes
            idx +=1

    def _handle_add_new_level(self):
        """Handles adding a new upgrade level to the current spell."""
        if not self.selected_spell:
            print("No spell selected to add upgrade level to.") # Or show UI message
            return

        if 'upgrades' not in self.selected_spell:
            self.selected_spell['upgrades'] = {}

        current_upgrades = self.selected_spell['upgrades']
        i = 1
        new_level_key = f"level_{i}"
        while new_level_key in current_upgrades:
            i += 1
            new_level_key = f"level_{i}"
        
        current_upgrades[new_level_key] = {} # Add new level with empty properties
        self.modified = True
        
        self._populate_upgrade_editor() # Refresh the list of level buttons
        # Optionally, automatically select the new level for editing:
        self._handle_upgrade_level_select(new_level_key)
        print(f"Added new upgrade level: {new_level_key}")

    def _handle_remove_selected_level(self):
        """Handles removing the currently selected upgrade level from the spell."""
        if not self.selected_spell or not self.selected_upgrade_level_key:
            print("No spell or upgrade level selected to remove.") # Or show UI message
            return

        current_upgrades = self.selected_spell.get('upgrades', {})
        if self.selected_upgrade_level_key in current_upgrades:
            del current_upgrades[self.selected_upgrade_level_key]
            self.modified = True
            
            removed_key = self.selected_upgrade_level_key
            self.selected_upgrade_level_key = None
            
            # _clear_upgrade_editor_ui() is called by _populate_upgrade_editor and _handle_upgrade_level_select
            # We need to ensure the detail panel for the (now deleted) level is cleared.
            # Simplest is to clear all dynamic upgrade UI and repopulate levels.
            self._clear_upgrade_editor_ui() # Clears detail panel and level buttons
            self._populate_upgrade_editor() # Repopulates level buttons
            # The detail panel title will be reset by _clear_upgrade_editor_ui

            print(f"Removed upgrade level: {removed_key}")
        else:
            print(f"Could not find level {self.selected_upgrade_level_key} to remove.")

    def _handle_add_property_to_level(self, property_name, default_value=0):
        """Adds a property to the currently selected upgrade level if it doesn't exist."""
        if not self.selected_spell or not self.selected_upgrade_level_key:
            print("No spell or upgrade level selected to add property to.")
            return

        if 'upgrades' not in self.selected_spell or \
           self.selected_upgrade_level_key not in self.selected_spell['upgrades']:
            print(f"Selected upgrade level {self.selected_upgrade_level_key} not found in spell data.")
            return

        level_props = self.selected_spell['upgrades'][self.selected_upgrade_level_key]
        
        if property_name not in level_props:
            level_props[property_name] = default_value
            self.modified = True
            self._handle_upgrade_level_select(self.selected_upgrade_level_key) # Refresh detail panel
            print(f"Added property '{property_name}' to level '{self.selected_upgrade_level_key}'.")
        else:
            print(f"Property '{property_name}' already exists in level '{self.selected_upgrade_level_key}'.")

    def _handle_remove_property_from_level(self, property_name):
        """Removes a property from the currently selected upgrade level."""
        if not self.selected_spell or not self.selected_upgrade_level_key:
            print("No spell or upgrade level selected to remove property from.")
            return

        if 'upgrades' not in self.selected_spell or \
           self.selected_upgrade_level_key not in self.selected_spell['upgrades']:
            print(f"Selected upgrade level {self.selected_upgrade_level_key} not found in spell data.")
            return

        level_props = self.selected_spell['upgrades'][self.selected_upgrade_level_key]
        
        if property_name in level_props:
            del level_props[property_name]
            # If the removed property was divergence-related, ensure consistency
            if property_name == 'divergence_target' and 'is_divergence' in level_props:
                level_props['is_divergence'] = False # Or remove it, depends on desired behavior
            elif property_name == 'is_divergence' and 'divergence_target' in level_props:
                del level_props['divergence_target']

            self.modified = True
            self._handle_upgrade_level_select(self.selected_upgrade_level_key) # Refresh detail panel
            print(f"Removed property '{property_name}' from level '{self.selected_upgrade_level_key}'.")
        else:
            print(f"Property '{property_name}' not found in level '{self.selected_upgrade_level_key}'.")

    def _handle_toggle_divergence(self):
        """Toggles the 'is_divergence' status for the selected upgrade level."""
        if not self.selected_spell or not self.selected_upgrade_level_key:
            print("No spell or upgrade level selected to toggle divergence.")
            return

        if 'upgrades' not in self.selected_spell or \
           self.selected_upgrade_level_key not in self.selected_spell['upgrades']:
            print(f"Selected upgrade level {self.selected_upgrade_level_key} not found for divergence toggle.")
            return
        
        level_props = self.selected_spell['upgrades'][self.selected_upgrade_level_key]
        
        current_status = level_props.get('is_divergence', False)
        level_props['is_divergence'] = not current_status
        self.modified = True

        if level_props['is_divergence']:
            # If it becomes a divergence, ensure 'divergence_target' exists or add it
            if 'divergence_target' not in level_props:
                level_props['divergence_target'] = "" # Default empty string, user must fill
        else:
            # If it's no longer a divergence, remove 'divergence_target'
            if 'divergence_target' in level_props:
                del level_props['divergence_target']

        self._handle_upgrade_level_select(self.selected_upgrade_level_key) # Refresh detail panel
        status_text = "enabled" if level_props['is_divergence'] else "disabled"
        print(f"Divergence {status_text} for level '{self.selected_upgrade_level_key}'.")

    def _populate_upgrade_detail_panel(self, level_key):
        """Populate the detail panel with properties of the selected upgrade level."""
        # Clear existing property input fields and buttons for properties
        for prop_input_id in list(self.upgrade_property_inputs.keys()): # Iterate over a copy for safe deletion
            self.ui_manager.remove_element(prop_input_id) # Remove InputBox
            self.ui_manager.remove_element(prop_input_id + "_label") # Remove Label
        self.upgrade_property_inputs.clear()

        # Remove old "add property" / "remove property" / "toggle divergence" buttons if they exist from a previous selection
        self.ui_manager.remove_element("add_property_dropdown") # Assuming we'll make a dropdown-like thing
        self.ui_manager.remove_element("add_selected_property_button") 
        self.ui_manager.remove_element("remove_selected_property_button") # We will re-add later if a prop is selected
        self.ui_manager.remove_element("toggle_divergence_button")
        self.ui_manager.remove_element("current_property_label") # A label to show which property is selected for removal
        self.ui_manager.remove_element("select_property_for_removal_dropdown")


        if not self.selected_spell or 'upgrades' not in self.selected_spell or \
           level_key not in self.selected_spell['upgrades']:
            return

        level_props = self.selected_spell['upgrades'].get(level_key, {})
        
        current_y = self.detail_panel_y + 10
        input_width = self.detail_panel_width - 140 # Space for label
        input_height = 30
        padding = 5

        # --- Add Property Dropdown and Button ---
        # For simplicity, we'll use a series of buttons for predefined properties for now
        # A true dropdown would require a more complex UI element
        add_prop_x = self.detail_panel_x + 10
        
        self.ui_manager.add_element("add_prop_title", TextBox(
            x=add_prop_x, y=current_y, width=self.detail_panel_width - 20, height=25,
            text="Add Property:", text_color=config.WHITE, background_color=None, font_size=18
        ))
        current_y += 30

        prop_button_width = (self.detail_panel_width - 20 - (len(config.PREDEFINED_UPGRADE_PROPERTIES) -1) * padding ) / len(config.PREDEFINED_UPGRADE_PROPERTIES)
        prop_button_width = max(50, prop_button_width) # Ensure some minimum width

        for i, prop_name in enumerate(config.PREDEFINED_UPGRADE_PROPERTIES):
            self.ui_manager.add_element(f"add_prop_button_{prop_name}", Button(
                x=add_prop_x + i * (prop_button_width + padding),
                y=current_y,
                width=prop_button_width,
                height=30,
                text=prop_name,
                on_click_data={"action": "add_property", "property_name": prop_name}
            ))
        current_y += 35 + padding

        # --- Toggle Divergence Button ---
        is_divergence = level_props.get('is_divergence', False)
        toggle_text = "Divergence: ON" if is_divergence else "Divergence: OFF"
        toggle_color = config.GREEN if is_divergence else config.RED
        self.ui_manager.add_element("toggle_divergence_button", Button(
            x=add_prop_x,
            y=current_y,
            width=self.detail_panel_width - 20,
            height=35,
            text=toggle_text,
            color=toggle_color,
            hover_color=(min(255,toggle_color[0]+30), min(255,toggle_color[1]+30), min(255,toggle_color[2]+30) ),
            on_click_data={"action": "toggle_divergence"}
        ))
        current_y += 40 + padding
        
        # --- Divider ---
        self.ui_manager.add_element("prop_divider", TextBox(
            x=self.detail_panel_x + 5, y=current_y, width=self.detail_panel_width -10, height=2,
            background_color=config.LIGHT_GREY
        ))
        current_y += 10 + padding

        # --- Existing Properties List and Remove Buttons ---
        self.ui_manager.add_element("current_props_title", TextBox(
            x=add_prop_x, y=current_y, width=self.detail_panel_width - 20, height=25,
            text="Current Properties:", text_color=config.WHITE, background_color=None, font_size=18
        ))
        current_y += 30

        for prop_key, prop_value in level_props.items():
            # Skip 'is_divergence' and 'divergence_target' if 'is_divergence' is false for cleaner UI
            if prop_key == 'divergence_target' and not level_props.get('is_divergence', False):
                continue
            if prop_key == 'is_divergence': # This is handled by the toggle button
                continue

            self.ui_manager.add_element(f"uplevel_prop_label_{level_key}_{prop_key}", TextBox(
                x=self.detail_panel_x + 10,
                y=current_y,
                width=120,
                height=input_height,
                text=f"{prop_key}:",
                text_color=config.WHITE,
                background_color=None
            ))
            
            prop_input_id = f"uplevel_prop_input_{level_key}_{prop_key}"
            input_box = InputBox(
                x=self.detail_panel_x + 130,
                y=current_y,
                width=input_width - 50, # Make space for remove button
                height=input_height,
                text=str(prop_value),
                data={"level_key": level_key, "property_key": prop_key}
            )
            self.ui_manager.add_element(prop_input_id, input_box)
            self.upgrade_property_inputs[(level_key, prop_key)] = prop_input_id

            self.ui_manager.add_element(f"remove_prop_button_{level_key}_{prop_key}", Button(
                x=self.detail_panel_x + 130 + input_width - 45,
                y=current_y,
                width=40,
                height=input_height,
                text="X",
                color=config.RED,
                hover_color=(255,100,100),
                on_click_data={"action": "remove_property", "property_name": prop_key}
            ))
            current_y += input_height + padding
        
        # Ensure the detail panel background covers all dynamic elements
        self.ui_manager.remove_element("upgrade_detail_bg") # Remove if exists
        self.ui_manager.add_element("upgrade_detail_bg", TextBox(
            x=self.detail_panel_x, y=self.detail_panel_y,
            width=self.detail_panel_width, height=max(self.detail_panel_height, current_y - self.detail_panel_y + 10),
            background_color=(60, 60, 80), border_color=config.BLACK
        ))


class RelicEditorState(BaseEditorState):
    """Relic editor state"""
    
    def __init__(self, game_manager):
        """Initialize the relic editor state"""
        super().__init__(game_manager, "RELIC EDITOR")
        self.relic_list = []
        self.selected_relic_id = None
        self.selected_relic_data = {} 
        self.detail_text_inputs = {} 
        self.effects_inputs = {} # For managing effects K-V pair UIs
        self.active_ability_inputs = {} # For active ability main fields
        self.active_ability_effects_inputs = {} # For active ability effects K-V UIs
        # Scroll variables for relic list (can be adapted from SpellEditorState if needed)
        self.relic_list_scroll_offset = 0
        self.max_visible_relics = 0
        self.relic_list_rect = None # For mouse wheel detection on the list area
    
    def load_data(self):
        """Load relic data"""
        self.items_data = self.data_handler.load_relics()
        if not self.items_data:
            DataHandler.create_default_files()
            self.items_data = self.data_handler.load_relics()
        self.relic_list = list(self.items_data.keys())
        print(f"Relic Editor: Loaded {len(self.relic_list)} relics: {self.relic_list}")
    
    def save_data(self):
        """Save relic data"""
        if not self.items_data:
            print("Relic Editor: No data to save.")
            return
        success = self.data_handler.save_json(self.items_data, config.RELICS_DATA)
        if success:
            self.modified = False
            # Simple feedback, could be a timed message UI element
            print("Relic data saved successfully.")
            self.ui_manager.add_element("save_message_relic", TextBox(
                x=config.SCREEN_WIDTH // 2 - 100, y=config.SCREEN_HEIGHT - 30,
                width=200, height=25, text="Relics Saved!",
                text_color=config.GREEN, alignment="center", background_color=(50,50,70) # Match bg
            ), temp_message_duration=2.0) # UIManager would need to handle temp messages
        else:
            print("ERROR: Failed to save relic data.")

    def create_editor_ui(self):
        """Create relic editor UI (Phase 1: List, Main Props, New/Delete/Apply)"""
        # self.ui_manager.elements.clear() # Clear elements from BaseEditorState.enter() if needed
        # super().enter() # Re-add common elements like title, save, back
        
        # Left panel - Relic list
        list_bg_width = 250
        list_bg_height = config.SCREEN_HEIGHT - 200 # Available height for list + buttons
        list_bg_x = 50
        list_bg_y = 100

        self.ui_manager.add_element("relic_list_main_bg", TextBox(
             x=list_bg_x, y=list_bg_y, width=list_bg_width, height=list_bg_height,
             background_color=(80, 80, 100), border_color=config.BLACK
        ))
        self.ui_manager.add_element("relic_list_title", TextBox(
            x=list_bg_x, y=list_bg_y + 5, width=list_bg_width, height=30,
            text="Relics", text_color=config.WHITE, alignment="center", font_size=24
        ))

        # Area for relic names (scrollable list part)
        self.relic_list_rect = pygame.Rect(list_bg_x + 5, list_bg_y + 40, list_bg_width - 10, list_bg_height - 90)
        # Calculate max_visible_relics (button height 30, spacing 5)
        if self.relic_list_rect.height > 0:
            self.max_visible_relics = self.relic_list_rect.height // 35
        else:
            self.max_visible_relics = 0

        # New Relic and Delete Relic buttons (below the list area)
        new_del_button_y = list_bg_y + list_bg_height - 45 # Position at bottom of list_bg
        self.ui_manager.add_element("new_relic_button", Button(
            x=list_bg_x + 5, y=new_del_button_y, width=(list_bg_width // 2) - 10, height=40,
            text="New", color=config.GREEN, text_color=config.BLACK
        ))
        self.ui_manager.add_element("delete_relic_button", Button(
            x=list_bg_x + (list_bg_width // 2) + 5, y=new_del_button_y, width=(list_bg_width // 2) - 10, height=40,
            text="Delete", color=config.RED, text_color=config.WHITE
        ))

        # Right panel - Relic details
        detail_x = list_bg_x + list_bg_width + 30
        detail_y = 100
        detail_width = config.SCREEN_WIDTH - detail_x - 30 
        detail_height = config.SCREEN_HEIGHT - detail_y - 80 # Space for save/back

        self.ui_manager.add_element("relic_detail_bg", TextBox(
            x=detail_x, y=detail_y, width=detail_width, height=detail_height,
            background_color=(100, 100, 120), border_color=config.BLACK
        ))
        self.ui_manager.add_element("relic_detail_title_text", TextBox(
            x=detail_x, y=detail_y + 5, width=detail_width, height=30,
            text="Relic Details: (Select a Relic)", text_color=config.WHITE, alignment="center", font_size=24
        ))

        # Main property input fields
        field_x_start = detail_x + 20
        field_y_current = detail_y + 45
        label_width = 100
        input_box_width = detail_width - label_width - 45 # padding
        input_height = 30
        field_spacing = 10 # Vertical spacing between field (label+input) end and next label start

        main_props_config = [
            ("name", "Name:", 1), # field_id, label_text, height_multiplier_for_input
            ("description", "Description:", 2),
            ("rarity", "Rarity:", 1),
            ("sprite_path", "Sprite Path:", 1)
        ]
        self.detail_text_inputs.clear()

        for prop_id, prop_label, height_multiplier in main_props_config:
            actual_input_height = input_height * height_multiplier
            self.ui_manager.add_element(f"relic_prop_label_{prop_id}", TextBox(
                x=field_x_start, y=field_y_current, width=label_width, height=actual_input_height,
                text=prop_label, text_color=config.WHITE, alignment="left"
            ))
            input_box_id = f"relic_prop_input_{prop_id}"
            self.ui_manager.add_element(input_box_id, InputBox(
                x=field_x_start + label_width + 5, y=field_y_current,
                width=input_box_width, height=actual_input_height,
                text="", text_color=config.BLACK, background_color=config.WHITE
            ))
            self.detail_text_inputs[prop_id] = input_box_id
            field_y_current += actual_input_height + field_spacing

        # Apply Changes button
        self.ui_manager.add_element("apply_relic_changes_button", Button(
            x=detail_x + detail_width - 170, y=detail_y + detail_height - 50,
            width=150, height=40, text="Apply Changes",
            color=config.BLUE, text_color=config.WHITE
        ))
        
        self._rebuild_relic_list_ui()
        self.select_relic(None) # Ensure details are initially blank

    def _rebuild_relic_list_ui(self):
        buttons_to_remove = [elem_id for elem_id in self.ui_manager.elements if elem_id.startswith("relic_list_item_button_")]
        for elem_id in buttons_to_remove:
            self.ui_manager.remove_element(elem_id)
        
        if not self.relic_list_rect: return # Should be set in create_editor_ui

        list_item_x = self.relic_list_rect.x
        list_item_y_start = self.relic_list_rect.y
        button_width = self.relic_list_rect.width
        button_height = 30
        button_spacing = 5
        
        # TODO: Implement scroll offset logic for self.relic_list if adapting from SpellEditorState
        # For now, display all visible based on self.max_visible_relics
        visible_relic_ids = self.relic_list[self.relic_list_scroll_offset : self.relic_list_scroll_offset + self.max_visible_relics]

        for i, relic_id in enumerate(visible_relic_ids):
            relic_name = self.items_data.get(relic_id, {}).get("name", relic_id)
            self.ui_manager.add_element(f"relic_list_item_button_{relic_id}", Button(
                x=list_item_x, y=list_item_y_start + i * (button_height + button_spacing),
                width=button_width, height=button_height,
                text=relic_name, color=config.GRAY, text_color=config.BLACK,
                on_click_data={"relic_id": relic_id} # Store relic_id for click handler
            ))
        # TODO: Update scroll up/down button active states if implemented

    def select_relic(self, relic_id):
        self.selected_relic_id = relic_id
        detail_title_text = "Relic Details: (Select a Relic)"
        if relic_id:
            self.selected_relic_data = self.items_data.get(relic_id, {})
            detail_title_text = f"Relic Details: {self.selected_relic_data.get('name', relic_id)}"
        else:
            self.selected_relic_data = {}
        
        title_element = self.ui_manager.get_element("relic_detail_title_text")
        if title_element and isinstance(title_element, TextBox):
            title_element.set_text(detail_title_text)

        for prop_id, input_box_id in self.detail_text_inputs.items():
            input_box = self.ui_manager.get_element(input_box_id)
            if input_box and isinstance(input_box, InputBox):
                value = self.selected_relic_data.get(prop_id, "")
                input_box.set_text(str(value))
        
        # TODO: Clear and populate effects UI and active ability UI here
        # self._populate_effects_ui()
        # self._populate_active_ability_ui()

    def apply_changes(self):
        if not self.selected_relic_id:
            print("No relic selected.")
            return

        current_data = self.items_data.get(self.selected_relic_id, {})
        updated_data = current_data.copy()
        changes_made = False

        for prop_id, input_box_id in self.detail_text_inputs.items():
            input_box = self.ui_manager.get_element(input_box_id)
            if input_box and isinstance(input_box, InputBox):
                new_value_str = input_box.text
                # Basic type handling, extend as needed
                original_value = updated_data.get(prop_id)
                # For now, all main props are strings, no conversion needed yet
                if original_value != new_value_str:
                    updated_data[prop_id] = new_value_str
                    changes_made = True
        
        # TODO: Apply changes from effects and active ability UI

        if changes_made:
            self.items_data[self.selected_relic_id] = updated_data
            self.selected_relic_data = updated_data # Keep current view consistent
            self.modified = True
            print(f"Applied changes to {self.selected_relic_id}")
            if "name" in self.detail_text_inputs and updated_data.get("name") != current_data.get("name"):
                self._rebuild_relic_list_ui() # Refresh list if name changed
        else:
            print("No changes detected to apply.")

    def create_new_relic(self):
        base_id = "new_relic"
        counter = 1
        new_id = f"{base_id}_{counter}"
        while new_id in self.items_data:
            counter += 1
            new_id = f"{base_id}_{counter}"
        
        self.items_data[new_id] = {
            "name": f"New Relic {counter}",
            "description": "A brand new powerful relic!",
            "rarity": "common",
            "sprite_path": "assets/sprites/items/default_relic.png",
            "effects": {}
        }
        self.relic_list.append(new_id)
        self.modified = True
        self._rebuild_relic_list_ui()
        self.select_relic(new_id)
        print(f"Created new relic: {new_id}")

    def delete_selected_relic(self):
        if not self.selected_relic_id:
            print("No relic selected to delete.")
            return
        
        # Remove from items data and spell list
        if self.selected_relic_id in self.items_data:
            del self.items_data[self.selected_relic_id]
        if self.selected_relic_id in self.relic_list: # Check before removing
            self.relic_list.remove(self.selected_relic_id)
            self.modified = True
            
            # Clear selection
            current_selected_id = self.selected_relic_id
            self.selected_relic_id = None
            self.selected_relic_data = None
            
            # Refresh the UI list
            self._rebuild_relic_list_ui()

            # Clear the detail panel
            for field_id, input_box_id in self.detail_text_inputs.items():
                input_box = self.ui_manager.get_element(input_box_id)
                if input_box and isinstance(input_box, InputBox):
                    input_box.set_text("") # Clear text
                elif input_box and isinstance(input_box, TextBox): # Fallback for safety if type is TextBox
                    input_box.set_text("")
            
            upgrades_info = self.ui_manager.get_element("upgrades_info")
            if upgrades_info and isinstance(upgrades_info, TextBox):
                upgrades_info.set_text("Select a relic to view and edit upgrade information.")
            
            # Deactivate any active input box from the deleted item
            if self.ui_manager.active_input_box:
                # Check if the active input box belonged to the deleted relic's details
                # This is a bit tricky without direct association. A simpler way:
                # If we just deleted a relic, it's safer to deactivate any active input box.
                self.ui_manager.active_input_box.is_active = False
                self.ui_manager.active_input_box = None

    def update(self, dt):
        super().update(dt) # Handles UIManager, Back, Save

        # Mouse wheel for relic list (TODO: adapt from SpellEditorState if scrolling is added)
        # if self.relic_list_rect and self.relic_list_rect.collidepoint(pygame.mouse.get_pos()):
        #     for event in self.current_events:
        #         if event.type == pygame.MOUSEWHEEL:
        #             # ... scroll logic ...
        #             self._rebuild_relic_list_ui()

        for element_id, was_clicked in self.last_clicked_elements.items():
            if was_clicked:
                if element_id.startswith("relic_list_item_button_"):
                    button = self.ui_manager.get_element(element_id)
                    if button and button.on_click_data and "relic_id" in button.on_click_data:
                        self.select_relic(button.on_click_data["relic_id"])
                elif element_id == "new_relic_button":
                    self.create_new_relic()
                elif element_id == "delete_relic_button":
                    self.delete_selected_relic()
                elif element_id == "apply_relic_changes_button":
                    self.apply_changes()
                # TODO: Handle clicks for adding/removing effects/active abilities

class EnemyEditorState(BaseEditorState):
    """Enemy editor state"""
    
    def __init__(self, game_manager):
        """Initialize the enemy editor state"""
        super().__init__(game_manager, "ENEMY EDITOR")
        self.enemy_list = []
        self.selected_enemy_id = None
        self.selected_enemy_data = {} 
        self.detail_text_inputs = {} 
        self.enemy_list_scroll_offset = 0
        self.max_visible_enemies = 0 # Placeholder, will be calculated
        self.enemy_list_rect = None # For mouse wheel detection
    
    def load_data(self):
        """Load enemy data"""
        self.items_data = self.data_handler.load_enemies()
        if not self.items_data: # If file doesn't exist or is empty
            DataHandler.create_default_files() # Create defaults if they don't exist
            self.items_data = self.data_handler.load_enemies() # Try loading again
        self.enemy_list = list(self.items_data.keys())
        print(f"Enemy Editor: Loaded {len(self.enemy_list)} enemies.")
            
    def save_data(self):
        """Save enemy data"""
        if not self.items_data:
            print("Enemy Editor: No data to save.")
            # Potentially show a UI message: "No data to save"
            return

        success = self.data_handler.save_json(self.items_data, config.ENEMIES_DATA)
        if success:
            self.modified = False
            print("Enemy data saved successfully.")
            # Use UIManager to show a temporary message if available
            self.ui_manager.add_element("save_message_enemy", TextBox(
                x=config.SCREEN_WIDTH // 2 - 100, y=config.SCREEN_HEIGHT - 30,
                width=200, height=25, text="Enemies Saved!",
                text_color=config.GREEN, alignment="center", background_color=(50,50,70) 
            ), temp_message_duration=2.0) 
        else:
            print("ERROR: Failed to save enemy data.")
            # Show an error message via UI
            self.ui_manager.add_element("save_error_enemy", TextBox(
                x=config.SCREEN_WIDTH // 2 - 100, y=config.SCREEN_HEIGHT - 30,
                width=200, height=25, text="Save Failed!",
                text_color=config.RED, alignment="center", background_color=(50,50,70) 
            ), temp_message_duration=2.0)

    def create_editor_ui(self):
        """Create enemy editor UI"""
        # Left panel - Enemy list
        list_bg_width = 250
        list_bg_height = config.SCREEN_HEIGHT - 200 # Available height for list + buttons
        list_bg_x = 50
        list_bg_y = 100

        self.ui_manager.add_element("enemy_list_main_bg", TextBox(
             x=list_bg_x, y=list_bg_y, width=list_bg_width, height=list_bg_height,
             background_color=(80, 80, 100), border_color=config.BLACK
        ))
        self.ui_manager.add_element("enemy_list_title", TextBox(
            x=list_bg_x, y=list_bg_y + 5, width=list_bg_width, height=30,
            text="Enemies", text_color=config.WHITE, alignment="center", font_size=24
        ))

        # Area for enemy names (scrollable list part)
        self.enemy_list_rect = pygame.Rect(list_bg_x + 5, list_bg_y + 40, list_bg_width - 10, list_bg_height - 90)
        if self.enemy_list_rect.height > 0:
            self.max_visible_enemies = self.enemy_list_rect.height // 35 # (30 for button, 5 for spacing)
        else:
            self.max_visible_enemies = 0

        # New Enemy and Delete Enemy buttons
        new_del_button_y = list_bg_y + list_bg_height - 45 
        self.ui_manager.add_element("new_enemy_button", Button(
            x=list_bg_x + 5, y=new_del_button_y, width=(list_bg_width // 2) - 10, height=40,
            text="New", color=config.GREEN, text_color=config.BLACK
        ))
        self.ui_manager.add_element("delete_enemy_button", Button(
            x=list_bg_x + (list_bg_width // 2) + 5, y=new_del_button_y, width=(list_bg_width // 2) - 10, height=40,
            text="Delete", color=config.RED, text_color=config.WHITE
        ))

        # Right panel - Enemy details
        detail_x = list_bg_x + list_bg_width + 30
        detail_y = 100
        detail_width = config.SCREEN_WIDTH - detail_x - 30 
        detail_height = config.SCREEN_HEIGHT - detail_y - 80 

        self.ui_manager.add_element("enemy_detail_bg", TextBox(
            x=detail_x, y=detail_y, width=detail_width, height=detail_height,
            background_color=(100, 100, 120), border_color=config.BLACK
        ))
        self.ui_manager.add_element("enemy_detail_title_text", TextBox(
            x=detail_x, y=detail_y + 5, width=detail_width, height=30,
            text="Enemy Details: (Select an Enemy)", text_color=config.WHITE, alignment="center", font_size=24
        ))

        # Main property input fields
        field_x_start = detail_x + 20
        field_y_current = detail_y + 45
        label_width = 120 # Increased width for longer labels
        input_box_width = detail_width - label_width - 45 
        input_height = 30
        field_spacing = 10 

        enemy_props_config = [
            ("name", "Name:"),
            ("health", "Health:"),
            ("damage", "Damage:"),
            ("speed", "Speed:"),
            ("xp_reward", "XP Reward:"),
            ("sprite_sheet", "Sprite Sheet:"),
            ("sprite_rows", "Sprite Rows:"),
            ("sprite_columns", "Sprite Columns:")
        ]
        self.detail_text_inputs.clear()

        for prop_id, prop_label in enemy_props_config:
            self.ui_manager.add_element(f"enemy_prop_label_{prop_id}", TextBox(
                x=field_x_start, y=field_y_current, width=label_width, height=input_height,
                text=prop_label, text_color=config.WHITE, alignment="left"
            ))
            input_box_id = f"enemy_prop_input_{prop_id}"
            self.ui_manager.add_element(input_box_id, InputBox(
                x=field_x_start + label_width + 5, y=field_y_current,
                width=input_box_width, height=input_height,
                text="", text_color=config.BLACK, background_color=config.WHITE
            ))
            self.detail_text_inputs[prop_id] = input_box_id
            field_y_current += input_height + field_spacing

        # Apply Changes button
        self.ui_manager.add_element("apply_enemy_changes_button", Button(
            x=detail_x + detail_width - 170, y=detail_y + detail_height - 50,
            width=150, height=40, text="Apply Changes",
            color=config.BLUE, text_color=config.WHITE
        ))
        
        self._rebuild_enemy_list_ui()
        self.select_enemy(None)

    def _rebuild_enemy_list_ui(self):
        buttons_to_remove = [elem_id for elem_id in self.ui_manager.elements if elem_id.startswith("enemy_list_item_button_")]
        for elem_id in buttons_to_remove:
            if self.ui_manager.get_element(elem_id): # Check if exists before removing
                 self.ui_manager.remove_element(elem_id)
        
        if not self.enemy_list_rect: return

        list_item_x = self.enemy_list_rect.x
        list_item_y_start = self.enemy_list_rect.y
        button_width = self.enemy_list_rect.width
        button_height = 30
        button_spacing = 5
        
        # Placeholder: Scrolling for enemy list will be Phase 2
        # For now, display all visible based on self.max_visible_enemies
        visible_enemy_ids = self.enemy_list[self.enemy_list_scroll_offset : self.enemy_list_scroll_offset + self.max_visible_enemies]
        if not visible_enemy_ids and self.enemy_list: # If offset is too high, show first page
             visible_enemy_ids = self.enemy_list[0 : self.max_visible_enemies]


        for i, enemy_id in enumerate(visible_enemy_ids):
            enemy_name = self.items_data.get(enemy_id, {}).get("name", enemy_id)
            self.ui_manager.add_element(f"enemy_list_item_button_{enemy_id}", Button(
                x=list_item_x, y=list_item_y_start + i * (button_height + button_spacing),
                width=button_width, height=button_height,
                text=enemy_name, color=config.GRAY, text_color=config.BLACK,
                on_click_data={"enemy_id": enemy_id} 
            ))

    def select_enemy(self, enemy_id):
        self.selected_enemy_id = enemy_id
        detail_title_text = "Enemy Details: (Select an Enemy)"
        if enemy_id and enemy_id in self.items_data:
            self.selected_enemy_data = self.items_data.get(enemy_id, {}).copy() # Important: work with a copy
            detail_title_text = f"Enemy Details: {self.selected_enemy_data.get('name', enemy_id)}"
        else:
            self.selected_enemy_id = None # Ensure it's None if enemy_id is invalid
            self.selected_enemy_data = {}
        
        title_element = self.ui_manager.get_element("enemy_detail_title_text")
        if title_element and isinstance(title_element, TextBox):
            title_element.set_text(detail_title_text)

        for prop_id, input_box_id in self.detail_text_inputs.items():
            input_box = self.ui_manager.get_element(input_box_id)
            if input_box and isinstance(input_box, InputBox):
                value = self.selected_enemy_data.get(prop_id, "")
                input_box.set_text(str(value))
                
    def _parse_value(self, value_str, target_type):
        try:
            if target_type == int:
                return int(value_str)
            elif target_type == float:
                return float(value_str)
            return value_str # Default to string
        except ValueError:
            print(f"Warning: Could not convert '{value_str}' to {target_type}. Returning 0 or original string.")
            if target_type in [int, float]:
                return 0
            return value_str


    def apply_changes(self):
        if not self.selected_enemy_id:
            print("No enemy selected to apply changes to.")
            # Show UI message: "No enemy selected"
            return

        if self.selected_enemy_id not in self.items_data:
            print(f"Error: Selected enemy ID '{self.selected_enemy_id}' not found in items_data.")
            return

        original_data = self.items_data[self.selected_enemy_id]
        updated_data = self.selected_enemy_data.copy() # Work on the copy from select_enemy
        changes_made = False

        field_types = {
            "name": str, "health": float, "damage": float, "speed": float,
            "xp_reward": int, "sprite_sheet": str, "sprite_rows": int, "sprite_columns": int
        }

        for prop_id, input_box_id in self.detail_text_inputs.items():
            input_box = self.ui_manager.get_element(input_box_id)
            if input_box and isinstance(input_box, InputBox):
                new_value_str = input_box.text
                target_type = field_types.get(prop_id, str)
                parsed_value = self._parse_value(new_value_str, target_type)

                if prop_id not in updated_data or updated_data[prop_id] != parsed_value:
                    updated_data[prop_id] = parsed_value
                    changes_made = True
        
        if changes_made:
            self.items_data[self.selected_enemy_id] = updated_data
            self.selected_enemy_data = updated_data.copy() # Update the state's copy too
            self.modified = True
            print(f"Applied changes to enemy: {self.selected_enemy_id}")
            self.ui_manager.add_element("apply_changes_enemy_msg", TextBox(
                 x=config.SCREEN_WIDTH // 2 - 100, y=config.SCREEN_HEIGHT - 60, # Adjust Y
                 width=200, height=25, text="Changes Applied!",
                 text_color=config.GREEN, alignment="center", background_color=(50,50,70)
            ), temp_message_duration=2.0)
            
            # Refresh list if name changed
            if original_data.get("name") != updated_data.get("name"):
                self._rebuild_enemy_list_ui()
        else:
            print("No changes detected for the selected enemy.")
            self.ui_manager.add_element("no_changes_enemy_msg", TextBox(
                 x=config.SCREEN_WIDTH // 2 - 100, y=config.SCREEN_HEIGHT - 60,
                 width=200, height=25, text="No Changes Made.",
                 text_color=config.YELLOW, alignment="center", background_color=(50,50,70)
            ), temp_message_duration=2.0)


    def create_new_enemy(self):
        base_id = "new_enemy"
        counter = 1
        new_id = f"{base_id}_{counter}"
        while new_id in self.items_data:
            counter += 1
            new_id = f"{base_id}_{counter}"
        
        # Default enemy structure
        self.items_data[new_id] = {
            "name": f"New Enemy {counter}",
            "health": 20,
            "damage": 5,
            "speed": 1,
            "xp_reward": 5,
            "sprite_sheet": "default_enemy.png", # Placeholder
            "sprite_rows": 1,
            "sprite_columns": 1
        }
        self.enemy_list.append(new_id)
        self.modified = True
        self._rebuild_enemy_list_ui()
        self.select_enemy(new_id) # Select the newly created enemy
        print(f"Created new enemy: {new_id}")

    def delete_selected_enemy(self):
        if not self.selected_enemy_id:
            print("No enemy selected to delete.")
            # Show UI message: "No enemy selected"
            return
        
        enemy_to_delete = self.selected_enemy_id
        if enemy_to_delete in self.items_data:
            del self.items_data[enemy_to_delete]
        if enemy_to_delete in self.enemy_list:
            self.enemy_list.remove(enemy_to_delete)
        
        self.modified = True
        print(f"Deleted enemy: {enemy_to_delete}")
        self.select_enemy(None) # Clear selection and detail panel
        self._rebuild_enemy_list_ui() # Refresh the list

    def update(self, dt):
        super().update(dt) # Handles UIManager, Back, Save clicks via BaseEditorState

        # Mouse wheel for enemy list (Phase 2 - Placeholder)
        # if self.enemy_list_rect and self.enemy_list_rect.collidepoint(pygame.mouse.get_pos()):
        #     for event in self.current_events: # Assuming self.current_events is populated
        #         if event.type == pygame.MOUSEWHEEL:
        #             # scroll logic ...
        #             self._rebuild_enemy_list_ui()

        for element_id, was_clicked in self.last_clicked_elements.items():
            if was_clicked:
                if element_id.startswith("enemy_list_item_button_"):
                    button = self.ui_manager.get_element(element_id)
                    if button and button.on_click_data and "enemy_id" in button.on_click_data:
                        self.select_enemy(button.on_click_data["enemy_id"])
                elif element_id == "new_enemy_button":
                    self.create_new_enemy()
                elif element_id == "delete_enemy_button":
                    self.delete_selected_enemy()
                elif element_id == "apply_enemy_changes_button":
                    self.apply_changes()

class WaveEditorState(BaseEditorState):
    """Wave editor state"""
    
    def __init__(self, game_manager):
        super().__init__(game_manager, "WAVE EDITOR")
        self.day_list = []
        self.selected_day_id = None
        self.selected_day_data = {} # Holds a copy of the day's data
        
        self.day_list_scroll_offset = 0
        self.max_visible_days = 0
        self.day_list_rect = None

        self.relic_choices_input_id = "wave_relic_choices_input"

        # Wave Sequences within a selected day
        self.wave_sequences_list_data = [] # This will hold the list of dicts for sequences
        self.selected_wave_sequence_index = None
        self.selected_wave_sequence_data_copy = {} # Copy for editing individual sequence

        self.wave_sequence_list_scroll_offset = 0
        self.max_visible_wave_sequences = 0
        self.wave_sequence_list_rect = None
        self.wave_sequence_duration_input_id = "wave_seq_duration_input"
        self.wave_sequence_enemies_text_id = "wave_seq_enemies_text"

        # Store loaded enemy types for potential dropdowns later
        self.available_enemy_types = list(DataHandler().load_enemies().keys())

    def load_data(self):
        self.items_data = self.data_handler.load_waves()
        if not self.items_data:
            DataHandler.create_default_files()
            self.items_data = self.data_handler.load_waves()
        self.day_list = sorted(list(self.items_data.keys())) # Sort day IDs for consistent order
        print(f"Wave Editor: Loaded {len(self.day_list)} days.")

    def save_data(self):
        if not self.items_data:
            print("Wave Editor: No data to save.")
            return
        # Ensure any pending changes to selected_day_data are written back to items_data
        # This is crucial if apply_changes isn't the only way data gets modified before save
        if self.selected_day_id and self.selected_day_id in self.items_data:
             self.items_data[self.selected_day_id] = self.selected_day_data # Save current view

        success = self.data_handler.save_json(self.items_data, config.WAVES_DATA)
        if success:
            self.modified = False
            print("Wave data saved successfully.")
            self.ui_manager.add_element("save_message_wave", TextBox(
                x=config.SCREEN_WIDTH // 2 - 100, y=config.SCREEN_HEIGHT - 30,
                width=200, height=25, text="Waves Saved!",
                text_color=config.GREEN, alignment="center", background_color=(50,50,70)
            ), temp_message_duration=2.0)
        else:
            print("ERROR: Failed to save wave data.")
            self.ui_manager.add_element("save_error_wave", TextBox(
                x=config.SCREEN_WIDTH // 2 - 100, y=config.SCREEN_HEIGHT - 30,
                width=200, height=25, text="Save Failed!",
                text_color=config.RED, alignment="center", background_color=(50,50,70)
            ), temp_message_duration=2.0)

    def create_editor_ui(self):
        panel_padding = 20
        button_height = 30
        title_height = 30
        item_button_height = 25 # Smaller buttons for list items
        item_button_spacing = 5
        input_height = 30 # Consistent input height with EnemyEditor

        # --- Panel 1: Day List (Left) ---
        panel1_x = panel_padding
        panel1_y = 80 # Below main editor title
        panel1_width = 200
        panel1_height = config.SCREEN_HEIGHT - panel1_y - 80 # Space for save/back buttons

        self.ui_manager.add_element("day_list_panel_bg", TextBox(
            x=panel1_x, y=panel1_y, width=panel1_width, height=panel1_height,
            background_color=(70,70,90), border_color=config.BLACK
        ))
        self.ui_manager.add_element("day_list_panel_title", TextBox(
            x=panel1_x, y=panel1_y + 5, width=panel1_width, height=title_height,
            text="Days", text_color=config.WHITE, alignment="center", font_size=24
        ))
        self.day_list_rect = pygame.Rect(
            panel1_x + 5, panel1_y + title_height + 10,
            panel1_width - 10, panel1_height - title_height - 15 - (button_height * 2 + 10) # Space for New/Delete
        )
        if self.day_list_rect.height > 0:
            self.max_visible_days = self.day_list_rect.height // (item_button_height + item_button_spacing)
        else: self.max_visible_days = 0

        self.ui_manager.add_element("new_day_button", Button(
            x=panel1_x + 5, y=panel1_y + panel1_height - (button_height * 2 + 5),
            width=panel1_width - 10, height=button_height, text="New Day",
            color=config.GREEN, text_color=config.BLACK
        ))
        self.ui_manager.add_element("delete_day_button", Button(
            x=panel1_x + 5, y=panel1_y + panel1_height - button_height,
            width=panel1_width - 10, height=button_height, text="Delete Selected Day",
            color=config.RED, text_color=config.WHITE
        ))

        # --- Panel 2: Day Details & Wave Sequences (Middle) ---
        panel2_x = panel1_x + panel1_width + panel_padding
        panel2_y = panel1_y
        panel2_width = 350
        panel2_height = panel1_height

        self.ui_manager.add_element("day_details_panel_bg", TextBox(
            x=panel2_x, y=panel2_y, width=panel2_width, height=panel2_height,
            background_color=(80,80,100), border_color=config.BLACK
        ))
        self.ui_manager.add_element("day_details_title", TextBox(
            x=panel2_x, y=panel2_y + 5, width=panel2_width, height=title_height,
            text="Day Details: None", text_color=config.WHITE, alignment="center", font_size=20
        ))
        
        relic_choice_y = panel2_y + title_height + 15
        self.ui_manager.add_element("relic_choices_label", TextBox(
            x=panel2_x + 10, y=relic_choice_y, width=120, height=input_height,
            text="Relic Choices:", text_color=config.WHITE, alignment="left"
        ))
        self.ui_manager.add_element(self.relic_choices_input_id, InputBox(
            x=panel2_x + 130, y=relic_choice_y, width=panel2_width - 140, height=input_height,
            text="0", text_color=config.BLACK, background_color=config.WHITE
        ))

        wave_seq_list_y_start = relic_choice_y + input_height + 15
        self.ui_manager.add_element("wave_seq_list_title", TextBox(
            x=panel2_x, y=wave_seq_list_y_start, width=panel2_width, height=title_height,
            text="Wave Sequences", text_color=config.WHITE, alignment="center", font_size=20
        ))
        self.wave_sequence_list_rect = pygame.Rect(
            panel2_x + 5, wave_seq_list_y_start + title_height + 5,
            panel2_width - 10, panel2_height - (wave_seq_list_y_start + title_height + 10) - (button_height * 3 + 15) # Space for Add/Remove and Apply Day Changes
        )
        if self.wave_sequence_list_rect.height > 0:
            self.max_visible_wave_sequences = self.wave_sequence_list_rect.height // (item_button_height + item_button_spacing)
        else: self.max_visible_wave_sequences = 0
        
        # Apply Day Changes Button - positioned above Add/Remove Sequence buttons
        self.ui_manager.add_element("apply_wave_day_changes_button", Button(
            x=panel2_x + 5, y=panel2_y + panel2_height - (button_height * 3 + 10),
            width=panel2_width - 10, height=button_height, text="Apply Day Changes",
            color=config.BLUE, text_color=config.WHITE
        ))
        self.ui_manager.add_element("add_wave_seq_button", Button(
            x=panel2_x + 5, y=panel2_y + panel2_height - (button_height * 2 + 5),
            width=panel2_width - 10, height=button_height, text="Add New Sequence",
            color=config.GREEN, text_color=config.BLACK
        ))
        self.ui_manager.add_element("remove_wave_seq_button", Button(
            x=panel2_x + 5, y=panel2_y + panel2_height - button_height,
            width=panel2_width - 10, height=button_height, text="Remove Selected Sequence",
            color=config.RED, text_color=config.WHITE
        ))

        # --- Panel 3: Wave Sequence Details (Right) ---
        panel3_x = panel2_x + panel2_width + panel_padding
        panel3_y = panel1_y
        panel3_width = config.SCREEN_WIDTH - panel3_x - panel_padding
        panel3_height = panel1_height

        self.ui_manager.add_element("wave_seq_detail_panel_bg", TextBox(
            x=panel3_x, y=panel3_y, width=panel3_width, height=panel3_height,
            background_color=(90,90,110), border_color=config.BLACK
        ))
        self.ui_manager.add_element("wave_seq_detail_title", TextBox(
            x=panel3_x, y=panel3_y + 5, width=panel3_width, height=title_height,
            text="Sequence Details: None", text_color=config.WHITE, alignment="center", font_size=20
        ))
        
        duration_y = panel3_y + title_height + 15
        self.ui_manager.add_element("duration_label", TextBox(
            x=panel3_x + 10, y=duration_y, width=80, height=input_height,
            text="Duration:", text_color=config.WHITE, alignment="left"
        ))
        self.ui_manager.add_element(self.wave_sequence_duration_input_id, InputBox(
            x=panel3_x + 90, y=duration_y, width=panel3_width - 100, height=input_height,
            text="0", text_color=config.BLACK, background_color=config.WHITE
        ))

        enemies_text_y = duration_y + input_height + 15
        self.ui_manager.add_element(self.wave_sequence_enemies_text_id, TextBox(
            x=panel3_x + 10, y=enemies_text_y,
            width=panel3_width - 20, height=panel3_height - (enemies_text_y - panel3_y) - 10,
            text="Enemy List Management - Phase 2", text_color=config.LIGHT_GRAY, alignment="center",
            background_color=(80,80,100), border_color=config.BLACK
        ))

        self._rebuild_day_list_ui()
        self.select_day(None)

    def _rebuild_day_list_ui(self):
        to_remove = [eid for eid in self.ui_manager.elements if eid.startswith("day_list_item_button_")]
        for eid in to_remove: self.ui_manager.remove_element(eid)

        if not self.day_list_rect: return
        item_button_height = 25
        item_button_spacing = 5
        
        visible_days = self.day_list[self.day_list_scroll_offset : self.day_list_scroll_offset + self.max_visible_days]
        if not visible_days and self.day_list: # Ensure first page shows if offset is bad
            visible_days = self.day_list[0 : self.max_visible_days]

        for i, day_id in enumerate(visible_days):
            self.ui_manager.add_element(f"day_list_item_button_{day_id}", Button(
                x=self.day_list_rect.x, y=self.day_list_rect.y + i * (item_button_height + item_button_spacing),
                width=self.day_list_rect.width, height=item_button_height,
                text=str(day_id), color=config.GRAY, text_color=config.BLACK,
                on_click_data={"day_id": day_id}
            ))
        # TODO: Scroll buttons for day list

    def select_day(self, day_id):
        self.selected_day_id = day_id
        title_el = self.ui_manager.get_element("day_details_title")
        relic_input_el = self.ui_manager.get_element(self.relic_choices_input_id)

        if day_id and day_id in self.items_data:
            self.selected_day_data = self.items_data[day_id].copy() # Work with a copy
            if title_el: title_el.set_text(f"Day Details: {day_id}")
            if relic_input_el: relic_input_el.set_text(str(self.selected_day_data.get("relic_choices", 0)))
            self.wave_sequences_list_data = self.selected_day_data.get("waves", []) # This is a reference to the list within the copy
        else:
            self.selected_day_id = None # Clear if invalid
            self.selected_day_data = {}
            if title_el: title_el.set_text("Day Details: None")
            if relic_input_el: relic_input_el.set_text("0")
            self.wave_sequences_list_data = []

        self.select_wave_sequence(None) # Clear sequence selection
        self._rebuild_wave_sequences_ui()
    
    def _rebuild_wave_sequences_ui(self):
        to_remove = [eid for eid in self.ui_manager.elements if eid.startswith("wave_seq_item_button_")]
        for eid in to_remove: self.ui_manager.remove_element(eid)

        if not self.wave_sequence_list_rect or not self.selected_day_id: return
        item_button_height = 25
        item_button_spacing = 5
        
        visible_sequences = self.wave_sequences_list_data[self.wave_sequence_list_scroll_offset : self.wave_sequence_list_scroll_offset + self.max_visible_wave_sequences]

        for i, seq_data in enumerate(visible_sequences):
            idx_in_full_list = i + self.wave_sequence_list_scroll_offset
            duration = seq_data.get("duration", "N/A")
            num_enemy_groups = len(seq_data.get("enemies", []))
            btn_text = f"Seq {idx_in_full_list+1} ({num_enemy_groups} grp, {duration}s)"
            self.ui_manager.add_element(f"wave_seq_item_button_{idx_in_full_list}", Button(
                x=self.wave_sequence_list_rect.x, 
                y=self.wave_sequence_list_rect.y + i * (item_button_height + item_button_spacing),
                width=self.wave_sequence_list_rect.width, height=item_button_height,
                text=btn_text, color=config.LIGHT_GRAY, text_color=config.BLACK,
                on_click_data={"seq_index": idx_in_full_list}
            ))
        # TODO: Scroll buttons for wave sequence list

    def select_wave_sequence(self, sequence_index):
        self.selected_wave_sequence_index = sequence_index
        title_el = self.ui_manager.get_element("wave_seq_detail_title")
        duration_input_el = self.ui_manager.get_element(self.wave_sequence_duration_input_id)
        enemies_text_el = self.ui_manager.get_element(self.wave_sequence_enemies_text_id)

        if sequence_index is not None and 0 <= sequence_index < len(self.wave_sequences_list_data):
            self.selected_wave_sequence_data_copy = self.wave_sequences_list_data[sequence_index].copy()
            if title_el: title_el.set_text(f"Sequence Details: {sequence_index + 1}")
            if duration_input_el: duration_input_el.set_text(str(self.selected_wave_sequence_data_copy.get("duration", 0)))
            if enemies_text_el: 
                enemies_str = "Enemies:\n" + "\n".join([f" - {e.get('type', 'N/A')}: {e.get('count',0)} every {e.get('interval',0)}s" for e in self.selected_wave_sequence_data_copy.get("enemies",[])])
                enemies_text_el.set_text(enemies_str if self.selected_wave_sequence_data_copy.get("enemies") else "No enemies defined.")

        else:
            self.selected_wave_sequence_index = None
            self.selected_wave_sequence_data_copy = {}
            if title_el: title_el.set_text("Sequence Details: None")
            if duration_input_el: duration_input_el.set_text("0")
            if enemies_text_el: enemies_text_el.set_text("Enemy List Management - Phase 2")

    def apply_changes(self): 
        if not self.selected_day_id or self.selected_day_id not in self.items_data:
            print("No valid day selected to apply changes to.")
            return

        changes_made = False
        
        relic_input_el = self.ui_manager.get_element(self.relic_choices_input_id)
        if relic_input_el:
            try:
                new_relic_choices = int(relic_input_el.text)
                if self.selected_day_data.get("relic_choices") != new_relic_choices:
                    self.selected_day_data["relic_choices"] = new_relic_choices
                    changes_made = True
            except ValueError:
                print(f"Invalid relic_choices value: {relic_input_el.text}")

        if self.selected_wave_sequence_index is not None and \
           0 <= self.selected_wave_sequence_index < len(self.wave_sequences_list_data):
            duration_input_el = self.ui_manager.get_element(self.wave_sequence_duration_input_id)
            if duration_input_el:
                try:
                    new_duration = int(duration_input_el.text)
                    # Check against the original list data, not the copy, to see if duration changed
                    if self.wave_sequences_list_data[self.selected_wave_sequence_index].get("duration") != new_duration:
                        self.wave_sequences_list_data[self.selected_wave_sequence_index]["duration"] = new_duration
                        changes_made = True
                    # Update the copy as well for consistency if it's used elsewhere before re-selection
                    self.selected_wave_sequence_data_copy["duration"] = new_duration 
                except ValueError:
                    print(f"Invalid duration value: {duration_input_el.text}")
            # Phase 2: Apply enemy list changes from self.selected_wave_sequence_data_copy to self.wave_sequences_list_data[self.selected_wave_sequence_index]["enemies"]

        if changes_made:
            self.selected_day_data["waves"] = self.wave_sequences_list_data # Ensure the main day data has the updated list of sequences
            self.items_data[self.selected_day_id] = self.selected_day_data.copy() # Save the updated day data back to master items
            self.modified = True
            print(f"Applied changes to day: {self.selected_day_id}")
            self._rebuild_wave_sequences_ui() 
            self.ui_manager.add_element("apply_wave_changes_msg", TextBox(
                x=config.SCREEN_WIDTH // 2 - 100, y=config.SCREEN_HEIGHT - 60,
                width=200, height=25, text="Day Changes Applied!",
                text_color=config.GREEN, alignment="center", background_color=(50,50,70)
            ), temp_message_duration=2.0)
        else:
            print("No changes detected to apply for the selected day/sequence.")

    def create_new_day(self):
        base_id = "day_"
        i = 1
        new_day_id = f"{base_id}{i}"
        while new_day_id in self.items_data:
            i += 1
            new_day_id = f"{base_id}{i}"
        
        self.items_data[new_day_id] = {"waves": [], "relic_choices": 1}
        self.day_list = sorted(list(self.items_data.keys())) 
        self.modified = True
        self._rebuild_day_list_ui()
        self.select_day(new_day_id)
        print(f"Created new day: {new_day_id}")

    def delete_selected_day(self):
        if not self.selected_day_id or self.selected_day_id not in self.items_data:
            print("No valid day selected to delete.")
            return
        deleted_id = self.selected_day_id
        del self.items_data[self.selected_day_id]
        self.day_list = sorted(list(self.items_data.keys()))
        self.modified = True
        self.select_day(None) 
        self._rebuild_day_list_ui() 
        print(f"Deleted day: {deleted_id}")

    def add_wave_sequence(self):
        if not self.selected_day_id or self.selected_day_id not in self.items_data:
            print("No day selected to add wave sequence to.")
            return
        new_sequence = {"enemies": [], "duration": 60} 
        self.wave_sequences_list_data.append(new_sequence)
        self.selected_day_data["waves"] = self.wave_sequences_list_data # Ensure the day data copy is updated
        self.modified = True
        self._rebuild_wave_sequences_ui()
        self.select_wave_sequence(len(self.wave_sequences_list_data) - 1)
        print(f"Added new wave sequence to day {self.selected_day_id}")

    def remove_selected_wave_sequence(self):
        if not self.selected_day_id or self.selected_wave_sequence_index is None or \
           not (0 <= self.selected_wave_sequence_index < len(self.wave_sequences_list_data)):
            print("No valid wave sequence selected to remove.")
            return
        
        removed_index = self.selected_wave_sequence_index
        del self.wave_sequences_list_data[self.selected_wave_sequence_index]
        self.selected_day_data["waves"] = self.wave_sequences_list_data # Ensure the day data copy is updated
        self.modified = True
        self.select_wave_sequence(None) 
        self._rebuild_wave_sequences_ui()
        print(f"Removed wave sequence at index {removed_index} from day {self.selected_day_id}")

    def update(self, dt):
        super().update(dt)

        for eid, clicked in self.last_clicked_elements.items():
            if clicked:
                if eid.startswith("day_list_item_button_"):
                    button = self.ui_manager.get_element(eid)
                    if button and button.on_click_data:
                        self.select_day(button.on_click_data.get("day_id"))
                elif eid == "new_day_button":
                    self.create_new_day()
                elif eid == "delete_day_button":
                    self.delete_selected_day()
                elif eid == "apply_wave_day_changes_button": 
                    self.apply_changes()
                elif eid.startswith("wave_seq_item_button_"):
                    button = self.ui_manager.get_element(eid)
                    if button and button.on_click_data:
                        self.select_wave_sequence(button.on_click_data.get("seq_index"))
                elif eid == "add_wave_seq_button":
                    self.add_wave_sequence()
                elif eid == "remove_wave_seq_button":
                    self.remove_selected_wave_sequence()

class BuildingEditorState(BaseEditorState):
    """Building editor state (Phase 1: List, Main Props, New/Delete/Apply)"""
    
    def __init__(self, game_manager):
        """Initialize the building editor state"""
        super().__init__(game_manager, "BUILDING EDITOR")
        self.building_list = []
        self.selected_building_id = None
        self.selected_building_data = {} 
        self.detail_text_inputs = {} 
        self.base_cost_display_id = "building_base_cost_display"
        
        self.building_list_scroll_offset = 0
        self.max_visible_buildings = 0 
        self.building_list_rect = None
    
    def load_data(self):
        """Load building data"""
        self.items_data = self.data_handler.load_buildings()
        if not self.items_data:
            print("Building Editor: No building data found, creating default.")
            DataHandler.create_default_files() # Ensure this doesn't require class instance
            self.items_data = self.data_handler.load_buildings()
        self.building_list = list(self.items_data.keys())
        print(f"Building Editor: Loaded {len(self.building_list)} buildings: {self.building_list}")
            
    def save_data(self):
        """Save building data"""
        if not self.items_data:
            print("Building Editor: No data to save.")
            self.ui_manager.add_element("save_message_building", TextBox(
                x=config.SCREEN_WIDTH // 2 - 150, y=config.SCREEN_HEIGHT - 30,
                width=300, height=25, text="No building data to save.",
                text_color=config.YELLOW, alignment="center", background_color=(50,50,70) 
            ), temp_message_duration=2.0)
            return

        success = self.data_handler.save_json(self.items_data, config.BUILDINGS_DATA)
        if success:
            self.modified = False
            print("Building data saved successfully.")
            self.ui_manager.add_element("save_message_building", TextBox(
                x=config.SCREEN_WIDTH // 2 - 100, y=config.SCREEN_HEIGHT - 30,
                width=200, height=25, text="Buildings Saved!",
                text_color=config.GREEN, alignment="center", background_color=(50,50,70) 
            ), temp_message_duration=2.0)
        else:
            print("ERROR: Failed to save building data.")
            self.ui_manager.add_element("save_error_building", TextBox(
                x=config.SCREEN_WIDTH // 2 - 100, y=config.SCREEN_HEIGHT - 30,
                width=200, height=25, text="Save Failed!",
                text_color=config.RED, alignment="center", background_color=(50,50,70) 
            ), temp_message_duration=2.0)

    def create_editor_ui(self):
        """Create building editor UI"""
        # Left panel - Building list
        list_bg_width = 250
        list_bg_height = config.SCREEN_HEIGHT - 200 
        list_bg_x = 50
        list_bg_y = 100

        self.ui_manager.add_element("building_list_main_bg", TextBox(
             x=list_bg_x, y=list_bg_y, width=list_bg_width, height=list_bg_height,
             background_color=(80, 80, 100), border_color=config.BLACK
        ))
        self.ui_manager.add_element("building_list_title", TextBox(
            x=list_bg_x, y=list_bg_y + 5, width=list_bg_width, height=30,
            text="Buildings", text_color=config.WHITE, alignment="center", font_size=24
        ))

        self.building_list_rect = pygame.Rect(
            list_bg_x + 5, list_bg_y + 40, 
            list_bg_width - 10, list_bg_height - 90 # Space for New/Delete buttons
        )
        if self.building_list_rect.height > 0:
            # Assuming item button height 25, spacing 5 => 30 per item
            self.max_visible_buildings = self.building_list_rect.height // 30 
        else:
            self.max_visible_buildings = 0

        new_del_button_y = list_bg_y + list_bg_height - 45 
        self.ui_manager.add_element("new_building_button", Button(
            x=list_bg_x + 5, y=new_del_button_y, width=(list_bg_width // 2) - 10, height=40,
            text="New", color=config.GREEN, text_color=config.BLACK
        ))
        self.ui_manager.add_element("delete_building_button", Button(
            x=list_bg_x + (list_bg_width // 2) + 5, y=new_del_button_y, width=(list_bg_width // 2) - 10, height=40,
            text="Delete", color=config.RED, text_color=config.WHITE
        ))

        # Right panel - Building details
        detail_x = list_bg_x + list_bg_width + 30
        detail_y = 100
        detail_width = config.SCREEN_WIDTH - detail_x - 30 
        detail_height = config.SCREEN_HEIGHT - detail_y - 80 

        self.ui_manager.add_element("building_detail_bg", TextBox(
            x=detail_x, y=detail_y, width=detail_width, height=detail_height,
            background_color=(100, 100, 120), border_color=config.BLACK
        ))
        self.ui_manager.add_element("building_detail_title_text", TextBox(
            x=detail_x, y=detail_y + 5, width=detail_width, height=30,
            text="Building Details: (Select a Building)", 
            text_color=config.WHITE, alignment="center", font_size=24
        ))

        # Main property input fields
        field_x_start = detail_x + 20
        field_y_current = detail_y + 45
        label_width = 120 
        input_box_width = detail_width - label_width - 45 
        input_height = 30
        field_spacing = 10 
        self.detail_text_inputs.clear()

        main_props_config = [
            ("name", "Name:", 1), 
            ("description", "Description:", 3), # Taller input for description
            ("category", "Category:", 1)
        ]

        for prop_id, prop_label, height_multiplier in main_props_config:
            actual_input_height = input_height * height_multiplier
            self.ui_manager.add_element(f"building_prop_label_{prop_id}", TextBox(
                x=field_x_start, y=field_y_current, width=label_width, height=actual_input_height,
                text=prop_label, text_color=config.WHITE, alignment="left"
            ))
            input_box_id = f"building_prop_input_{prop_id}"
            self.ui_manager.add_element(input_box_id, InputBox(
                x=field_x_start + label_width + 5, y=field_y_current,
                width=input_box_width, height=actual_input_height,
                text="", text_color=config.BLACK, background_color=config.WHITE
            ))
            self.detail_text_inputs[prop_id] = input_box_id
            field_y_current += actual_input_height + field_spacing
        
        # Base Cost Display
        base_cost_label_y = field_y_current + 5
        self.ui_manager.add_element("base_cost_label", TextBox(
            x=field_x_start, y=base_cost_label_y, width=label_width + input_box_width + 5, height=input_height,
            text="Base Cost (View Only - Edit in Phase 2):", text_color=config.WHITE, alignment="left"
        ))
        base_cost_display_y = base_cost_label_y + input_height
        self.ui_manager.add_element(self.base_cost_display_id, TextBox(
            x=field_x_start, y=base_cost_display_y, 
            width=label_width + input_box_width + 5, height=100, # Height for multiple lines
            text="Select a building to see base costs.", 
            text_color=config.LIGHT_GRAY, background_color=(70,70,90), 
            border_color=config.BLACK, alignment="left", font_size=18
        ))

        # Apply Changes button
        self.ui_manager.add_element("apply_building_changes_button", Button(
            x=detail_x + detail_width - 170, y=detail_y + detail_height - 50,
            width=150, height=40, text="Apply Changes",
            color=config.BLUE, text_color=config.WHITE
        ))
        
        self._rebuild_building_list_ui()
        self.select_building(None)

    def _rebuild_building_list_ui(self):
        buttons_to_remove = [elem_id for elem_id in self.ui_manager.elements if elem_id.startswith("building_list_item_button_")]
        for elem_id in buttons_to_remove:
            if self.ui_manager.get_element(elem_id):
                 self.ui_manager.remove_element(elem_id)
        
        if not self.building_list_rect: return

        list_item_x = self.building_list_rect.x
        list_item_y_start = self.building_list_rect.y
        button_width = self.building_list_rect.width
        button_height = 25 # Smaller buttons for list items
        button_spacing = 5
        
        # Basic scrolling for Phase 1, no separate scroll buttons yet
        visible_building_ids = self.building_list[self.building_list_scroll_offset : self.building_list_scroll_offset + self.max_visible_buildings]
        if not visible_building_ids and self.building_list: # If offset is too high, show first page
             visible_building_ids = self.building_list[0 : self.max_visible_buildings]

        for i, building_id in enumerate(visible_building_ids):
            building_name = self.items_data.get(building_id, {}).get("name", building_id)
            self.ui_manager.add_element(f"building_list_item_button_{building_id}", Button(
                x=list_item_x, y=list_item_y_start + i * (button_height + button_spacing),
                width=button_width, height=button_height,
                text=building_name, color=config.GRAY, text_color=config.BLACK,
                on_click_data={"building_id": building_id} 
            ))

    def select_building(self, building_id):
        self.selected_building_id = building_id
        detail_title_text = "Building Details: (Select a Building)"
        
        if building_id and building_id in self.items_data:
            self.selected_building_data = self.items_data[building_id].copy() # Work with a copy
            detail_title_text = f"Building Details: {self.selected_building_data.get('name', building_id)}"
        else:
            self.selected_building_id = None 
            self.selected_building_data = {}
        
        title_element = self.ui_manager.get_element("building_detail_title_text")
        if title_element and isinstance(title_element, TextBox):
            title_element.set_text(detail_title_text)

        for prop_id, input_box_id in self.detail_text_inputs.items():
            input_box = self.ui_manager.get_element(input_box_id)
            if input_box and isinstance(input_box, InputBox):
                value = self.selected_building_data.get(prop_id, "")
                input_box.set_text(str(value))
        
        base_cost_text = "Base Costs:\n"
        base_costs = self.selected_building_data.get("base_cost", {})
        if base_costs:
            for resource, amount in base_costs.items():
                base_cost_text += f"  {resource.title()}: {amount}\n"
        else:
            base_cost_text += "  None defined." if self.selected_building_id else "  Select a building.\n"

        base_cost_display_element = self.ui_manager.get_element(self.base_cost_display_id)
        if base_cost_display_element and isinstance(base_cost_display_element, TextBox):
            base_cost_display_element.set_text(base_cost_text)

    def apply_changes(self):
        if not self.selected_building_id or self.selected_building_id not in self.items_data:
            print("No building selected to apply changes to.")
            self.ui_manager.add_element("apply_building_msg", TextBox(
                x=config.SCREEN_WIDTH // 2 - 150, y=config.SCREEN_HEIGHT - 60,
                width=300, height=25, text="No building selected.",
                text_color=config.YELLOW, alignment="center", background_color=(50,50,70)
            ), temp_message_duration=2.0)
            return

        original_data = self.items_data[self.selected_building_id]
        updated_data = self.selected_building_data.copy() # Work on the copy
        changes_made = False

        for prop_id, input_box_id in self.detail_text_inputs.items():
            input_box = self.ui_manager.get_element(input_box_id)
            if input_box and isinstance(input_box, InputBox):
                new_value_str = input_box.text
                # For Phase 1, all main editable props are strings.
                if updated_data.get(prop_id) != new_value_str:
                    updated_data[prop_id] = new_value_str
                    changes_made = True
        
        if changes_made:
            self.items_data[self.selected_building_id] = updated_data
            self.selected_building_data = updated_data.copy() # Update state's copy
            self.modified = True
            print(f"Applied changes to building: {self.selected_building_id}")
            self.ui_manager.add_element("apply_building_msg", TextBox(
                 x=config.SCREEN_WIDTH // 2 - 100, y=config.SCREEN_HEIGHT - 60, 
                 width=200, height=25, text="Changes Applied!",
                 text_color=config.GREEN, alignment="center", background_color=(50,50,70)
            ), temp_message_duration=2.0)
            
            if original_data.get("name") != updated_data.get("name"):
                self._rebuild_building_list_ui() # Refresh list if name changed
        else:
            print("No changes detected for the selected building.")
            self.ui_manager.add_element("apply_building_msg", TextBox(
                 x=config.SCREEN_WIDTH // 2 - 100, y=config.SCREEN_HEIGHT - 60,
                 width=200, height=25, text="No Changes Made.",
                 text_color=config.YELLOW, alignment="center", background_color=(50,50,70)
            ), temp_message_duration=2.0)

    def create_new_building(self):
        base_id = "new_building"
        counter = 1
        new_id = f"{base_id}_{counter}"
        while new_id in self.items_data:
            counter += 1
            new_id = f"{base_id}_{counter}"
        
        self.items_data[new_id] = {
            "name": f"New Building {counter}",
            "description": "A new construct for the city.",
            "category": "utility", # Default category
            "base_cost": {"wood": 10, "stone": 10},
            "levels": {
                "1": { 
                    "cost": {"wood":0, "stone":0}, # Level 1 cost is often 0 or part of base
                    "bonuses": {"placeholder_bonus": 1},
                    "production": {} 
                } 
            }
        }
        self.building_list.append(new_id)
        # Sort if desired: self.building_list.sort()
        self.modified = True
        self._rebuild_building_list_ui()
        self.select_building(new_id)
        print(f"Created new building: {new_id}")

    def delete_selected_building(self):
        if not self.selected_building_id:
            print("No building selected to delete.")
            self.ui_manager.add_element("delete_building_msg", TextBox(
                x=config.SCREEN_WIDTH // 2 - 150, y=config.SCREEN_HEIGHT - 60,
                width=300, height=25, text="No building selected.",
                text_color=config.YELLOW, alignment="center", background_color=(50,50,70)
            ), temp_message_duration=2.0)
            return
        
        building_to_delete = self.selected_building_id
        if building_to_delete in self.items_data:
            del self.items_data[building_to_delete]
        if building_to_delete in self.building_list:
            self.building_list.remove(building_to_delete)
        
        self.modified = True
        print(f"Deleted building: {building_to_delete}")
        self.select_building(None) 
        self._rebuild_building_list_ui()
        self.ui_manager.add_element("delete_building_msg", TextBox(
            x=config.SCREEN_WIDTH // 2 - 150, y=config.SCREEN_HEIGHT - 60,
            width=300, height=25, text=f"Deleted {building_to_delete}",
            text_color=config.ORANGE, alignment="center", background_color=(50,50,70)
        ), temp_message_duration=2.0)


    def update(self, dt):
        super().update(dt) 

        # Basic mouse wheel scroll for building list (no dedicated buttons in Phase 1)
        if self.building_list_rect and self.building_list_rect.collidepoint(pygame.mouse.get_pos()):
            for event in self.current_events: 
                if event.type == pygame.MOUSEWHEEL:
                    if event.y > 0:  # Scroll Up
                        self.building_list_scroll_offset = max(0, self.building_list_scroll_offset - 1)
                    elif event.y < 0:  # Scroll Down
                        max_scroll = len(self.building_list) - self.max_visible_buildings
                        if max_scroll < 0: max_scroll = 0
                        self.building_list_scroll_offset = min(max_scroll, self.building_list_scroll_offset + 1)
                    self._rebuild_building_list_ui()
                    # self.current_events.remove(event) # Consume event if needed
                    break 


        for element_id, was_clicked in self.last_clicked_elements.items():
            if was_clicked:
                if element_id.startswith("building_list_item_button_"):
                    button = self.ui_manager.get_element(element_id)
                    if button and button.on_click_data and "building_id" in button.on_click_data:
                        self.select_building(button.on_click_data["building_id"])
                elif element_id == "new_building_button":
                    self.create_new_building()
                elif element_id == "delete_building_button":
                    self.delete_selected_building()
                elif element_id == "apply_building_changes_button":
                    self.apply_changes()