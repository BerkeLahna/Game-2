import pygame
import random
time

# Additional Enemy classes and functions
class Enemy(GameObject):
    """
    Enemy that moves into screen, attacks player with lasers, then relocates.
    Supports levels with scaling HP, damage, and varied attack patterns.
    """
    def __init__(self, level=1):
        # Initialize off-screen via move_into_screen helper
        base = move_into_screen()
        super().__init__(base.rect.x, base.rect.y,
                         base.rect.width, base.rect.height,
                         hp=10 + (level-1)*5,
                         x_speed=base.x_speed, y_speed=base.y_speed,
                         image=meteorite_images[random.randint(1,6)])
        self.level = level
        self.max_hp = self.hp
        # Damage per laser shot scales with level
        self.damage = globals.laser_damage + (level-1)*globals.laser_damage*0.2
        # Attack pattern selection
        # 1: single shot, 2: burst shot, 3: spread (for higher levels)
        self.pattern = random.choice(self.get_available_patterns())
        # Attack control
        self.shots_remaining = self.get_shot_count()
        self.last_shot_time = time.time()
        self.shot_interval = 1.0  # seconds between shots
        self.is_boss = (level % 5 == 0)
        if self.is_boss:
            self.shot_interval = 0.6
            self.shots_remaining = self.shots_remaining * 2
        self.state = 'enter'  # other states: 'attack', 'relocate'
        self.state_start = time.time()

    def get_available_patterns(self):
        patterns = ['single']
        if self.level >= 2:
            patterns.append('burst')
        if self.level >= 3:
            patterns.append('spread')
        if self.is_boss:
            patterns.append('omni')
        return patterns

    def get_shot_count(self):
        # determine shots per attack cycle
        return 2 + (self.level - 1)

    def update(self, dt, player_pos):
        """
        Update movement and attack behavior based on state.
        """
        now = time.time()
        if self.state == 'enter':
            # Move until fully on-screen
            self.move()
            if 0 <= self.rect.x <= globals.SCREEN_WIDTH - self.rect.width:
                self.state = 'attack'
                self.state_start = now
        elif self.state == 'attack':
            # Fire lasers at intervals
            if self.shots_remaining > 0 and now - self.last_shot_time >= self.shot_interval:
                self.shoot(player_pos)
                self.shots_remaining -= 1
                self.last_shot_time = now
            if self.shots_remaining <= 0:
                self.state = 'relocate'
                self.state_start = now
        elif self.state == 'relocate':
            # Fade out or move off-screen, then reset
            self.reset_for_next_cycle()

    def shoot(self, player_pos):
        """
        Create one or more lasers based on pattern aimed at player.
        """
        sx, sy = self.rect.center
        px, py = player_pos
        if self.pattern == 'single':
            new_laser = Laser((sx, sy), player_pos, self.damage)
            globals.active_enemy_lasers.append(new_laser)
        elif self.pattern == 'burst':
            # fire 3 quick shots
            for i in range(3):
                new_laser = Laser((sx, sy), player_pos, self.damage)
                globals.active_enemy_lasers.append(new_laser)
        elif self.pattern == 'spread':
            # spread 5 beams around angle to player
            angle = math.atan2(py-sy, px-sx)
            spread = math.radians(30)
            for i in range(5):
                offset = angle - spread/2 + spread*i/4
                ex = sx + math.cos(offset)*1000
                ey = sy + math.sin(offset)*1000
                new_laser = Laser((sx, sy), (ex, ey), self.damage)
                globals.active_enemy_lasers.append(new_laser)
        elif self.pattern == 'omni':
            # boss fires in all directions
            for deg in range(0, 360, 30):
                rad = math.radians(deg)
                ex = sx + math.cos(rad)*1000
                ey = sy + math.sin(rad)*1000
                new_laser = Laser((sx, sy), (ex, ey), self.damage)
                globals.active_enemy_lasers.append(new_laser)

    def reset_for_next_cycle(self):
        # reposition and reset stats
        new_enemy = Enemy(self.level)
        # copy new position and stats
        self.rect = new_enemy.rect
        self.x_speed = new_enemy.x_speed
        self.y_speed = new_enemy.y_speed
        self.hp = new_enemy.hp
        self.max_hp = new_enemy.max_hp
        self.pattern = new_enemy.pattern
        self.shots_remaining = new_enemy.shots_remaining
        self.shot_interval = new_enemy.shot_interval
        self.is_boss = new_enemy.is_boss
        self.state = 'enter'
        self.state_start = time.time()


def spawn_enemies(level, count):
    """
    Utility to spawn multiple enemies for a given level.
    """
    enemies = []
    for _ in range(count):
        enemies.append(Enemy(level))
    return enemies

# Remember to integrate globals.active_enemy_lasers = [] at top of gameplay_page
