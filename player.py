import pygame
import math
import globals
import assets
from game_object import GameObject



class Player(GameObject):
    def __init__(self):
        # Initialize as GameObject (x, y, width, height, hp, x_speed, y_speed, image)
        super().__init__(
            x=globals.SCREEN_WIDTH // 2, 
            y=globals.SCREEN_HEIGHT // 2, 
            width=globals.player_size, 
            height=globals.player_size, 
            hp=globals.player_max_hp, 
            x_speed=0, 
            y_speed=0, 
            image=assets.player_image
        )
        self.radius = 30
        self.rotation_angle = 0
        self.current_rotation_angle = 0

    def update(self, dt):
        """Handles both movement and energy depletion."""
        # 1. Update Position based on Mouse
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - self.rect.centerx
        dy = mouse_y - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 5:
            move_x = (dx / distance) * globals.player_movement_speed
            move_y = (dy / distance) * globals.player_movement_speed
            self.rect.x += move_x
            self.rect.y += move_y
            self.rotation_angle = math.degrees(math.atan2(-move_y, move_x)) - 90

        # 2. Update Energy (Moved from gameplay.py)
        globals.player_energy -= globals.energy_depletion_rate * dt * 100

    def draw(self, screen):
        """Handles rotated rendering."""
        rotated_image = pygame.transform.rotate(self.original_image, self.rotation_angle)
        new_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, new_rect)
        
    def move(self, player_pos, mouse_pos):

        player_x, player_y = player_pos
        mouse_x, mouse_y = mouse_pos

        dx = mouse_x - player_x
        dy = mouse_y - player_y

        distance = math.hypot(dx, dy)

        speed = min(globals.player_movement_speed, distance * 0.05)

        angle_radians = math.atan2(dy, dx)
        angle_degrees = math.degrees(angle_radians)

        rotation_angle = 270 - angle_degrees

        current_normalized = (self.current_rotation_angle + 180) % 360 - 180
        target_normalized = (rotation_angle + 180) % 360 - 180

        diff = target_normalized - current_normalized

        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360

        self.current_rotation_angle += diff * globals.player_turn_speed
        self.current_rotation_angle %= 360

        if distance <= speed:
            player_x = mouse_x
            player_y = mouse_y
        else:
            ratio = speed / distance
            player_x += dx * ratio
            player_y += dy * ratio

        return player_x, player_y, self.current_rotation_angle