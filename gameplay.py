import pygame
import sys
import random
import math
from skilltree import skill_tree_page
import globals
import time 
from buttons import *

explosion_images = {
    1 : pygame.transform.scale(pygame.image.load('Images/Explosion/explosion1.png'), (60,60)),
    2 : pygame.transform.scale(pygame.image.load('Images/Explosion/explosion2.png'), (60,60)),
    3 : pygame.transform.scale(pygame.image.load('Images/Explosion/explosion3.png'), (60,60)),
    4 : pygame.transform.scale(pygame.image.load('Images/Explosion/explosion4.png'), (60,60)),
    5 : pygame.transform.scale(pygame.image.load('Images/Explosion/explosion5_scuffed.png'), (60,60)),
    6 : pygame.transform.scale(pygame.image.load('Images/Explosion/explosion6.png'), (60,60)),
    7 : pygame.transform.scale(pygame.image.load('Images/Explosion/explosion7.png'), (60,60))
}


meteorite_images = {
    1 : pygame.transform.scale(pygame.image.load('Images/Meteors/meteor1.jpeg'), (50,50)),
    2 : pygame.transform.scale(pygame.image.load('Images/Meteors/meteor2.jpeg'), (50,50)),
    3 : pygame.transform.scale(pygame.image.load('Images/Meteors/meteor3.jpeg'), (50,50)),
    4 : pygame.transform.scale(pygame.image.load('Images/Meteors/meteor4.jpeg'), (50,50)),
    5 : pygame.transform.scale(pygame.image.load('Images/Meteors/meteor5.jpeg'), (50,50)),
    6 : pygame.transform.scale(pygame.image.load('Images/Meteors/meteor6.jpeg'), (50,50))
}

skill_tree_button = create_button("Skill Tree", 810, 490, 300, 75)
Restart_button = create_button(   "Restart",    810, 560, 300, 75)
quit_button = create_button(      "Quit",       810, 630, 300, 75)
continue_button = create_button(  "Continue",   810, 420, 300, 75)

game_over_buttons = [
    quit_button,
    Restart_button,
    skill_tree_button
]

pause_menu_buttons = [
    continue_button,
    Restart_button,
    quit_button,
    skill_tree_button
]
    


explosion_sound = pygame.mixer.Sound("Images/Explosion/explosion_alternate1.mp3")

obstacles = []

current_player_rotation_angle = 0 

background_image = pygame.image.load('Images/menu (1).jpeg')  
background_image = pygame.transform.scale(background_image, (1920, 1080)) 

