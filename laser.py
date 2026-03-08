import pygame
import math
import globals
import time
from game_object import GameObject
from enemy import Enemy

# Laser class to handle player laser mechanics (continuous beam)
class Laser:
    def __init__(self, start_pos, end_pos, damage_per_second, max_range):
        self.start_pos = pygame.math.Vector2(start_pos)
        self.end_pos = pygame.math.Vector2(end_pos) # This will be updated dynamically
        self.damage_per_second = damage_per_second
        self.duration = 0
        self.active = False # Laser starts inactive, activated by gameplay loop
        self.max_range = max_range


    def update(self, dt, targets):
        if not self.active: return [] # Return empty list if inactive

        # The 'lifetime' concept is removed for continuous laser.
        # The 'active' state is controlled externally by gameplay.py.

        # Check if the target is within max range. If not, the laser should be deactivated externally.
        # This check is primarily for the drawing and damage application.
        # If the target moves out of range, gameplay.py should set self.active = False.
        # This update method assumes it's only called if the laser *should* be active.

        self.duration += dt
        targets_to_remove = self.damage_targets(targets, dt)
        return targets_to_remove


    def damage_targets(self, targets, dt):
        targets_to_remove = []
        # Iterate over a copy of the list to avoid issues when removing elements during iteration
        for target in list(targets):
            if hasattr(target, 'rect') and hasattr(target, 'hp'):
                # For a continuous laser, check if the target's center is within the beam's path
                # Since end_pos is dynamically updated to the target's center, a simple distance check is fine.
                distance_to_target_center = pygame.math.Vector2(self.end_pos).distance_to(target.rect.center)
                if distance_to_target_center <= target.rect.width // 2: # Check if target is 'hit' by the beam
                    damage_taken = self.damage_per_second * dt
                    globals.money += damage_taken
                    target.hp -= damage_taken

                    if target.hp <= 0:
                        targets_to_remove.append(target)
                        # No self.active = False here; the laser stays on as long as conditions allow.

        return targets_to_remove


    def draw(self, screen):
        if self.active: # Only draw if active
            pygame.draw.line(screen, (255, 0, 0), self.start_pos, self.end_pos, 3) # Red laser line

