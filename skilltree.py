import pygame
import sys
import math
import assets
import globals
from skills import Skill
# from buttons import Skills

background_image = pygame.image.load(assets.resource_path('Images/high_quality_futuristic_space_ (2).jpeg'))  # Ensure you have this image in the same folder or provide the correct path
background_image = pygame.transform.scale(background_image, (globals.SCREEN_WIDTH, globals.SCREEN_HEIGHT))  # Scale it to fit the screen

skill_images = {
    1 : pygame.transform.scale(pygame.image.load(assets.resource_path('Images/Skill-1.jpeg')), (80,80)),
    2 : pygame.transform.scale(pygame.image.load(assets.resource_path('Images/Skill - 2.jpeg')), (80,80))
   
}

mask = pygame.mask.from_surface(skill_images[1])
circle_surface = pygame.Surface((80, 80), pygame.SRCALPHA)  # Create a surface with transparency
pygame.draw.circle(circle_surface, (255, 255, 255), (40, 40), 30)  # Draw a white circle with radius 40
circle_mask = pygame.mask.from_surface(circle_surface)  # Create a mask from the circle surface

# Apply the mask to the image
skill_images[1].set_colorkey((0, 0, 0))  # Set transparency for black pixels (if needed)
skill_images[1].blit(circle_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)  # Apply circular mask to image

# Define constants for line appearance (you can adjust these values)
LINE_THICKNESS = 7        # The main line thickness
OUTLINE_THICKNESS = 10    # The thickness of the black outline (must be > LINE_THICKNESS)
NUM_GRADIENT_SEGMENTS = 100 # Number of segments to draw for the gradient (more = smoother, but more CPU)