raw_player_image = pygame.image.load('Images/Ships/ship-2.jpeg').convert_alpha()
raw_player_image = pygame.transform.scale(raw_player_image, (globals.player_size, globals.player_size))
original_player_image = pygame.Surface(
    (globals.player_size, globals.player_size), pygame.SRCALPHA
)
original_player_image.blit(raw_player_image, (0, 0))
temp_mask_surface = pygame.Surface(
    (globals.player_size, globals.player_size), pygame.SRCALPHA
)
pygame.draw.circle(
    temp_mask_surface, (255, 255, 255, 255),
    (globals.player_size // 2, globals.player_size // 2),
    globals.player_size // 2
)
original_player_image.blit(temp_mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)



player_image = original_player_image.copy() 




# Function to check if two circles collide
def check_collision(player_pos, player_radius, obstacle):
    # Calculate distance between player center and obstacle center
    distance = pygame.math.Vector2(player_pos).distance_to(obstacle.center)
    return distance < player_radius + obstacle.width // 2  # If the distance is less than the combined radius

# Function to display the game over screen with buttons
def game_over_screen(screen, font, player_pos, no_fuel = False ):
    global mouse_x, mouse_y
    fuel_empty_rect = pygame.Rect(globals.SCREEN_WIDTH /2 - 145, 360, 300, 75)
    game_over_rect = pygame.Rect(globals.SCREEN_WIDTH /2 - 145, 300, 300, 75)

    
    if not no_fuel:
        pygame.draw.circle(screen, (255, 120, 51), player_pos, 30)
        explosion_sound.play()
        explosion_delay = 100
        last_explosion_time = pygame.time.get_ticks()
        explosion_frame = 1
        while explosion_frame < len(explosion_images):
            now = pygame.time.get_ticks()
            if now - last_explosion_time > explosion_delay:
                explosion_frame += 1
                last_explosion_time = now
            explosion_image = explosion_images[explosion_frame].convert_alpha()
            x,y = player_pos
            screen.blit(explosion_image, (x-30,y-30))
            pygame.display.update(x,y,60,60)
    
       
    top = (100, 180, 220, 55)
    bottom = (30, 60, 90, 55)
    rect_gradient = create_vertical_color_gradient((400, 1080), top, bottom)
    screen.blit(rect_gradient, ( globals.SCREEN_WIDTH /2 - 200, 0))  

    game_over_text = text_styling((game_over_rect,"Game Over"), screen)
    if no_fuel:
        
        fuel_empty_text = text_styling((fuel_empty_rect,"Ran Out Of Fuel"), screen)     
    
    return choice_menu(game_over_buttons,screen)

def pause_screen(screen, font):
    font = pygame.font.SysFont("8-Bit-Madness", 46)
    font.set_bold(True)
    pause_text_rect = pygame.Rect(globals.SCREEN_WIDTH /2 - 145, 300, 300, 75)
    top = (100, 180, 220, 55)
    bottom = (30, 60, 90, 55)
    rect_gradient = create_vertical_color_gradient((400, 1080), top, bottom)
    screen.blit(rect_gradient, ( globals.SCREEN_WIDTH /2 - 200, 0))  
    
    pause_text = text_styling( (pause_text_rect,"Paused"), screen)
    return choice_menu(pause_menu_buttons,screen)
    
def choice_menu(button_list, screen):
        while True:
    
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    for button in button_list:
                        if button[0].collidepoint(mouse_x, mouse_y):
                            return button[1]
                        
            mouse_x, mouse_y = pygame.mouse.get_pos()
            for button in button_list:
                if button[0].collidepoint(mouse_x,mouse_y):
                    button_draw(button, screen, hover = True)
                else:
                    button_draw(button, screen)



            pygame.display.update()
        


def game_over_result(screen, font, player_pos, no_fuel = False):
        result = game_over_screen(screen, font, player_pos, no_fuel )
        obstacles.clear()

        if result == "Skill Tree":
            skill_tree_page(screen, (255,255,255), font, gameplay_page)
        elif result == "Restart":
            gameplay_page(screen, (255, 255, 255), font)  # Restart gameplay
        elif result == "Quit":
            pygame.quit()
            sys.exit()
            
def pause_screen_result(screen, font, text = "Paused"):
        result = pause_screen(screen, font)
        if result == "Skill Tree":
            skill_tree_page(screen, (255,255,255), font, gameplay_page)
        elif result == "Continue":
            return
        elif result == "Restart":
            gameplay_page(screen, (255, 255, 255), font)  # Restart gameplay
        elif result == "Quit":
            pygame.quit()
            sys.exit()

# Laser class to handle laser mechanics
class Laser:
    def __init__(self, start_pos, end_pos, damage_per_second):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.damage_per_second = damage_per_second  # Dynamic damage per second
        self.duration = 0  # Duration in seconds
        self.length = math.dist(start_pos, end_pos)  # Calculate the length of the laser

    def update(self, dt, obstacles):
        self.duration += dt
        # Apply damage continuously while the laser is active
        self.damage_obstacles(obstacles, dt)

    def damage_obstacles(self, obstacles, dt):
        for obstacle in obstacles:
            distance_to_obstacle = pygame.math.Vector2(self.end_pos).distance_to(obstacle.rect.center)
            if distance_to_obstacle <= obstacle.rect.width // 2:  # Check if obstacle is within range
                # Damage applied per frame, based on damage per second and time delta (dt)
                damage_taken = self.damage_per_second * dt  # Adjust damage per frame
                globals.money += damage_taken  # Increment money based on damage dealt
                obstacle.hp -= damage_taken  # Reduce the object’s HP
                obstacle.last_damage = damage_taken  # Track the last damage taken by the obstacle

                if obstacle.hp <= 0:
                    obstacles.remove(obstacle)  # Remove the obstacle if HP reaches 0

    def draw(self, screen):
        pygame.draw.line(screen, (255, 0, 0), self.start_pos, self.end_pos, 3)  # Red laser line

# GameObject class to represent obstacles with health
class GameObject:
    def __init__(self, x, y, width, height, hp, x_speed, y_speed, image = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.hp = hp
        self.x_speed = x_speed  # Speed of the obstacle
        self.y_speed = y_speed
        self.image = image
    def move(self):
        self.rect.x += self.x_speed  # Move the obstacle horizontally
        self.rect.y += self.y_speed  # Move the obstacle vertically
        
          # Check if the obstacle is out of view and reset it to a random off-screen position
        if self.rect.x + self.rect.width < 0 or self.rect.x > 1920 or self.rect.y + self.rect.height < 0 or self.rect.y > 1080:
            self.reset_position()  # Reset position if off-screen
            
    def reset_position(self):
        move_into_screen(self)
        self.hp = 10  # Reset health to 10 when it goes off-screen


def move_into_screen(x = 0, y = 0, x_speed = 0, y_speed = 0):
        direction = random.choice(['left', 'right', 'top', 'bottom'])
        if direction == 'left':
            x = -50  # Place off-screen to the left
            y = random.randint(0, 1080)  # Random y position within the screen height
            x_speed = random.uniform(1, 3)  # Random speed between 1 and 3 pixels per frame
            y_speed = random.uniform(-1, 1)  # Random vertical speed (up or down)
        elif direction == 'right':
            x = 1920  # Place off-screen to the right
            y = random.randint(0, 1080)  # Random y position within the screen height
            x_speed = random.uniform(-3, -1)  # Random speed between -1 and -3 (towards left)
            y_speed = random.uniform(-1, 1)  # Random vertical speed (up or down)
        elif direction == 'top':
            x = random.randint(0, 1920)  # Random x position within the screen width
            y = -50  # Place off-screen above the window
            x_speed = random.uniform(-1, 1)  # Random horizontal speed (left or right)
            y_speed = random.uniform(1, 3)  # Random downward speed
        elif direction == 'bottom':
            x = random.randint(0, 1920)  # Random x position within the screen width
            y = 1080  # Place off-screen below the window
            x_speed = random.uniform(-1, 1)  # Random horizontal speed (left or right)
            y_speed = random.uniform(-3, -1)  # Random upward speed
        return GameObject(x, y, 50, 50, 10, x_speed, y_speed, meteorite_images[random.randint(1,6)])
            
def generate_obstacles():
    num_obstacles = random.randint(3, 6)  # Generate between 1 and 4 obstacles
    for _ in range(num_obstacles):
        obstacle = move_into_screen()
        obstacles.append(obstacle)
    return obstacles






def player_move(player_pos, mouse_pos):
    global current_player_rotation_angle
    player_x, player_y = player_pos
    mouse_x, mouse_y = mouse_pos
    

    # Calculate the difference in x and y directions
    delta_x = mouse_x - player_x
    delta_y = mouse_y - player_y

        
    # Calculate the distance to the mouse position
    distance = math.sqrt(delta_x ** 2 + delta_y ** 2)

    # Calculate the variable speed based on the distance
    # The farther the distance, the faster the speed, capped at max_speed
    speed = min(globals.player_movement_speed, (distance * 0.05))  # You can tweak 0.1 to control the speed curve
    
    angle_radians = math.atan2(delta_y, delta_x)
    angle_degrees = math.degrees(angle_radians)
    rotation_angle = 270 - angle_degrees
    
    current_normalized = (current_player_rotation_angle  + 180) % 360 - 180
    target_normalized = (rotation_angle + 180) % 360 - 180

    # Calculate the shortest angle difference
    angle_difference = target_normalized - current_normalized
    if angle_difference > 180:
        angle_difference -= 360
    elif angle_difference < -180:
        angle_difference += 360
        
    current_player_rotation_angle += angle_difference * globals.player_turn_speed

    # Keep the angle within a reasonable range (e.g., 0 to 360)
    current_player_rotation_angle %= 360


    # If the player is within the movement speed, just move to the mouse position
    if distance <= speed:
        player_x = mouse_x
        player_y = mouse_y
    else:
        # Scale the movement to the calculated speed
        move_ratio = speed / distance
        player_x += delta_x * move_ratio
        player_y += delta_y * move_ratio

    return (player_x, player_y, current_player_rotation_angle)



# Main gameplay loop with collision and laser mechanics
def gameplay_page(screen, WHITE, font):
    global obstacles
    obstacles.clear()

    energy_font = pygame.font.Font(None, 18)  # Font for energy display
    # obstacles  = []  # List to hold obstacles
    
    # Set up the clock for consistent frame rate
    clock = pygame.time.Clock()
    # mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_x, mouse_y = globals.SCREEN_WIDTH/2, globals.SCREEN_HEIGHT/2
    player_x,player_y = mouse_x, mouse_y

    # Player settings
    player_radius = 30  # Size of the player (circle)
    player_color = (0, 0, 255)  # Blue color for the player
    globals.player_energy = globals.player_max_energy  # Set initial player energy

    last_obstacle_time = time.time()  # Track the last time obstacles were generated
    obstacle_generation_interval = random.uniform(0, 1)  # Random interval between 2 and 5 seconds
    
    # Laser list to hold the lasers created in the game
    lasers = []

    while True:
        
        screen.fill(WHITE)  # Clear the screen with white background
        screen.blit(background_image, (0, 0))

        pygame.mouse.set_visible(False)  # Hide mouse cursor during gameplay
        current_time = time.time()
        if current_time - last_obstacle_time >= obstacle_generation_interval:
            obstacles = generate_obstacles()  # Generate new obstacles
            last_obstacle_time = current_time  # Update the time
            obstacle_generation_interval = random.uniform(2, 5)  # Set new random interval

        # Draw the obstacles
        for obstacle in obstacles:
            obstacle.move()  # Move the obstacle
            
            # pygame.draw.rect(screen, (255, 0, 0), obstacle.rect)  # Red color for obstacles

 

        # Get the current mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        player_x, player_y, rotation_angle = player_move((player_x,player_y), (mouse_x, mouse_y))
        # player_image = pygame.transform.rotate(original_player_image, rotation_angle)
        rotated_player_image = pygame.transform.rotate(original_player_image, current_player_rotation_angle)
        player_rect_for_blit = rotated_player_image.get_rect(center=(player_x, player_y))
        # player_rect = player_image.get_rect(center=(player_x, player_y))
        player_pos = (player_x, player_y)
        screen.blit(rotated_player_image, player_rect_for_blit)
        
        # pygame.draw.circle(screen, player_color, player_pos, player_radius)


        globals.player_energy -= globals.energy_depletion_rate*10  # Decrease player energy over time
        if globals.player_energy <= 0:
            pygame.mouse.set_visible(True)  # Show mouse cursor again
            game_over_result(screen, font, player_pos, no_fuel = True)  # Show game over screen
            
 
        energy_bar_x, energy_bar_y = 20, 20
        energy_bar_width, energy_bar_height = 200, 25
        pygame.draw.rect(screen, (100, 100, 100), (energy_bar_x, energy_bar_y, energy_bar_width, energy_bar_height))
        # Draw current energy (green)
        energy_width = int((globals.player_energy / globals.player_max_energy) * energy_bar_width)
        pygame.draw.rect(screen, (0, 255, 0), (energy_bar_x, energy_bar_y, energy_width, energy_bar_height))

        # Draw border around energy bar (black)
        pygame.draw.rect(screen, (0, 0, 0), (energy_bar_x, energy_bar_y, energy_bar_width, energy_bar_height), 2)

        # Optional: Show "Energy" label
        energy_text = energy_font.render("Energy", True, (0, 0, 0))
        screen.blit(energy_text , (energy_bar_x + 6, energy_bar_y + 6))

        money_text = font.render(f"Money: {round(globals.money, 2)}", True, (0, 0, 0))  # Black color for the text
        screen.blit(money_text, (10, 50))  # Display money below energy
        
        # Draw obstacles (rectangles)
        for obstacle in obstacles:
            screen.blit(obstacle.image, (obstacle.rect.x, obstacle.rect.y))
            
        # Display FPS in the top right corner
        fps = int(clock.get_fps())
        fps_text = font.render(f"FPS: {fps}", True, (0, 0, 0))  # Black color for the text
        screen.blit(fps_text, (screen.get_width() - fps_text.get_width() - 10, 10))
        
        enemies = len(obstacles)  # Count the number of enemies
        enemies_text = font.render(f"enemies: {enemies}", True, (0, 0, 0))  # Black color for the text
        screen.blit(enemies_text, (screen.get_width() - fps_text.get_width() - 60, 50))

        # Check for collisions with any obstacles
        for obstacle in obstacles:
            if check_collision(player_pos, player_radius, obstacle.rect):
                pygame.mouse.set_visible(True)  # Show mouse cursor again

                game_over_result(screen, font, player_pos)  # Show game over screen if collision occurs

        # Laser mechanics
        # Count how many lasers are currently active BEFORE attempting to create new ones
        active_lasers = sum(1 for obstacle in obstacles if hasattr(obstacle, 'laser') and obstacle.laser is not None)

        for obstacle in obstacles:
            obstacle_center = obstacle.rect.center
            distance_to_obstacle = pygame.math.Vector2(player_pos).distance_to(obstacle_center)

            # Draw health bar above the obstacle
            health_bar_width = 50
            health_bar_height = 10
            health_percentage = obstacle.hp / 10
            pygame.draw.rect(screen, (0, 255, 0), (obstacle.rect.x , obstacle.rect.y - 15, health_bar_width * health_percentage, health_bar_height))
            pygame.draw.rect(screen, (0, 0, 0), (obstacle.rect.x , obstacle.rect.y - 15, health_bar_width, health_bar_height), 2)

            if distance_to_obstacle < 150:
                # Only create a new laser if under the max limit
                if (not hasattr(obstacle, 'laser') or obstacle.laser is None) and active_lasers < globals.max_lasers:
                    obstacle.laser = Laser(player_pos, obstacle_center, globals.laser_damage)
                    active_lasers += 1  # Increment since a new laser is created

                if hasattr(obstacle, 'laser') and obstacle.laser is not None:
                    obstacle.laser.start_pos = player_pos
                    obstacle.laser.end_pos = obstacle_center
                    obstacle.laser.update(clock.get_time() / 1000.0, obstacles)
                    obstacle.laser.draw(screen)

                # Remove laser if obstacle is dead
                if obstacle.hp <= 0 and hasattr(obstacle, 'laser') and obstacle.laser is not None:
                    obstacle.laser = None
                    active_lasers -= 1

            else:
                # Player is not near, remove laser if exists
                if hasattr(obstacle, 'laser') and obstacle.laser is not None:
                    obstacle.laser = None
                    active_lasers -= 1
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mouse.set_visible(True)
                    pause_screen_result(screen, font, "Paused")  # Show game over screen when Escape is pressed
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Update the display
        pygame.display.update()

        # Control the frame rate (60 FPS)
        clock.tick(60)
