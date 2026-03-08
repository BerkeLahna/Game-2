import pygame
import sys
import random
import math
from skilltree import skill_tree_page
import globals
import time
from buttons import *
from enemy import Enemy
from enemy_laser import EnemyLaser
from laser import Laser
from game_object import GameObject, get_offscreen_spawn_and_direction, meteorite_images

explosion_images = {
    1 : pygame.transform.scale(pygame.image.load('Images/Explosion/explosion1.png'), (60,60)),
    2 : pygame.transform.scale(pygame.image.load('Images/Explosion/explosion2.png'), (60,60)),
    3 : pygame.transform.scale(pygame.image.load('Images/Explosion/explosion3.png'), (60,60)),
    4 : pygame.transform.scale(pygame.image.load('Images/Explosion/explosion4.png'), (60,60)),
    5 : pygame.transform.scale(pygame.image.load('Images/Explosion/explosion5_scuffed.png'), (60,60)),
    6 : pygame.transform.scale(pygame.image.load('Images/Explosion/explosion6.png'), (60,60)),
    7 : pygame.transform.scale(pygame.image.load('Images/Explosion/explosion7.png'), (60,60))
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
enemies = []

current_player_rotation_angle = 0

background_image = pygame.image.load('Images/menu (1).jpeg')
background_image = pygame.transform.scale(background_image, (1920, 1080))

raw_player_image = pygame.image.load('Images/Ships/ship-2.png').convert_alpha()
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
def check_collision(player_pos, player_radius, other_rect):
    distance = pygame.math.Vector2(player_pos).distance_to(other_rect.center)
    # Adjusted offset for more forgiving projectile collision
    return distance < (player_radius + other_rect.width // 2 - 5)

def game_over_screen(screen, font, player_pos, no_fuel = False ):
    pygame.mouse.set_visible(True)
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
    pygame.mouse.set_visible(True)
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
        enemies.clear()

        if result == "Skill Tree":
            skill_tree_page(screen, (255,255,255), font, gameplay_page)
        elif result == "Restart":
            globals.player_hp = globals.player_max_hp
            globals.player_energy = globals.player_max_energy
            globals.money = 0
            gameplay_page(screen, (255, 255, 255), font)
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
            globals.player_hp = globals.player_max_hp
            globals.player_energy = globals.player_max_energy
            globals.money = 0
            gameplay_page(screen, (255, 255, 255), font)
        elif result == "Quit":
            pygame.quit()
            sys.exit()


def generate_obstacles():
    num_obstacles = random.randint(3, 6)
    new_obstacles = []
    for _ in range(num_obstacles):
        x, y, x_speed_per_sec, y_speed_per_sec = get_offscreen_spawn_and_direction(50, 50)
        obstacle = GameObject(x, y, 50, 50, 10, x_speed_per_sec, y_speed_per_sec, meteorite_images[random.randint(1,6)])
        new_obstacles.append(obstacle)
    return new_obstacles

def spawn_enemies(level, count):
    new_enemies = []
    for _ in range(count):
        new_enemies.append(Enemy(level))
    return new_enemies

def player_move(player_pos, mouse_pos):
    global current_player_rotation_angle
    player_x, player_y = player_pos
    mouse_x, mouse_y = mouse_pos

    delta_x = mouse_x - player_x
    delta_y = mouse_y - player_y

    distance = math.sqrt(delta_x ** 2 + delta_y ** 2)

    speed = min(globals.player_movement_speed, (distance * 0.05))

    angle_radians = math.atan2(delta_y, delta_x)
    angle_degrees = math.degrees(angle_radians)
    rotation_angle = 270 - angle_degrees

    current_normalized = (current_player_rotation_angle + 180) % 360 - 180
    target_normalized = (rotation_angle + 180) % 360 - 180

    angle_difference = target_normalized - current_normalized
    if angle_difference > 180:
        angle_difference -= 360
    elif angle_difference < -180:
        angle_difference += 360

    current_player_rotation_angle += angle_difference * globals.player_turn_speed
    current_player_rotation_angle %= 360

    if distance <= speed:
        player_x = mouse_x
        player_y = mouse_y
    else:
        move_ratio = speed / distance
        player_x += delta_x * move_ratio
        player_y += delta_y * move_ratio

    return (player_x, player_y, current_player_rotation_angle)


def gameplay_page(screen, WHITE, font):
    global obstacles, enemies, globals

    obstacles.clear()
    enemies.clear()
    globals.player_hp = globals.player_max_hp
    globals.player_energy = globals.player_max_energy
    globals.money = 0
    game_level = 1

    energy_font = pygame.font.Font(None, 18)
    hp_font = pygame.font.Font(None, 18)

    clock = pygame.time.Clock()
    mouse_x, mouse_y = globals.SCREEN_WIDTH / 2, globals.SCREEN_HEIGHT / 2
    player_x, player_y = mouse_x, mouse_y

    player_radius = 30

    last_obstacle_time = time.time()
    obstacle_generation_interval = random.uniform(0, 1)
    last_enemy_spawn_time = time.time()
    enemy_spawn_interval = 5.0

    player_laser = None
    gameplay_page.last_player_laser_time = 0


    while True:
        dt = clock.get_time() / 1000.0

        screen.fill(WHITE)
        screen.blit(background_image, (0, 0))
        pygame.mouse.set_visible(False)

        current_time = time.time()

        if current_time - last_obstacle_time >= obstacle_generation_interval:
            obstacles.extend(generate_obstacles())
            last_obstacle_time = current_time
            obstacle_generation_interval = random.uniform(2, 5)

        if current_time - last_enemy_spawn_time >= enemy_spawn_interval:
            enemies.extend(spawn_enemies(game_level, 1))
            last_enemy_spawn_time = current_time
            enemy_spawn_interval = random.uniform(5, 10)

            game_level += 1
            print(f"Game Level: {game_level}")


        # --- Update and Draw Obstacles (Meteors) ---
        meteors_to_remove = []
        for obstacle in list(obstacles):
            if obstacle.move(dt):
                meteors_to_remove.append(obstacle)
                continue

            screen.blit(obstacle.image, (obstacle.rect.x, obstacle.rect.y))

            health_bar_width = obstacle.rect.width
            health_bar_height = 8
            health_percentage = obstacle.hp / obstacle.max_hp
            pygame.draw.rect(screen, (255, 0, 0), (obstacle.rect.x, obstacle.rect.y - health_bar_height - 5, health_bar_width, health_bar_height))
            pygame.draw.rect(screen, (0, 255, 0), (obstacle.rect.x, obstacle.rect.y - health_bar_height - 5, health_bar_width * health_percentage, health_bar_height))
            pygame.draw.rect(screen, (0, 0, 0), (obstacle.rect.x, obstacle.rect.y - health_bar_height - 5, health_bar_width, health_bar_height), 1)

            if check_collision((player_x, player_y), player_radius, obstacle.rect):
                game_over_result(screen, font, (player_x, player_y))
                return

        for meteor in meteors_to_remove:
            if meteor in obstacles:
                obstacles.remove(meteor)


        # --- Update and Draw Enemies ---
        enemies_to_remove = []
        for enemy in list(enemies):
            enemy.update(dt, (player_x, player_y), player_radius)
            enemy.draw(screen)

            if check_collision((player_x, player_y), player_radius, enemy.rect):
                game_over_result(screen, font, (player_x, player_y))
                return

            if enemy.hp <= 0:
                enemies_to_remove.append(enemy)

        for enemy in enemies_to_remove:
            if enemy in enemies:
                enemies.remove(enemy)
                explosion_sound.play()


        # --- Enemy Laser Damage and Removal ---
        for enemy in list(enemies):
            lasers_to_remove_from_enemy = []
            for enemy_laser in list(enemy.lasers):
                # Update enemy laser's position
                enemy_laser.update(dt)
                enemy_laser.draw(screen) # Draw the projectile

                # Check for collision with player
                if enemy_laser.active and check_collision((player_x, player_y), player_radius, enemy_laser.rect):
                    globals.player_hp -= enemy_laser.damage_per_second * dt # Apply damage
                    enemy_laser.active = False # Deactivate laser on hit

                if not enemy_laser.active:
                    lasers_to_remove_from_enemy.append(enemy_laser)

            for laser_to_remove in lasers_to_remove_from_enemy:
                if laser_to_remove in enemy.lasers:
                    enemy.lasers.remove(laser_to_remove)


        # --- Player Movement and Energy ---
        mouse_x, mouse_y = pygame.mouse.get_pos()
        player_x, player_y, rotation_angle = player_move((player_x, player_y), (mouse_x, mouse_y))
        player_pos = (player_x, player_y)
        rotated_player_image = pygame.transform.rotate(original_player_image, current_player_rotation_angle)
        player_rect_for_blit = rotated_player_image.get_rect(center=(player_x, player_y))
        screen.blit(rotated_player_image, player_rect_for_blit)

        globals.player_energy -= globals.energy_depletion_rate * dt * 100
        if globals.player_energy <= 0:
            game_over_result(screen, font, player_pos, no_fuel=True)
            return

        # Check for game over due to HP after all damage calculations
        if globals.player_hp <= 0:
            game_over_result(screen, font, player_pos)
            return


        # --- Player Laser Mechanics (Automatic Continuous Firing) ---
        closest_target = None
        min_dist = float('inf')
        all_targets = obstacles + enemies
        for target in all_targets:
            distance_to_target_from_player = pygame.math.Vector2(player_pos).distance_to(target.rect.center)
            if distance_to_target_from_player <= globals.player_laser_max_range and distance_to_target_from_player < min_dist:
                min_dist = distance_to_target_from_player
                closest_target = target

        if closest_target and globals.player_energy > 0:
            if player_laser is None:
                player_laser = Laser(player_pos, closest_target.rect.center, globals.laser_damage, globals.player_laser_max_range)
            player_laser.active = True
            player_laser.start_pos = pygame.math.Vector2(player_pos)
            player_laser.end_pos = pygame.math.Vector2(closest_target.rect.center)

            if current_time - gameplay_page.last_player_laser_time > 0.1:
                globals.player_energy -= 1
                gameplay_page.last_player_laser_time = current_time

            targets_destroyed_by_laser = player_laser.update(dt, obstacles + enemies)
            player_laser.draw(screen)

            if targets_destroyed_by_laser:
                for target in targets_destroyed_by_laser:
                    if target in obstacles:
                        obstacles.remove(target)
                        explosion_sound.play()
                    elif target in enemies:
                        enemies.remove(target)
                        explosion_sound.play()
        else:
            if player_laser is not None:
                player_laser.active = False


        # --- UI Elements ---
        energy_bar_x, energy_bar_y = 20, 20
        energy_bar_width, energy_bar_height = 200, 25
        pygame.draw.rect(screen, (100, 100, 100), (energy_bar_x, energy_bar_y, energy_bar_width, energy_bar_height))
        energy_width = int((globals.player_energy / globals.player_max_energy) * energy_bar_width)
        pygame.draw.rect(screen, (0, 255, 0), (energy_bar_x, energy_bar_y, energy_width, energy_bar_height))
        pygame.draw.rect(screen, (0, 0, 0), (energy_bar_x, energy_bar_y, energy_bar_width, energy_bar_height), 2)
        energy_text = energy_font.render("Energy", True, (0, 0, 0))
        screen.blit(energy_text, (energy_bar_x + 6, energy_bar_y + 6))

        hp_bar_x, hp_bar_y = 20, 60
        hp_bar_width, hp_bar_height = 200, 25
        pygame.draw.rect(screen, (100, 100, 100), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height))
        hp_width = int((globals.player_hp / globals.player_max_hp) * hp_bar_width)
        pygame.draw.rect(screen, (255, 0, 0), (hp_bar_x, hp_bar_y, hp_width, hp_bar_height))
        pygame.draw.rect(screen, (0, 0, 0), (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height), 2)
        hp_text = hp_font.render("HP", True, (0, 0, 0))
        screen.blit(hp_text, (hp_bar_x + 6, hp_bar_y + 6))

        money_text = font.render(f"Money: {round(globals.money, 2)}", True, (0, 0, 0))
        screen.blit(money_text, (10, 100))

        fps = int(clock.get_fps())
        fps_text = font.render(f"FPS: {fps}", True, (0, 0, 0))
        screen.blit(fps_text, (screen.get_width() - fps_text.get_width() - 10, 10))

        enemies_count_text = font.render(f"Enemies: {len(enemies)}", True, (0, 0, 0))
        screen.blit(enemies_count_text, (screen.get_width() - enemies_count_text.get_width() - 10, 50))

        game_level_text = font.render(f"Level: {game_level}", True, (0, 0, 0))
        screen.blit(game_level_text, (screen.get_width() - game_level_text.get_width() - 10, 90))


        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_screen_result(screen, font, "Paused")
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()
        clock.tick(60)
