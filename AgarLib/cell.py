import random
from operator import add

from AgarLib.instruments import polar_to_cartesian, cartesian_to_polar, random_pos, random_color
from AgarLib.interfaces import Circle, Victim


class Cell(Circle, Victim):
    FRICTION = 0.2
    FOOD_SIZES = (5, 10, 15)
    MAX_SPEED = 15

    def __init__(self, pos, rad, col, angle=0, speed=0):
        super().__init__(pos, rad)
        self.col = col
        self.angle = angle
        self.speed = speed

    def __repr__(self):
        return f'{self.__class__.__name__} | pos={self.pos} | rad = {self.rad}'

    def update_velocity(self, angle, speed):
        v1 = polar_to_cartesian(angle, speed)
        v2 = polar_to_cartesian(self.angle, self.speed)

        v3 = list(map(add, v1, v2))

        self.angle, self.speed = cartesian_to_polar(*v3)

        if self.speed > self.MAX_SPEED:
            self.speed = self.MAX_SPEED

    def move(self):
        temp = self.speed

        self.speed -= self.FRICTION
        diff = polar_to_cartesian(self.angle, self.speed)
        self.pos = list(map(add, self.pos, diff))

        if temp <= 1 < self.speed:
            self.speed = 1
        elif 1 < temp < self.speed:
            self.speed = temp

    def die(self, killer):
        if 1.5*self.area() <= killer.area() and Circle.intersects(self, killer):
            return self
        return None

    @classmethod
    def random_cell(cls, bounds):
        pos = random_pos(bounds)
        rad = random.choices(cls.FOOD_SIZES)[0]
        col = random_color()
        return cls(pos, rad, col)
