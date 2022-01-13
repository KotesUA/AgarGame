import math
from abc import ABC, abstractmethod
from operator import sub


class Killer(ABC):
    @abstractmethod
    def murder(self, victim):
        pass


class Victim(ABC):
    @abstractmethod
    def die(self, killer):
        pass


class Circle:
    def __init__(self, pos, rad):
        self.pos = pos
        self.rad = rad

    def distance_to(self, circle):
        dist = tuple(map(sub, self.pos, circle.pos))
        return math.hypot(*dist)

    def intersects(self, circle):
        return self.distance_to(circle) < self.rad + circle.rad

    def area(self):
        return math.pi * self.rad**2