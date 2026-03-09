import pygame
import globals

explosion_images = None
explosion_sound = None
hp_bar_img = None
energy_bar_img = None
background_image = None
player_image = None
logo_background = None
menu_logo = None



def load_assets():

    global explosion_images
    global explosion_sound
    global hp_bar_img
    global energy_bar_img
    global background_image
    global player_image
    global logo_background
    global menu_logo


    # --- EXPLOSIONS ---
    explosion_images = {
        i: pygame.transform.scale(
            pygame.image.load(
                f'Images/Explosion/explosion{i if i != 5 else "5_scuffed"}.png'
            ).convert_alpha(),
            (60, 60)
        )
        for i in range(1, 8)
    }

    explosion_sound = pygame.mixer.Sound(
        "Images/Explosion/explosion_alternate1.mp3"
    )

    # --- UI ---
    raw_hp = pygame.image.load(r'Images\hp_bar_full.png').convert_alpha()
    raw_energy = pygame.image.load(r'Images\energy_bar_full.png').convert_alpha()

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
    background_image = pygame.image.load('Images/menu (1).jpeg')
    background_image = pygame.transform.scale(background_image, (1920,1080))

    logo_background = pygame.image.load("Images/wp10105509.jpg").convert()
    logo_background = pygame.transform.scale(logo_background, (1920,1080))

    menu_logo = pygame.image.load('Images/menu-logo-test.png')
    
    # --- PLAYER ---
    raw_player = pygame.image.load('Images/Ships/ship-2.png').convert_alpha()
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