def create_button(text, x, y, width, height, font, screen, color=(0, 255, 0)):
    button_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, color, button_rect)  # Green button color
    
    # Add text to the button
    button_text = font.render(text, True, (0, 0, 0))  # Black text
    screen.blit(button_text, (button_rect.centerx - button_text.get_width() // 2, 
                              button_rect.centery - button_text.get_height() // 2))

    return button_rect


import re

def load_buttons():
    loaded_buttons = []
    skill_descriptions = { # Your descriptions
        "energy_depletion_rate": "Lowers energy use.",
        "max_lasers": "Increases max active lasers.",
        "player_energy": "Boosts max energy.",
        "laser_damage": "Increases laser damage.",
        "player_movement_speed": "Enhances ship speed."
    }
    try:
        with open(assets.resource_path('Images/buttons.txt'), "r") as file:
            for line_num, line in enumerate(file):
                try:
                    content = line.strip().split('(')[1].split(')')[0]
                    parts = [p.strip() for p in content.split(',')]

                    raw_name = parts[0].strip("'\"")
                    x = int(parts[1])
                    y = int(parts[2])
                    level = int(parts[3])
                    max_level = int(parts[4]) 
                    visibility = parts[5].lower() == 'true'
                    # New: parent_attr_names string (optional)
                    parent_names_str = parts[6].strip("'\"") if len(parts) > 5 else ""

                    attr_name = raw_name # Assuming raw_name is the attr_name
                    
                    img_key = (line_num % len(skill_images)) + 1 if skill_images else None
                    img = skill_images.get(img_key)

                    desc = skill_descriptions.get(attr_name, f"Modifies {attr_name.replace('_', ' ').title()}.")
                    display_text = attr_name.replace('_', ' ').title()
                    
                    # You might want to add required_parent_level to your file too if it varies
                    loaded_buttons.append(Skill(text=display_text, x=x, y=y,
                                                attr_name=attr_name, level=level, max_level=max_level,
                                                visible=visibility, image=img, description=desc,
                                                parent_attr_names=parent_names_str,
                                                required_parent_level=1)) # Default to 1
                except Exception as e:
                    print(f"Error parsing skill line: {line.strip()} - {e}")
    except FileNotFoundError:
        print("buttons.txt not found.")
    return loaded_buttons
    


SkillsList = load_buttons() # Changed variable name from Skills
SkillsDict = {skill.attr_name: skill for skill in SkillsList}


def skill_tree_page(screen, WHITE, main_font, gameplay_page_func):

    # --- Initial Unlock Status Update ---
    # Iteratively update unlock status to handle chains of dependencies
    # (e.g., C depends on B, B depends on A)
    for _ in range(len(SkillsList)): # Iterate a few times to ensure propagation
        updated_in_pass = False
        for skill in SkillsList:
            old_status = skill.is_unlocked
            skill.update_unlock_status(SkillsDict)
            if skill.is_unlocked != old_status:
                updated_in_pass = True
        if not updated_in_pass: # No changes in this pass, statuses are stable
            break

    tooltip_font = pygame.font.Font(None, 22)
    running = True
    while running:
        screen.blit(background_image, (0, 0))
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEMOTION:
                for skill in SkillsList:
                    skill.is_hovered = skill.rect.collidepoint(mouse_x, mouse_y)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    for skill in SkillsList:
                        if skill.rect.collidepoint(mouse_x, mouse_y):
                            if not skill.is_unlocked:
                                print(f"Skill '{skill.text}' is locked.")
                                # Optionally: Add a sound effect or brief on-screen message
                            elif skill.level >= skill.max_level:
                                print(f"Skill '{skill.text}' is already maxed out.")
                            else:
                                cost = (skill.level + 1) * 10 # Example cost
                                if globals.money >= cost:
                                    if skill.level_up(): # level_up now returns True on success
                                        globals.money -= cost
                                        print(f"Leveled up '{skill.text}' to Lvl {skill.level}. Money: {globals.money:.2f}")
                                        # Potentially unlocked other skills, so re-check all
                                        for s_check in SkillsList:
                                            s_check.update_unlock_status(SkillsDict)
                                    # else: level_up handles print for max level if not already caught
                                else:
                                    print(f"Not enough money for '{skill.text}'. Cost: {cost}, Have: {globals.money:.2f}")
                            break # Process only one skill click

                    if play_button.collidepoint(mouse_x, mouse_y): # play_button logic
                        gameplay_page_func(screen, WHITE, main_font, assets.background_image)
                        running = False

        # --- Drawing ---
        # 1. Draw Connector Lines (drawn first, so they are behind skills)
        for skill in SkillsList:
            for parent_attr_name in skill.parent_attr_names:
                parent_skill = SkillsDict.get(parent_attr_name)

                # ONLY draw line if both parent AND child skills are visible
                if parent_skill and skill.visible and parent_skill.visible:
                    start_pos = parent_skill.rect.center
                    end_pos = skill.rect.center

                    # Determine the start and end colors for the gradient based on unlock status
                    # These are RGB values; overall transparency will be applied when blitting the temp surface.
                    if parent_skill.level >= skill.required_parent_level and skill.is_unlocked:
                        # Gradient for UNLOCKED lines (e.g., bright green to dark green)
                        gradient_start_rgb = (100, 255, 100)
                        gradient_end_rgb = (0, 150, 0)
                        overall_line_alpha = 180 # Fully opaque
                    else:
                        # Gradient for LOCKED lines (e.g., light grey to dark grey)
                        gradient_start_rgb = (100, 100, 100)
                        gradient_end_rgb = (50, 50, 50)
                        overall_line_alpha = 120 # Semi-transparent (adjust as needed, 0 for fully transparent)

                    outline_rgb = (0, 0, 0) # Solid black for the outline

                    # Calculate the bounding box for the line to create a temporary surface
                    # Add some padding for the outline thickness
                    min_x = min(start_pos[0], end_pos[0]) - OUTLINE_THICKNESS
                    max_x = max(start_pos[0], end_pos[0]) + OUTLINE_THICKNESS
                    min_y = min(start_pos[1], end_pos[1]) - OUTLINE_THICKNESS
                    max_y = max(start_pos[1], end_pos[1]) + OUTLINE_THICKNESS

                    line_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

                    # Create a temporary surface with alpha for drawing the line
                    # It's important that this surface is SRCALPHA to handle transparency
                    line_surface = pygame.Surface(line_rect.size, pygame.SRCALPHA)

                    # Adjust start/end positions relative to the new temporary surface
                    local_start_pos = (start_pos[0] - line_rect.x, start_pos[1] - line_rect.y)
                    local_end_pos = (end_pos[0] - line_rect.x, end_pos[1] - line_rect.y)

                    # Draw the black outline onto the temporary surface
                    pygame.draw.line(line_surface, outline_rgb, local_start_pos, local_end_pos, OUTLINE_THICKNESS)

                    # Calculate the vector components of the line for gradient segments
                    dx = local_end_pos[0] - local_start_pos[0]
                    dy = local_end_pos[1] - local_start_pos[1]

                    # Draw the gradient line segments onto the temporary surface
                    for i in range(NUM_GRADIENT_SEGMENTS):
                        t = i / NUM_GRADIENT_SEGMENTS

                        seg_start_x = local_start_pos[0] + dx * t
                        seg_start_y = local_start_pos[1] + dy * t

                        seg_end_x = local_start_pos[0] + dx * (t + 1 / NUM_GRADIENT_SEGMENTS)
                        seg_end_y = local_start_pos[1] + dy * (t + 1 / NUM_GRADIENT_SEGMENTS)

                        # Interpolate RGB color for the current segment
                        r = int(gradient_start_rgb[0] + (gradient_end_rgb[0] - gradient_start_rgb[0]) * t)
                        g = int(gradient_start_rgb[1] + (gradient_end_rgb[1] - gradient_start_rgb[1]) * t)
                        b = int(gradient_start_rgb[2] + (gradient_end_rgb[2] - gradient_start_rgb[2]) * t)

                        segment_color = (r, g, b) # No alpha here, as the surface itself has alpha

                        pygame.draw.line(line_surface, segment_color, (seg_start_x, seg_start_y), (seg_end_x, seg_end_y), LINE_THICKNESS)

                    # Blit the temporary line surface onto the main screen, applying overall transparency
                    line_surface.set_alpha(overall_line_alpha)
                    screen.blit(line_surface, line_rect.topleft)

        # 2. Draw Skills
        for skill in SkillsList:
            skill.draw(screen)

        # 3. Draw Tooltip (on top)
        hovered_skill = None
        for skill in SkillsList:
            if skill.is_hovered:
                hovered_skill = skill
                break
        if hovered_skill:
            hovered_skill.draw_tooltip(screen, (mouse_x, mouse_y), tooltip_font, SkillsDict)

        # UI Elements (Money, Play Button)
        money_text_surface = main_font.render(f"Money: {round(globals.money, 2)}", True, (220, 220, 220))
        screen.blit(money_text_surface, (globals.SCREEN_WIDTH - 250, globals.SCREEN_HEIGHT - 70))
        play_button = create_button("Play", globals.SCREEN_WIDTH - 220, globals.SCREEN_HEIGHT - 130, 200, 50, main_font, screen)
        if play_button.collidepoint(mouse_x, mouse_y): # Highlight play button
             pygame.draw.rect(screen, (0, 200, 0), play_button)
             # Re-render text if desired for hover state
             button_text_surf = main_font.render("Play", True, (0,0,0))
             screen.blit(button_text_surf, (play_button.centerx - button_text_surf.get_width() // 2, play_button.centery - button_text_surf.get_height() // 2))


        pygame.display.update()


