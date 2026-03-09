import pygame
import math
import random
import globals # Assuming globals.py exists and has SCREEN_WIDTH, SCREEN_HEIGHT
import assets

# Utility function for getting off-screen spawn points and speeds
def get_offscreen_spawn_and_direction(width, height):
    direction = random.choice(['left', 'right', 'top', 'bottom'])
    x, y = 0, 0
    # Speeds in pixels per second
    x_speed, y_speed = 0, 0

    if direction == 'left':
        x = -width
        y = random.randint(0, globals.SCREEN_HEIGHT - height)
        x_speed = random.uniform(50, 150) # Speed towards right
        y_speed = random.uniform(-50, 50) # Vertical drift
    elif direction == 'right':
        x = globals.SCREEN_WIDTH
        y = random.randint(0, globals.SCREEN_HEIGHT - height)
        x_speed = random.uniform(-150, -50) # Speed towards left
        y_speed = random.uniform(-50, 50) # Vertical drift
    elif direction == 'top':
        x = random.randint(0, globals.SCREEN_WIDTH - width)
        y = -height
        x_speed = random.uniform(-50, 50) # Horizontal drift
        y_speed = random.uniform(50, 150) # Speed downwards
    elif direction == 'bottom':
        x = random.randint(0, globals.SCREEN_WIDTH - width)
        y = globals.SCREEN_HEIGHT
        x_speed = random.uniform(-50, 50) # Horizontal drift
        y_speed = random.uniform(-150, -50) # Speed upwards
    return x, y, x_speed, y_speed


# GameObject class to represent obstacles with health
class GameObject:
    def __init__(self, x, y, width, height, hp, x_speed, y_speed, image=None):
        self.original_image = image  
        self.image = image 
        
        if self.image:
            self.rect = self.image.get_rect(center=(x, y))
        else:
            self.rect = pygame.Rect(x, y, width, height)
            
        self.rect = self.rect.inflate(-20, -20) 
        self.hp = hp
        self.max_hp = hp
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.angle = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-100, 100)


    def move(self, dt):
        self.rect.x += self.x_speed * dt  # Move the obstacle horizontally
        self.rect.y += self.y_speed * dt  # Move the obstacle vertically

        # Update the angle and rotate the image for meteors
        if self.original_image: # Only rotate if there's an image
            self.angle += self.rotation_speed * dt
            self.image = pygame.transform.rotate(self.original_image, self.angle)
            self.rect = self.image.get_rect(center=self.rect.center) # Update rect to keep center

        # Check if the obstacle is out of view and reset it to a random off-screen position
        # Added a buffer of 100 pixels to ensure they are fully off-screen
        if self.rect.x + self.rect.width < -100 or self.rect.x > globals.SCREEN_WIDTH + 100 or \
           self.rect.y + self.rect.height < -100 or self.rect.y > globals.SCREEN_HEIGHT + 100:
            self.reset_position()
            return True # Indicate that the object was reset
        return False # Indicate that the object is still on-screen


    def reset_position(self):
        new_x, new_y, new_x_speed, new_y_speed = get_offscreen_spawn_and_direction(self.rect.width, self.rect.height)
        # Update position
        self.rect.center = (new_x, new_y) 
        self.x_speed = new_x_speed
        self.y_speed = new_y_speed
        self.hp = self.max_hp
        self.angle = random.uniform(0, 360)
        
        if self.original_image:
            self.image = pygame.transform.rotate(self.original_image, self.angle)
            # Re-center the rect after rotation
            self.rect = self.image.get_rect(center=self.rect.center)
