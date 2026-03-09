import math

max_lasers = 1
laser_damage = 10
player_max_energy = 5000
player_energy = player_max_energy
player_movement_speed = 5
energy_depletion_rate = 1
player_max_hp = 1
player_laser_max_range = 100 # Max distance player laser can reach in pixels


energy_view1 = 1000
energy_view = math.log(energy_view1,10)
money = 1010100
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
player_turn_speed = 0.05
player_size = 60
player_hp = player_max_hp
enemy_laser_damage_per_second = 60 # Damage enemy lasers deal to player per second
enemy_projectile_speed = 300
active_enemy_lasers = [] # This list is no longer used for enemy lasers (they are managed by Enemy class)

# New global for player laser max range
