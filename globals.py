import math

max_lasers = 1
laser_damage = 4
player_max_energy = 6000
player_energy = player_max_energy
player_movement_speed = 5
energy_depletion_rate = 1
energy_view1 = 1000
energy_view = math.log(energy_view1,10)
money = 0
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
player_turn_speed = 0.05
player_size = 60
player_max_hp = 100
player_hp = player_max_hp
enemy_laser_damage_per_second = 15 # Damage enemy lasers deal to player per second
enemy_projectile_speed = 300