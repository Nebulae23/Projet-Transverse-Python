"""
Magic Survivor - Main Module

This module contains the entry point for the game.
"""

import os
import sys
import pygame
from src.game_manager import GameManager
from src.data_handler import DataHandler
from src import config

def setup_data_directories():
    """Set up the data directories if they don't exist"""
    # Create data directory
    os.makedirs(config.DATA_DIR, exist_ok=True)
    
    # Create asset directories
    os.makedirs(config.FONT_DIR, exist_ok=True)
    os.makedirs(config.EFFECTS_DIR, exist_ok=True)
    os.makedirs(config.MUSIC_DIR, exist_ok=True)
    
    # Create sprite directories
    os.makedirs(config.PLAYER_SPRITES, exist_ok=True)
    os.makedirs(config.ENEMY_SPRITES, exist_ok=True)
    os.makedirs(config.PROJECTILE_SPRITES, exist_ok=True)
    os.makedirs(config.ITEM_SPRITES, exist_ok=True)
    os.makedirs(config.BUILDING_SPRITES, exist_ok=True)
    os.makedirs(config.UI_SPRITES, exist_ok=True)

def check_hardware():
    """Check hardware capabilities and set up the best rendering options"""
    # Initialize pygame
    pygame.init()
    
    # Check for GPU acceleration
    # Note: This is a basic check, not a comprehensive one
    renderers = [pygame.display.get_driver()]
    print(f"Available renderers: {renderers}")
    
    # Check display info
    display_info = pygame.display.Info()
    print(f"Display info: {display_info.current_w}x{display_info.current_h}, {display_info.bitsize} bits")
    
    # Set video mode flags based on hardware capabilities
    flags = pygame.HWSURFACE | pygame.DOUBLEBUF
    
    # Check if fullscreen is possible
    # Note: We're not using fullscreen by default
    # if display_info.current_w >= config.SCREEN_WIDTH and display_info.current_h >= config.SCREEN_HEIGHT:
    #     flags |= pygame.FULLSCREEN
    
    return flags

def setup_default_assets():
    """Set up default assets if they don't exist"""
    # Create placeholder player sprite if it doesn't exist
    player_sprite_path = os.path.join(config.PLAYER_SPRITES, "player.png")
    if not os.path.exists(player_sprite_path):
        # Create a simple placeholder sprite
        player_surface = pygame.Surface((32, 32))
        player_surface.fill((0, 0, 255))  # Blue rectangle
        pygame.draw.rect(player_surface, (200, 200, 255), (8, 8, 16, 16))
        pygame.image.save(player_surface, player_sprite_path)
        print(f"Created placeholder player sprite at {player_sprite_path}")
    
    # Create placeholder enemy sprite if it doesn't exist
    enemy_sprite_path = os.path.join(config.ENEMY_SPRITES, "enemy.png")
    if not os.path.exists(enemy_sprite_path):
        # Create a simple placeholder sprite
        enemy_surface = pygame.Surface((32, 32))
        enemy_surface.fill((255, 0, 0))  # Red rectangle
        pygame.draw.rect(enemy_surface, (255, 200, 200), (8, 8, 16, 16))
        pygame.image.save(enemy_surface, enemy_sprite_path)
        print(f"Created placeholder enemy sprite at {enemy_sprite_path}")
    
    # Create placeholder projectile sprite if it doesn't exist
    projectile_sprite_path = os.path.join(config.PROJECTILE_SPRITES, "projectile.png")
    if not os.path.exists(projectile_sprite_path):
        # Create a simple placeholder sprite
        projectile_surface = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(projectile_surface, (0, 255, 255), (8, 8), 6)
        pygame.image.save(projectile_surface, projectile_sprite_path)
        print(f"Created placeholder projectile sprite at {projectile_sprite_path}")
    
    # Create placeholder building sprite if it doesn't exist
    building_sprite_path = os.path.join(config.BUILDING_SPRITES, "building.png")
    if not os.path.exists(building_sprite_path):
        # Create a simple placeholder sprite
        building_surface = pygame.Surface((64, 64))
        building_surface.fill((150, 150, 150))  # Gray rectangle
        pygame.draw.rect(building_surface, (100, 100, 100), (8, 8, 48, 48))
        pygame.draw.rect(building_surface, (50, 50, 50), (24, 32, 16, 32))  # Door
        pygame.image.save(building_surface, building_sprite_path)
        print(f"Created placeholder building sprite at {building_sprite_path}")

def main():
    """Main entry point for the game"""
    # Setup data directories
    setup_data_directories()
    
    # Check hardware and get optimal video flags
    video_flags = check_hardware()
    
    # Initialize pygame with the optimal settings
    pygame.init()
    pygame.display.set_mode(config.SCREEN_SIZE, video_flags)
    pygame.display.set_caption("Magic Survivor")
    
    # Create default game data if it doesn't exist
    DataHandler.create_default_files()
    
    # Setup default assets (placeholder sprites)
    setup_default_assets()
    
    # Create and run the game - GameManager will initialize with MainMenuState
    game_manager = GameManager()
    
    try:
        # Run the game
        game_manager.run()
    except Exception as e:
        # Handle any unexpected errors
        print(f"Error in game: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up pygame
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()