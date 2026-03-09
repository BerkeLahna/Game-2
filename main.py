import pygame
import sys
from gameplay import gameplay_page
import buttons
import assets
from menus import *

# --- INIT PYGAME ---
pygame.init()
pygame.mixer.init()

# --- SCREEN ---
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Miner")

# --- INITIALIZE BUTTONS & ASSETS ---
buttons.init_buttons()  # sets main_menu_font
assets.load_assets()   # your asset loading function

WHITE = (255, 255, 255)




# --- MAIN MENU FUNCTION ---
def main_menu():
    clock = pygame.time.Clock()

    # Create buttons
    start_button = buttons.create_button("Start", WIDTH // 2 - 150, HEIGHT // 2 - 40, 300, 75)
    options_button = buttons.create_button("Options", WIDTH // 2 - 150, HEIGHT // 2 + 40, 300, 75)
    quit_button = buttons.create_button("Quit", WIDTH // 2 - 150, HEIGHT // 2 + 120, 300, 75)
    buttons_list = [start_button, options_button, quit_button]

    # Scrolling background
    bg_x1, bg_x2 = 0, WIDTH
    scroll_speed = 0.5

    while True:
        # Move background
        bg_x1 -= scroll_speed
        bg_x2 -= scroll_speed
        if bg_x1 <= -WIDTH: bg_x1 = WIDTH
        if bg_x2 <= -WIDTH: bg_x2 = WIDTH

        # Draw backgrounds
        screen.blit(assets.logo_background, (bg_x1, 0))
        screen.blit(assets.logo_background, (bg_x2, 0))
        screen.blit(assets.background_image, (0, 0))
        screen.blit(assets.menu_logo, (WIDTH // 2 - assets.menu_logo.get_width() // 2 - 20, 80))

        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Draw buttons with hover
        for button in buttons_list:
            hover = button[0].collidepoint(mouse_x, mouse_y)
            buttons.button_draw(button, screen, hover)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button[0].collidepoint(mouse_x, mouse_y):
                    gameplay_page(screen, WHITE, buttons.main_menu_font, assets.background_image)
                elif quit_button[0].collidepoint(mouse_x, mouse_y):
                    pygame.quit()
                    sys.exit()
                elif options_button[0].collidepoint(mouse_x, mouse_y):
                    menus.options_menu(screen)

        pygame.display.update()
        clock.tick(60)

# --- RUN ---
if __name__ == "__main__":
    main_menu()