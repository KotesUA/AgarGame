import math
import random
from operator import add, sub
from typing import Tuple


def polar_to_cartesian(angle: float, val: float) -> Tuple[float, float]:
    return val * math.cos(angle), val * math.sin(angle)


def cartesian_to_polar(x, y) -> Tuple[float, float]:
    return math.atan2(x, y), math.sqrt(x ** 2 + y ** 2)


def random_pos(bounds: Tuple[int, int]):
    return [random.randint(-bounds[0], bounds[0]), random.randint(-bounds[1], bounds[1])]


def random_color() -> Tuple[int, int, int]:
    COLOR_LIST = [(37, 7, 255), (35, 183, 253), (48, 254, 241), (19, 80, 254), (6, 254, 13), (255, 7, 23)]
    return random.choice(COLOR_LIST)


def get_velocity(
    vector_pos: Tuple[float, float], angle: float, speed: float, pos: Tuple[float, float]
) -> Tuple[float, float]:
    vec = polar_to_cartesian(angle, speed * 500)
    vec_end = list(map(add, vector_pos, vec))

    relative_vec = list(map(sub, vec_end, pos))
    relative_vec = cartesian_to_polar(*relative_vec)
    return relative_vec
