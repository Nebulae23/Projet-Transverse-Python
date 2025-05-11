"""
Magic Survivor - Night Phase

This module handles the night phase of the game (the survivor/combat phase).
"""

import pygame
import math
import random
from src import config
from src.game_state_base import GameState
from src.game_manager import PauseState
from src.player_character import Player
from src.projectile_system import ProjectileManager
from src.enemy_system import EnemyManager
from src.spell_system import SpellManager
from src.relic_system import RelicManager, Relic
from src.ui_manager import UIManager, Button, ProgressBar, TextBox

class NightPhaseState(GameState):
    """Night phase game state (survivor combat)"""
    
    def __init__(self, game_manager, player_data_dict, current_day_number):
        """Initialize the night phase state
        
        Args:
            game_manager (GameManager): Reference to the game manager
            player_data_dict (dict): Dictionary containing player's saved data.
            current_day_number (int): The current day number.
        """
        super().__init__(game_manager)
        self.player_session_data = player_data_dict
        self.current_day = current_day_number
        self.current_frame_events = []
        
        # Create player
        self.player = Player(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2, self.game_manager)
        
        # Subsystems
        self.projectile_manager = self.game_manager.projectile_manager
        self.enemy_manager = EnemyManager()
        self.spell_manager = SpellManager()
        self.relic_manager = RelicManager()
        self.ui_manager = UIManager()
        
        # Load player data
        self.spell_manager.load_player_spells(self.player_session_data)
        self.relic_manager.load_player_relics(self.player_session_data)
        
        # Apply relic effects to player
        self.relic_manager.apply_stat_effects(self.player)
        
        # UI elements
        self.setup_ui()
        
        # State variables
        self.wave_complete = False
        self.wave_end_timer = 0
        self.relic_choice_active = False
        self.relic_choices = []
        self.paused = False
        self.game_over = False
        
        # Wall definitions
        self.wall_rects = {}
        self.wall_rects["top"] = pygame.Rect(0, 0, config.SCREEN_WIDTH, config.CITY_WALL_THICKNESS)
        self.wall_rects["bottom"] = pygame.Rect(0, config.SCREEN_HEIGHT - config.CITY_WALL_THICKNESS, config.SCREEN_WIDTH, config.CITY_WALL_THICKNESS)
        self.wall_rects["left"] = pygame.Rect(0, 0, config.CITY_WALL_THICKNESS, config.SCREEN_HEIGHT)
        self.wall_rects["right"] = pygame.Rect(config.SCREEN_WIDTH - config.CITY_WALL_THICKNESS, 0, config.CITY_WALL_THICKNESS, config.SCREEN_HEIGHT)

        # Start the first wave
        self.enemy_manager.start_night(self.current_day)
    
    def setup_ui(self):
        """Set up the UI elements"""
        # Health bar
        self.ui_manager.add_element("health_bar", ProgressBar(
            x=10,
            y=10,
            width=200,
            height=20,
            value=self.player.current_hp,
            max_value=self.player.max_hp,
            color=config.GREEN
        ))
        
        # XP bar
        self.ui_manager.add_element("xp_bar", ProgressBar(
            x=10,
            y=40,
            width=200,
            height=10,
            value=self.player.xp,
            max_value=self.player.xp_to_next_level,
            color=config.BLUE
        ))
        
        # Level display
        self.ui_manager.add_element("level_text", TextBox(
            x=220,
            y=10,
            width=50,
            height=20,
            text=f"Lv {self.player.level}",
            text_color=config.WHITE
        ))
        
        # Timer display
        self.ui_manager.add_element("wave_timer", TextBox(
            x=config.SCREEN_WIDTH - 100,
            y=10,
            width=90,
            height=20,
            text="Wave 1",
            text_color=config.WHITE,
            alignment="right"
        ))

        # City Health UI
        city_health_label_x = config.SCREEN_WIDTH // 2 - 100
        city_health_label_y = 10 
        city_health_label_width = 200
        city_health_label_height = 20 

        city_health_bar_x = city_health_label_x
        city_health_bar_y = city_health_label_y + city_health_label_height + 5 # Bar below label
        city_health_bar_width = city_health_label_width
        city_health_bar_height = 20

        self.ui_manager.add_element("city_health_label", TextBox(
            x=city_health_label_x,
            y=city_health_label_y,
            width=city_health_label_width,
            height=city_health_label_height,
            text="City Health",
            font_size=18,
            text_color=config.WHITE,
            alignment="center"
        ))

        self.ui_manager.add_element("city_health_bar", ProgressBar(
            x=city_health_bar_x,
            y=city_health_bar_y,
            width=city_health_bar_width,
            height=city_health_bar_height,
            value=self.game_manager.city_current_hp,
            max_value=self.game_manager.city_max_hp,
            color=config.CYAN,
            background_color=config.DARK_GRAY,
            border_color=config.WHITE
        ))
    
    def handle_events(self, events):
        """Handle events in the night phase"""
        self.current_frame_events = events
        
        for event in events:
            if event.type == pygame.QUIT:
                self.game_manager.quit_game()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.relic_choice_active:
                        # If relic choice is active, ESC might cancel it or do nothing
                        pass # Or self.cancel_relic_choice() if implemented
                    else:
                        self.game_manager.push_state(PauseState(self.game_manager))
                # Test keybinds for different spells
                elif event.key == pygame.K_1: # Cast Basic Homing Projectile
                    projectile = self.player.cast_spell("basic_projectile", *pygame.mouse.get_pos())
                    if projectile:
                        self.projectile_manager.add_projectile(projectile)
                elif event.key == pygame.K_2: # Cast Orbiting Blades
                    projectile = self.player.cast_spell("orbiting_blades", *pygame.mouse.get_pos()) # Target pos might be ignored by orbiting
                    if projectile:
                        self.projectile_manager.add_projectile(projectile)
                elif event.key == pygame.K_3: # Cast Fireball (Straight)
                    projectile = self.player.cast_spell("fireball", *pygame.mouse.get_pos())
                    if projectile:
                        self.projectile_manager.add_projectile(projectile)
                elif event.key == pygame.K_4: # Cast Wave Pulse (Sine Wave)
                    projectile = self.player.cast_spell("wave_pulse", *pygame.mouse.get_pos())
                    if projectile:
                        self.projectile_manager.add_projectile(projectile)
                elif event.key == pygame.K_5: # Cast Returning Disk (Boomerang)
                    projectile = self.player.cast_spell("returning_disk", *pygame.mouse.get_pos())
                    if projectile:
                        self.projectile_manager.add_projectile(projectile)
                elif event.key == pygame.K_6: # Cast Chain Spark
                    projectile = self.player.cast_spell("chain_spark", *pygame.mouse.get_pos())
                    if projectile:
                        self.projectile_manager.add_projectile(projectile)
                elif event.key == pygame.K_7: # Cast Piercing Bolt
                    projectile = self.player.cast_spell("piercing_bolt", *pygame.mouse.get_pos())
                    if projectile:
                        self.projectile_manager.add_projectile(projectile)
                elif event.key == pygame.K_8: # Cast Meteor Shard (Ground AOE)
                    projectile = self.player.cast_spell("meteor_shard", *pygame.mouse.get_pos())
                    if projectile:
                        self.projectile_manager.add_projectile(projectile)
                elif event.key == pygame.K_9: # Cast Forking Bolt
                    projectile = self.player.cast_spell("forking_bolt", *pygame.mouse.get_pos())
                    if projectile:
                        self.projectile_manager.add_projectile(projectile)
                elif event.key == pygame.K_0: # Cast Spiral Blast
                    projectile = self.player.cast_spell("spiral_blast", *pygame.mouse.get_pos())
                    if projectile:
                        self.projectile_manager.add_projectile(projectile)
                elif event.key == pygame.K_g: # Cast Growing Orb
                    projectile = self.player.cast_spell("growing_orb_spell", *pygame.mouse.get_pos())
                    if projectile:
                        self.projectile_manager.add_projectile(projectile)
                        
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Manual attack (base projectile spell via click)
                if not self.relic_choice_active:
                    projectile = self.player.handle_basic_attack(*event.pos) # Unpack tuple
                    if projectile:
                        self.projectile_manager.add_projectile(projectile)
        
        # Handle UI clicks (now done in UIManager directly)
    
    def update(self, dt):
        """Update the night phase
        
        Args:
            dt (float): Time elapsed since last update in seconds
        """
        # Standard game logic updates if not paused by relic choice or game over
        if not (self.relic_choice_active or self.game_over):
            # Update player
            keys_pressed = pygame.key.get_pressed()
            self.player.update(dt, keys_pressed)
            
            # Update projectiles
            self.projectile_manager.update(dt, self.enemy_manager.get_enemies())
            
            # Update enemies
            self.enemy_manager.update(dt, (self.player.rect.centerx, self.player.rect.centery), self.wall_rects, self.damage_city)
            
            # Update spells
            new_projectiles = self.spell_manager.update(
                dt, 
                self.player.rect.centerx, 
                self.player.rect.centery, 
                self.enemy_manager.get_enemies()
            )
            for projectile in new_projectiles:
                self.projectile_manager.add_projectile(projectile)
            
            # Check for collisions
            self.check_collisions()
            
            # Check wave status
            if self.wave_complete:
                self.wave_end_timer -= dt
                if self.wave_end_timer <= 0:
                    if self.enemy_manager.is_night_complete():
                        self.transition_to_day()
                    else:
                        self.offer_relic_choice()
            elif self.enemy_manager.is_wave_complete():
                self.wave_complete = True
                self.wave_end_timer = 3.0
            
            # Update specific UI elements values (dynamic ones)
            if self.ui_manager.get_element("health_bar"):
                 self.ui_manager.get_element("health_bar").update_value(self.player.current_hp)
            if self.ui_manager.get_element("xp_bar"):
                self.ui_manager.get_element("xp_bar").update_value(self.player.xp)
            if self.ui_manager.get_element("level_text"):
                self.ui_manager.get_element("level_text").set_text(f"Lv {self.player.level}")
            if self.ui_manager.get_element("city_health_bar"):
                self.ui_manager.get_element("city_health_bar").update_value(self.game_manager.city_current_hp)
            
            # Check for city game over
            if self.game_manager.city_current_hp <= 0 and not self.game_over:
                self.game_over = True
                self.game_manager.city_current_hp = 0
                self.setup_game_over_ui()

        # Always update the UI Manager with all events for the frame
        # This handles hover states and click processing for all UI elements
        clicked_elements = self.ui_manager.update(pygame.mouse.get_pos(), self.current_frame_events, dt)

        # Process UI clicks
        for element_id, click_data in clicked_elements.items():
            if element_id.startswith("relic_choice_") and self.relic_choice_active:
                if isinstance(click_data, int): # Expecting index from on_click_data
                    self.select_relic(click_data)
                else:
                    print(f"Warning: Relic choice button {element_id} click_data was not an int: {click_data}")
            elif element_id == "return_button" and click_data == "return_to_menu" and self.game_over:
                from src.game_manager import MainMenuState # Local import
                self.game_manager.clear_states()
                self.game_manager.push_state(MainMenuState(self.game_manager))
    
    def check_collisions(self):
        """Check for collisions between game objects"""
        # Projectile-enemy collisions
        collisions = self.projectile_manager.check_enemy_collisions(self.enemy_manager.get_enemies())
        
        # Process enemy damage and death
        dead_enemies = []
        for enemy, projectile, damage in collisions:
            if not enemy.take_damage(damage):
                dead_enemies.append(enemy)
        
        # Handle enemy deaths and award XP
        if dead_enemies:
            total_xp = self.enemy_manager.handle_enemy_deaths(dead_enemies)
            # Award XP to player
            if self.player.gain_xp(total_xp):
                # Player leveled up
                self.handle_level_up()
        
        # Enemy-player collisions
        for enemy in self.enemy_manager.get_enemies():
            if pygame.sprite.collide_rect(enemy, self.player):
                if enemy.can_attack():
                    damage = enemy.get_attack_damage()
                    if not self.player.take_damage(damage):
                        self.game_over = True
                        self.setup_game_over_ui()
                    enemy.attack_performed()
    
    def handle_level_up(self):
        """Handle player leveling up"""
        # Update XP bar with new max
        self.ui_manager.get_element("xp_bar").max_value = self.player.xp_to_next_level
        
        # TODO: Offer temporary upgrades during night phase
    
    def offer_relic_choice(self):
        """Offer a choice of relics to the player"""
        self.relic_choice_active = True
        self.relic_choices = self.relic_manager.get_relic_choices(3)
        
        # Create UI for relic choice
        self.setup_relic_choice_ui()
    
    def setup_relic_choice_ui(self):
        """Set up the UI for relic choice"""
        # Title
        self.ui_manager.add_element("relic_choice_title", TextBox(
            x=config.SCREEN_WIDTH // 2 - 150,
            y=100,
            width=300,
            height=40,
            text="Choose a Relic",
            text_color=config.WHITE,
            font_size=36,
            alignment="center"
        ))
        
        # Relic choices
        for i, relic_data in enumerate(self.relic_choices):
            relic = Relic(f"choice_{i}", relic_data)
            x = config.SCREEN_WIDTH // 2 - 150
            y = 200 + i * 120
            
            # Background
            self.ui_manager.add_element(f"relic_choice_bg_{i}", TextBox(
                x=x,
                y=y,
                width=300,
                height=100,
                background_color=config.GRAY,
                border_color=config.BLACK
            ))
            
            # Name
            self.ui_manager.add_element(f"relic_choice_name_{i}", TextBox(
                x=x + 10,
                y=y + 10,
                width=280,
                height=20,
                text=relic.name,
                text_color=config.BLACK,
                font_size=24,
                alignment="left"
            ))
            
            # Description
            self.ui_manager.add_element(f"relic_choice_desc_{i}", TextBox(
                x=x + 10,
                y=y + 40,
                width=280,
                height=50,
                text=relic.description,
                text_color=config.BLACK,
                font_size=16,
                alignment="left"
            ))
            
            # Button (invisible, but clickable)
            self.ui_manager.add_element(f"relic_choice_{i}", Button(
                x=x,
                y=y,
                width=300,
                height=100,
                text="",
                color=(0, 0, 0, 0),  # Invisible
                hover_color=(255, 255, 255, 50),  # Semi-transparent white on hover
                on_click_data=i
            ))
    
    def select_relic(self, index):
        """Select a relic from the choices
        
        Args:
            index (int): Index of the chosen relic
        """
        if 0 <= index < len(self.relic_choices):
            relic_data = self.relic_choices[index]
            relic_id = list(self.relic_manager.relic_data.keys())[
                list(self.relic_manager.relic_data.values()).index(relic_data)
            ]
            
            # Add the relic to the player
            self.relic_manager.add_relic(relic_id)
            self.player_session_data["relics"].append(relic_id)
            
            # Apply the relic's effects
            self.relic_manager.apply_stat_effects(self.player)
            
            # Clear relic choice UI
            self.clear_relic_choice_ui()
            
            # Continue to the next wave
            self.relic_choice_active = False
            self.wave_complete = False
            self.enemy_manager._start_wave(self.enemy_manager.current_wave + 1)
    
    def clear_relic_choice_ui(self):
        """Clear the relic choice UI elements"""
        # Remove all relic choice UI elements
        elements_to_remove = []
        for element_id in self.ui_manager.elements:
            if element_id.startswith("relic_choice_"):
                elements_to_remove.append(element_id)
        
        for element_id in elements_to_remove:
            self.ui_manager.remove_element(element_id)
    
    def damage_city(self, amount):
        """Callback function for enemies to damage the city."""
        if not self.game_over: # Don't continue damaging if game is already over
            self.game_manager.city_current_hp -= amount
            # Health clamping to 0 will be handled in update or game over check

    def setup_game_over_ui(self):
        """Set up the game over UI"""
        game_over_message = "Game Over"
        if self.player.current_hp <= 0:
            game_over_message = "You have fallen!"
        elif self.game_manager.city_current_hp <= 0:
            game_over_message = "The city has fallen!"

        # Game over text
        self.ui_manager.add_element("game_over_text", TextBox(
            x=config.SCREEN_WIDTH // 2 - 150,
            y=config.SCREEN_HEIGHT // 2 - 50,
            width=300,
            height=60,
            text=game_over_message,
            text_color=config.RED,
            font_size=48,
            alignment="center"
        ))
        
        # Return to menu button
        self.ui_manager.add_element("return_button", Button(
            x=config.SCREEN_WIDTH // 2 - 100,
            y=config.SCREEN_HEIGHT // 2 + 50,
            width=200,
            height=40,
            text="Return to Menu",
            color=config.GRAY,
            hover_color=config.WHITE,
            text_color=config.BLACK,
            on_click_data="return_to_menu"
        ))
    
    def transition_to_day(self):
        """Transition back to the day phase"""
        from src.day_night_manager import DayPhaseState
        self.game_manager.change_state(DayPhaseState(self.game_manager, load_saved=True))
    
    def render(self, screen):
        """Render the night phase
        
        Args:
            screen (pygame.Surface): Screen to render to
        """
        # Fill the screen with a "night" color
        screen.fill((25, 25, 50))  # Dark blue for night
        
        # Render walls
        for wall_side, rect in self.wall_rects.items():
            pygame.draw.rect(screen, config.CITY_WALL_COLOR, rect)

        # Render game objects
        self.projectile_manager.render(screen)
        self.enemy_manager.render(screen)
        
        # Render player
        screen.blit(self.player.image, self.player.rect)
        
        # Render UI elements
        self.ui_manager.render(screen)
    
    def enter(self):
        """Called when entering the night phase state"""
        pass
    
    def exit(self):
        """Called when exiting the night phase state"""
        pass 