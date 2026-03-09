import pygame
import random
import math
import time
import assets
from game_object import GameObject, get_offscreen_spawn_and_direction
from enemy_laser import EnemyLaser # Explicitly import EnemyLaser
import globals

# Load enemy image (ensure this path is correct)
try:
    enemy_image = pygame.image.load(assets.resource_path('Images/Ships/ship-6.png'))
    enemy_image = pygame.transform.scale(enemy_image, (60, 60))
except pygame.error:
    print("Warning: enemy_image (ship-6.png) not found. Using a placeholder.")
    enemy_image = pygame.Surface((60, 60), pygame.SRCALPHA)
    pygame.draw.rect(enemy_image, (100, 50, 150), enemy_image.get_rect(), border_radius=5) # Placeholder

try:
    enemy_boss_image = pygame.image.load(assets.resource_path('Images/Ships/ship-5.png'))
    enemy_boss_image = pygame.transform.scale(enemy_boss_image, (120, 120))
except pygame.error:
    print("Warning: enemy_boss_image (enemy_boss.png) not found. Using a placeholder.")
    enemy_boss_image = pygame.Surface((90, 90), pygame.SRCALPHA)
    pygame.draw.circle(enemy_boss_image, (150, 50, 100), (45,45), 40) # Placeholder

# Enemy Module
class Enemy(GameObject):

    def __init__(self, level=1):
        x, y, x_speed_per_sec, y_speed_per_sec = get_offscreen_spawn_and_direction(70, 70)
    
        base_width = 70
        base_height = 70
        base_hp = 10
        base_speed = 100
        initial_rad = math.atan2(y_speed_per_sec, x_speed_per_sec)
        self.current_rotation = 270 - math.degrees(initial_rad) 
        self.is_turning = False
        self.rotation_threshold = 2.0  
        self.turn_speed = 5
        self.level = level
        width = base_width + (level - 1) * 5
        height = base_height + (level - 1) * 5
        hp = base_hp * level
        speed = base_speed + (level - 1) * 20

        self.is_boss_flag = (level % 5 == 0)
        if self.is_boss_flag:
            width = int(width * 1.5)
            height = int(height * 1.5)
            hp = int(hp * 3)
            speed = int(speed * 0.7)
            current_enemy_image = enemy_boss_image
        else:
            current_enemy_image = enemy_image

        scaled_image = pygame.transform.scale(current_enemy_image, (width, height))

        super().__init__(x=x,
                         y=y,
                         width=width,
                         height=height,
                         hp=hp,
                         x_speed=x_speed_per_sec,
                         y_speed=y_speed_per_sec,
                         image=scaled_image)

        self.max_hp = self.hp
        self.speed = speed
        self.mask = pygame.mask.from_surface(self.image)
        self.damage = globals.enemy_laser_damage_per_second + (globals.enemy_laser_damage_per_second * (self.level + 1))/10


        self.pattern = random.choice(self._available_patterns())
        self.shots_per_cycle = 2 + (level - 1)
        if self.is_boss_flag:
            self.shots_per_cycle *= 2
            self.shot_interval = 0.6
        else:
            self.shot_interval = 1.0
        self.shots_remaining = self.shots_per_cycle
        self.last_shot_time = time.time()

        self.state = 'enter'
        self.target_pos = None
        self.relocate_cooldown = 3.0
        self.last_relocate_trigger_time = time.time()

        self.lasers = []


    def is_boss(self):
        return self.is_boss_flag

    def _available_patterns(self):
        patterns = ['single']
        if self.level >= 2:
            patterns.append('burst')
        if self.level >= 3:
            patterns.append('spread')
        if self.is_boss_flag:
            patterns.append('omni')
        return patterns

    def update(self, dt, player_pos, player_radius):
        now = time.time()
        
        # 1. ALWAYS Update Lasers (independent of ship rotation/movement)
        lasers_to_remove = []
        for laser in self.lasers:
            laser.update(dt)
            if not laser.active:
                lasers_to_remove.append(laser)
        for laser in lasers_to_remove:
            if laser in self.lasers:
                self.lasers.remove(laser)

        # 2. Determine Rotation Target based on State
        target_dx, target_dy = 0, 0
        if self.state == 'attack':
            target_dx = player_pos[0] - self.rect.centerx
            target_dy = player_pos[1] - self.rect.centery
        elif self.state == 'relocate' and self.target_pos:
            target_dx = self.target_pos[0] - self.rect.centerx
            target_dy = self.target_pos[1] - self.rect.centery
        elif self.state == 'enter':
            target_dx = self.x_speed
            target_dy = self.y_speed

        # 3. Handle Rotation Logic
        if abs(target_dx) > 0.1 or abs(target_dy) > 0.1:
            target_rad = math.atan2(target_dy, target_dx)
            target_angle = 270 - math.degrees(target_rad)
            angle_diff = (target_angle - self.current_rotation + 180) % 360 - 180
            
            if abs(angle_diff) > self.rotation_threshold:
                self.is_turning = True
                self.current_rotation += angle_diff * self.turn_speed * dt
            else:
                self.is_turning = False
                self.current_rotation = target_angle 

            self.current_rotation %= 360
            self.image = pygame.transform.rotate(self.original_image, self.current_rotation)
            self.rect = self.image.get_rect(center=self.rect.center)
            
            self.mask = pygame.mask.from_surface(self.image)

        # 4. State Machine: Movement and Transitions
        # We only move if we aren't busy turning
        can_move = not self.is_turning 

        if self.state == 'enter' and can_move:
            super().move(dt)
            if (0 <= self.rect.x <= globals.SCREEN_WIDTH - self.rect.width and
                0 <= self.rect.y <= globals.SCREEN_HEIGHT - self.rect.height):
                self._switch_to_attack(now)

        elif self.state == 'relocate' and can_move:
            # Move towards target_pos
            dir_vec = pygame.math.Vector2(self.target_pos) - pygame.math.Vector2(self.rect.center)
            dist = dir_vec.length()
            
            if dist > self.speed * dt:
                dir_vec = dir_vec.normalize()
                self.rect.x += dir_vec.x * self.speed * dt
                self.rect.y += dir_vec.y * self.speed * dt
            else:
                # Arrived at destination
                self.rect.center = self.target_pos
                self._switch_to_attack(now)
        
        # 5. Shooting Phase (Only in Attack State)
        if self.state == 'attack':
            # Only shoot if aimed at player (not turning)
            if not self.is_turning:
                if self.shots_remaining > 0 and now - self.last_shot_time >= self.shot_interval:
                    self._shoot(player_pos)
                    self.shots_remaining -= 1
                    self.last_shot_time = now
            
            # Switch to relocate after shots are done OR time is up
            if self.shots_remaining <= 0 or now - self.last_relocate_trigger_time >= self.relocate_cooldown:
                self.state = 'relocate'
                self._set_relocate_target()

    def _switch_to_attack(self, current_time):
        """Helper to reset all variables when entering combat mode."""
        self.state = 'attack'
        self.shots_remaining = self.shots_per_cycle
        self.last_relocate_trigger_time = current_time
        self.x_speed = 0 # Stop base movement
        self.y_speed = 0


    def _set_relocate_target(self):
        self.target_pos = (random.randint(self.rect.width, globals.SCREEN_WIDTH - self.rect.width),
                           random.randint(self.rect.height, globals.SCREEN_HEIGHT - self.rect.height))

    def _shoot(self, player_pos):
        sx, sy = self.rect.center
        px, py = player_pos
        # Pass globals.enemy_laser_damage_per_second to EnemyLaser
        if self.pattern == 'single':
            self.lasers.append(EnemyLaser((sx, sy), player_pos, globals.enemy_laser_damage_per_second))
        elif self.pattern == 'burst':
            for _ in range(3):
                self.lasers.append(EnemyLaser((sx, sy), player_pos, globals.enemy_laser_damage_per_second))
        elif self.pattern == 'spread':
            angle = math.atan2(py - sy, px - sx)
            spread = math.radians(30)
            for i in range(5):
                offset = angle - spread/2 + spread * i/4
                ex = sx + math.cos(offset) * 1000
                ey = sy + math.sin(offset) * 1000
                self.lasers.append(EnemyLaser((sx, sy), (ex, ey), globals.enemy_laser_damage_per_second ))
        elif self.pattern == 'omni':
            for deg in range(0, 360, 30):
                rad = math.radians(deg)
                ex = sx + math.cos(rad) * 1000
                ey = sy + math.sin(rad) * 1000
                self.lasers.append(EnemyLaser((sx, sy), (ex, ey), globals.enemy_laser_damage_per_second ))

    def draw(self, screen):
        screen.blit(self.image, self.rect)

        # Health bar
        hb_w, hb_h = self.rect.width, 8
        hp_frac = self.hp / self.max_hp
        pygame.draw.rect(screen, (255, 0, 0), (self.rect.x, self.rect.y - hb_h - 2, hb_w, hb_h))
        pygame.draw.rect(screen, (0, 255, 0), (self.rect.x, self.rect.y - hb_h - 2, int(hb_w * hp_frac), hb_h))

        # Draw enemy's projectiles
        for laser in self.lasers:
            laser.draw(screen)

