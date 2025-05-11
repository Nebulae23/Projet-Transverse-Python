"""
Magic Survivor - Player Character

This module contains the Player class, which represents the player character.
"""

import math
import os
import pygame
from src import config

class Player(pygame.sprite.Sprite):
    """Player character class"""
    
    # Animation states
    ANIM_IDLE = "idle"
    ANIM_WALK = "walk"
    ANIM_ATTACK = "attack"
    
    # Facing directions
    FACING_DOWN = 0
    FACING_LEFT = 1
    FACING_RIGHT = 2
    FACING_UP = 3
    
    def __init__(self, x, y, game_manager, player_data=None):
        """Initialize the player
        
        Args:
            x (int): Initial x position
            y (int): Initial y position
            game_manager (GameManager): Reference to the game manager
            player_data (dict, optional): Player data loaded from save
        """
        super().__init__()
        self.game_manager = game_manager # Store game_manager instance
        
        # Load player sprites
        self.sprites = self._load_sprites()
        
        # Set initial image
        self.current_anim = self.ANIM_IDLE
        self.facing = self.FACING_DOWN
        self.anim_frame = 0
        self.anim_timer = 0
        self.anim_speed = 0.1  # Time between frames
        self.is_attacking = False  # Initialize is_attacking
        
        # Position and movement
        self.x = float(x)
        self.y = float(y)
        self.dx = 0  # Direction vector X
        self.dy = 0  # Direction vector Y
        self.speed = config.PLAYER_SPEED
        self.is_moving = False  # Initialize is_moving flag
        
        # Debug initialization - print attributes
        print("Player initialization:")
        print(f"is_moving: {hasattr(self, 'is_moving')}")
        print(f"is_attacking: {hasattr(self, 'is_attacking')}")
        
        # Load player data and update the image after all attributes are set
        if player_data:
            self._load_player_data(player_data)
        else:
            # Combat stats
            self.max_hp = config.PLAYER_BASE_HP
            self.current_hp = self.max_hp
            self.base_attack_damage = config.PLAYER_BASE_ATTACK_DAMAGE
            self.base_attack_cooldown = config.PLAYER_BASE_ATTACK_COOLDOWN
            
            # Progression
            self.level = 1
            self.xp = 0
            self.xp_to_next_level = config.PLAYER_XP_PER_LEVEL
            
            # Equipment and abilities
            self.spells = [
                "basic_projectile", 
                "fireball",       # Auto-cast spell
                "ice_shard"       # Auto-cast spell
            ]  # List of spell IDs
            self.relics = []  # List of relic IDs
            self.resources = {} # Will be populated by _load_player_data or default
            
        # Update image should be called after all attributes are initialized
        self.update_image()
        
        # Set up rect
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        # Attack state
        self.attack_timer = 0
        
        # Derived stats (affected by relics, level, etc.)
        self.derived_stats = {
            "movement_speed_percent": 0,
            "max_health_percent": 0,
            "spell_damage_percent": 0,
            "spell_cooldown_percent": 0,
            "xp_gain_percent": 0
        }
        
        # Hitbox for collision detection (smaller than the visual sprite)
        hitbox_size = min(self.rect.width, self.rect.height) // 2
        self.hitbox = pygame.Rect(0, 0, hitbox_size, hitbox_size)
        self.update_hitbox()
        
    def _load_sprites(self):
        """Load player sprites
        
        Returns:
            dict: Dictionary of animation frames
        """
        sprites = {
            self.ANIM_IDLE: {
                self.FACING_DOWN: [],
                self.FACING_LEFT: [],
                self.FACING_RIGHT: [],
                self.FACING_UP: []
            },
            self.ANIM_WALK: {
                self.FACING_DOWN: [],
                self.FACING_LEFT: [],
                self.FACING_RIGHT: [],
                self.FACING_UP: []
            },
            self.ANIM_ATTACK: {
                self.FACING_DOWN: [],
                self.FACING_LEFT: [],
                self.FACING_RIGHT: [],
                self.FACING_UP: []
            }
        }
        
        # Try to load actual sprites
        sprite_path = os.path.join(config.PLAYER_SPRITES, "player.png")
        if os.path.exists(sprite_path):
            try:
                # Try to load a sprite sheet
                sprite_sheet = pygame.image.load(sprite_path).convert_alpha()
                
                # For now, just create a simple 4-direction, 4-frame placeholder
                # In a real implementation, this would be properly sliced based on the sheet layout
                frame_width = sprite_sheet.get_width() // 4
                frame_height = sprite_sheet.get_height() // 4
                
                for row in range(4):  # 4 directions
                    for col in range(4):  # 4 frames per animation
                        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                        frame.blit(sprite_sheet, (0, 0), 
                                 (col * frame_width, row * frame_height, frame_width, frame_height))
                        
                        # Assign to the appropriate animation and direction
                        # This is a simplified approach; real games would have a more complex mapping
                        if col < 1:
                            sprites[self.ANIM_IDLE][row].append(frame)
                        elif col < 3:
                            sprites[self.ANIM_WALK][row].append(frame)
                        else:
                            sprites[self.ANIM_ATTACK][row].append(frame)
            except Exception as e:
                print(f"Error loading player sprite sheet: {e}")
                self._create_placeholder_sprites(sprites)
        else:
            self._create_placeholder_sprites(sprites)
        
        return sprites
    
    def _create_placeholder_sprites(self, sprites):
        """Create placeholder sprites
        
        Args:
            sprites (dict): Dictionary to populate with placeholder sprites
        """
        # Create a simple placeholder sprite for each animation and direction
        colors = {
            self.FACING_DOWN: (0, 0, 255),    # Blue
            self.FACING_LEFT: (0, 255, 255),  # Cyan
            self.FACING_RIGHT: (0, 255, 0),   # Green
            self.FACING_UP: (255, 0, 255)     # Magenta
        }
        
        for anim in sprites:
            for direction in sprites[anim]:
                # Create basic colored circle with direction indicator
                color = colors[direction]
                for i in range(2):  # Just 2 frames per animation
                    frame = pygame.Surface((32, 32), pygame.SRCALPHA)
                    # Background circle
                    pygame.draw.circle(frame, color, (16, 16), 14)
                    # Direction indicator
                    if direction == self.FACING_DOWN:
                        pygame.draw.polygon(frame, (255, 255, 255), [(16, 24), (12, 16), (20, 16)])
                    elif direction == self.FACING_LEFT:
                        pygame.draw.polygon(frame, (255, 255, 255), [(8, 16), (16, 12), (16, 20)])
                    elif direction == self.FACING_RIGHT:
                        pygame.draw.polygon(frame, (255, 255, 255), [(24, 16), (16, 12), (16, 20)])
                    elif direction == self.FACING_UP:
                        pygame.draw.polygon(frame, (255, 255, 255), [(16, 8), (12, 16), (20, 16)])
                    
                    # For attack animation, add an indicator
                    if anim == self.ANIM_ATTACK:
                        pygame.draw.circle(frame, (255, 0, 0), (16, 16), 6)
                    
                    # For walk animation, modify slightly
                    if anim == self.ANIM_WALK and i == 1:
                        # Slightly different second frame
                        pygame.draw.circle(frame, (255, 255, 0), (16, 16), 4)
                    
                    sprites[anim][direction].append(frame)
    
    def _load_player_data(self, player_data):
        """Load player data from saved state
        
        Args:
            player_data (dict): Player data
        """
        # Load stats
        stats = player_data.get("stats", {})
        self.max_hp = stats.get("max_health", config.PLAYER_BASE_HP)
        self.current_hp = stats.get("current_health", self.max_hp)
        self.base_attack_damage = stats.get("damage", config.PLAYER_BASE_ATTACK_DAMAGE)
        self.base_attack_cooldown = stats.get("attack_cooldown", config.PLAYER_BASE_ATTACK_COOLDOWN)
        self.speed = stats.get("speed", config.PLAYER_SPEED)
        
        # Load progression
        self.level = player_data.get("level", 1)
        self.xp = player_data.get("xp", 0)
        self.xp_to_next_level = self.level * config.PLAYER_XP_PER_LEVEL
        
        # Load equipment
        self.spells = player_data.get("spells", ["basic_projectile"])
        self.relics = player_data.get("relics", [])
        # Load resources
        self.resources = player_data.get("resources", config.STARTING_RESOURCES.copy() if hasattr(config, 'STARTING_RESOURCES') else {})
    
    def update_image(self):
        """Update the current image based on animation state and frame"""
        # Debug - verify attributes exist before using them
        if not hasattr(self, 'is_attacking'):
            print("ERROR: is_attacking attribute missing")
            self.is_attacking = False
            
        if not hasattr(self, 'is_moving'):
            print("ERROR: is_moving attribute missing")
            self.is_moving = False
            
        # Update animation state based on player state
        if self.is_attacking:
            self.current_anim = self.ANIM_ATTACK
        elif self.is_moving:
            self.current_anim = self.ANIM_WALK
        else:
            self.current_anim = self.ANIM_IDLE
        
        # Update animation frame (wrap around if needed)
        anim_frames = self.sprites.get(self.current_anim, {}).get(self.facing, [])
        if anim_frames:
            frame_count = len(anim_frames)
            if frame_count > 0:
                self.anim_frame = self.anim_frame % frame_count
                self.image = anim_frames[self.anim_frame]
        else:
            # Fallback to a colored rectangle if no frames are available
            self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (255, 0, 0), (0, 0, 32, 32))
    
    def update_hitbox(self):
        """Update the hitbox position to match the player's position"""
        self.hitbox.center = self.rect.center
    
    def update(self, dt, keys_pressed):
        """Update the player
        
        Args:
            dt (float): Time elapsed since last update in seconds
            keys_pressed (dict): Dictionary of pressed keys
        """
        # Handle basic movement
        self._handle_movement(dt, keys_pressed)
        
        # Update hitbox position
        self.update_hitbox()
        
        # Update animation timer
        self.anim_timer += dt
        if self.anim_timer >= self.anim_speed:
            self.anim_timer -= self.anim_speed
            self.anim_frame += 1
        
        # Decrement attack timer if active
        if self.attack_timer > 0:
            self.attack_timer -= dt
            
        # Check if we need to stop attacking animation
        if self.is_attacking and self.attack_timer <= 0:
            self.is_attacking = False
            self.current_anim = self.ANIM_IDLE if not self.is_moving else self.ANIM_WALK
        
        # Automatic spell casting for spells marked as automatic
        self._update_automatic_spells(dt)
        
        # Update the player's image
        self.update_image()
    
    def _update_automatic_spells(self, dt):
        """Handle automatic spell casting
        
        Args:
            dt (float): Time elapsed since last update in seconds
        """
        # Skip if player has no spells
        if not hasattr(self, 'spells') or not self.spells:
            return
        
        # Skip if player has no spell cooldowns initialized
        if not hasattr(self, 'spell_cooldowns'):
            self.spell_cooldowns = {}
            
        # Get spell data from game manager
        spell_data = self.game_manager.data_handler.spells
        
        # Check each spell
        for spell_id in self.spells:
            # Skip basic_projectile, which is manual
            if spell_id == "basic_projectile":
                continue
                
            # Get spell data
            current_spell_data = spell_data.get(spell_id)
            if not current_spell_data:
                continue
                
            # Check if spell is automatic
            if current_spell_data.get("automatic", True):
                # Initialize cooldown if needed
                if spell_id not in self.spell_cooldowns:
                    self.spell_cooldowns[spell_id] = 0
                
                # Update cooldown
                if self.spell_cooldowns[spell_id] > 0:
                    self.spell_cooldowns[spell_id] -= dt
                else:
                    # Find target position - check for enemies first
                    target_x, target_y = self.rect.centerx, self.rect.centery
                    
                    # Try to get enemies list from game manager's enemy manager
                    enemies = None
                    if hasattr(self.game_manager, 'state_stack') and self.game_manager.state_stack:
                        current_state = self.game_manager.state_stack[-1]
                        if hasattr(current_state, 'enemy_manager'):
                            enemies = current_state.enemy_manager.get_enemies()
                    
                    if enemies and len(enemies) > 0:
                        # Find the closest enemy
                        closest_enemy = None
                        min_distance = float('inf')
                        
                        for enemy in enemies:
                            if hasattr(enemy, 'rect') and enemy.active:
                                dx = enemy.rect.centerx - self.rect.centerx
                                dy = enemy.rect.centery - self.rect.centery
                                distance = dx**2 + dy**2  # Using squared distance for efficiency
                                
                                if distance < min_distance:
                                    min_distance = distance
                                    closest_enemy = enemy
                        
                        if closest_enemy:
                            # Target the closest enemy
                            target_x = closest_enemy.rect.centerx
                            target_y = closest_enemy.rect.centery
                            print(f"Auto-casting {spell_id} at closest enemy at ({target_x}, {target_y})")
                        else:
                            # No active enemies found, cast in a random direction
                            import random
                            angle = random.uniform(0, 6.28)  # Random angle in radians (0 to 2π)
                            distance = random.uniform(100, 300)  # Random distance
                            target_x = self.rect.centerx + math.cos(angle) * distance
                            target_y = self.rect.centery + math.sin(angle) * distance
                            print(f"Auto-casting {spell_id} in random direction")
                    else:
                        # No enemies available, cast in random direction
                        import random
                        angle = random.uniform(0, 6.28)  # Random angle in radians (0 to 2π)
                        distance = random.uniform(100, 300)  # Random distance
                        target_x = self.rect.centerx + math.cos(angle) * distance
                        target_y = self.rect.centery + math.sin(angle) * distance
                        print(f"Auto-casting {spell_id} in random direction (no enemies)")
                    
                    # Cast the spell
                    projectile = self.cast_spell(spell_id, target_x, target_y)
                    if projectile:
                        # Get the projectile manager from the current state
                        projectile_manager = None
                        
                        # First try from the current state
                        if hasattr(self.game_manager, 'state_stack') and self.game_manager.state_stack:
                            current_state = self.game_manager.state_stack[-1]
                            if hasattr(current_state, 'projectile_manager'):
                                projectile_manager = current_state.projectile_manager
                        
                        # If not found in state, try from game_manager
                        if not projectile_manager and hasattr(self.game_manager, 'projectile_manager'):
                            projectile_manager = self.game_manager.projectile_manager
                        
                        # Add projectile to the projectile manager if found
                        if projectile_manager:
                            projectile_manager.add_projectile(projectile)
                            print(f"Projectile created on world map: {projectile}")
                        else:
                            print("Warning: No projectile manager found to add projectile to!")
                        
                    # Reset cooldown
                    cooldown_time = current_spell_data.get("cooldown", 1.0)
                    self.spell_cooldowns[spell_id] = cooldown_time
    
    def _handle_movement(self, dt, keys_pressed):
        """Handle player movement
        
        Args:
            dt (float): Time elapsed since last update in seconds
            keys_pressed (pygame.key.ScancodeWrapper): Current pressed keys
        """
        # Calculate movement direction
        dx = 0
        dy = 0
        
        if keys_pressed[pygame.K_w] or keys_pressed[pygame.K_UP]:
            dy -= 1
            self.facing = self.FACING_UP
        if keys_pressed[pygame.K_s] or keys_pressed[pygame.K_DOWN]:
            dy += 1
            self.facing = self.FACING_DOWN
        if keys_pressed[pygame.K_a] or keys_pressed[pygame.K_LEFT]:
            dx -= 1
            self.facing = self.FACING_LEFT
        if keys_pressed[pygame.K_d] or keys_pressed[pygame.K_RIGHT]:
            dx += 1
            self.facing = self.FACING_RIGHT
        
        # Set movement state
        self.is_moving = dx != 0 or dy != 0
        
        # Store direction vector
        self.dx = dx
        self.dy = dy
        
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            magnitude = math.sqrt(dx * dx + dy * dy)
            dx /= magnitude
            dy /= magnitude
        
        # Calculate actual speed with modifiers
        modified_speed = self.speed * (1 + self.derived_stats["movement_speed_percent"] / 100)
        
        # Apply movement
        self.x += dx * modified_speed * dt * 60  # Normalize for 60 FPS
        self.y += dy * modified_speed * dt * 60
        
        # Update rect position
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        
        # La limitation aux bornes de la carte est gérée dans world_map.py
    
    def handle_basic_attack(self, target_x, target_y):
        """Handle basic attack action
        
        Args:
            target_x (float): Target x position
            target_y (float): Target y position
            
        Returns:
            Projectile or None: The created projectile, or None if on cooldown
        """
        current_time = pygame.time.get_ticks()
        if current_time - self.attack_timer < self.base_attack_cooldown * 1000:
            return None  # Attack on cooldown
        
        self.attack_timer = current_time
        
        # Use the first spell in the player's spell list as the basic attack
        # This can be made more sophisticated later (e.g., dedicated basic attack slot)
        basic_attack_spell_id = self.spells[0] if self.spells else None
        if not basic_attack_spell_id:
            print("Player has no spells to use for basic attack!")
            return None

        print(f"[Player.handle_basic_attack] Casting spell: {basic_attack_spell_id}")
        
        # Get spell data from DataHandler (via GameManager)
        spell_data = self.game_manager.data_handler.spells.get(basic_attack_spell_id)
        if not spell_data:
            print(f"Spell data not found for {basic_attack_spell_id}")
            return None

        print(f"[Player.handle_basic_attack] Casting spell: {basic_attack_spell_id}, Traj props: {spell_data.get('trajectory_properties')}")

        projectile_speed = spell_data.get("speed", config.DEFAULT_PROJECTILE_SPEED)
        projectile_range = spell_data.get("range", config.DEFAULT_PROJECTILE_RANGE)
        projectile_damage = spell_data.get("damage", self.base_attack_damage)
        trajectory_properties = spell_data.get("trajectory_properties", {})

        # Calculate direction vector
        dx = target_x - self.rect.centerx
        dy = target_y - self.rect.centery
        magnitude = math.sqrt(dx**2 + dy**2)
        if magnitude > 0:
            dx_normalized = dx / magnitude
            dy_normalized = dy / magnitude
        else:
            dx_normalized = 0
            dy_normalized = -1 # Default upwards if no direction

        if hasattr(self.game_manager, 'projectile_manager') and self.game_manager.projectile_manager:
            new_projectile = self.game_manager.projectile_manager.create_projectile(
                owner=self,
                start_x=self.rect.centerx,
                start_y=self.rect.centery,
                target_x=target_x,
                target_y=target_y,
                dx=dx_normalized,
                dy=dy_normalized,
                damage=projectile_damage,
                speed=projectile_speed,
                range_val=projectile_range,
                projectile_type=basic_attack_spell_id,
                trajectory_properties=trajectory_properties
            )
            return new_projectile
        else:
            print("Player has no projectile_manager or it's None in current state!")
        return None
    
    def take_damage(self, amount):
        """Take damage
        
        Args:
            amount (float): Amount of damage to take
            
        Returns:
            bool: True if the player is still alive, False otherwise
        """
        self.current_hp -= amount
        return self.current_hp > 0
    
    def heal(self, amount):
        """Heal the player
        
        Args:
            amount (float): Amount to heal
        """
        self.current_hp = min(self.current_hp + amount, self.max_hp)
    
    def gain_xp(self, amount):
        """Gain experience
        
        Args:
            amount (float): Amount of XP to gain
            
        Returns:
            bool: True if the player leveled up, False otherwise
        """
        # Apply XP gain modifiers
        modified_amount = amount * (1 + self.derived_stats["xp_gain_percent"] / 100)
        self.xp += modified_amount
        
        if self.xp >= self.xp_to_next_level:
            self._level_up()
            return True
        
        return False
    
    def _level_up(self):
        """Level up the player"""
        self.level += 1
        self.xp -= self.xp_to_next_level
        self.xp_to_next_level = self.level * config.PLAYER_XP_PER_LEVEL
        
        # Increase base stats
        self.max_hp += 10
        self.current_hp = self.max_hp  # Fully heal on level up
        self.base_attack_damage += 2
        
        # Notify game manager about level up so it can show spell selection UI
        print(f"Player._level_up: Leveled up to level {self.level}!")
        print(f"Player._level_up: game_manager exists: {hasattr(self, 'game_manager')}")
        
        if hasattr(self, 'game_manager'):
            print(f"Player._level_up: handle_player_level_up exists on game_manager: {hasattr(self.game_manager, 'handle_player_level_up')}")
            
        if hasattr(self.game_manager, "handle_player_level_up"):
            print(f"Player._level_up: Calling game_manager.handle_player_level_up({self.level})")
            self.game_manager.handle_player_level_up(self.level)
        else:
            print("Player._level_up: ERROR! game_manager.handle_player_level_up method not found!")
    
    @staticmethod
    def calculate_xp_for_level(level_number):
        """Calculates the total XP needed to reach a given level.
        Assumes XP for level 1 is PLAYER_XP_PER_LEVEL, for level 2 is 2*PLAYER_XP_PER_LEVEL, etc.
        This represents the XP cap *for that level*.
        """
        if level_number < 1:
            return 0 # Or handle as an error/minimum value if preferred
        return level_number * config.PLAYER_XP_PER_LEVEL
    
    def equip_relic(self, relic_id, relic_data):
        """Equip a relic
        
        Args:
            relic_id (str): ID of the relic
            relic_data (dict): Relic data
        """
        if relic_id not in self.relics:
            self.relics.append(relic_id)
            
            # Apply relic effects to derived stats
            for stat, value in relic_data.get("effects", {}).items():
                if stat in self.derived_stats:
                    self.derived_stats[stat] += value
    
    def equip_spell(self, spell_id):
        """Equip a spell
        
        Args:
            spell_id (str): ID of the spell
        """
        if spell_id not in self.spells:
            self.spells.append(spell_id)
    
    def get_hp_percentage(self):
        """Get the current HP as a percentage
        
        Returns:
            float: HP percentage (0-100)
        """
        return (self.current_hp / self.max_hp) * 100
    
    def get_xp_percentage(self):
        """Get the current XP as a percentage of the next level
        
        Returns:
            float: XP percentage (0-100)
        """
        return (self.xp / self.xp_to_next_level) * 100
    
    def get_save_data(self):
        """Get data for saving
        
        Returns:
            dict: Player data for saving
        """
        return {
            "level": self.level,
            "xp": self.xp,
            "position": {
                "x": self.x,
                "y": self.y
            },
            "stats": {
                "max_health": self.max_hp,
                "current_health": self.current_hp,
                "damage": self.base_attack_damage,
                "attack_cooldown": self.base_attack_cooldown,
                "speed": self.speed
            },
            "spells": self.spells,
            "relics": self.relics,
            "resources": self.resources
        }
    
    def check_collision(self, rect):
        """Check if the player's hitbox collides with the given rect
        
        Args:
            rect (pygame.Rect): Rectangle to check collision with
            
        Returns:
            bool: True if colliding, False otherwise
        """
        return self.hitbox.colliderect(rect)
    
    def cast_spell(self, spell_id_to_cast, target_x, target_y):
        """Casts a specific spell by ID, aimed at target_x, target_y.
        For testing trajectories, this version has no cooldown.
        """
        # Calculate direction (needed for non-orbiting, non-self-targeted spells)
        dx = target_x - self.rect.centerx
        dy = target_y - self.rect.centery
        magnitude = math.sqrt(dx**2 + dy**2)
        if magnitude > 0:
            dx_normalized = dx / magnitude
            dy_normalized = dy / magnitude
        else:
            # Default direction if target is same as player (e.g., for self-cast or if magnitude is 0)
            dx_normalized = 0 
            dy_normalized = -1 # Could be based on player facing or (0,0) for pure self-cast

        spell_data = self.game_manager.data_handler.spells.get(spell_id_to_cast)
        if not spell_data:
            print(f"Player attempting to cast unknown spell: {spell_id_to_cast}")
            return None

        # Check cooldown, mana, etc. (not implemented yet)

        # Create and return a projectile if it's a projectile spell
        if spell_data.get("type") == "PROJECTILE" or "PROJECTILE" in spell_data.get("type", ""): # Handles PROJECTILE_AOE etc.
            from src.projectile_system import Projectile # Local import to avoid circular
            
            # Determine projectile properties from spell_data
            # These are just examples, actual properties will depend on spell_data structure
            # Ensure spell_data has trajectory_properties and other necessary fields.
            
            trajectory_props = spell_data.get("trajectory_properties", {})
            
            # Use default values from config if not specified in spell_data
            # Fallback to avoid KeyError if spell_data is incomplete
            effective_speed = spell_data.get("speed", config.DEFAULT_PROJECTILE_SPEED)
            effective_range = spell_data.get("range", config.DEFAULT_PROJECTILE_RANGE)
            damage = spell_data.get("damage", 0) # Default to 0 if not specified
            
            # Create the projectile instance
            projectile = Projectile(
                start_x=self.rect.centerx, 
                start_y=self.rect.centery,
                dx=dx_normalized,
                dy=dy_normalized,
                speed=effective_speed,
                range_val=effective_range, 
                damage=damage,
                owner=self, # Pass player instance as owner
                projectile_type=spell_id_to_cast, # CHANGED from spell_id
                trajectory_properties=trajectory_props
            )
            return projectile
        
        print(f"Spell type {spell_data.get('type')} not yet implemented for casting.")
        return None

    def add_resource(self, resource_type, amount):
        """Add a resource to the player's inventory"""
        if amount <= 0:
            return

        current_amount = self.resources.get(resource_type, 0)
        self.resources[resource_type] = current_amount + amount
        print(f"Player now has {self.resources[resource_type]} {resource_type}")

        # Ensure player_data in game_manager is updated if it's the source of truth for saving
        if self.game_manager and hasattr(self.game_manager, 'player_data') and self.game_manager.player_data is not None:
            if "resources" not in self.game_manager.player_data:
                self.game_manager.player_data["resources"] = {}
            self.game_manager.player_data["resources"][resource_type] = self.resources[resource_type]
        elif self.game_manager and not hasattr(self.game_manager, 'player_data'):
             # This might occur if player_data is directly on player and not mirrored in game_manager
             # For now, assume player_data on game_manager is the one to sync for saving.
             pass

    # --- Get Render Sort Key ---
    def get_render_sort_key(self):
        """Returns the y-coordinate of the bottom of the sprite, for depth sorting."""
        return self.rect.bottom

    def render(self, surface, camera):
        """Render the player on the given surface, adjusted by the camera."""
        if self.image and self.rect:
            surface.blit(self.image, camera.apply_rect(self.rect))
        else:
            # Optional: Add a log or a placeholder draw if image/rect are missing
            print(f"Player render called but image or rect is missing. Image: {self.image}, Rect: {self.rect}") 