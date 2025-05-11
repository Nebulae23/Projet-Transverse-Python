"""
Magic Survivor - Camera System

This module provides a camera system for scrollable maps and following the player.
"""

import pygame
from src import config

class Camera:
    """Camera class for controlling the viewport"""
    
    def __init__(self, width, height):
        """Initialize the camera
        
        Args:
            width (int): Width of the camera viewport
            height (int): Height of the camera viewport
        """
        self.rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
        self.target = None
        self.zoom = 1.0
        self.max_zoom = 2.0
        self.min_zoom = 0.5
        self.bounds = None  # (min_x, min_y, max_x, max_y)
        self.lerp_factor = 0.1  # For smooth camera movement
    
    def set_target(self, target):
        """Set a target for the camera to follow
        
        Args:
            target: An object with x and y attributes (like the player)
        """
        self.target = target
    
    def set_bounds(self, min_x, min_y, max_x, max_y):
        """Set bounds for the camera
        
        Args:
            min_x (float): Minimum x position
            min_y (float): Minimum y position
            max_x (float): Maximum x position
            max_y (float): Maximum y position
        """
        self.bounds = (min_x, min_y, max_x, max_y)
    
    def update(self, dt):
        """Update the camera position
        
        Args:
            dt (float): Time elapsed since last update in seconds
        """
        if self.target:
            # Calculate target position (centered on target)
            target_x = self.target.x - self.width / 2
            target_y = self.target.y - self.height / 2
            
            # Use lerp for smooth camera movement
            self.x += (target_x - self.x) * self.lerp_factor * 60 * dt
            self.y += (target_y - self.y) * self.lerp_factor * 60 * dt
        
        # Apply bounds if set
        if self.bounds:
            min_x, min_y, max_x, max_y = self.bounds
            self.x = max(min_x, min(self.x, max_x - self.width))
            self.y = max(min_y, min(self.y, max_y - self.height))
        
        # Update the rect
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
    
    def apply(self, entity):
        """Translate an entity's position to screen coordinates
        
        Args:
            entity: An object with a rect attribute
            
        Returns:
            pygame.Rect: The entity's rect in screen coordinates
        """
        return pygame.Rect(
            entity.rect.x - self.rect.x,
            entity.rect.y - self.rect.y,
            entity.rect.width,
            entity.rect.height
        )
    
    def apply_rect(self, rect):
        """Translate a rect to screen coordinates
        
        Args:
            rect (pygame.Rect): The rect to translate
            
        Returns:
            pygame.Rect: The rect in screen coordinates
        """
        return pygame.Rect(
            rect.x - self.rect.x,
            rect.y - self.rect.y,
            rect.width,
            rect.height
        )
    
    def apply_point(self, x, y):
        """Translate a point to screen coordinates
        
        Args:
            x (float): The x coordinate
            y (float): The y coordinate
            
        Returns:
            tuple: The point in screen coordinates (x, y)
        """
        return (x - self.rect.x, y - self.rect.y)
    
    def reverse_apply_point(self, screen_x, screen_y):
        """Translate screen coordinates to world coordinates
        
        Args:
            screen_x (float): The screen x coordinate
            screen_y (float): The screen y coordinate
            
        Returns:
            tuple: The point in world coordinates (x, y)
        """
        return (screen_x + self.rect.x, screen_y + self.rect.y)
    
    def zoom_in(self, amount=0.1):
        """Zoom in the camera
        
        Args:
            amount (float): Amount to zoom in
        """
        self.zoom = min(self.zoom + amount, self.max_zoom)
    
    def zoom_out(self, amount=0.1):
        """Zoom out the camera
        
        Args:
            amount (float): Amount to zoom out
        """
        self.zoom = max(self.zoom - amount, self.min_zoom) 