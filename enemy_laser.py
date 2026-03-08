import pygame
import random
import time
import globals

# EnemyLaser class to handle enemy laser mechanics (moving projectile)
class EnemyLaser:
    def __init__(self, start_pos, target_pos, damage_per_second): # Added damage_per_second
        self.start_pos = pygame.math.Vector2(start_pos)
        self.target_pos = pygame.math.Vector2(target_pos) # This is the target point when fired
        self.active = True
        self.speed = globals.enemy_projectile_speed # Use global speed for enemy projectiles
        self.lifetime = 2.0 # Laser exists for 2 seconds
        self.creation_time = time.time()
        self.damage_per_second = damage_per_second # Store damage per second

        self.direction = self.target_pos - self.start_pos
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()
        else: # If start and target are the same, pick a random direction
            self.direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()

        # Create a rect for collision detection, initially at start_pos
        self.rect = pygame.Rect(self.start_pos.x, self.start_pos.y, 10, 10) # Small rect for collision


    def update(self, dt):
        if not self.active: return

        # Move the laser projectile
        self.start_pos += self.direction * self.speed * dt
        self.rect.center = (int(self.start_pos.x), int(self.start_pos.y))

        # Check if laser has exceeded its lifetime
        if time.time() - self.creation_time > self.lifetime:
            self.active = False
            return

        # Check if laser is off-screen
        if not (0 - self.rect.width <= self.rect.x <= globals.SCREEN_WIDTH + self.rect.width and
                0 - self.rect.height <= self.rect.y <= globals.SCREEN_HEIGHT + self.rect.height):
            self.active = False


    def draw(self, screen):
        if self.active:
            # Draw a small circle for the laser projectile
            pygame.draw.circle(screen, (255, 255, 0), (int(self.start_pos.x), int(self.start_pos.y)), 5) # Yellow circle projectile
