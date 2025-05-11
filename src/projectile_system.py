"""
Magic Survivor - Projectile System

This module handles the projectile system, which includes the Projectile class
and projectile-related utilities.
"""

import pygame
import math
from src import config
from src.data_handler import DataHandler # Import DataHandler

class Projectile(pygame.sprite.Sprite):
    """Represents a projectile in the game"""
    def __init__(self, owner, start_x, start_y, dx, dy, damage, speed, range_val, projectile_type, trajectory_properties):
        super().__init__()
        self.owner = owner
        self.x = float(start_x)
        self.y = float(start_y)
        self.dx = dx # Normalized direction vector x
        self.dy = dy # Normalized direction vector y
        self.damage = damage
        self.speed = speed
        self.range = range_val
        self.projectile_type = projectile_type
        self.trajectory_properties = trajectory_properties
        self.trajectory_type = self.trajectory_properties.get("type", "STRAIGHT")

        # Placeholder sprite: a colored circle
        # Allow radius and color to be defined in trajectory_properties in spell data
        default_color = config.YELLOW # Fallback color if not specified in spell
        radius = self.trajectory_properties.get("radius", 5) 
        # Ensure color is a tuple, not a list, if fetched from JSON
        color_value = self.trajectory_properties.get("color", default_color)
        if isinstance(color_value, list):
            color = tuple(color_value)
        else:
            color = color_value

        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        
        self.distance_traveled = 0
        self.active = True # Projectile is active by default

        # Trajectory-specific initializations
        if self.trajectory_type == "ORBITING":
            self.orbit_radius = self.trajectory_properties.get("orbit_radius", 75)
            self.angular_speed = self.trajectory_properties.get("angular_speed", 2) # Radians per second
            self.duration = self.trajectory_properties.get("duration", 10) # Seconds
            self.current_angle = self.trajectory_properties.get("initial_angle", 0) # Allow specifying initial angle
            self.lifetime_timer = 0
            # Initial position will be set in the first update relative to owner
            # dx, dy, speed, range are not used by ORBITING type in the same way.
        elif self.trajectory_type == "SINE_WAVE":
            self.amplitude = self.trajectory_properties.get("amplitude", 30)
            self.frequency = self.trajectory_properties.get("frequency", 5) # Higher frequency = more oscillations
            self.sine_wave_angle = 0 # This will increment to drive the sine function
            self.base_x = self.x # Store initial position to calculate perpendicular offset
            self.base_y = self.y
            self.path_dx = self.dx # Store the main direction of travel
            self.path_dy = self.dy
        elif self.trajectory_type == "BOOMERANG":
            self.returning = False
            self.initial_dx = self.dx # Store initial direction for return reference if needed
            self.initial_dy = self.dy
            # Range here means max outward distance before returning
        elif self.trajectory_type == "CHAIN":
            self.max_chains = self.trajectory_properties.get("max_chains", 3)
            self.chain_radius_sq = self.trajectory_properties.get("chain_radius", 150)**2 # Use squared for efficiency
            self.chain_count = 0
            self.last_hit_enemy_id = None # Store ID to prevent re-hitting same enemy instance immediately
            self.homing_strength = self.trajectory_properties.get("homing_strength", 0.1) # Chains can also home
        elif self.trajectory_type == "PIERCING":
            self.pierce_count = self.trajectory_properties.get("pierce_count", 3)
            self.hit_enemies_count = 0
            self.hit_enemy_ids = set() # Set to store IDs of enemies already hit by this projectile
        elif self.trajectory_type == "GROUND_AOE":
            # Target coordinates are implicitly passed via dx, dy and speed if projectile is created at player
            # but for GROUND_AOE, the projectile is more of a marker for a location. Player.cast_spell gives raw target_x, target_y.
            # We need to ensure ProjectileManager.create_projectile receives these and passes them if not already.
            # The ProjectileManager.create_projectile signature does include target_x, target_y so we can use them.
            # For now, assume they are available via trajectory_properties or direct params. Let's refine if needed.
            self.target_x = trajectory_properties.get("raw_target_x", self.x + self.dx * 1000) # Fallback
            self.target_y = trajectory_properties.get("raw_target_y", self.y + self.dy * 1000) # Fallback
            
            self.travel_speed = self.trajectory_properties.get("travel_speed", 500)
            self.aoe_radius = self.trajectory_properties.get("aoe_radius", 75)
            self.aoe_damage = self.trajectory_properties.get("aoe_damage", 30)
            self.aoe_duration = self.trajectory_properties.get("aoe_duration", 0.2)
            self.delay_after_arrival = self.trajectory_properties.get("delay_after_arrival", 0.3)
            self.marker_radius = self.trajectory_properties.get("marker_radius", 6)
            self.marker_color = tuple(self.trajectory_properties.get("marker_color", [255,120,0]))
            self.aoe_visual_color = tuple(self.trajectory_properties.get("aoe_visual_color", [255,60,0,180]))

            self.aoe_state = "traveling" # traveling, arrived, exploding
            self.arrival_timer = 0.0
            self.explosion_timer = 0.0
            self.aoe_damage_applied = False

            # Initial image is the marker
            self.image = pygame.Surface((self.marker_radius * 2, self.marker_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.marker_color, (self.marker_radius, self.marker_radius), self.marker_radius)
            self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
            
            # Calculate direction towards target_x, target_y for the marker travel
            dx_to_target = self.target_x - self.x
            dy_to_target = self.target_y - self.y
            dist_to_target = math.sqrt(dx_to_target**2 + dy_to_target**2)
            if dist_to_target > 0:
                self.dx = dx_to_target / dist_to_target
                self.dy = dy_to_target / dist_to_target
            else: # Already at target or no direction, might happen if spell is cast on self
                self.dx, self.dy = 0, 0
                self.aoe_state = "arrived" # Skip traveling
                self.arrival_timer = self.delay_after_arrival
        elif self.trajectory_type == "FORKING":
            self.fork_condition_type = self.trajectory_properties.get("fork_condition_type", "DISTANCE")
            self.fork_condition_value = self.trajectory_properties.get("fork_condition_value", 150)
            self.fork_count = self.trajectory_properties.get("fork_count", 3)
            self.fork_angle_spread_rad = math.radians(self.trajectory_properties.get("fork_angle_spread", 45))
            self.child_spell_id = self.trajectory_properties.get("child_spell_id", None)
            self.has_forked = False
            self.timer_for_fork = 0.0 # Used if fork_condition_type is TIMER
            self.fork_now_on_hit_signal = False # For ON_FIRST_HIT
        elif self.trajectory_type == "SPIRAL":
            self.expansion_speed = self.trajectory_properties.get("expansion_speed", 40)
            self.rotation_speed_rad = math.radians(self.trajectory_properties.get("rotation_speed", 720))
            self.base_travel_speed = self.trajectory_properties.get("base_travel_speed", 150)
            self.duration = self.trajectory_properties.get("duration", 1.5)
            self.initial_radius = self.trajectory_properties.get("initial_radius", 5)
            
            self.current_spiral_radius = float(self.initial_radius)
            self.current_spiral_angle_rad = 0.0
            self.lifetime_timer = 0.0
            
            self.center_x = self.x # Initial center of the spiral is projectile's spawn point
            self.center_y = self.y
            # self.base_dx and self.base_dy will use the projectile's initial self.dx, self.dy for direction
            self.base_dx = self.dx 
            self.base_dy = self.dy
        elif self.trajectory_type == "GROWING_ORB":
            self.initial_radius = float(self.trajectory_properties.get("initial_radius", 5))
            self.max_radius = float(self.trajectory_properties.get("max_radius", 30))
            self.growth_rate = float(self.trajectory_properties.get("growth_rate", 10))
            self.growth_duration = float(self.trajectory_properties.get("growth_duration", float('inf')))
            self.current_radius = self.initial_radius
            self.growth_active_timer = 0.0
            self.orb_color = tuple(self.trajectory_properties.get("color", [255, 255, 255]))

            # Initial image and rect for GROWING_ORB
            radius_int = int(self.current_radius)
            # Ensure radius_int is at least 1 to prevent Surface errors with zero dimension
            radius_int = max(1, radius_int) 
            self.image = pygame.Surface((radius_int * 2, radius_int * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.orb_color, (radius_int, radius_int), radius_int)
            self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def update(self, dt, enemies_list): # enemies_list for future homing etc.
        """Update the projectile's position and state.
        Returns a list of child projectile creation data if forking occurs, else None.
        """
        if not self.active:
            return None

        children_to_spawn = None # Initialize to None

        # Standard movement logic first (can be any type, e.g. STRAIGHT, HOMING)
        # For FORKING parent, let's assume STRAIGHT for now.
        if self.trajectory_type not in ["ORBITING", "GROUND_AOE"]: # Types that have very different movement
            if self.trajectory_type == "HOMING" or self.trajectory_type == "CHAIN":
                # Simplified Homing/Chain movement part (copied and adapted)
                target = None
                min_dist_sq = float('inf')
                homing_strength = self.trajectory_properties.get("homing_strength", 0.05) if self.trajectory_type == "HOMING" else self.homing_strength

                if enemies_list:
                    for enemy in enemies_list:
                        if self.trajectory_type == "CHAIN" and hasattr(enemy, 'id') and enemy.id == self.last_hit_enemy_id:
                            continue
                        if hasattr(enemy, 'rect') and hasattr(enemy, 'active') and not enemy.active:
                            continue
                        dist_sq = (enemy.rect.centerx - self.x)**2 + (enemy.rect.centery - self.y)**2
                        if dist_sq < min_dist_sq:
                            min_dist_sq = dist_sq
                            target = enemy
                if target:
                    target_dx_vec = target.rect.centerx - self.x
                    target_dy_vec = target.rect.centery - self.y
                    magnitude = math.sqrt(target_dx_vec**2 + target_dy_vec**2)
                    if magnitude > 0:
                        target_dx_vec /= magnitude
                        target_dy_vec /= magnitude
                    self.dx = (1 - homing_strength) * self.dx + homing_strength * target_dx_vec
                    self.dy = (1 - homing_strength) * self.dy + homing_strength * target_dy_vec
                    current_magnitude = math.sqrt(self.dx**2 + self.dy**2)
                    if current_magnitude > 0:
                        self.dx /= current_magnitude
                        self.dy /= current_magnitude
            
            # Common movement for STRAIGHT, HOMING, CHAIN (after direction update), PIERCING, FORKING
            self.x += self.dx * self.speed * dt
            self.y += self.dy * self.speed * dt
            self.rect.center = (int(self.x), int(self.y))
            self.distance_traveled += self.speed * dt
            if self.distance_traveled > self.range and self.trajectory_type not in ["FORKING"]: # Forking has its own range logic for fork condition
                self.active = False

        # Trajectory-specific update logic
        if self.trajectory_type == "ORBITING":
            if not self.owner or not hasattr(self.owner, 'rect'): # Ensure owner and its rect exist
                self.active = False
                return

            self.lifetime_timer += dt
            if self.lifetime_timer > self.duration:
                self.active = False
                return

            self.current_angle += self.angular_speed * dt
            # Ensure current_angle stays within 0 to 2*PI if needed, though math.cos/sin handle it
            # self.current_angle %= (2 * math.pi) 

            offset_x = math.cos(self.current_angle) * self.orbit_radius
            offset_y = math.sin(self.current_angle) * self.orbit_radius
            
            self.x = self.owner.rect.centerx + offset_x
            self.y = self.owner.rect.centery + offset_y
            self.rect.center = (int(self.x), int(self.y))
            # No distance_traveled or range check; lifetime is by duration.
        elif self.trajectory_type == "SINE_WAVE":
            # Move along the main path
            self.base_x += self.path_dx * self.speed * dt
            self.base_y += self.path_dy * self.speed * dt
            self.distance_traveled += self.speed * dt

            # Update the angle for the sine wave calculation
            # Frequency determines how fast the angle changes relative to distance or time
            # Let's tie frequency to distance traveled for more consistent wave shape regardless of speed changes
            self.sine_wave_angle += self.frequency * (self.speed * dt) * 0.1 # Adjust 0.1 to scale frequency effect
            
            # Calculate perpendicular offset
            # Perpendicular vector to (path_dx, path_dy) is (-path_dy, path_dx)
            perpendicular_dx = -self.path_dy
            perpendicular_dy = self.path_dx
            
            offset = self.amplitude * math.sin(self.sine_wave_angle)
            
            self.x = self.base_x + perpendicular_dx * offset
            self.y = self.base_y + perpendicular_dy * offset
            self.rect.center = (int(self.x), int(self.y))

            if self.distance_traveled > self.range:
                self.active = False
        elif self.trajectory_type == "BOOMERANG":
            if not self.returning:
                # Outward phase
                self.x += self.dx * self.speed * dt
                self.y += self.dy * self.speed * dt
                self.rect.center = (int(self.x), int(self.y))
                self.distance_traveled += self.speed * dt

                if self.distance_traveled >= self.range:
                    self.returning = True
                    # Reverse direction for return trip
                    self.dx = -self.dx
                    self.dy = -self.dy
                    # Reset distance for return trip measurement, or use a separate counter
                    self.distance_traveled = 0 
            else:
                # Return phase
                self.x += self.dx * self.speed * dt
                self.y += self.dy * self.speed * dt
                self.rect.center = (int(self.x), int(self.y))
                self.distance_traveled += self.speed * dt # Measures distance on return leg

                # Deactivation condition: Reached owner or traveled too far on return
                if self.owner and hasattr(self.owner, 'rect'):
                    # Check collision with a slightly larger rect around owner to ensure it hits
                    owner_hitbox = self.owner.rect.inflate(self.rect.width, self.rect.height) 
                    if self.rect.colliderect(owner_hitbox):
                        self.active = False
                
                # Fallback deactivation if it misses owner and travels too far
                if self.distance_traveled > self.range * 1.5: # Allow some overshoot
                    self.active = False
        elif self.trajectory_type == "CHAIN":
            # CHAIN projectiles use homing logic for each segment
            target = None
            min_dist_sq = float('inf')

            # Find current target (similar to HOMING)
            # This part might need to be smarter if it has already hit its primary target and is looking for a chain
            # For now, assume it's always trying to home towards *some* target if not hit one this frame
            if enemies_list:
                for enemy in enemies_list:
                    if hasattr(enemy, 'id') and enemy.id == self.last_hit_enemy_id:
                        continue # Don't re-target the enemy just hit in the same frame/logic cycle
                    if hasattr(enemy, 'rect') and hasattr(enemy, 'active') and not enemy.active:
                        continue 
                    dist_sq = (enemy.rect.centerx - self.x)**2 + (enemy.rect.centery - self.y)**2
                    if dist_sq < min_dist_sq:
                        min_dist_sq = dist_sq
                        target = enemy
            
            if target:
                target_dx_vec = target.rect.centerx - self.x
                target_dy_vec = target.rect.centery - self.y
                magnitude = math.sqrt(target_dx_vec**2 + target_dy_vec**2)
                if magnitude > 0:
                    target_dx_vec /= magnitude
                    target_dy_vec /= magnitude
                
                self.dx = (1 - self.homing_strength) * self.dx + self.homing_strength * target_dx_vec
                self.dy = (1 - self.homing_strength) * self.dy + self.homing_strength * target_dy_vec
                
                current_magnitude = math.sqrt(self.dx**2 + self.dy**2)
                if current_magnitude > 0:
                    self.dx /= current_magnitude
                    self.dy /= current_magnitude
            
            self.x += self.dx * self.speed * dt
            self.y += self.dy * self.speed * dt
            self.rect.center = (int(self.x), int(self.y))
            self.distance_traveled += self.speed * dt
            if self.distance_traveled > self.range: # Range for current segment
                self.active = False # Deactivate if it travels too far without hitting anything
        elif self.trajectory_type == "PIERCING":
            # PIERCING projectiles use STRAIGHT movement logic
            self.x += self.dx * self.speed * dt
            self.y += self.dy * self.speed * dt
            self.rect.center = (int(self.x), int(self.y))
            self.distance_traveled += self.speed * dt
            if self.distance_traveled > self.range:
                self.active = False
        elif self.trajectory_type == "GROUND_AOE":
            if self.aoe_state == "traveling":
                # Move towards target_x, target_y
                self.x += self.dx * self.travel_speed * dt
                self.y += self.dy * self.travel_speed * dt
                self.rect.center = (int(self.x), int(self.y))

                # Check for arrival (distance to target_x, target_y)
                if math.hypot(self.target_x - self.x, self.target_y - self.y) < self.travel_speed * dt: # Close enough
                    self.x, self.y = self.target_x, self.target_y # Snap to target
                    self.rect.center = (int(self.x), int(self.y))
                    self.aoe_state = "arrived"
                    self.arrival_timer = self.delay_after_arrival
                    # Marker becomes invisible or very small, main rect stays for AOE later
                    self.image = pygame.Surface((1,1), pygame.SRCALPHA) 
            
            elif self.aoe_state == "arrived":
                self.arrival_timer -= dt
                if self.arrival_timer <= 0:
                    self.aoe_state = "exploding"
                    self.explosion_timer = self.aoe_duration
                    self.aoe_damage_applied = False # Ensure damage is applied once per explosion state
                    
                    # Change image to AOE visual
                    aoe_diameter = self.aoe_radius * 2
                    self.image = pygame.Surface((aoe_diameter, aoe_diameter), pygame.SRCALPHA)
                    pygame.draw.circle(self.image, self.aoe_visual_color, (self.aoe_radius, self.aoe_radius), self.aoe_radius)
                    self.rect = self.image.get_rect(center=(int(self.x), int(self.y))) # Update rect to AOE size

            elif self.aoe_state == "exploding":
                if not self.aoe_damage_applied:
                    # Apply damage to enemies in AOE radius
                    for enemy in enemies_list:
                        if hasattr(enemy, 'rect') and enemy.active:
                            dist_sq = (enemy.rect.centerx - self.x)**2 + (enemy.rect.centery - self.y)**2
                            if dist_sq <= self.aoe_radius**2:
                                enemy.take_damage(self.aoe_damage)
                    self.aoe_damage_applied = True # Damage applied for this explosion
                
                self.explosion_timer -= dt
                if self.explosion_timer <= 0:
                    self.active = False
        elif self.trajectory_type == "FORKING":
            if not self.has_forked:
                fork_now = False
                if self.fork_condition_type == "DISTANCE":
                    if self.distance_traveled >= self.fork_condition_value:
                        fork_now = True
                elif self.fork_condition_type == "TIMER":
                    self.timer_for_fork += dt
                    if self.timer_for_fork >= self.fork_condition_value:
                        fork_now = True
                elif self.fork_condition_type == "ON_FIRST_HIT" and self.fork_now_on_hit_signal:
                    fork_now = True
                    self.fork_now_on_hit_signal = False # Reset signal

                if fork_now and self.child_spell_id:
                    self.has_forked = True
                    self.active = False # Parent deactivates
                    children_to_spawn = []
                    
                    base_angle = math.atan2(self.dy, self.dx)
                    if self.fork_count == 1:
                        angle_step = 0 # Single child continues in same direction
                    else:
                        angle_step = self.fork_angle_spread_rad / (self.fork_count -1)
                    
                    start_angle_offset = -self.fork_angle_spread_rad / 2 if self.fork_count > 1 else 0

                    for i in range(self.fork_count):
                        current_angle = base_angle + start_angle_offset + (i * angle_step)
                        child_dx = math.cos(current_angle)
                        child_dy = math.sin(current_angle)
                        # Child inherits parent's owner
                        children_to_spawn.append({
                            "owner": self.owner,
                            "spell_id": self.child_spell_id,
                            "start_x": self.x,
                            "start_y": self.y,
                            "target_x": self.x + child_dx * 100, # Dummy target for direction
                            "target_y": self.y + child_dy * 100, # Dummy target for direction
                            # dx, dy, damage, speed, range, etc. will be from child_spell_id's data
                        })
            elif self.has_forked and not self.active : # Already forked and should be inactive
                pass # Should be removed by manager
            elif self.distance_traveled > self.range: # If it reaches its original range before forking
                 self.active = False
        elif self.trajectory_type == "SPIRAL":
            self.lifetime_timer += dt
            if self.lifetime_timer > self.duration:
                self.active = False
                return children_to_spawn # Should be None for SPIRAL

            # Update spiral center position based on base_dx, base_dy
            self.center_x += self.base_dx * self.base_travel_speed * dt
            self.center_y += self.base_dy * self.base_travel_speed * dt

            # Update spiral parameters
            self.current_spiral_radius += self.expansion_speed * dt
            self.current_spiral_angle_rad += self.rotation_speed_rad * dt

            # Calculate projectile's actual position based on spiral parameters
            offset_x = math.cos(self.current_spiral_angle_rad) * self.current_spiral_radius
            offset_y = math.sin(self.current_spiral_angle_rad) * self.current_spiral_radius
            
            self.x = self.center_x + offset_x
            self.y = self.center_y + offset_y
            self.rect.center = (int(self.x), int(self.y))

        elif self.trajectory_type == "GROWING_ORB":
            # Movement Logic
            self.x += self.dx * self.speed * dt
            self.y += self.dy * self.speed * dt
            self.distance_traveled += self.speed * dt

            # Growth Logic
            self.growth_active_timer += dt
            if self.current_radius < self.max_radius and self.growth_active_timer < self.growth_duration:
                self.current_radius += self.growth_rate * dt
                self.current_radius = min(self.current_radius, self.max_radius)
                
                # Dynamic Image/Rect Update
                radius_int = int(self.current_radius)
                # Ensure radius_int is at least 1 to prevent Surface errors with zero dimension
                radius_int = max(1, radius_int) 
                new_center = self.rect.center # Store center before recreating rect
                self.image = pygame.Surface((radius_int * 2, radius_int * 2), pygame.SRCALPHA)
                pygame.draw.circle(self.image, self.orb_color, (radius_int, radius_int), radius_int)
                self.rect = self.image.get_rect(center=new_center) # Use stored center
            
            # Update Position (after movement and growth)
            self.rect.center = (int(self.x), int(self.y))

            # Deactivation Logic
            if self.distance_traveled > self.range:
                self.active = False

        # Common deactivation checks (can be refactored)
        # if not (0 <= self.rect.centerx <= config.SCREEN_WIDTH and 
        #           0 <= self.rect.centery <= config.SCREEN_HEIGHT):
        #     pass # Manager handles world boundary culling

        return children_to_spawn

    def render(self, screen, camera=None):
        """Render the projectile"""
        if self.active:
            if camera:
                screen.blit(self.image, camera.apply(self))
            else:
                screen.blit(self.image, self.rect)

    def on_hit_enemy(self, hit_enemy, all_enemies_list):
        """Called when a projectile hits an enemy. Handles chain/pierce logic if applicable.
        Returns a list of child projectile creation data if forking on hit occurs, else None.
        """
        children_to_spawn_on_hit = None

        if self.trajectory_type == "CHAIN":
            self.chain_count += 1
            self.last_hit_enemy_id = getattr(hit_enemy, 'id', None) # Assumes enemy has a unique 'id' attribute

            if self.chain_count >= self.max_chains:
                self.active = False # Max chains reached
                return children_to_spawn_on_hit

            # Find next target for chaining
            next_target = None
            min_dist_sq = self.chain_radius_sq # Only search within chain_radius_sq

            for enemy in all_enemies_list:
                if not enemy.active or getattr(enemy, 'id', None) == self.last_hit_enemy_id:
                    continue
                
                dist_sq = (enemy.rect.centerx - self.x)**2 + (enemy.rect.centery - self.y)**2
                if dist_sq < min_dist_sq:
                    min_dist_sq = dist_sq
                    next_target = enemy
            
            if next_target:
                # Aim at the new target
                target_dx_vec = next_target.rect.centerx - self.x
                target_dy_vec = next_target.rect.centery - self.y
                magnitude = math.sqrt(target_dx_vec**2 + target_dy_vec**2)
                if magnitude > 0:
                    self.dx = target_dx_vec / magnitude
                    self.dy = target_dy_vec / magnitude
                self.distance_traveled = 0 # Reset distance for the new chain segment
                # self.last_hit_enemy_id will be updated if this new target is hit
            else:
                self.active = False # No next target found in range
        elif self.trajectory_type == "PIERCING":
            enemy_id = getattr(hit_enemy, 'id', None)
            if enemy_id is not None and enemy_id not in self.hit_enemy_ids:
                self.hit_enemy_ids.add(enemy_id)
                self.hit_enemies_count += 1
                if self.hit_enemies_count >= self.pierce_count:
                    self.active = False # Max pierces reached
            # If enemy_id is None or already hit, the projectile continues without consuming a pierce count for this specific collision
            # It will still be active unless max pierces are met from distinct enemies.
        elif self.trajectory_type == "GROUND_AOE":
            # This type does not interact with enemies via on_hit_enemy during its travel.
            # Its damage is applied in its update() method during the 'exploding' state.
            pass # Do nothing, let update() handle its lifecycle and damage.
        elif self.trajectory_type == "FORKING" and self.fork_condition_type == "ON_FIRST_HIT":
            if not self.has_forked and self.child_spell_id:
                # Don't spawn here. Just mark for forking. Update() will handle spawning.
                # This also means the projectile itself does its damage on this hit before forking.
                self.fork_now_on_hit_signal = True # New flag
            
            # Standard deactivation on hit for the parent if it doesn't fork immediately
            # or if forking condition is not ON_FIRST_HIT.
            # However, if it *is* going to fork due to this hit, update() will make it inactive.
            # If it's NOT an ON_FIRST_HIT type, normal active = False applies if not other type.
            if not self.fork_now_on_hit_signal: # If not about to fork due to this hit specifically
                 self.active = False
            # If self.fork_now_on_hit_signal is True, update() will make it inactive after creating children.

        else:
            self.active = False
        
        return None # on_hit_enemy no longer returns children directly


class ProjectileManager:
    """Manages active projectiles in the game"""
    def __init__(self, game_manager): # Added game_manager argument
        self.game_manager = game_manager # Store game_manager reference
        self.projectiles = pygame.sprite.Group()
        self.spell_data = DataHandler.load_spells() # Load spell data for projectile properties

    def create_projectile(self, owner, start_x, start_y, target_x, target_y, 
                          dx, dy, damage, speed, range_val, 
                          projectile_type, trajectory_properties):
        """Creates a new projectile and returns it (does not add to manager's list here)"""
        
        # For GROUND_AOE, we need to pass the raw target coordinates into the projectile
        # The trajectory_properties is a good place for this.
        # Ensure the calling code (Player.cast_spell) puts them there.
        current_traj_props = trajectory_properties.copy() # Avoid modifying the original dict from spell_data
        if current_traj_props.get("type") == "GROUND_AOE": # Corrected condition
            current_traj_props['raw_target_x'] = target_x
            current_traj_props['raw_target_y'] = target_y

        new_projectile = Projectile(
            owner=owner,
            start_x=start_x, start_y=start_y,
            dx=dx, dy=dy, 
            damage=damage, speed=speed, range_val=range_val,
            projectile_type=projectile_type, # This is the spell_id, not the trajectory_type string
            trajectory_properties=current_traj_props # Pass potentially modified props
        )
        return new_projectile

    def add_projectile(self, projectile):
        """Adds an existing projectile instance to the manager."""
        self.projectiles.add(projectile)

    def update(self, dt, enemies_list): # enemies_list needed for Projectile.update
        """Update all projectiles"""
        newly_spawned_children = []
        for projectile in list(self.projectiles): # Iterate over a copy for safe removal
            children_data = projectile.update(dt, enemies_list)
            if children_data:
                for child_info in children_data:
                    # Fetch child spell full definition
                    child_spell_def = self.spell_data.get(child_info["spell_id"])
                    if not child_spell_def:
                        print(f"Warning: Child spell ID {child_info['spell_id']} not found.")
                        continue
                    
                    # Calculate dx, dy for the child based on its start and dummy target
                    cdx = child_info["target_x"] - child_info["start_x"]
                    cdy = child_info["target_y"] - child_info["start_y"]
                    cmag = math.sqrt(cdx**2 + cdy**2)
                    if cmag > 0:
                        cdx /= cmag
                        cdy /= cmag
                    
                    # Create and add child projectile
                    # Note: child_spell_def provides damage, speed, range, trajectory_properties for the child
                    child_projectile = self.create_projectile(
                        owner=child_info["owner"],
                        start_x=child_info["start_x"],
                        start_y=child_info["start_y"],
                        target_x=child_info["target_x"], # For consistency, though dx,dy are prime
                        target_y=child_info["target_y"],
                        dx=cdx,
                        dy=cdy,
                        damage=child_spell_def.get("damage", 0),
                        speed=child_spell_def.get("speed", 100),
                        range_val=child_spell_def.get("range", 100),
                        projectile_type=child_info["spell_id"], # This is the spell_id
                        trajectory_properties=child_spell_def.get("trajectory_properties", {})
                    )
                    newly_spawned_children.append(child_projectile)

            if not projectile.active: # If projectile marked itself inactive (or forked)
                self.projectiles.remove(projectile)
        
        for child in newly_spawned_children:
            self.add_projectile(child)

    def render(self, screen, camera=None):
        """Render all projectiles"""
        for projectile in self.projectiles:
            projectile.render(screen, camera) # Projectile handles camera offset itself

    def check_enemy_collisions(self, enemies_group):
        """Check for collisions between projectiles and enemies.
        
        Args:
            enemies_group (pygame.sprite.Group or list): Group/list of enemies to check against.
            
        Returns:
            list: A list of (enemy, projectile, damage_amount) tuples for each collision.
        """
        collisions = []
        for projectile in self.projectiles:
            hit_enemies = pygame.sprite.spritecollide(projectile, enemies_group, False) 
            
            for enemy in hit_enemies:
                collisions.append((enemy, projectile, projectile.damage))
                projectile.on_hit_enemy(enemy, enemies_group) # This might set flags or change projectile state
                                                            # but does not directly spawn children here.
                if not projectile.active: 
                    break 
        
        # Child spawning is handled in ProjectileManager.update based on projectile.update() return value
        return collisions

# Need to ensure DataHandler is available here if ProjectileManager loads spell data in __init__
from src.data_handler import DataHandler # Ensure this import is present

def create_basic_projectile(x, y, target_x, target_y, damage, source="player"):
    """Create a basic projectile heading towards a target
    
    Args:
        x (float): Starting x position
        y (float): Starting y position
        target_x (float): Target x position
        target_y (float): Target y position
        damage (float): Damage amount
        source (str): Source of the projectile
        
    Returns:
        Projectile: The created projectile
    """
    # Calculate direction
    dx = target_x - x
    dy = target_y - y
    
    # Normalize
    magnitude = math.sqrt(dx * dx + dy * dy)
    if magnitude > 0:
        dx /= magnitude
        dy /= magnitude
    
    return Projectile(x, y, dx, dy, damage, source=source, trajectory_type=config.TRAJ_STRAIGHT) 