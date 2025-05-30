import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
BUTTON_WIDTH = 80
BUTTON_HEIGHT = 80
WHITE = (255, 255, 255)
BUTTON_COLOR = (0, 128, 255)
HOVER_COLOR = (0, 200, 255)
LINE_COLOR = (0, 0, 255)

# Set up screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Draggable Buttons")

# Create a font object for text rendering
font = pygame.font.SysFont("Arial", 20)

# Store buttons with their positions
buttons = []
dragging_button = None
drag_offset = (0, 0)
connected_buttons = []  # List to store pairs of buttons to connect
start_connection_button = None

# Button class
class Button:
    def __init__(self, x, y, level ,visibility=True, text="ClickMe"):
        self.rect = pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.color = BUTTON_COLOR
        self.text = text
        self.text_surface = font.render(self.text, True, (255, 255, 255))
        self.visibility = visibility
        self.level = level

    def draw(self, surface):
        if self.visibility:
            pygame.draw.rect(surface, self.color, self.rect)
            surface.blit(self.text_surface, (self.rect.centerx - self.text_surface.get_width() / 2,
                                             self.rect.centery - self.text_surface.get_height() / 2))
        else:
            pygame.draw.rect(surface, (200, 200, 200), self.rect)  # Draw a gray rectangle if not visible

    def is_hovered(self, pos):
        return self.rect.collidepoint(pos)

    def set_position(self, x, y):
        self.rect.topleft = (x, y)

    def set_text(self, text):
        self.text = text
        self.text_surface = font.render(self.text, True, (255, 255, 255))


# Function to save button coordinates to a file
def save_buttons(buttons):
    with open("buttons.txt", "w") as file:
        for button in buttons:
            file.write(f"Skill({button.text},{button.rect.x},{button.rect.y},{button.level},{button.visibility})\n")

# Function to load button coordinates from a file
def load_buttons():
    loaded_buttons = []
    try:
        with open("buttons.txt", "r") as file:
            for line in file:
                # Parse the button positions from the file (assuming format: Skill('', x, y))
                parts = line.strip().split('(')[1].split(')')[0]
                name, x, y, level, visibility = parts.split(',')
                visibility = visibility.strip() == 'True'  # Convert string to actual boolean
                loaded_buttons.append(Button(int(x), int(y), level, visibility, name))
    except FileNotFoundError:
        pass  # No buttons to load if the file doesn't exist
    return loaded_buttons

# Function to handle text input when clicking a button
def get_input_text():
    input_text = ""
    active = True
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Enter key to finish input
                    active = False
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]  # Delete last character
                else:
                    input_text += event.unicode  # Add new character to input text

        # Clear the screen and redraw the buttons
        screen.fill(WHITE)
        for button in buttons:
            button.draw(screen)

        # Display the text input box
        input_surface = font.render(input_text, True, (0, 0, 0))
        pygame.draw.rect(screen, (200, 200, 200), (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 300, 40))
        screen.blit(input_surface, (SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 + 10))

        pygame.display.flip()

    return input_text

# Function to check if a point is close to a line
def is_point_near_line(px, py, x1, y1, x2, y2, tolerance=5):
    # Calculate the distance from point (px, py) to the line segment (x1, y1) to (x2, y2)
    line_length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    if line_length == 0:
        return False  # Prevent division by zero if the line segment has zero length
    # Find the perpendicular distance from the point to the line
    area = abs((x2 - x1) * (y1 - py) - (x1 - px) * (y2 - y1))
    distance = area / line_length
    return distance <= tolerance

# Load saved buttons
buttons = load_buttons()

running = True
while running:
    screen.fill(WHITE)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_buttons(buttons)  # Save button positions when quitting
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                for button in buttons:
                    if button.is_hovered(event.pos):
                        dragging_button = button
                        drag_offset = (button.rect.x - event.pos[0], button.rect.y - event.pos[1])
                        break
                else:
                    # Create a new button where clicked
                    buttons.append(Button(event.pos[0] - BUTTON_WIDTH // 2, event.pos[1] - BUTTON_HEIGHT // 2, True))
            
            if event.button == 2:  
                for button in buttons:
                    if button.is_hovered(event.pos):
                        # Allow text change when button is clicked
                        new_text = get_input_text()
                        button.set_text(new_text)  # Update button text
                        break
            if event.button == 3:
                # Right mouse button to remove a button
                for button in buttons:
                    if button.is_hovered(event.pos):
                        buttons.remove(button)
                        break
                        
        elif event.type == pygame.MOUSEMOTION:
            if dragging_button:
                mouse_x, mouse_y = event.pos
                new_x = mouse_x + drag_offset[0]
                new_y = mouse_y + drag_offset[1]
                dragging_button.set_position(new_x, new_y)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging_button = None
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_v:
                for button in buttons:
                    if button.is_hovered(pygame.mouse.get_pos()):
                        button.visibility = not button.visibility
                      
            elif event.key == pygame.K_c:
                for button in buttons:
                    if button.is_hovered(pygame.mouse.get_pos()):
                        if start_connection_button is None:
                            start_connection_button = button
                        else:
                            if button != start_connection_button:
                                connected_buttons.append((start_connection_button, button))
                                start_connection_button = None
                        break
                
            elif event.key == pygame.K_x:
                # Check if the mouse is over any connection line
                for button1, button2 in connected_buttons:
                    if is_point_near_line(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], 
                                          button1.rect.centerx, button1.rect.centery,
                                          button2.rect.centerx, button2.rect.centery):
                        connected_buttons.remove((button1, button2))
                        break
            
    # Draw all buttons
    for button in buttons:
        button.draw(screen)
    for button1, button2 in connected_buttons:
        pygame.draw.line(screen, LINE_COLOR, button1.rect.center, button2.rect.center, 2)

    if start_connection_button:
        pygame.draw.line(screen, LINE_COLOR, start_connection_button.rect.center, pygame.mouse.get_pos(), 1)

    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
