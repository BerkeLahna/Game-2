import pygame
import numpy as np
 
 
# Colors
WHITE = (255, 255, 255)
BUTTON_COLOR = (0, 255, 0)  # Green buttons
BUTTON_HOVER_COLOR = (0, 200, 0)  # Darker green when hovered
BUTTON_TEXT_COLOR = (90, 115, 255, 0.62*255) # Black text for buttons

main_menu_font = pygame.font.SysFont("8-Bit-Madness", 46)
main_menu_font.set_bold(True)

button_image = pygame.image.load('Images/button.png')  
button_image = pygame.transform.scale(button_image, (300, 75))  # Scale it to fit the screen
not_button_image = pygame.image.load('Images/wp10105509.jpg')  


button_hover_image = pygame.image.load('Images/button-hover.png')  
button_hover_image = pygame.transform.scale(button_hover_image, (300, 75))  # Scale it to fit the screen


def create_rect_with_vertical_alpha_gradient(size, color_rgb, start_alpha=255, end_alpha=0):
    width, height = size
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    for y in range(height):
        alpha = int(start_alpha + (end_alpha - start_alpha) * (y / height))
        pygame.draw.line(surface, (*color_rgb, alpha), (0, y), (width, y))
    
    return surface

def create_vertical_color_gradient(size, top_color, bottom_color):
    width, height = size
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    for y in range(height):
        t = y / height
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        a = int(top_color[3] + (bottom_color[3] - top_color[3]) * t) if len(top_color) == 4 else 255
        pygame.draw.line(surface, (r, g, b, a), (0, y), (width, y))
    
    return surface


# Function to create a button
def create_button(text, x, y, width, height):
    button_rect = pygame.Rect(x, y, width, height)


    return (button_rect, text)



def button_draw(button, screen,hover=False):
    rect, label = button
    
    # Draw button background
    
    if not hover:
        # screen.blit(button_image, (rect.x, rect.y))
        screen.blit(button_image, (rect.x, rect.y))

    else:
        screen.blit(button_hover_image, (rect.x, rect.y))

    
    text_styling(button, screen)

def text_styling(button, screen):
    rect, label = button

    # Shadow surface same as before
    shadow_surface = main_menu_font.render(label, True, (0, 0, 0))
    shadow_surface = shadow_surface.convert_alpha()
    shadow_surface.set_alpha(100)
    
    # Calculate centered positions
    text_surface = render_text_with_vertical_gradient(main_menu_font, label, BUTTON_TEXT_COLOR, 200, 100)
    # text_surface = render_text_with_vertical_color_gradient(main_menu_font, label, (232, 214, 53, 255) ,(247, 222, 0, 100))
    text_x = rect.centerx - text_surface.get_width() // 2
    text_y = rect.centery - text_surface.get_height() // 2
    
    # Draw shadow offset
    screen.blit(shadow_surface, (text_x + 4, text_y + 4))

    border_color = (0, 0, 0)
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx != 0 or dy != 0:
                border_text = main_menu_font.render(label, True, border_color)
                border_text = border_text.convert_alpha()
                screen.blit(border_text, (text_x + dx, text_y + dy))
    
    # Finally blit the gradient text (main text)
    screen.blit(text_surface, (text_x, text_y))

    



def render_text_with_vertical_gradient(font, text, color_rgb = BUTTON_TEXT_COLOR, start_alpha=255, end_alpha=100):
    # Render text surface (no alpha in color tuple, just RGB)
    text_surface = main_menu_font.render(text, True, color_rgb).convert_alpha()
    width, height = text_surface.get_size()

    # Create a gradient alpha mask once (no fill in loop!)
    gradient = pygame.Surface((width, height), pygame.SRCALPHA)
    
    for y in range(height):
        alpha = int(start_alpha + (end_alpha - start_alpha) * (y / height))
        alpha = max(0, min(255, alpha))
        # Draw horizontal line with white and alpha = alpha value
        pygame.draw.line(gradient, (255, 255, 255, alpha), (0, y), (width, y))
    
    # Multiply text alpha by gradient alpha mask
    text_alpha = pygame.surfarray.pixels_alpha(text_surface)
    grad_alpha = pygame.surfarray.pixels_alpha(gradient)
    
    # Multiply pixel alphas, scaling down from 0-255
    new_alpha = (text_alpha.astype(np.uint16) * grad_alpha.astype(np.uint16) // 255).astype(np.uint8)
    text_alpha[:] = new_alpha
    
    del text_alpha
    del grad_alpha
    
    return text_surface

import numpy as np




## PAIN

# def render_text_with_vertical_color_gradient(font, text, top_color, bottom_color):

#     text_surface = font.render(text, True, (255, 255, 255)).convert_alpha()

#     if text_surface.get_size() == (0, 0):
#         print(f"Error: Failed to render text '{text}'. Returning empty surface.")
#         return pygame.Surface((1, 1), pygame.SRCALPHA)

#     width, height = text_surface.get_size()
#     # print(f"DEBUG: Text surface '{text}' initial size: {width}x{height}") # Re-enable for debugging

#     gradient_surface = pygame.Surface((width, height), pygame.SRCALPHA)
#     for y in range(height):
#         t = y / (height - 1)
#         r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
#         g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
#         b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
#         a = int(top_color[3] + (bottom_color[3] - top_color[3]) * t) if len(top_color) == 4 else 255
#         pygame.draw.line(gradient_surface, (r, g, b, a), (0, y), (width, y))

#     text_pixels_rgb = pygame.surfarray.pixels3d(text_surface)
#     text_pixels_alpha = pygame.surfarray.pixels_alpha(text_surface)
#     gradient_pixels_rgb = pygame.surfarray.pixels3d(gradient_surface)
#     gradient_pixels_alpha = pygame.surfarray.pixels_alpha(gradient_surface)

#     # This RGB blending worked for your setup
#     text_pixels_rgb[:] = text_pixels_rgb * gradient_pixels_rgb

#     # This alpha forcing worked for your setup
#     text_pixels_alpha[text_pixels_alpha > 0] = 255 # Force full alpha where text pixels exist


#     del text_pixels_rgb
#     del text_pixels_alpha
#     del gradient_pixels_rgb
#     del gradient_pixels_alpha

#     return text_surface

