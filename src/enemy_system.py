"""
Magic Survivor - Enemy System

This module handles the enemy system, including enemy classes and the enemy manager.
"""

import pygame
import math
import random
import uuid # Added for unique enemy IDs
from src import config
from src.data_handler import DataHandler

class Enemy(pygame.sprite.Sprite):
    """Base enemy class"""
    
    def __init__(self, enemy_id, x, y, enemy_type, enemy_data):
        """Initialize an enemy
        
        Args:
            enemy_id (str): Unique ID for the enemy.
            x (float): Initial x position
            y (float): Initial y position
            enemy_type (str): Type of enemy
            enemy_data (dict): Enemy data from DataHandler
        """
        super().__init__()
        self.id = enemy_id # Store unique ID
        self.active = True # Flag to track if the enemy is active
        
        # Store enemy type and data
        self.enemy_type = enemy_type
        self.data = enemy_data
        
        # Create a simple red square placeholder
        self.radius = 16  # Radius for collision detection (can be adjusted if square size changes significantly)
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        
        # Red color for the square
        fill_color = (255, 0, 0) # Red
        # Optional: border_color = (0, 0, 0) # Black border
        
        # Draw a red square
        # The rect is (left, top, width, height)
        # To center a 32x32 square on a 32x32 surface, it's (0, 0, 32, 32)
        pygame.draw.rect(self.image, fill_color, (0, 0, 32, 32))
        # Optional: to draw a border
        # pygame.draw.rect(self.image, border_color, (0, 0, 32, 32), 2) # 2 is border thickness
        
        # Position and movement
        self.rect = self.image.get_rect(center=(x, y))
        self.x = float(x)
        self.y = float(y)
        self.speed = self.data.get("speed", 2)
        self.vx = 0  # Initialize velocity components
        self.vy = 0
        
        # Combat stats
        self.max_hp = self.data.get("health", 30)
        self.current_hp = self.max_hp
        self.attack_damage = self.data.get("damage", 5)
        self.attack_cooldown = self.data.get("attack_cooldown", 1.5) # Time between attacks
        self.attack_cooldown_timer = 0.0
        self.is_attacking_wall = False
        self.xp_reward = self.data.get("xp_reward", 10)
        
        # Add health bar above enemy - MOVED here after combat stats initialization
        self.health_width = 30
        self.health_height = 4
        self.health_x = 1
        self.health_y = -6
        self._update_health_bar()
        
        # AI and behavior
        self.state = "chase"  # "chase", "attack", "flee", etc.
        self.attack_timer = 0
    
    def update(self, dt, player_pos, wall_rects, damage_city_callback):
        """Update the enemy
        
        Args:
            dt (float): Time elapsed since last update in seconds
            player_pos (tuple): Player's position (x, y)
            wall_rects (dict): Dictionary of wall rectangles
            damage_city_callback (callable): Callback for damaging the city
        """
        if not self.active:
            return

        # Calculate city center position from wall_rects if available
        city_center_pos = player_pos  # Default to player position if no walls
        if isinstance(wall_rects, dict) and wall_rects:
            # Calculate the center of the city from the wall rects
            x_positions = []
            y_positions = []
            for wall_key, wall_r in wall_rects.items():
                x_positions.extend([wall_r.left, wall_r.right])
                y_positions.extend([wall_r.top, wall_r.bottom])
            
            if x_positions and y_positions:
                city_center_x = sum(x_positions) / len(x_positions)
                city_center_y = sum(y_positions) / len(y_positions)
                city_center_pos = (city_center_x, city_center_y)

        # Standard movement towards city_center_pos if not attacking wall
        if not self.is_attacking_wall:
            old_x, old_y = self.rect.centerx, self.rect.centery
            
            dx = city_center_pos[0] - self.rect.centerx
            dy = city_center_pos[1] - self.rect.centery
            distance = math.hypot(dx, dy)

            if distance > 0:
                self.vx = dx / distance
                self.vy = dy / distance
            else:
                self.vx, self.vy = 0, 0
            
            # Store calculated velocity values
            calculated_vx = self.vx
            calculated_vy = self.vy
            
            # Apply the movement
            # Add proper timestep scaling - this is likely the issue
            move_speed = self.speed * dt
            self.rect.x += self.vx * move_speed
            self.rect.y += self.vy * move_speed
            
            # Update self.x and self.y to match rect position (these were likely not being updated)
            self.x = self.rect.centerx
            self.y = self.rect.centery
            
            # Debug output for movement
            # Only print occasionally to avoid console spam
            if random.random() < 0.01:  # 1% chance to print each update
                print(f"Enemy {self.enemy_type} moved from ({old_x}, {old_y}) to ({self.rect.centerx}, {self.rect.centery})")
                print(f"  Distance to target: {distance}")
                print(f"  Velocity: ({calculated_vx}, {calculated_vy})")
                print(f"  Move amount: {move_speed}")
                print(f"  Target: {city_center_pos}")

        # Check for wall collision
        collided_wall_key = None
        if isinstance(wall_rects, dict) and wall_rects:
            for wall_key, wall_r in wall_rects.items():
                if self.rect.colliderect(wall_r):
                    self.is_attacking_wall = True
                    collided_wall_key = wall_key # Store which wall was hit
                    # Simple pushback to prevent sinking into the wall
                    if wall_key == "top": self.rect.top = wall_r.bottom
                    elif wall_key == "bottom": self.rect.bottom = wall_r.top
                    elif wall_key == "left": self.rect.left = wall_r.right
                    elif wall_key == "right": self.rect.right = wall_r.left
                    self.vx, self.vy = 0, 0 # Stop moving
                    break
            
            if self.is_attacking_wall:
                if callable(damage_city_callback) and self.can_attack(): 
                    damage_city_callback(self.get_attack_damage()) 
                    self.attack_performed() # Resets attack_cooldown_timer
            else: 
                # If not currently colliding, it's not attacking a wall.
                # This handles cases where it might have been pushed back.
                is_still_colliding = False
                for wall_r in wall_rects.values(): # Re-check all walls
                    if self.rect.colliderect(wall_r):
                        is_still_colliding = True
                        break
                if not is_still_colliding:
                    self.is_attacking_wall = False
        else:
            self.is_attacking_wall = False

        self.update_animation(dt)
    
    def _update_health_bar(self):
        """Update the health bar to reflect current health"""
        # Only need to update the part of the image containing the health bar
        # Clear the area first
        pygame.draw.rect(self.image, (0, 0, 0, 0), (self.health_x, self.health_y, self.health_width, self.health_height), 0, 0, pygame.SRCALPHA)
        
        # Background
        pygame.draw.rect(self.image, (50, 50, 50), (self.health_x, self.health_y, self.health_width, self.health_height))
        
        # Health fill - scale width based on current/max health
        health_percentage = max(0, self.current_hp / self.max_hp)
        current_health_width = int(self.health_width * health_percentage)
        pygame.draw.rect(self.image, (255, 0, 0), (self.health_x, self.health_y, current_health_width, self.health_height))

    def take_damage(self, amount):
        """Take damage
        
        Args:
            amount (float): Amount of damage to take
            
        Returns:
            bool: True if the enemy is still alive, False otherwise
        """
        self.current_hp -= amount
        self._update_health_bar()  # Update health bar after taking damage
        return self.current_hp > 0
    
    def is_in_attack_range(self, player_pos):
        """Check if the player is in attack range
        
        Args:
            player_pos (tuple): Player's position (x, y)
            
        Returns:
            bool: True if in range, False otherwise
        """
        # Calculate distance to player
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # For now, consider melee range only (enemy radius + player radius)
        return distance < self.radius + 16  # 16 is assumed player radius
    
    def get_attack_damage(self):
        """Get the attack damage
        
        Returns:
            float: Attack damage
        """
        return self.attack_damage
    
    def can_attack(self):
        """Check if the enemy can attack
        
        Returns:
            bool: True if can attack, False otherwise
        """
        return self.attack_cooldown_timer <= 0
    
    def attack_performed(self):
        """Called after an attack is performed"""
        self.attack_cooldown_timer = self.attack_cooldown
    
    def get_xp_reward(self):
        """Get the XP reward for defeating this enemy
        
        Returns:
            float: XP reward
        """
        return self.xp_reward

    def update_animation(self, dt):
        """Update any animation frames for the enemy
        
        Args:
            dt (float): Time elapsed since last update in seconds
        """
        # For now, just decrement the attack cooldown timer
        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= dt
        
        # Animation switching would go here when sprite sheets are implemented
        pass

    def render(self, screen, camera=None):
        """Render the enemy
        
        Args:
            screen (pygame.Surface): Screen to render to
            camera (Camera): Optional camera object for rendering
        """
        if self.active:
            if camera:
                # If we have a camera, use it to offset the rendering position
                adjusted_rect = camera.apply(self)
                screen.blit(self.image, adjusted_rect)
                
                # Add enemy type label below the enemy
                try:
                    # Get font - use a small size
                    font = pygame.font.Font(None, 16) 
                    # Create the label surface
                    enemy_name = self.data.get("name", self.enemy_type.capitalize())
                    label = font.render(enemy_name, True, (255, 255, 255))
                    # Position it below the enemy, centered
                    label_x = adjusted_rect.centerx - label.get_width() // 2
                    label_y = adjusted_rect.bottom + 2
                    screen.blit(label, (label_x, label_y))
                except Exception as e:
                    # In case of font issues, just skip the label
                    print(f"Error rendering enemy label: {e}")
            else:
                # Otherwise just draw at the normal position
                screen.blit(self.image, self.rect)
                
                # Draw label when not using camera as well
                try:
                    font = pygame.font.Font(None, 16)
                    enemy_name = self.data.get("name", self.enemy_type.capitalize())
                    label = font.render(enemy_name, True, (255, 255, 255))
                    label_x = self.rect.centerx - label.get_width() // 2
                    label_y = self.rect.bottom + 2
                    screen.blit(label, (label_x, label_y))
                except Exception as e:
                    print(f"Error rendering enemy label: {e}")

    def get_render_sort_key(self):
        """Get the Y-coordinate for render sorting
        
        Returns:
            float: Y-coordinate for sorting (higher values rendered on top)
        """
        # Use the bottom of the sprite for Y-sorting
        return self.rect.bottom


