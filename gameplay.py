import pygame
import time
import random
import globals
import sys

from enemy import Enemy
from laser import Laser
from game_object import GameObject, get_offscreen_spawn_and_direction
from player import player_move
import assets
from ui import draw_ui_bar
from menus import *

# Assuming these exist in your buttons/menus module based on your snippet
# from buttons import button_draw, create_vertical_color_gradient, text_styling

obstacles = []
enemies = []

def generate_obstacles(count):
    """Generate a list of meteors (obstacles) with random positions and stats."""
    generated = []
    for _ in range(count):
        img = random.choice(list(assets.meteorite_images.values()))
        width, height = img.get_size()
        x, y, x_speed, y_speed = get_offscreen_spawn_and_direction(width, height)
        hp = random.randint(1, 3)
        generated.append(GameObject(x, y, width, height, hp, x_speed, y_speed, image=img))
    return generated

def spawn_enemies(level, count):
    """Spawn a batch of enemies for the given level."""
    return [Enemy(level) for _ in range(count)]

def check_collision(circle_pos, circle_radius, rect):
    """Circle-rectangle collision detection."""
    cx, cy = circle_pos
    closest_x = max(rect.left, min(cx, rect.right))
    closest_y = max(rect.top, min(cy, rect.bottom))
    dx = cx - closest_x
    dy = cy - closest_y
    return dx*dx + dy*dy <= circle_radius * circle_radius

# --- NEW MENU & RESULT FUNCTIONS ---

def choice_menu(button_list, screen):
    menu_clock = pygame.time.Clock() 
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for button in button_list:
                    if button[0].collidepoint(mouse_x, mouse_y):
                        pygame.mixer.music.set_volume(0.3)
                        return button[1]

        mouse_x, mouse_y = pygame.mouse.get_pos()
        for button in button_list:
            hover = button[0].collidepoint(mouse_x, mouse_y)
            button_draw(button, screen, hover=hover)

        pygame.display.update()
        menu_clock.tick(60)

def game_over_screen(screen, font, player_pos, no_fuel=False):
    pygame.mouse.set_visible(True)
    fuel_empty_rect = pygame.Rect(globals.SCREEN_WIDTH / 2 - 145, 360, 300, 75)
    game_over_rect = pygame.Rect(globals.SCREEN_WIDTH / 2 - 145, 300, 300, 75)

    if not no_fuel:
        pygame.draw.circle(screen, (255, 120, 51), player_pos, 30)
        assets.explosion_sound.play()
        explosion_delay = 100
        last_explosion_time = pygame.time.get_ticks()
        
        # Iterate through explosion frames
        for i in range(1, len(assets.explosion_images) + 1):
            explosion_image = assets.explosion_images[i]
            x, y = player_pos
            screen.blit(explosion_image, (x - 30, y - 30))
            pygame.display.update(x - 30, y - 30, 60, 60)
            pygame.time.delay(explosion_delay)

    top = (100, 180, 220, 55)
    bottom = (30, 60, 90, 55)
    rect_gradient = create_vertical_color_gradient((400, 1080), top, bottom)
    screen.blit(rect_gradient, (globals.SCREEN_WIDTH / 2 - 200, 0))

    text_styling((game_over_rect, "Game Over"), screen)
    if no_fuel:
        text_styling((fuel_empty_rect, "Ran Out Of Fuel"), screen)

    return choice_menu(game_over_buttons, screen)

def game_over_result(screen, font, player_pos, no_fuel=False):
    result = game_over_screen(screen, font, player_pos, no_fuel)
    obstacles.clear()
    enemies.clear()

    if result == "Skill Tree":
        skill_tree_page(screen, (255, 255, 255), font, gameplay_page)
    elif result == "Restart":
        globals.player_hp = globals.player_max_hp
        globals.player_energy = globals.player_max_energy
        globals.money = 0
        gameplay_page(screen, (255, 255, 255), font, assets.background_image)
    elif result == "Quit":
        pygame.quit()
        sys.exit()

