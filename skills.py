import pygame
import globals

pygame.init()
screen = pygame.display.set_mode((1920, 1080))
text_font = pygame.font.SysFont("Arial", 18)
level_font = pygame.font.SysFont("Arial", 24)
width = 80
height = 80
color = (0, 255, 0)  # Green color for skills
hover_color = (0, 200, 0)  # Darker green when hovered





class Skill:
    def __init__(self, text, x, y, attr_name, level=0, max_level=3,visible = True, image = None, description = "", parent_attr_names=None, required_parent_level=1):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.level = level
        self.max_level = max_level
        self.visible = visible
        self.attr_name = attr_name  # Name of the attribute in globals.player
        self.image = image
        self.hover_image = image
        self.description = description if description else f"Modifies {self.attr_name.replace('_', ' ').title()}."
        
        # --- Progression System Attributes ---
        self.parent_attr_names = [] # List of attribute names of parent skills
        if isinstance(parent_attr_names, str) and parent_attr_names.strip():
            self.parent_attr_names = [p.strip() for p in parent_attr_names.split(';') if p.strip()]
        elif isinstance(parent_attr_names, list):
            self.parent_attr_names = [p.strip() for p in parent_attr_names if p.strip()]

        self.required_parent_level = required_parent_level
        self.is_unlocked = not self.parent_attr_names  # Unlocked if no parents

        # --- Tooltip Attributes ---
        self.tooltip_bg_color = (25, 25, 35, 220)  # Dark semi-transparent background
        self.tooltip_text_color = (230, 230, 230) # Light grey text
        self.tooltip_padding = 10
        self.tooltip_line_spacing = 5
        
        # --- Visuals for Locked State & Connections ---
        self.locked_overlay_color = (0, 0, 0, 170)  # Darker overlay for locked skills
        self.connector_line_color = (180, 180, 180)
        self.locked_connector_line_color = (80, 80, 80, 0)

    def update_unlock_status(self, skills_dict):
        if not self.parent_attr_names:
            self.is_unlocked = True # No parents, always unlocked
            return

        all_parents_met = True
        for parent_name in self.parent_attr_names:
            parent_skill = skills_dict.get(parent_name)
            if not parent_skill or parent_skill.level < self.required_parent_level:
                all_parents_met = False
                break
        self.is_unlocked = all_parents_met
        if not self.parent_attr_names:
            self.visible = True  # Root skills are always visible
        else:
            all_parents_are_unlocked_for_visibility = True
            for parent_name in self.parent_attr_names:
                parent_skill = skills_dict.get(parent_name)
                # If parent skill doesn't exist OR parent is NOT unlocked (based on its own level requirements)
                if not parent_skill or not parent_skill.is_unlocked:
                    all_parents_are_unlocked_for_visibility = False
                    break  # No need to check further parents
            self.visible = all_parents_are_unlocked_for_visibility

        
    def draw(self, screen): # Modified to show locked state
        if not self.visible:
            return

        # Standard drawing (hover or image)
        if self.is_hovered and self.is_unlocked:
            
            if self.hover_image.get_width() < self.image.get_width()*1.2:
                x_increase, y_increase = (self.hover_image.get_width()+1), (self.hover_image.get_height()+1)
                self.hover_image = self.image
                self.hover_image = pygame.transform.scale(self.hover_image, (x_increase, y_increase))
            screen.blit(self.hover_image , (self.rect.centerx - self.hover_image.get_width() // 2, self.rect.centery - self.hover_image.get_height() // 2))


        elif self.is_hovered and not self.is_unlocked: # Hovering a locked skill
            pygame.draw.rect(screen, (60,60,60), self.rect) # Dim hover color
            ts = text_font.render(self.text, True, (150,150,150))
            screen.blit(ts, (self.rect.centerx - ts.get_width() // 2, self.rect.centery - ts.get_height() // 2))
        elif self.image:
            screen.blit(self.image, self.rect)
        else: # Fallback box
            pygame.draw.rect(screen, (50,50,50), self.rect)

        # Overlay if locked
        if not self.is_unlocked:
            overlay = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            overlay.fill(self.locked_overlay_color)
            screen.blit(overlay, self.rect.topleft)
        

        if self.level >= self.max_level and self.is_unlocked:
            maxed_text =text_font.render("Maxed Out", True, (200, 0, 0)) # font global
            screen.blit(maxed_text, (self.rect.centerx - maxed_text.get_width() // 2, self.rect.bottom + 5))

            
    def level_up(self): # Modified to check lock status and return success
        if not self.is_unlocked:
            print(f"Attempted to level up locked skill: {self.text}")
            return False # Purchase failed

        if self.level < self.max_level:
            self.level += 1
            # getattr and setattr for globals (ensure 'globals' module is correctly set up)
            current_val = getattr(globals, self.attr_name)
            new_val = self.multiplier1(current_val)
            setattr(globals, self.attr_name, new_val)
            return True # Purchase successful
        return False # Already max level
                
    def multiplier1(self, current):
        # (Your existing multiplier1 logic)
        if self.attr_name == "energy_depletion_rate": return current * 0.9
        if self.attr_name == "max_lasers": return current + 1
        if self.attr_name == "player_laser_max_range": return current + 100
        if self.attr_name == "player_energy": return current * 1.1
        if self.attr_name == "laser_damage": return current + 1
        if self.attr_name == "player_movement_speed": return current * 1.1
        if self.attr_name == "player_max_hp": return current + 1
        return current


        

    def get_next_level_effect_description(self):
        if self.level >= self.max_level:
            return "Max Level Reached"

        if self.attr_name == "energy_depletion_rate":
            return "Next Lvl: Energy use -10%"
        elif self.attr_name == "max_lasers":
            return "Next Lvl: Max lasers +1"
        elif self.attr_name == "player_laser_max_range":
            return "Next Lvl: Laser range + 10%"
        elif self.attr_name == "player_energy":
            return "Next Lvl: Max energy +10%"
        elif self.attr_name == "laser_damage":
            return "Next Lvl: Laser damage +1"
        elif self.attr_name == "player_movement_speed":
            return "Next Lvl: Speed +10%"
        return "Next Lvl: Effect varies"
    
    def draw_tooltip(self, screen, mouse_pos, tooltip_font, skills_dict): # Modified for lock info
        if not self.is_hovered or not self.visible:
            return

        lines = [
            f"{self.text.replace('_', ' ').title()}",
            f"Level: {self.level} / {self.max_level}",
            f"Cost: {self.level*10}"
        ]

        if not self.is_unlocked:
            lines.append("Status: LOCKED")
            parent_req_texts = []
            for p_name in self.parent_attr_names:
                p_skill = skills_dict.get(p_name)
                p_text = p_skill.text if p_skill else p_name.replace('_',' ').title()
                parent_req_texts.append(f"{p_text} (Lvl {self.required_parent_level})")
            if parent_req_texts:
                lines.append(f"Requires: {', '.join(parent_req_texts)}")
        else: # Unlocked
            lines.append(f"{self.description}")
            if self.level < self.max_level:
                lines.append(self.get_next_level_effect_description())
            else:
                lines.append("Max Level Reached")

        # (Tooltip rendering code from previous response - unchanged)
        text_surfaces = [tooltip_font.render(line, True, self.tooltip_text_color) for line in lines]
        max_text_width = 0
        total_text_height = (len(text_surfaces) - 1) * self.tooltip_line_spacing
        for surf in text_surfaces:
            if surf.get_width() > max_text_width: max_text_width = surf.get_width()
            total_text_height += surf.get_height()
        tooltip_width = max_text_width + 2 * self.tooltip_padding
        tooltip_height = total_text_height + 2 * self.tooltip_padding
        tooltip_x = mouse_pos[0] + 20
        tooltip_y = mouse_pos[1] + 15
        screen_rect = screen.get_rect()
        if tooltip_x + tooltip_width > screen_rect.right: tooltip_x = mouse_pos[0] - tooltip_width - 20
        if tooltip_y + tooltip_height > screen_rect.bottom: tooltip_y = mouse_pos[1] - tooltip_height - 15
        tooltip_x = max(screen_rect.left, min(tooltip_x, screen_rect.right - tooltip_width))
        tooltip_y = max(screen_rect.top, min(tooltip_y, screen_rect.bottom - tooltip_height))
        tooltip_surface = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
        tooltip_surface.fill(self.tooltip_bg_color)
        screen.blit(tooltip_surface, (tooltip_x, tooltip_y))
        current_y_offset = self.tooltip_padding
        for i, surf in enumerate(text_surfaces):
            screen.blit(surf, (tooltip_x + self.tooltip_padding, tooltip_y + current_y_offset))
            current_y_offset += surf.get_height() + (self.tooltip_line_spacing if i < len(text_surfaces) -1 else 0)
