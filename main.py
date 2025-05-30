import pygame
import sys
from gameplay import gameplay_page
from buttons import *

# Initialize Pygame
pygame.init()

# Screen size and color
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game with Collisions and Skill Tree")

background_image = pygame.image.load('Images/menu (1).jpeg')  # Ensure you have this image in the same folder or provide the correct path
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))  # Scale it to fit the screen
transparent_rect = pygame.Surface((600, 300), pygame.SRCALPHA)
background_image.set_colorkey((0, 0, 0))  # Set transparency for black pixels (if needed)
background_image.blit(transparent_rect, (650, 175), special_flags=pygame.BLEND_RGBA_MIN)  

logo_background =  pygame.image.load("Images/wp10105509.jpg").convert()
logo_background = pygame.transform.scale(logo_background, (WIDTH, HEIGHT))  # Scale if necessary

# Load background music
try:
    pygame.mixer.music.load('Images/lofi.mp3') 
    pygame.mixer.music.set_volume(0.3) # Set volume (0.0 to 1.0)
    pygame.mixer.music.play(-1) # Play the music indefinitely (-1 means loop forever)
except pygame.error as e:
    print(f"Could not load or play music: {e}")



menu_logo = pygame.image.load('Images/menu-logo-test.png')  


buttons = []
# Font for rendering text

font = pygame.font.SysFont("8-Bit-Madness", 46)


# Main menu or startup logic here
def main_menu():
    clock = pygame.time.Clock()  # Create clock for frame rate control

    start_button = create_button("Start", WIDTH // 2 - 150, HEIGHT // 2 - 40, 300, 75)
    options_button = create_button("Options", WIDTH // 2 - 150, HEIGHT // 2 + 40, 300, 75)
    quit_button = create_button("Quit", WIDTH // 2 - 150, HEIGHT // 2 + 120, 300, 75)
    
    buttons.append(start_button)
    buttons.append(options_button)
    buttons.append(quit_button)
    
    bg_x1 = 0
    bg_x2 = WIDTH
    scroll_speed = 0.5
        
    while True:
        # Move background
        bg_x1 -= scroll_speed
        bg_x2 -= scroll_speed
        # Reset background position when off-screen
        if bg_x1 <= -WIDTH:
            bg_x1 = WIDTH
        if bg_x2 <= -WIDTH:
            bg_x2 = WIDTH
        # Draw backgrounds
        screen.blit(logo_background, (bg_x1, 0))
        screen.blit(logo_background, (bg_x2, 0))
        screen.blit(background_image, (0, 0))
        screen.blit(menu_logo, (WIDTH // 2 - menu_logo.get_width() // 2- 20, 80))
        # Create the buttons


        for button in buttons:
            button_draw(button, screen)


        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                # Check if buttons were clicked
                if start_button[0].collidepoint(mouse_x, mouse_y):
                    gameplay_page(screen, WHITE, font)  # Go to gameplay when Start is clicked
                    # gameplay_page(screen, background_image,background_image, font)
                elif quit_button[0].collidepoint(mouse_x, mouse_y):
                    pygame.quit()
                    sys.exit()
                # Options button logic (could be expanded later)
                elif options_button[0].collidepoint(mouse_x, mouse_y):
                    print("Options button clicked")  # Placeholder for options screen

        # Hover effect for buttons
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for button in buttons:
            if button[0].collidepoint(mouse_x, mouse_y):
   
                button_draw(button, screen,hover=True)


        pygame.display.update()

        # Limit to 60 FPS
        clock.tick(60)

# Run the main menu
main_menu()
