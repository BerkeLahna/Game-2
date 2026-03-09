import pygame
import globals
import sys
import os
import options

explosion_images = None
explosion_sound = None
hp_bar_img = None
energy_bar_img = None
background_image = None
player_image = None
logo_background = None
menu_logo = None
meteorite_images = None


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def load_assets():

    global explosion_images
    global explosion_sound
    global hp_bar_img
    global energy_bar_img
    global background_image
    global player_image
    global logo_background
    global menu_logo
    global meteorite_images
    
    # Meteorite images are now defined here, as this is the GameObject base for them
    meteorite_images = {
        1 : pygame.transform.scale(pygame.image.load( resource_path('Images/Meteors/meteor1.png')), (50,50)),
        2 : pygame.transform.scale(pygame.image.load( resource_path('Images/Meteors/meteor2.png')), (50,50)),
        3 : pygame.transform.scale(pygame.image.load( resource_path('Images/Meteors/meteor3.png')), (50,50)),
        4 : pygame.transform.scale(pygame.image.load( resource_path('Images/Meteors/meteor4.png')), (50,50)),
        5 : pygame.transform.scale(pygame.image.load( resource_path('Images/Meteors/meteor5.png')), (50,50)),
        6 : pygame.transform.scale(pygame.image.load( resource_path('Images/Meteors/meteor6.png')), (50,50))
        }

    
    # --- MUSIC ---
    try:
        pygame.mixer.music.load(resource_path('Images/lofi.mp3'))
        # CHANGE THIS LINE: Access the settings instance
        pygame.mixer.music.set_volume(options.settings.music_volume) 
        pygame.mixer.music.play(-1)
    except pygame.error as e:
        print(f"Music error: {e}")


    # --- EXPLOSIONS ---
    explosion_images = {
        i: pygame.transform.scale(
            pygame.image.load(
               resource_path(f'Images/Explosion/explosion{i if i != 5 else "5_scuffed"}.png')
            ).convert_alpha(),
            (60, 60)
        )
        for i in range(1, 8)
    }

    explosion_sound = pygame.mixer.Sound(
        resource_path("Images/Explosion/explosion_alternate1.mp3")
    )

    # --- UI ---
    raw_hp = pygame.image.load(resource_path('Images/hp_bar_full.png')).convert_alpha()
    raw_energy = pygame.image.load(resource_path('Images/energy_bar_full.png')).convert_alpha()

    scale = 0.6

    hp_bar_img = pygame.transform.scale(
        raw_hp,
        (int(raw_hp.get_width()*scale), int(raw_hp.get_height()*scale))
    )

    energy_bar_img = pygame.transform.scale(
        raw_energy,
        (int(raw_energy.get_width()*scale), int(raw_energy.get_height()*scale))
    )

    # --- BACKGROUND ---
    background_image = pygame.image.load(resource_path('Images/menu (1).jpeg'))
    background_image = pygame.transform.scale(background_image, (1920,1080))

    logo_background = pygame.image.load(resource_path("Images/wp10105509.jpg")).convert()
    logo_background = pygame.transform.scale(logo_background, (1920,1080))

    menu_logo = pygame.image.load(resource_path('Images/menu-logo-test.png')).convert_alpha()

    # --- PLAYER ---
    raw_player = pygame.image.load(resource_path('Images/Ships/ship-2.png')).convert_alpha()
    raw_player = pygame.transform.scale(
        raw_player,
        (globals.player_size, globals.player_size)
    )

    player_image = pygame.Surface(
        (globals.player_size, globals.player_size),
        pygame.SRCALPHA
    )
    player_image.blit(raw_player, (0,0))

    mask = pygame.Surface(
        (globals.player_size, globals.player_size),
        pygame.SRCALPHA
    )
    pygame.draw.circle(
        mask,
        (255,255,255,255),
        (globals.player_size//2, globals.player_size//2),
        globals.player_size//2
    )
    player_image.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MULT)
    

def sync_volume():
    """Call this when you change the slider in the options menu"""
    pygame.mixer.music.set_volume(options.settings.music_volume)