def pause_screen(screen, font):
    pygame.mixer.music.set_volume(0.1)
    pygame.mouse.set_visible(True)
    # Re-init font for specific style if needed
    p_font = pygame.font.SysFont("8-Bit-Madness", 46)
    p_font.set_bold(True)
    
    pause_text_rect = pygame.Rect(globals.SCREEN_WIDTH / 2 - 145, 300, 300, 75)
    top = (100, 180, 220, 55)
    bottom = (30, 60, 90, 55)
    rect_gradient = create_vertical_color_gradient((400, 1080), top, bottom)
    screen.blit(rect_gradient, (globals.SCREEN_WIDTH / 2 - 200, 0))

    text_styling((pause_text_rect, "Paused"), screen)
    return choice_menu(pause_menu_buttons, screen)

def pause_screen_result(screen, font):
    pause_start = time.time()  # Record when we paused
    result = pause_screen(screen, font)
    pause_end = time.time()    # Record when we unpaused
    
    pause_duration = pause_end - pause_start # Calculate total time spent paused

    if result == "Continue":
        pygame.mouse.set_visible(False)
        return pause_duration 
    if result == "Skill Tree":
        skill_tree_page(screen, (255, 255, 255), font, gameplay_page)
        return
    elif result == "Restart":
        globals.player_hp = globals.player_max_hp
        globals.player_energy = globals.player_max_energy
        globals.money = 0
        gameplay_page(screen, (255, 255, 255), font, assets.background_image)
    elif result == "Quit":
        pygame.quit()
        sys.exit()

# --- MAIN GAMEPLAY LOOP ---

