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
        
        # Create more distinctive placeholder sprites based on enemy type
        self.radius = 16  # Radius for collision detection
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        
        # Color coding based on enemy type
        enemy_colors = {
            "slime": (0, 255, 0),       # Green for slimes
            "goblin": (255, 180, 0),    # Orange for goblins
            "skeleton": (200, 200, 200), # Light gray for skeletons
            "default": (255, 0, 0)      # Red for any undefined enemy
        }
        
        # Default shape patterns based on enemy type
        border_color = (255, 255, 0)  # Yellow border for all enemies
        fill_color = enemy_colors.get(enemy_type, enemy_colors["default"])
        
        # Base circle for all enemies
        pygame.draw.circle(self.image, fill_color, (16, 16), 16)
        pygame.draw.circle(self.image, border_color, (16, 16), 16, 2)
        
        # Add distinctive patterns based on enemy type
        if enemy_type == "slime":
            # Slime: green blob with eyes
            pygame.draw.circle(self.image, (255, 255, 255), (11, 11), 4)  # Left eye
            pygame.draw.circle(self.image, (255, 255, 255), (21, 11), 4)  # Right eye
            pygame.draw.circle(self.image, (0, 0, 0), (11, 11), 2)  # Left pupil
            pygame.draw.circle(self.image, (0, 0, 0), (21, 11), 2)  # Right pupil
            pygame.draw.arc(self.image, (0, 0, 0), (8, 15, 16, 8), 0, 3.14, 2)  # Smile
            
        elif enemy_type == "goblin":
            # Goblin: orange with pointy ears and angry eyes
            # Draw ears
            pygame.draw.polygon(self.image, fill_color, [(6, 6), (10, 0), (14, 6)])  # Left ear
            pygame.draw.polygon(self.image, fill_color, [(18, 6), (22, 0), (26, 6)])  # Right ear
            # Eyes
            pygame.draw.line(self.image, (0, 0, 0), (10, 10), (14, 13), 2)  # Left eye
            pygame.draw.line(self.image, (0, 0, 0), (22, 10), (18, 13), 2)  # Right eye
            # Frown
            pygame.draw.arc(self.image, (0, 0, 0), (8, 18, 16, 8), 3.14, 6.28, 2)  # Frown
            
        elif enemy_type == "skeleton":
            # Skeleton: gray with bone patterns and hollowed eyes
            # Skull features
            pygame.draw.rect(self.image, (0, 0, 0), (9, 9, 5, 5))  # Left eye socket
            pygame.draw.rect(self.image, (0, 0, 0), (18, 9, 5, 5))  # Right eye socket
            pygame.draw.polygon(self.image, (0, 0, 0), [(13, 18), (16, 24), (19, 18)])  # Nose hole
            pygame.draw.line(self.image, (0, 0, 0), (10, 22), (22, 22), 1)  # Teeth line
            
            # Crossbones (simplified)
            pygame.draw.line(self.image, (255, 255, 255), (6, 26), (26, 6), 3)  # Diagonal bone 1
            pygame.draw.line(self.image, (255, 255, 255), (6, 6), (26, 26), 3)  # Diagonal bone 2
        
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
        if not self.active:
            return

        # Standard movement towards player_pos if not attacking wall
        if not self.is_attacking_wall:
            dx = player_pos[0] - self.rect.centerx
            dy = player_pos[1] - self.rect.centery
            distance = math.hypot(dx, dy)

            if distance > 0:
                self.vx = dx / distance
                self.vy = dy / distance
            else:
                self.vx, self.vy = 0, 0
            
            self.rect.x += self.vx * self.speed * dt
            self.rect.y += self.vy * self.speed * dt

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
        # Ensure attack_cooldown_timer is managed by can_attack and attack_performed
        # If not, it might need: self.attack_cooldown_timer -= dt
    
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
                self._start_wave(self.current_wave + 1)
            else:
                # Update spawn timers and spawn enemies
                self._handle_enemy_spawning(dt, player_pos)
    
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
                        self._spawn_enemy(enemy_type, player_pos)
    
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
        
        # Generate spawn position (e.g., random edge of screen)
        # For now, spawn randomly around player outside a certain radius
        angle = random.uniform(0, 2 * math.pi)
        spawn_radius = 400 # Distance from player to spawn
        spawn_x = player_pos[0] + spawn_radius * math.cos(angle)
        spawn_y = player_pos[1] + spawn_radius * math.sin(angle)
        
        # Create enemy instance with a unique ID
        new_enemy_id = str(uuid.uuid4())
        enemy = Enemy(new_enemy_id, spawn_x, spawn_y, enemy_type, enemy_data)
        self.enemies.add(enemy)
    
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
        return self.current_wave >= len(self.waves_data.get("waves", [])) and len(self.enemies) == 0 