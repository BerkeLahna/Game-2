import pygame
import sys
import globals
import buttons
from buttons import *
from skilltree import skill_tree_page
import options 
import assets
import time

# --- BUTTON LIST DEFINITIONS ---
# These must be defined for choice_menu to iterate over them
pause_menu_buttons = [
    [pygame.Rect(globals.SCREEN_WIDTH // 2 - 150, 400, 300, 75), "Continue"],
    [pygame.Rect(globals.SCREEN_WIDTH // 2 - 150, 480, 300, 75), "Settings"],
    [pygame.Rect(globals.SCREEN_WIDTH // 2 - 150, 560, 300, 75), "Restart"],
    [pygame.Rect(globals.SCREEN_WIDTH // 2 - 150, 640, 300, 75), "Skill Tree"],
    [pygame.Rect(globals.SCREEN_WIDTH // 2 - 150, 720, 300, 75), "Quit"]
]

game_over_buttons = [
    [pygame.Rect(globals.SCREEN_WIDTH // 2 - 150, 450, 300, 75), "Restart"],
    [pygame.Rect(globals.SCREEN_WIDTH // 2 - 150, 530, 300, 75), "Settings"],
    [pygame.Rect(globals.SCREEN_WIDTH // 2 - 150, 610, 300, 75), "Skill Tree"],
    [pygame.Rect(globals.SCREEN_WIDTH // 2 - 150, 690, 300, 75), "Quit"]
]

def create_vertical_color_gradient(size, top_color, bottom_color):
    """Creates a vertical linear gradient surface."""
    width, height = size
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    for y in range(height):
        t = y / height
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        # Handle alpha if provided in the color tuple
        a = int(top_color[3] + (bottom_color[3] - top_color[3]) * t) if len(top_color) == 4 else 255
        pygame.draw.line(surface, (r, g, b, a), (0, y), (width, y))
    
    return surface

def text_styling(data, screen):
    """Renders centered text based on a tuple of (rect, text_string)."""
    rect, text_str = data
    
    # Use the specific font from the buttons module
    # We use a try/except or direct reference to buttons.main_menu_font
    try:
        import buttons
        font = buttons.main_menu_font
    except AttributeError:
        # Fallback if the font isn't initialized yet
        font = pygame.font.SysFont("Arial", 40)
        
    text_surf = font.render(text_str, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)
    
def choice_menu(button_list, screen):
    """Handles the interactive loop for menu selection."""
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                for button in button_list:
                    if button[0].collidepoint(mx, my):
                       
                        return button[1]

        mx, my = pygame.mouse.get_pos()

        for button in button_list:
            # Pass hover state to button_draw
            button_draw(button, screen, button[0].collidepoint(mx, my))

        pygame.display.update()
        clock.tick(60)
        
        
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
    # Local import at the very start
    from gameplay import gameplay_page 
    
    result = game_over_screen(screen, font, player_pos, no_fuel)
    
    # These lists are globals in gameplay.py; 
    # make sure they are accessible or move clearing logic to gameplay.py
    import gameplay
    gameplay.obstacles.clear()
    gameplay.enemies.clear()

    if result == "Skill Tree":
        skill_tree_page(screen, (255, 255, 255), font, gameplay_page)
    elif result == "Settings":
        options_menu(screen)
    elif result == "Restart":
        globals.player_hp = globals.player_max_hp
        globals.player_energy = globals.player_max_energy
        gameplay_page(screen, (255, 255, 255), font, assets.background_image)
    elif result == "Quit":
        pygame.quit()
        sys.exit()

# menus.py

def pause_screen(screen, font):
    pygame.mouse.set_visible(True)
    
    # 1. Capture the game state (meteors, ship, etc.) BEFORE drawing any UI
    # This acts as our "clean" background for all sub-menus
    game_snapshot = screen.copy() 
    
    pause_text_rect = pygame.Rect(globals.SCREEN_WIDTH / 2 - 145, 300, 300, 75)
    
    # --- Internal loop for the Pause Menu ---
    while True:
        # 2. Always draw the clean game snapshot first
        screen.blit(game_snapshot, (0, 0))
        
        # 3. Draw the Pause UI
        top = (100, 180, 220, 55)
        bottom = (30, 60, 90, 55)
        rect_gradient = create_vertical_color_gradient((400, 1080), top, bottom)
        screen.blit(rect_gradient, (globals.SCREEN_WIDTH / 2 - 200, 0))
        text_styling((pause_text_rect, "Paused"), screen)

        # 4. Handle Button Interactions
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in pause_menu_buttons:
                    if button[0].collidepoint(mx, my):
                        # If Settings is clicked, we pass the CLEAN snapshot to it
                        if button[1] == "Settings":
                            options_menu(screen, game_snapshot)
                            # After options closes, the loop continues and 
                            # re-draws the pause menu over the snapshot
                            continue 
                        return button[1]

        for button in pause_menu_buttons:
            button_draw(button, screen, button[0].collidepoint(mx, my))

        pygame.display.update()
# menus.py

# menus.py

def pause_screen_result(screen, font):
    from gameplay import gameplay_page
    
    game_snapshot = screen.copy()
    pause_start = time.time()
    result = pause_screen(screen, font)
    
    if result == "Settings":
        settings_time = options_menu(screen, game_snapshot) 
        return (time.time() - pause_start) + pause_screen_result(screen, font)
        
    if result == "Continue":
        return (time.time() - pause_start)
    
    # CHANGE THIS LINE: Capitalize the 'T' to match pause_menu_buttons
    if result == "Skill Tree": 
        skill_tree_page(screen, (255, 255, 255), font, gameplay_page)
    
    if result == "Restart":
        globals.player_hp = globals.player_max_hp
        globals.player_energy = globals.player_max_energy
        gameplay_page(screen, (255, 255, 255), font, assets.background_image)
        return 0
        
    elif result == "Quit":
        pygame.quit()
        sys.exit()
# menus.py

def options_menu(screen, game_snapshot):
    running = True
    clock = pygame.time.Clock()
    start_time = time.time()
    
    # 1. Prepare Vertical Handle (Rotate 90 then Scale)
    from buttons import button_image, button_hover_image, render_text_with_vertical_gradient, main_menu_font, BUTTON_TEXT_COLOR
    rotated_base = pygame.transform.rotate(button_image, 90)
    rotated_hover_base = pygame.transform.rotate(button_hover_image, 90)
    handle_img = pygame.transform.scale(rotated_base, (30, 60))
    handle_hover_img = pygame.transform.scale(rotated_hover_base, (30, 60))
    
    original_volume = options.settings.music_volume
    temp_volume = original_volume
    pre_mute_volume = original_volume if original_volume > 0 else 0.3 
    is_dragging = False
    
    panel_width = 400
    panel_rect = pygame.Rect(globals.SCREEN_WIDTH // 2 - (panel_width // 2), 0, panel_width, 1080)
    
    # UI Rects
    slider_track = pygame.Rect(panel_rect.x + 50, 350, 300, 20)
    mute_rect = pygame.Rect(panel_rect.x + 50, 450, 300, 75)
    confirm_rect = pygame.Rect(panel_rect.x + 50, 550, 300, 75)
    cancel_rect = pygame.Rect(panel_rect.x + 50, 700, 300, 75)

    while running:
        screen.blit(game_snapshot, (0, 0))
        
        gradient_surf = create_vertical_color_gradient((panel_width, 1080), (100, 180, 220, 55), (30, 60, 90, 55))
        screen.blit(gradient_surf, (panel_rect.x, 0))

        mx, my = pygame.mouse.get_pos()

        # Handle Positioning
        h_w, h_h = 30, 60
        h_x = slider_track.x + (temp_volume * slider_track.width) - (h_w // 2)
        h_y = slider_track.centery - (h_h // 2)
        handle_rect = pygame.Rect(h_x, h_y, h_w, h_h)

        # Draw Slider Track
        pygame.draw.rect(screen, (60, 60, 60), slider_track, border_radius=5)
        
        # Draw Handle
        if handle_rect.collidepoint(mx, my) or is_dragging:
            screen.blit(handle_hover_img, (h_x, h_y))
        else:
            screen.blit(handle_img, (h_x, h_y))

        # --- NEW: STYLIZED VOLUME PERCENTAGE ---
        vol_percentage = int(temp_volume * 100)
        percentage_str = f"{vol_percentage}%"
        # Use your custom gradient text renderer from buttons.py
        vol_text_surf = render_text_with_vertical_gradient(main_menu_font, percentage_str, BUTTON_TEXT_COLOR)
        
        # Position text centered above the handle
        text_x = handle_rect.centerx - vol_text_surf.get_width() // 2
        text_y = handle_rect.top - vol_text_surf.get_height() - 10
        
        # Draw Shadow (matches your button text style)
        shadow = main_menu_font.render(percentage_str, True, (0, 0, 0))
        shadow.set_alpha(100)
        screen.blit(shadow, (text_x + 3, text_y + 3))
        screen.blit(vol_text_surf, (text_x, text_y))

        # Draw Buttons
        mute_text = "MUTE" if temp_volume > 0 else "UNMUTE"
        button_draw([mute_rect, mute_text], screen, mute_rect.collidepoint(mx, my))
        button_draw([confirm_rect, "Confirm"], screen, confirm_rect.collidepoint(mx, my))
        button_draw([cancel_rect, "Cancel"], screen, cancel_rect.collidepoint(mx, my))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if handle_rect.collidepoint(mx, my) or slider_track.collidepoint(mx, my):
                    is_dragging = True
                
                if mute_rect.collidepoint(mx, my):
                    if temp_volume > 0:
                        pre_mute_volume = temp_volume 
                        temp_volume = 0
                    else:
                        temp_volume = pre_mute_volume 
                    pygame.mixer.music.set_volume(temp_volume)
                
                if confirm_rect.collidepoint(mx, my):
                    options.settings.music_volume = temp_volume
                    assets.sync_volume()
                    running = False
                
                if cancel_rect.collidepoint(mx, my):
                    pygame.mixer.music.set_volume(original_volume)
                    running = False

            if event.type == pygame.MOUSEBUTTONUP:
                is_dragging = False

        if is_dragging:
            rel_x = mx - slider_track.x
            temp_volume = max(0.0, min(1.0, rel_x / slider_track.width))
            if temp_volume > 0:
                pre_mute_volume = temp_volume
            pygame.mixer.music.set_volume(temp_volume)

        pygame.display.update()
        clock.tick(60)

    return time.time() - start_time