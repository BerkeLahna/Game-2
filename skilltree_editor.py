import pygame
import sys
import math
import os
from skills import Skill # Import the Skill class
import globals # Assuming globals.py exists for SCREEN_WIDTH, SCREEN_HEIGHT

# Initialize Pygame
pygame.init()

background_image = pygame.image.load('Images/high_quality_futuristic_space_ (2).jpeg')  # Ensure you have this image in the same folder or provide the correct path
background_image = pygame.transform.scale(background_image, (globals.SCREEN_WIDTH, globals.SCREEN_HEIGHT))  # Scale it to fit the screen

# Constants
SCREEN_WIDTH = globals.SCREEN_WIDTH
SCREEN_HEIGHT = globals.SCREEN_HEIGHT
SKILL_WIDTH = 80
SKILL_HEIGHT = 80
WHITE = (255, 255, 255)
LINE_COLOR = (0, 0, 255) # Color for connection lines in editor

# Set up screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Skill Tree Editor")

# Create a font object for text rendering
font = pygame.font.SysFont("Arial", 20)
input_font = pygame.font.SysFont("Arial", 24) # Font for input box
tooltip_font = pygame.font.Font(None, 22) # Font for tooltip display


# --- Skill Images and Descriptions (copied from skilltree.py for editor's self-containment) ---
try:
    skill_images = {
        1 : pygame.transform.scale(pygame.image.load('Images/skill-1.jpeg'), (SKILL_WIDTH, SKILL_HEIGHT)),
        2 : pygame.transform.scale(pygame.image.load('Images/skill-2.jpeg'), (SKILL_WIDTH, SKILL_HEIGHT))
    }
