import math
import random
from operator import add, sub


def polar_to_cartesian(angle: object, val: object) -> object:
    return [val * math.cos(angle), val * math.sin(angle)]


def cartesian_to_polar(x, y):
    return [math.atan2(x, y), math.sqrt(x**2 + y**2)]


def random_pos(bounds):
    return [random.randint(-bounds[0], bounds[0]), random.randint(-bounds[1], bounds[1])]


def random_color():
    COLOR_LIST = [
        (37, 7, 255),
        (35, 183, 253),
        (48, 254, 241),
        (19, 80, 254),
        (6, 254, 13),
        (255, 7, 23)
    ]
    return random.choice(COLOR_LIST)


def get_velocity(vector_pos, angle, speed, pos):
    vec = polar_to_cartesian(angle, speed*500)
    vec_end = list(map(add, vector_pos, vec))

    relative_vec = list(map(sub, vec_end, pos))
    relative_vec = cartesian_to_polar(*relative_vec)
    return relative_vec
