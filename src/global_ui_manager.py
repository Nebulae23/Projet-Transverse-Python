"""
Magic Survivor - Global UI Manager

This module provides a global UI manager that can manage UI elements across
different game states and support UI layers.
"""

import pygame
from src import config
from src.ui_manager import Button, ProgressBar, TextBox

class UILayer:
    """UI layer class for organizing UI elements by depth"""
    
    def __init__(self, name, z_index=0):
        """Initialize a UI layer
        
        Args:
            name (str): Name of the layer
            z_index (int): Z-index of the layer (higher values are drawn on top)
        """
        self.name = name
        self.z_index = z_index
        self.elements = {}  # Dict of {element_id: element}
        self.visible = True
    
    def add_element(self, element_id, element):
        """Add a UI element to the layer
        
        Args:
            element_id (str): ID for the element
            element: UI element to add
        """
        self.elements[element_id] = element
    
    def remove_element(self, element_id):
        """Remove a UI element from the layer
        
        Args:
            element_id (str): ID of the element to remove
        """
        if element_id in self.elements:
            del self.elements[element_id]
    
    def get_element(self, element_id):
        """Get a UI element from the layer
        
        Args:
            element_id (str): ID of the element to get
            
        Returns:
            The UI element, or None if not found
        """
        return self.elements.get(element_id)
    
    def update(self, mouse_pos, events):
        """Update all UI elements in the layer
        
        Args:
            mouse_pos (tuple): Current mouse position (x, y)
            events (list): List of pygame events
            
        Returns:
            dict: Dictionary of {element_id: True} for elements that were clicked
        """
        if not self.visible:
            return {}
            
        clicked = {}
        
        # Update buttons
        for element_id, element in self.elements.items():
            if isinstance(element, Button):
                element.update(mouse_pos)
                
                for event in events:
                    if element.is_clicked(event):
                        clicked[element_id] = True
        
        return clicked
    
    def render(self, screen):
        """Render all UI elements in the layer
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        if not self.visible:
            return
            
        for element in self.elements.values():
            element.render(screen)
    
    def set_visible(self, visible):
        """Set the visibility of the layer
        
        Args:
            visible (bool): Whether the layer should be visible
        """
        self.visible = visible


class GlobalUIManager:
    """Global UI manager for managing UI across game states"""
    
    # Standard layer names and z-indices
    LAYER_BACKGROUND = "background"  # z_index = 0, for backgrounds
    LAYER_WORLD = "world"            # z_index = 10, for world elements
    LAYER_INTERFACE = "interface"    # z_index = 20, for main UI
    LAYER_OVERLAY = "overlay"        # z_index = 30, for popups, modals
    LAYER_DEBUG = "debug"            # z_index = 40, for debug info
    
    def __init__(self, game_manager):
        """Initialize the global UI manager"""
        self.game_manager = game_manager
        # Create standard layers
        self.layers = {
            self.LAYER_BACKGROUND: UILayer(self.LAYER_BACKGROUND, 0),
            self.LAYER_WORLD: UILayer(self.LAYER_WORLD, 10),
            self.LAYER_INTERFACE: UILayer(self.LAYER_INTERFACE, 20),
            self.LAYER_OVERLAY: UILayer(self.LAYER_OVERLAY, 30),
            self.LAYER_DEBUG: UILayer(self.LAYER_DEBUG, 40)
        }
        
        # Modal state
        self.modal_active = False
        self.modal_layer = None
        
        # Persistent UI elements (available across states)
        self._setup_persistent_ui()
    
    def _setup_persistent_ui(self):
        """Set up persistent UI elements"""
        # Character button (top-right corner)
        self.add_element(
            "character_button",
            Button(
                x=config.SCREEN_WIDTH - 50,
                y=60,
                width=40,
                height=40,
                text="C",
                color=config.BLUE,
                hover_color=config.WHITE,
                text_color=config.BLACK
            ),
            self.LAYER_INTERFACE
        )
        
        # Equipment button (next to character button)
        self.add_element(
            "equipment_button",
            Button(
                x=config.SCREEN_WIDTH - 100,
                y=60,
                width=40,
                height=40,
                text="E",
                color=config.GREEN,
                hover_color=config.WHITE,
                text_color=config.BLACK
            ),
            self.LAYER_INTERFACE
        )
        
        # Abilities button (next to equipment button)
        self.add_element(
            "abilities_button",
            Button(
                x=config.SCREEN_WIDTH - 150,
                y=60,
                width=40,
                height=40,
                text="A",
                color=config.PURPLE,
                hover_color=config.WHITE,
                text_color=config.BLACK
            ),
            self.LAYER_INTERFACE
        )
    
    def create_layer(self, layer_name, z_index):
        """Create a new UI layer
        
        Args:
            layer_name (str): Name of the layer
            z_index (int): Z-index of the layer
        """
        if layer_name not in self.layers:
            self.layers[layer_name] = UILayer(layer_name, z_index)
    
    def add_element(self, element_id, element, layer_name=LAYER_INTERFACE):
        """Add a UI element to a layer
        
        Args:
            element_id (str): ID for the element
            element: UI element to add
            layer_name (str): Name of the layer to add to
        """
        if layer_name in self.layers:
            self.layers[layer_name].add_element(element_id, element)
    
    def remove_element(self, element_id, layer_name=None):
        """Remove a UI element
        
        Args:
            element_id (str): ID of the element to remove
            layer_name (str): Name of the layer to remove from, or None to search all layers
        """
        if layer_name:
            if layer_name in self.layers:
                self.layers[layer_name].remove_element(element_id)
        else:
            # Search all layers
            for layer in self.layers.values():
                layer.remove_element(element_id)
    
    def get_element(self, element_id, layer_name=None):
        """Get a UI element
        
        Args:
            element_id (str): ID of the element to get
            layer_name (str): Name of the layer to get from, or None to search all layers
            
        Returns:
            The UI element, or None if not found
        """
        if layer_name:
            if layer_name in self.layers:
                return self.layers[layer_name].get_element(element_id)
            return None
        else:
            # Search all layers
            for layer in self.layers.values():
                element = layer.get_element(element_id)
                if element:
                    return element
            return None
    
    def set_layer_visible(self, layer_name, visible):
        """Set the visibility of a layer
        
        Args:
            layer_name (str): Name of the layer
            visible (bool): Whether the layer should be visible
        """
        if layer_name in self.layers:
            self.layers[layer_name].set_visible(visible)
    
    def show_modal(self, layer_name):
        """Show a layer as a modal (disabling other layers)
        
        Args:
            layer_name (str): Name of the layer to show as modal
        """
        if layer_name in self.layers:
            self.modal_active = True
            self.modal_layer = layer_name
    
    def hide_modal(self):
        """Hide the current modal layer"""
        self.modal_active = False
        self.modal_layer = None
    
    def update(self, mouse_pos, events):
        """Update all UI elements
        
        Args:
            mouse_pos (tuple): Current mouse position (x, y)
            events (list): List of pygame events
            
        Returns:
            dict: Dictionary of {element_id: True} for elements that were clicked
        """
        clicked = {}
        
        if self.modal_active and self.modal_layer in self.layers:
            # Only update the modal layer
            modal_clicked = self.layers[self.modal_layer].update(mouse_pos, events)
            clicked.update(modal_clicked)
        else:
            # Update all layers in order of z-index (lowest to highest)
            sorted_layers = sorted(self.layers.values(), key=lambda layer: layer.z_index)
            
            for layer in sorted_layers:
                layer_clicked = layer.update(mouse_pos, events)
                clicked.update(layer_clicked)
        
        return clicked
    
    def render(self, screen):
        """Render all UI elements
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        # Render layers in order of z-index (lowest to highest)
        sorted_layers = sorted(self.layers.values(), key=lambda layer: layer.z_index)
        
        for layer in sorted_layers:
            layer.render(screen)
    
    def create_panel(self, title, x, y, width, height, layer_name=LAYER_OVERLAY):
        """Create a panel with a title
        
        Args:
            title (str): Title of the panel
            x (int): X position of the panel
            y (int): Y position of the panel
            width (int): Width of the panel
            height (int): Height of the panel
            layer_name (str): Name of the layer to add to
            
        Returns:
            str: ID of the panel
        """
        panel_id = f"panel_{title.lower().replace(' ', '_')}"
        
        # Background
        self.add_element(
            f"{panel_id}_bg",
            TextBox(
                x=x,
                y=y,
                width=width,
                height=height,
                background_color=(100, 100, 120, 200),  # Semi-transparent
                border_color=config.BLACK
            ),
            layer_name
        )
        
        # Title
        self.add_element(
            f"{panel_id}_title",
            TextBox(
                x=x,
                y=y,
                width=width,
                height=30,
                text=title,
                text_color=config.WHITE,
                background_color=(50, 50, 70),
                border_color=config.BLACK,
                alignment="center"
            ),
            layer_name
        )
        
        # Close button
        self.add_element(
            f"{panel_id}_close",
            Button(
                x=x + width - 30,
                y=y,
                width=30,
                height=30,
                text="X",
                color=(200, 50, 50),
                hover_color=(255, 100, 100),
                text_color=config.WHITE
            ),
            layer_name
        )
        
        return panel_id
    
    def remove_panel(self, panel_id, layer_name=LAYER_OVERLAY):
        """Remove a panel
        
        Args:
            panel_id (str): ID of the panel to remove
            layer_name (str): Name of the layer the panel is on
        """
        self.remove_element(f"{panel_id}_bg", layer_name)
        self.remove_element(f"{panel_id}_title", layer_name)
        self.remove_element(f"{panel_id}_close", layer_name)
        
        # Find and remove any other elements with this panel ID prefix
        if layer_name in self.layers:
            to_remove = []
            for element_id in self.layers[layer_name].elements:
                if element_id.startswith(f"{panel_id}_"):
                    to_remove.append(element_id)
            
            for element_id in to_remove:
                self.remove_element(element_id, layer_name) 