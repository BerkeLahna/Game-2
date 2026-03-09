import math
import globals

current_player_rotation_angle = 0


def player_move(player_pos, mouse_pos):
    global current_player_rotation_angle

    player_x, player_y = player_pos
    mouse_x, mouse_y = mouse_pos

    dx = mouse_x - player_x
    dy = mouse_y - player_y

    distance = math.hypot(dx, dy)

    speed = min(globals.player_movement_speed, distance * 0.05)

    angle_radians = math.atan2(dy, dx)
    angle_degrees = math.degrees(angle_radians)

    rotation_angle = 270 - angle_degrees

    current_normalized = (current_player_rotation_angle + 180) % 360 - 180
    target_normalized = (rotation_angle + 180) % 360 - 180

    diff = target_normalized - current_normalized

    if diff > 180:
        diff -= 360
    elif diff < -180:
        diff += 360

    current_player_rotation_angle += diff * globals.player_turn_speed
    current_player_rotation_angle %= 360

    if distance <= speed:
        player_x = mouse_x
        player_y = mouse_y
    else:
        ratio = speed / distance
        player_x += dx * ratio
        player_y += dy * ratio

    return player_x, player_y, current_player_rotation_angle