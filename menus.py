import pygame
import sys
import globals
from buttons import *
from skilltree import skill_tree_page

# --- BUTTON LIST DEFINITIONS ---
# These must be defined for choice_menu to iterate over them
pause_menu_buttons = [
    [pygame.Rect(globals.SCREEN_WIDTH // 2 - 150, 400, 300, 75), "Continue"],
    [pygame.Rect(globals.SCREEN_WIDTH // 2 - 150, 480, 300, 75), "Restart"],
    [pygame.Rect(globals.SCREEN_WIDTH // 2 - 150, 560, 300, 75), "Skill Tree"],
    [pygame.Rect(globals.SCREEN_WIDTH // 2 - 150, 640, 300, 75), "Quit"]
]

game_over_buttons = [
    [pygame.Rect(globals.SCREEN_WIDTH // 2 - 150, 450, 300, 75), "Restart"],
    [pygame.Rect(globals.SCREEN_WIDTH // 2 - 150, 530, 300, 75), "Skill Tree"],
    [pygame.Rect(globals.SCREEN_WIDTH // 2 - 150, 610, 300, 75), "Quit"]
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
                        # Reset volume when leaving the menu
                        pygame.mixer.music.set_volume(0.3)
                        return button[1]

        mx, my = pygame.mouse.get_pos()

        for button in button_list:
            # Pass hover state to button_draw
            button_draw(button, screen, button[0].collidepoint(mx, my))

        pygame.display.update()
        clock.tick(60)