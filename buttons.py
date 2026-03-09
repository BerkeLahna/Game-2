import pygame
import numpy as np
import assets

# ------------------------- COLORS -------------------------
WHITE = (255, 255, 255)
BUTTON_COLOR = (0, 255, 0)
BUTTON_HOVER_COLOR = (0, 200, 0)
BUTTON_TEXT_COLOR = (90, 115, 255)

# ------------------------- FONT -------------------------
main_menu_font = None

def init_buttons():
    global main_menu_font
    main_menu_font = pygame.font.SysFont("8-Bit-Madness", 46)
    main_menu_font.set_bold(True)

# ------------------------- IMAGES -------------------------
button_image = pygame.transform.scale(pygame.image.load(assets.resource_path("Images/button.png")), (300, 75))
button_hover_image = pygame.transform.scale(pygame.image.load(assets.resource_path("Images/button-hover.png")), (300, 75))
not_button_image = pygame.image.load(assets.resource_path("Images/wp10105509.jpg"))

# ------------------------- BUTTONS -------------------------
def create_button(text, x, y, width, height):
    return pygame.Rect(x, y, width, height), text

def button_draw(button, screen, hover=False):
    rect, label = button
    image = button_hover_image if hover else button_image
    screen.blit(image, rect.topleft)
    draw_button_text(label, rect, screen)

# ------------------------- TEXT -------------------------
def draw_button_text(label, rect, screen):
    text_surface = render_text_with_vertical_gradient(main_menu_font, label, BUTTON_TEXT_COLOR, 200, 100)
    text_x = rect.centerx - text_surface.get_width() // 2
    text_y = rect.centery - text_surface.get_height() // 2

    # Shadow
    shadow = main_menu_font.render(label, True, (0, 0, 0))
    shadow.set_alpha(100)
    screen.blit(shadow, (text_x + 4, text_y + 4))

    # Border
    border = main_menu_font.render(label, True, (0, 0, 0))
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                screen.blit(border, (text_x + dx, text_y + dy))

    # Main text
    screen.blit(text_surface, (text_x, text_y))

# ------------------------- GRADIENT TEXT -------------------------
def render_text_with_vertical_gradient(font, text, color, start_alpha=255, end_alpha=100):
    text_surface = font.render(text, True, color).convert_alpha()
    width, height = text_surface.get_size()

    gradient = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(height):
        alpha = int(start_alpha + (end_alpha - start_alpha) * (y / height))
        alpha = max(0, min(255, alpha))
        pygame.draw.line(gradient, (255, 255, 255, alpha), (0, y), (width, y))

    text_alpha = pygame.surfarray.pixels_alpha(text_surface)
    grad_alpha = pygame.surfarray.pixels_alpha(gradient)
    text_alpha[:] = (text_alpha.astype(np.uint16) * grad_alpha.astype(np.uint16) // 255).astype(np.uint8)
    del text_alpha, grad_alpha

    return text_surface

