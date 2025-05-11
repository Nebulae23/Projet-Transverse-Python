import pygame
from src import config

class GameState:
    """Base class for all game states"""
    
    def __init__(self, game_manager):
        """Initialize the game state
        
        Args:
            game_manager (GameManager): Reference to the game manager
        """
        self.game_manager = game_manager
        self.is_transparent = False  # If True, states below this will be rendered
        self.transition_progress = 0.0  # For smooth transitions
        self.transition_in = False  # Whether transitioning in or out
        self.transition_speed = 2.0  # Units per second (0-1 scale)
    
    def handle_events(self, events):
        """Handle pygame events
        
        Args:
            events (list): List of pygame events
        """
        pass
    
    def update(self, dt):
        """Update the game state
        
        Args:
            dt (float): Time elapsed since last update in seconds
        """
        # Update transitions
        if self.transition_in:
            self.transition_progress = min(1.0, self.transition_progress + self.transition_speed * dt)
        else:
            self.transition_progress = max(0.0, self.transition_progress - self.transition_speed * dt)
    
    def render(self, screen):
        """Render the game state
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        pass
    
    def render_transition(self, screen):
        """Render transition effects
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        if self.transition_progress < 1.0:
            # Fade in/out effect
            overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
            alpha = int(255 * (1.0 - self.transition_progress))
            overlay.fill((0, 0, 0, alpha))
            screen.blit(overlay, (0, 0))
    
    def enter(self):
        """Called when entering this state"""
        self.transition_progress = 0.0
        self.transition_in = True
    
    def exit(self):
        """Called when exiting this state"""
        pass
    
    def start_transition_out(self, callback=None):
        """Start transitioning out of this state
        
        Args:
            callback (function): Function to call when transition completes
        """
        self.transition_in = False
        self.transition_callback = callback
    
    def resume(self):
        """Called when this state is resumed (becomes active again)"""
        pass
    
    def pause(self):
        """Called when this state is paused (another state is pushed on top)"""
        pass 