class EnemyManager:
    """Manages enemies in the game"""
    
    def __init__(self):
        """Initialize the enemy manager"""
        self.enemies = pygame.sprite.Group()
        self.enemy_data = DataHandler.load_enemies()
        self.waves_data = DataHandler.load_waves()
        
        # Wave control
        self.current_day = 1
        self.current_wave = 0
        self.wave_timer = 0
        self.spawn_timers = {}  # Dict of {enemy_type: timer}
        
        # Placeholders for enemy types to spawn in current wave
        self.current_wave_data = None
    
    def start_night(self, day):
        """Start a night with waves based on the day
        
        Args:
            day (int): Current day number
        """
        self.current_day = day
        self.current_wave = 0
        
        # Clear any existing enemies
        self.enemies.empty()
        
        # Get wave data for this day
        day_key = f"day_{day}"
        
        # Get all waves data and extract the specific day
        if day_key in self.waves_data:
            self.day_waves = self.waves_data[day_key]
        else:
            # If no specific data for this day, use day 1 or generate random waves
            print(f"No wave data found for day {day}, using day_1 data instead")
            self.day_waves = self.waves_data.get("day_1", {"waves": []})
        
        # Print wave data for debugging
        print(f"Day {day} waves data: {self.day_waves}")
        
        # Create a default wave if none exists
        if not self.day_waves.get("waves", []):
            print("No waves found, creating default wave")
            self.day_waves = {
                "waves": [
                    {
                        "enemies": [
                            {"type": "slime", "count": 10, "interval": 1.0}
                        ],
                        "duration": 60
                    }
                ]
            }
        
        # Start the first wave
        self._start_wave(0)
    
    def _start_wave(self, wave_index):
        """Start a specific wave
        
        Args:
            wave_index (int): Index of the wave to start
        """
        if wave_index < len(self.day_waves.get("waves", [])):
            self.current_wave = wave_index
            self.current_wave_data = self.day_waves["waves"][wave_index]
            self.wave_timer = self.current_wave_data.get("duration", 60)
            
            # Print details for debugging
            print(f"Starting wave {wave_index+1} with {len(self.current_wave_data.get('enemies', []))} enemy types")
            print(f"Wave data: {self.current_wave_data}")
            
            # Initialize spawn timers
            self.spawn_timers = {}
            for enemy_spawn in self.current_wave_data.get("enemies", []):
                enemy_type = enemy_spawn.get("type", "slime")
                self.spawn_timers[enemy_type] = 0  # Start spawning immediately
                print(f"Will spawn {enemy_spawn.get('count', 0)} {enemy_type} every {enemy_spawn.get('interval', 1.0)} seconds")
        else:
            print(f"Wave index {wave_index} is out of range, no more waves")
            self.current_wave_data = None
            self.wave_timer = 0
    
    def update(self, dt, player_pos, wall_rects, damage_city_callback):
        """Update all enemies and handle spawning logic."""
        # Update existing enemies
        for enemy in list(self.enemies): # Iterate on a copy for safe removal
            enemy.update(dt, player_pos, wall_rects, damage_city_callback)
            if not enemy.active:
                self.enemies.remove(enemy)
        
        # Update wave timer
        if self.current_wave_data:
            self.wave_timer -= dt
            if self.wave_timer <= 0:
                # Wave is over, start the next one
                print(f"Wave {self.current_wave + 1} ended. Starting wave {self.current_wave + 2}")
                self._start_wave(self.current_wave + 1)
            else:
                # Update spawn timers and spawn enemies
                self._handle_enemy_spawning(dt, player_pos)
                
                # Debug output every 5 seconds (using modulo on wave_timer)
                if int(self.wave_timer) % 5 == 0 and self.wave_timer % 1 < dt:
                    print(f"Wave {self.current_wave + 1} in progress: {self.wave_timer:.1f}s left, {len(self.enemies)} enemies active")
    
    def _handle_enemy_spawning(self, dt, player_pos):
        """Handle enemy spawning based on wave data
        
        Args:
            dt (float): Time elapsed since last update in seconds
            player_pos (tuple): Player's position (x, y)
        """
        if not self.current_wave_data:
            return
        
        for enemy_spawn in self.current_wave_data.get("enemies", []):
            enemy_type = enemy_spawn.get("type", "slime")
            
            # Update spawn timer
            if enemy_type in self.spawn_timers:
                self.spawn_timers[enemy_type] -= dt
                
                # Spawn an enemy if timer expired and count not exceeded
                if self.spawn_timers[enemy_type] <= 0:
                    # Reset timer
                    self.spawn_timers[enemy_type] = enemy_spawn.get("interval", 1.0)
                    
                    # Check if we've spawned enough of this type
                    spawned_count = sum(1 for enemy in self.enemies if enemy.enemy_type == enemy_type)
                    max_count = enemy_spawn.get("count", 10)
                    
                    if spawned_count < max_count:
                        print(f"Spawning {enemy_type}: {spawned_count+1}/{max_count}")
                        self._spawn_enemy(enemy_type, player_pos)
                    elif spawned_count >= max_count:
                        # Debug: Already reached max count
                        if int(self.wave_timer) % 10 == 0 and self.wave_timer % 1 < dt:
                            print(f"Max count reached for {enemy_type}: {spawned_count}/{max_count}")
            else:
                # This shouldn't normally happen - timer missing for an enemy type
                print(f"Warning: Spawn timer not initialized for {enemy_type} in wave {self.current_wave+1}")
    
    def _spawn_enemy(self, enemy_type, player_pos):
        """Spawn an enemy of a specific type
        
        Args:
            enemy_type (str): Type of enemy to spawn
            player_pos (tuple): Player's position (x, y)
        """
        enemy_data = self.enemy_data.get(enemy_type)
        if not enemy_data:
            print(f"Warning: Unknown enemy type: {enemy_type}")
            return
        
        # Ensure enemy has a proper speed that's not too slow
        if "speed" not in enemy_data or enemy_data["speed"] < 30:
            enemy_data = enemy_data.copy()  # Make a copy to avoid modifying the original
            
            # Set higher speed values based on enemy type
            if enemy_type == "slime":
                enemy_data["speed"] = 40
            elif enemy_type == "goblin":
                enemy_data["speed"] = 60
            elif enemy_type == "skeleton":
                enemy_data["speed"] = 45
            else:
                enemy_data["speed"] = 50  # Default for unknown enemy types
                
            print(f"Set {enemy_type} speed to {enemy_data['speed']}")
        
        # Generate spawn position at the edge of the map
        # Choose one of the four map edges
        edge = random.choice(["top", "bottom", "left", "right"])
        
        # Map dimensions - conservative estimates in case the actual map is smaller
        MAP_WIDTH = 2560  # Using estimates, adjust based on your actual map size
        MAP_HEIGHT = 2560
        
        # Spawn coordinates
        spawn_x = 0
        spawn_y = 0
        
        if edge == "top":
            spawn_x = random.randint(0, MAP_WIDTH)
            spawn_y = 0
        elif edge == "bottom":
            spawn_x = random.randint(0, MAP_WIDTH)
            spawn_y = MAP_HEIGHT
        elif edge == "left":
            spawn_x = 0
            spawn_y = random.randint(0, MAP_HEIGHT)
        elif edge == "right":
            spawn_x = MAP_WIDTH
            spawn_y = random.randint(0, MAP_HEIGHT)
        
        try:
            # Create enemy instance with a unique ID
            new_enemy_id = str(uuid.uuid4())
            enemy = Enemy(new_enemy_id, spawn_x, spawn_y, enemy_type, enemy_data)
            self.enemies.add(enemy)
            
            # Update the enemy count counter
            old_count = len(self.enemies) - 1
            new_count = len(self.enemies)
            print(f"Enemy count changed: {old_count} → {new_count}")
            
            # Debug successful spawn
            print(f"Created {enemy_type} at edge: {edge}, position: ({spawn_x}, {spawn_y})")
        except Exception as e:
            print(f"Error creating enemy {enemy_type}: {e}")
    
    def render(self, screen, camera=None):
        """Render all enemies
        
        Args:
            screen (pygame.Surface): Screen to render to
            camera (Camera): Optional camera for scrolling
        """
        if camera:
            # Use each enemy's render method with camera
            for enemy in self.enemies:
                enemy.render(screen, camera)
        else:
            # Fallback to simple drawing if no camera is provided
            self.enemies.draw(screen)
    
    def get_enemies(self):
        """Get the enemy sprite group
        
        Returns:
            pygame.sprite.Group: Enemy sprite group
        """
        return self.enemies
    
    def handle_enemy_deaths(self, dead_enemies):
        """Handle enemy deaths
        
        Args:
            dead_enemies (list): List of Enemy instances that have died
            
        Returns:
            int: Total XP from killed enemies
        """
        total_xp = 0
        
        for enemy in dead_enemies:
            total_xp += enemy.get_xp_reward()
            self.enemies.remove(enemy)
        
        return total_xp
    
    def is_wave_complete(self):
        """Check if the current wave is complete
        
        Returns:
            bool: True if complete, False otherwise
        """
        return self.wave_timer <= 0 and len(self.enemies) == 0
    
    def is_night_complete(self):
        """Check if the night is complete (all waves done)
        
        Returns:
            bool: True if complete, False otherwise
        """
        waves_count = len(self.day_waves.get("waves", []))
        enemies_count = len(self.enemies)
        is_complete = self.current_wave >= waves_count and enemies_count == 0
        
        # Debug info to help troubleshoot
        if is_complete:
            print(f"Night complete: current_wave={self.current_wave}, total_waves={waves_count}, enemies={enemies_count}")
        
        return is_complete 