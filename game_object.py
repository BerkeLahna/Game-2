import pygame
import math
import random
import globals 
import assets




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
        self.is_exploding = False
        self.explosion_timer = 0
        self.explosion_duration = 0.5 

    def take_damage(self, amount):
        """Standard way to apply damage and check for death."""
        if not self.is_exploding:
            self.hp -= amount
            if self.hp <= 0:
                self.trigger_explosion()

    def trigger_explosion(self):
        self.is_exploding = True
        self.hp = 0
        assets.explosion_sound.play() # Play sound once upon death

    @property
    def should_remove(self):
        """Replaces 'is_dead' to account for the animation time."""
        return self.hp <= 0 and not self.is_exploding

    def move(self, dt):
        self.rect.x += self.x_speed * dt 
        self.rect.y += self.y_speed * dt  

        if self.original_image: 
            self.angle += self.rotation_speed * dt
            self.image = pygame.transform.rotate(self.original_image, self.angle)
            self.rect = self.image.get_rect(center=self.rect.center) 

 
        if self.rect.x + self.rect.width < -100 or self.rect.x > globals.SCREEN_WIDTH + 100 or \
           self.rect.y + self.rect.height < -100 or self.rect.y > globals.SCREEN_HEIGHT + 100:
            self.reset_position()
            return True 
        return False

    def draw(self, screen, dt):
        if self.is_exploding:
            self.explosion_timer += dt
            explosion_radius = int((self.explosion_timer / self.explosion_duration) * self.rect.width)
            pygame.draw.circle(screen, (255, 165, 0), self.rect.center, explosion_radius)
            
            if self.explosion_timer >= self.explosion_duration:
                self.is_exploding = False # This will now let 'should_remove' return True
        else:
            screen.blit(self.image, self.rect)
    @property
    def is_dead(self):
        """Returns True if the object's health has depleted."""
        return self.hp <= 0
    
    
    def reset_position(self):
        new_x, new_y, new_x_speed, new_y_speed = self.random_spawn(self.rect.width, self.rect.height)
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
    # Inside game_object.py

    def check_collision(self, circle_pos, circle_radius, rect):
        scaled_radius = circle_radius * 0.5
        
        shrink_x = -(rect.width * 0.1)
        shrink_y = -(rect.height * 0.1)
        scaled_rect = rect.inflate(shrink_x, shrink_y)

        closest_x = max(scaled_rect.left, min(circle_pos[0], scaled_rect.right))
        closest_y = max(scaled_rect.top, min(circle_pos[1], scaled_rect.bottom))

        dx = circle_pos[0] - closest_x
        dy = circle_pos[1] - closest_y

        distance_squared = (dx ** 2) + (dy ** 2)
        return distance_squared < (scaled_radius ** 2)
    
    def random_spawn(self, width, height):
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