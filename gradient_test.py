import pygame
import sys
import numpy as np

# --- Pygame Initialization ---
pygame.init()

# Define screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Gradient Text Example")

# --- Font Loading (CRITICAL CHANGE HERE) ---
FONT_FILENAME = "my_font.ttf" # <<< RENAME THIS TO YOUR FONT FILE (e.g., "Roboto-Regular.ttf")
FONT_SIZE = 150 # Keep it large for debugging

try:
    # Attempt to load the specified .ttf font file
    font = pygame.font.Font(FONT_FILENAME, FONT_SIZE)
    print(f"Successfully loaded font: {FONT_FILENAME}")
except FileNotFoundError:
    print(f"ERROR: Font file '{FONT_FILENAME}' not found.")
    print("Please place a .ttf font file (e.g., 'Roboto-Regular.ttf' from Google Fonts)")
    print("in the same directory as this script, or specify its full path.")
    print("Falling back to default Pygame font (may have rendering issues).")
    font = pygame.font.Font(None, FONT_SIZE) # Fallback to default font
except Exception as e:
    print(f"ERROR: Could not load font '{FONT_FILENAME}': {e}")
    print("Falling back to default Pygame font (may have rendering issues).")
    font = pygame.font.Font(None, FONT_SIZE)

# --- Helper Functions (Keep as they were) ---
def create_button(text, x, y, width, height):
    rect = pygame.Rect(x, y, width, height)
    return (rect, text)

def button_draw(button_data, surface):
    rect, text = button_data
    pygame.draw.rect(surface, (100, 100, 100), rect, border_radius=10)
    pygame.draw.rect(surface, (150, 150, 150), rect, 2, border_radius=10)
    button_font = pygame.font.Font(None, 36)
    text_surf = button_font.render(text, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)

def create_vertical_color_gradient(size, top_color, bottom_color):
    width, height = size
    gradient_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(height):
        t = y / (height - 1)
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        a = int(top_color[3] + (bottom_color[3] - top_color[3]) * t) if len(top_color) == 4 else 255
        pygame.draw.line(gradient_surf, (r, g, b, a), (0, y), (width, y))
    return gradient_surf

# --- MODIFIED render_text_with_vertical_color_gradient function ---

def render_text_with_vertical_color_gradient(font, text, top_color, bottom_color):
    """
    Renders text with a vertical color gradient applied to it.
    Includes debugging prints for alpha values and a slight change to RGB blending.
    """
    # Step 1: Render the text initially in white.
    # .convert_alpha() is crucial for per-pixel alpha blending.
    text_surface = font.render(text, True, (255, 255, 255)).convert_alpha()

    if text_surface.get_size() == (0, 0):
        print(f"Error: Failed to render text '{text}'. Returning empty surface.")
        return pygame.Surface((1, 1), pygame.SRCALPHA)

    width, height = text_surface.get_size()
    print(f"DEBUG: Text surface '{text}' initial size: {width}x{height}")

    # Step 2: Create a gradient surface.
    gradient_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(height):
        t = y / (height - 1)
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        a = int(top_color[3] + (bottom_color[3] - top_color[3]) * t) if len(top_color) == 4 else 255
        pygame.draw.line(gradient_surface, (r, g, b, a), (0, y), (width, y))

    # Step 3: Apply the gradient to the text surface using pixel arrays.
    text_pixels_rgb = pygame.surfarray.pixels3d(text_surface)
    text_pixels_alpha = pygame.surfarray.pixels_alpha(text_surface)
    gradient_pixels_rgb = pygame.surfarray.pixels3d(gradient_surface)
    gradient_pixels_alpha = pygame.surfarray.pixels_alpha(gradient_surface)

    # Check alpha values before blending
    print(f"DEBUG: Initial text_alpha min/max: {np.min(text_pixels_alpha)} / {np.max(text_pixels_alpha)}")
    print(f"DEBUG: Gradient_alpha min/max: {np.min(gradient_pixels_alpha)} / {np.max(gradient_pixels_alpha)}")

    # --- MODIFIED RGB BLENDING ---
    # We remove the // 255 for now. With white text (255), multiplying by gradient color
    # should directly result in the gradient color. This is a common pattern with surfarray.
    text_pixels_rgb[:] = text_pixels_rgb * gradient_pixels_rgb

    # Force full alpha where text exists (as per previous debugging step)
    text_pixels_alpha[text_pixels_alpha > 0] = 255

    # Check alpha values after blending
    print(f"DEBUG: Final text_alpha min/max: {np.min(text_pixels_alpha)} / {np.max(text_pixels_alpha)}")

    # Release the pixel array locks.
    del text_pixels_rgb
    del text_pixels_alpha
    del gradient_pixels_rgb
    del gradient_pixels_alpha

    return text_surface

# --- Your pause_screen function (as in the last debugging step) ---
# This part remains the same, as the issue is likely in font loading or gradient application.
def pause_screen(screen, font):
    skill_tree_button = create_button("Skill Tree", SCREEN_WIDTH / 2 - 145, 420, 300, 75)
    continue_button = create_button("Continue", SCREEN_WIDTH / 2 - 145, 490, 300, 75)
    restart_button = create_button("Restart", SCREEN_WIDTH / 2 - 145, 560, 300, 75)
    quit_button = create_button("Quit", SCREEN_WIDTH / 2 - 145, 630, 300, 75)

    top_bg_color = (100, 180, 220, 255)
    bottom_bg_color = (30, 60, 90, 255)
    rect_gradient_bg = create_vertical_color_gradient((400, 1080), top_bg_color, bottom_bg_color)

    # Use the 'font' object passed in, which is now the (hopefully) loaded .ttf font
    gradient_paused_text_surface = render_text_with_vertical_color_gradient(
        font, # Use the main 'font' object
        "Paused",
        (255, 255, 0, 255),   # top color (Bright Yellow)
        (0, 0, 255, 255)      # bottom color (Bright Blue)
    )
    gradient_text_blit_pos = (10, 10) # Still blitting to top-left for easy visibility

    while True:
        screen.fill((0, 0, 0))
        screen.blit(rect_gradient_bg, (SCREEN_WIDTH / 2 - rect_gradient_bg.get_width() / 2, 0))

        screen.blit(gradient_paused_text_surface, gradient_text_blit_pos)

        button_draw(continue_button, screen)
        button_draw(restart_button, screen)
        button_draw(quit_button, screen)
        button_draw(skill_tree_button, screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if restart_button[0].collidepoint(mouse_x, mouse_y):
                    print("Restart button clicked!")
                    return "Restart"
                if continue_button[0].collidepoint(mouse_x, mouse_y):
                    print("Continue button clicked!")
                    return "Continue"
                if skill_tree_button[0].collidepoint(mouse_x, mouse_y):
                    print("Skill Tree button clicked!")
                    return "skill tree"
                if quit_button[0].collidepoint(mouse_x, mouse_y):
                    print("Quit button clicked!")
                    pygame.quit()
                    sys.exit()
        pygame.display.update()

# --- Main Game Loop (for demonstration) ---
def main_game_loop():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    action = pause_screen(screen, font) # Pass the main font
                    if action == "Restart":
                        print("Game Restarted!")
                    elif action == "Continue":
                        print("Game Continued!")
                    elif action == "skill tree":
                        print("Skill Tree opened!")
        
        screen.fill((50, 50, 150))
        pygame.draw.circle(screen, (255, 255, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 50)
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_game_loop()