except pygame.error as e:
    print(f"Warning: Could not load skill images. Ensure Images/Skill-1.png and Images/Skill-2.png exist. Error: {e}")
    skill_images = {
        1: pygame.Surface((SKILL_WIDTH, SKILL_HEIGHT), pygame.SRCALPHA),
        2: pygame.Surface((SKILL_WIDTH, SKILL_HEIGHT), pygame.SRCALPHA)
    }
    pygame.draw.rect(skill_images[1], (100, 100, 200), skill_images[1].get_rect(), border_radius=5)
    pygame.draw.circle(skill_images[2], (200, 100, 100), (SKILL_WIDTH//2, SKILL_HEIGHT//2), SKILL_WIDTH//2 - 5)


# skill_descriptions are no longer used for saving/loading but can be for initial creation defaults
skill_descriptions = {
    "energy_depletion_rate": "Lowers energy use.",
    "max_lasers": "Increases max active lasers.",
    "player_energy": "Boosts max energy.",
    "laser_damage": "Increases laser damage.",
    "player_movement_speed": "Enhances ship speed."
}
# --- End Skill Images and Descriptions ---


# Store Skill objects
skills = []
skills_dict = {} # Dictionary for quick lookup by attr_name, needed for tooltip and unlock logic
dragging_skill = None
drag_offset = (0, 0)
connected_buttons = [] # List to store (parent_skill, child_skill) tuples for drawing lines

start_connection_skill = None # Stores the first skill selected for connection


# Function to save skill data to a file in the new format
def save_skills(skills_list):
    with open("buttons.txt", "w") as file:
        for skill in skills_list:
            parent_names_str = ";".join(skill.parent_attr_names)
            file.write(f"Skill({skill.attr_name},{skill.rect.x},{skill.rect.y},{skill.level},{skill.visible},{parent_names_str})\n")

# Function to load skill data from a file in the new format
def load_skills():
    loaded_skills = []
    temp_connections_data = []
    try:
        with open("buttons.txt", "r") as file:
            for line_num, line in enumerate(file):
                try:
                    content_str = line.strip()
                    if not content_str.startswith("Skill(") or not content_str.endswith(")"):
                        print(f"Skipping malformed line {line_num + 1}: {line.strip()} (does not match Skill(...) format)")
                        continue
                    
                    inner_content = content_str[len("Skill("):-1]
                    parts = [p.strip() for p in inner_content.split(',')]

                    if len(parts) < 5:
                        print(f"Skipping malformed line {line_num + 1}: {line.strip()} (too few arguments)")
                        continue

                    attr_name = parts[0].strip()
                    x = int(parts[1])
                    y = int(parts[2])
                    level = int(parts[3])
                    visible = parts[4].lower() == 'true'
                    parent_names_str = parts[5].strip() if len(parts) > 5 else ""

                    img_key = (line_num % len(skill_images)) + 1 if skill_images else None
                    img = skill_images.get(img_key)

                    skill = Skill(text=attr_name.replace('_', ' ').title(), x=x, y=y,
                                  attr_name=attr_name, level=level,
                                  visible=visible, image=img,
                                  description=skill_descriptions.get(attr_name, f"Modifies {attr_name.replace('_', ' ').title()}."),
                                  parent_attr_names=[],
                                  required_parent_level=1)
                    loaded_skills.append(skill)
                    temp_connections_data.append((skill.attr_name, parent_names_str))

                except Exception as e:
                    print(f"Error parsing skill line {line_num + 1}: {line.strip()} - {e}")
    except FileNotFoundError:
        print("buttons.txt not found. Starting with no skills.")

    skills_dict_temp = {s.attr_name: s for s in loaded_skills}
    reconstructed_connections = []
    for child_attr_name, parent_names_str in temp_connections_data:
        child_skill = skills_dict_temp.get(child_attr_name)
        if child_skill:
            parent_attr_names_list = [p.strip() for p in parent_names_str.split(';') if p.strip()]
            child_skill.parent_attr_names = parent_attr_names_list

            for p_name in parent_attr_names_list:
                parent_skill = skills_dict_temp.get(p_name)
                if parent_skill:
                    reconstructed_connections.append((parent_skill, child_skill))
                else:
                    print(f"Warning: Parent skill '{p_name}' not found for child '{child_attr_name}'.")

    return loaded_skills, reconstructed_connections


# Function to handle text input for skill creation/editing (simplified)
def get_skill_data_input(current_attr_name=None):
    data = {
        'attr_name': current_attr_name if current_attr_name else '',
    }
    
    input_fields = {
        'attr_name': {'label': "Attribute Name (e.g., max_lasers): ", 'rect': pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 50, 400, 40)},
    }
    
    active_field = 'attr_name'
    cursor_visible = True
    cursor_timer = 0
    
    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return data
                elif event.key == pygame.K_BACKSPACE:
                    data[active_field] = data[active_field][:-1]
                else:
                    data[active_field] += event.unicode
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                for field_name, field_info in input_fields.items():
                    if field_info['rect'].collidepoint(event.pos):
                        active_field = field_name
                        break
        
        # screen.fill(WHITE)
        
        for field_name, field_info in input_fields.items():
            pygame.draw.rect(screen, (200, 200, 200), field_info['rect'])
            pygame.draw.rect(screen, (0, 0, 0), field_info['rect'], 2)
            
            label_surf = input_font.render(field_info['label'], True, (0, 0, 0))
            screen.blit(label_surf, (field_info['rect'].x, field_info['rect'].y - 30))
            
            text_surf = input_font.render(data[field_name], True, (0, 0, 0))
            screen.blit(text_surf, (field_info['rect'].x + 5, field_info['rect'].y + 5))
            
            if active_field == field_name:
                cursor_timer = (cursor_timer + 1) % 60
                if cursor_timer < 30:
                    cursor_x = field_info['rect'].x + 5 + text_surf.get_width()
                    pygame.draw.line(screen, (0,0,0), (cursor_x, field_info['rect'].y + 5), (cursor_x, field_info['rect'].y + field_info['rect'].height - 5), 2)
        
        pygame.display.flip()
        pygame.time.Clock().tick(60)


# Function to check if a point is close to a line
def is_point_near_line(px, py, x1, y1, x2, y2, tolerance=10):
    line_length_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2
    if line_length_sq == 0:
        return False

    t = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / float(line_length_sq)
    t = max(0, min(1, t))

    closest_x = x1 + t * (x2 - x1)
    closest_y = y1 + t * (y2 - y1)

    distance = math.sqrt((px - closest_x) ** 2 + (py - closest_y) ** 2)
    return distance <= tolerance


# Load saved skills and connections
skills, connected_buttons = load_skills()
skills_dict = {s.attr_name: s for s in skills} # Initialize skills_dict after loading


running = True
while running:
    # screen.fill(WHITE)
    mouse_x, mouse_y = pygame.mouse.get_pos()
    screen.blit(background_image, (0, 0))

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_skills(skills)
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button (for dragging or creating)
                for skill in skills:
                    if skill.rect.collidepoint(event.pos):
                        dragging_skill = skill
                        drag_offset = (skill.rect.x - event.pos[0], skill.rect.y - event.pos[1])
                        break
                else: # No skill was clicked, create a new one
                    new_skill_data = get_skill_data_input()
                    if new_skill_data and new_skill_data['attr_name']:
                        if any(s.attr_name == new_skill_data['attr_name'] for s in skills):
                            print(f"Skill with attribute name '{new_skill_data['attr_name']}' already exists.")
                        else:
                            new_skill = Skill(
                                text=new_skill_data['attr_name'].replace('_', ' ').title(),
                                x=event.pos[0] - SKILL_WIDTH // 2,
                                y=event.pos[1] - SKILL_HEIGHT // 2,
                                attr_name=new_skill_data['attr_name'],
                                level=0,
                                visible=True,
                                image=skill_images.get(1),
                                description=skill_descriptions.get(new_skill_data['attr_name'], f"Modifies {new_skill_data['attr_name'].replace('_', ' ').title()}."),
                                parent_attr_names=[],
                                required_parent_level=1
                            )
                            skills.append(new_skill)
                            skills_dict[new_skill.attr_name] = new_skill # Add to dict
                            print(f"Created new skill: {new_skill.attr_name}")

            elif event.button == 2: # Middle mouse button (for editing skill data)
                for skill in skills:
                    if skill.rect.collidepoint(event.pos):
                        updated_data = get_skill_data_input(skill.attr_name)
                        if updated_data and updated_data['attr_name']:
                            if updated_data['attr_name'] != skill.attr_name and \
                               any(s.attr_name == updated_data['attr_name'] for s in skills if s != skill):
                                print(f"Cannot change attribute name to '{updated_data['attr_name']}': already exists.")
                            else:
                                # Update skill attributes
                                old_attr_name = skill.attr_name
                                skill.attr_name = updated_data['attr_name']
                                skill.text = updated_data['attr_name'].replace('_', ' ').title()
                                # Update skills_dict keys if attr_name changed
                                if old_attr_name != skill.attr_name:
                                    del skills_dict[old_attr_name]
                                    skills_dict[skill.attr_name] = skill
                                    # Update parent_attr_names in other skills if they referenced the old name
                                    for s_other in skills:
                                        if old_attr_name in s_other.parent_attr_names:
                                            s_other.parent_attr_names = [
                                                skill.attr_name if p == old_attr_name else p
                                                for p in s_other.parent_attr_names
                                            ]
                                print(f"Updated skill: {skill.attr_name}")
                        break

            elif event.button == 3: # Right mouse button (for removing a skill)
                for skill in skills:
                    if skill.rect.collidepoint(event.pos):
                        skills.remove(skill)
                        del skills_dict[skill.attr_name] # Remove from dict
                        connected_buttons = [conn for conn in connected_buttons if conn[0] != skill and conn[1] != skill]
                        for s in skills:
                            if skill.attr_name in s.parent_attr_names:
                                s.parent_attr_names.remove(skill.attr_name)
                        print(f"Removed skill: {skill.attr_name}")
                        break
                        
        elif event.type == pygame.MOUSEMOTION:
            if dragging_skill:
                new_x = mouse_x + drag_offset[0]
                new_y = mouse_y + drag_offset[1]
                dragging_skill.rect.topleft = (new_x, new_y)
            
            for skill in skills:
                skill.is_hovered = skill.rect.collidepoint(mouse_x, mouse_y)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging_skill = None
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_v: # Toggle visibility
                for skill in skills:
                    if skill.is_hovered:
                        skill.visible = not skill.visible
                        print(f"Skill '{skill.attr_name}' visibility toggled to {skill.visible}")
                        break
                      
            elif event.key == pygame.K_c: # Connect skills
                for skill in skills:
                    if skill.is_hovered:
                        if start_connection_skill is None:
                            start_connection_skill = skill
                            print(f"Start connection from: {skill.attr_name}")
                        else:
                            if skill != start_connection_skill:
                                if (start_connection_skill, skill) not in connected_buttons and \
                                   (skill, start_connection_skill) not in connected_buttons:
                                    
                                    if start_connection_skill.attr_name not in skill.parent_attr_names:
                                        skill.parent_attr_names.append(start_connection_skill.attr_name)
                                        connected_buttons.append((start_connection_skill, skill))
                                        print(f"Connected {start_connection_skill.attr_name} to {skill.attr_name}")
                                    else:
                                        print(f"Connection from {start_connection_skill.attr_name} to {skill.attr_name} already exists.")
                                else:
                                    print("Connection already exists or is a self-connection.")
                            start_connection_skill = None
                        break
                
            elif event.key == pygame.K_x: # Remove connection
                connection_removed = False
                for conn_parent, conn_child in list(connected_buttons):
                    if is_point_near_line(mouse_x, mouse_y, conn_parent.rect.centerx, conn_parent.rect.centery,
                                          conn_child.rect.centerx, conn_child.rect.centery):
                        if conn_parent.attr_name in conn_child.parent_attr_names:
                            conn_child.parent_attr_names.remove(conn_parent.attr_name)
                        connected_buttons.remove((conn_parent, conn_child))
                        print(f"Removed connection from {conn_parent.attr_name} to {conn_child.attr_name}")
                        connection_removed = True
                        break
                if not connection_removed:
                    print("No connection found near mouse to remove.")
            
            elif event.key == pygame.K_s: # Save skills
                save_skills(skills)
                print("Skills saved to buttons.txt")

    # Draw all skills
    for skill in skills:
        skill.draw(screen)

    # Draw connections
    for button1, button2 in connected_buttons:
        pygame.draw.line(screen, LINE_COLOR, button1.rect.center, button2.rect.center, 2)

    # Draw temporary connection line if starting a connection
    if start_connection_skill:
        pygame.draw.line(screen, LINE_COLOR, start_connection_skill.rect.center, (mouse_x, mouse_y), 1)

    # Draw Tooltip (on top)
    hovered_skill = None
    for skill in skills:
        if skill.is_hovered:
            hovered_skill = skill
            break
    if hovered_skill:
        # Pass skills_dict for tooltip to check parent unlock status
        hovered_skill.draw_tooltip(screen, (mouse_x, mouse_y), tooltip_font, skills_dict)


    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()