def gameplay_page(screen, white, font, background_image = assets.background_image):
    global obstacles, enemies
    obstacles.clear()
    enemies.clear()
    globals.player_hp = globals.player_max_hp
    globals.player_energy = globals.player_max_energy
    game_level = 1

    clock = pygame.time.Clock()
    player_x, player_y = globals.SCREEN_WIDTH / 2, globals.SCREEN_HEIGHT / 2
    player_radius = 30

    last_obstacle_time = time.time()
    obstacle_generation_interval = random.uniform(0, 1)
    last_enemy_spawn_time = time.time()
    enemy_spawn_interval = 5.0

    player_laser = None
    gameplay_page.last_player_laser_time = 0

    while True:
        dt = clock.tick(60) / 1000.0
        screen.blit(background_image, (0, 0))
        pygame.mouse.set_visible(False)
        current_time = time.time()

        # Spawning Logic
        if current_time - last_obstacle_time >= obstacle_generation_interval:
            obstacles.extend(generate_obstacles(3))
            last_obstacle_time = current_time
            obstacle_generation_interval = random.uniform(2, 5)

        if current_time - last_enemy_spawn_time >= enemy_spawn_interval:
            enemies.extend(spawn_enemies(game_level, 1))
            last_enemy_spawn_time = current_time
            enemy_spawn_interval = random.uniform(5, 10)
            game_level += 1

        obstacles = [obs for obs in obstacles if obs.hp > 0 and not obs.move(dt)]
        
        for obstacle in obstacles:
            # Draw the obstacle
            screen.blit(obstacle.image, (obstacle.rect.x, obstacle.rect.y))
            
            # Draw Health Bar
            fixed_bar_width = 50 
            health_percentage = max(0, obstacle.hp / obstacle.max_hp)
            bar_x = obstacle.rect.centerx - (fixed_bar_width // 2)
            bar_y = obstacle.rect.y - 13
            pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, fixed_bar_width, 8))
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, fixed_bar_width * health_percentage, 8))

            # Collision with Player
            if check_collision((player_x, player_y), player_radius, obstacle.rect):
                assets.explosion_sound.play()
                temp_hp = obstacle.hp
                obstacle.hp -= globals.player_hp
                globals.player_hp -= temp_hp
                # Obstacle is marked for removal automatically next frame because hp <= 0

        # --- 2. UPDATE & FILTER ENEMIES ---
        enemies = [en for en in enemies if en.hp > 0]
        
        for enemy in enemies:
            enemy.update(dt, (player_x, player_y), player_radius)
            enemy.draw(screen)
            
            if check_collision((player_x, player_y), player_radius, enemy.rect):
                assets.explosion_sound.play()
                if enemy.hp > globals.player_hp:
                    game_over_result(screen, font, (player_x, player_y))
                    return
                globals.player_hp -= enemy.hp
                enemy.hp = 0 # Mark for removal

        # Update Enemies
        enemies_to_remove = []
        for enemy in list(enemies):
            enemy.update(dt, (player_x, player_y), player_radius)
            enemy.draw(screen)
            if check_collision((player_x, player_y), player_radius, enemy.rect):
                if enemy.hp > globals.player_hp:
                    game_over_result(screen, font, (player_x, player_y))
                    return
                globals.player_hp -= enemy.hp
            if enemy.hp <= 0:
                enemies_to_remove.append(enemy)

        for enemy in enemies_to_remove:
            if enemy in enemies:
                enemies.remove(enemy)
                assets.explosion_sound.play()

        # Player Movement
        mouse_x, mouse_y = pygame.mouse.get_pos()
        player_x, player_y, rotation_angle = player_move((player_x, player_y), (mouse_x, mouse_y))
        rotated_player_image = pygame.transform.rotate(assets.player_image, rotation_angle)
        screen.blit(rotated_player_image, rotated_player_image.get_rect(center=(player_x, player_y)))

        # Fuel / Energy
        globals.player_energy -= globals.energy_depletion_rate * dt * 100
        if globals.player_energy <= 0:
            game_over_result(screen, font, (player_x, player_y), no_fuel=True)
            return
        if globals.player_hp <= 0:
            game_over_result(screen, font, (player_x, player_y))
            return

        # Laser Logic
        all_targets = obstacles + enemies
        closest_target = None
        min_dist = float('inf')
        for target in all_targets:
            dist = pygame.math.Vector2(player_x, player_y).distance_to(target.rect.center)
            if dist <= globals.player_laser_max_range and dist < min_dist:
                min_dist, closest_target = dist, target

        if closest_target and globals.player_energy > 0:
            if player_laser is None:
                player_laser = Laser((player_x, player_y), closest_target.rect.center, globals.laser_damage, globals.player_laser_max_range)
            player_laser.active = True
            player_laser.start_pos = pygame.math.Vector2(player_x, player_y)
            player_laser.end_pos = pygame.math.Vector2(closest_target.rect.center)
            
            if current_time - gameplay_page.last_player_laser_time > 0.1:
                globals.player_energy -= 1
                gameplay_page.last_player_laser_time = current_time
            
            player_laser.update(dt, all_targets)
            player_laser.draw(screen)
        elif player_laser:
            player_laser.active = False

        # UI
        draw_ui_bar(screen, 20, 10, globals.player_energy, globals.player_max_energy, assets.energy_bar_img)
        draw_ui_bar(screen, 20, 80, globals.player_hp, globals.player_max_hp, assets.hp_bar_img)
        
        # Stats
        money_txt = font.render(f"Money: {round(globals.money, 2)}", True, (255, 255, 255))
        screen.blit(money_txt, (25, 80 + assets.hp_bar_img.get_height() + 5))

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # 1. Run the pause menu and get the time spent inside it
                p_offset = pause_screen_result(screen, font)
                
                # 2. If the user chose "Continue" (which returns the float duration)
                if isinstance(p_offset, (int, float)):
                    # Shift the timestamps forward so the "wait" time remains the same
                    last_obstacle_time += p_offset
                    last_enemy_spawn_time += p_offset
                    gameplay_page.last_player_laser_time += p_offset
                    
                    # 3. CRITICAL: Reset the pygame clock so 'dt' isn't huge on the next frame
                    clock.tick() 
                
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()