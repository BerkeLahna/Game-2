import pygame
import math
import random
import globals # Assuming globals.py exists and has SCREEN_WIDTH, SCREEN_HEIGHT

# Meteorite images are now defined here, as this is the GameObject base for them
meteorite_images = {
    1 : pygame.transform.scale(pygame.image.load('Images/Meteors/meteor1.png'), (50,50)),
    2 : pygame.transform.scale(pygame.image.load('Images/Meteors/meteor2.png'), (50,50)),
    3 : pygame.transform.scale(pygame.image.load('Images/Meteors/meteor3.png'), (50,50)),
    4 : pygame.transform.scale(pygame.image.load('Images/Meteors/meteor4.png'), (50,50)),
    5 : pygame.transform.scale(pygame.image.load('Images/Meteors/meteor5.png'), (50,50)),
    6 : pygame.transform.scale(pygame.image.load('Images/Meteors/meteor6.png'), (50,50))
}

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
        self.rect = pygame.Rect(x, y, width, height)
        self.hp = hp
        self.max_hp = hp  # Store max HP for health bar
        self.x_speed = x_speed  # Speed of the obstacle in pixels per second
        self.y_speed = y_speed  # Speed of the obstacle in pixels per second
        self.original_image = image  # Store the original image for rotation
        self.image = image # Current image (will be rotated)
        self.angle = random.uniform(0, 360)  # Initial random angle
        self.rotation_speed = random.uniform(-100, 100)  # Random rotation speed in degrees per second


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
        # Reset position and speed using the utility function
        new_x, new_y, new_x_speed, new_y_speed = get_offscreen_spawn_and_direction(self.rect.width, self.rect.height)
        self.rect.x = new_x
        self.rect.y = new_y
        self.x_speed = new_x_speed
        self.y_speed = new_y_speed
        self.hp = self.max_hp  # Reset health to max HP
        self.angle = random.uniform(0, 360) # Reset angle
        self.rotation_speed = random.uniform(-100, 100) # Reset rotation speed
        if self.original_image:
            self.image = pygame.transform.rotate(self.original_image, self.angle)
            self.rect = self.image.get_rect(center=(self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height // 2))

