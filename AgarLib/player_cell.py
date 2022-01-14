import math
from operator import add, sub

from AgarLib.cell import Cell
from AgarLib.instruments import polar_to_cartesian, cartesian_to_polar
from AgarLib.interfaces import Killer


class PlayerCell(Cell, Killer):
    START_SIZE = 10
    SHOT_SIZE = 10
    SHOT_SPEED = 5
    SPLIT_SPEED = 5
    SPLIT_COOLDOWN = 300
    MIN_SPLIT = 100

    def __init__(self, pos, rad, col, angle=0, speed=0):
        super(PlayerCell, self).__init__(pos, rad, col)
        self.cooldown = self.SPLIT_COOLDOWN
        self.pool = 0

    def move(self):
        self.cooldown_tick()
        self.eat_pool()
        super(PlayerCell, self).move()

    def area(self):
        return super().area() + self.pool

    def murder(self, victim):
        return victim.die(self)

    def cooldown_tick(self):
        if self.cooldown > 0:
            self.cooldown -= 1

    def add_area(self, area):
        self.rad = math.sqrt((super().area()+area) / math.pi)

    def remove_area(self, area):
        self.rad = math.sqrt((super().area() + area) / math.pi)

    def eat_pool(self, lim = 0.1):
        if self.pool > 0:
            area = self.pool*lim
            self.pool *= 1 - lim
        else:
            area = 0
        return area

    def eat(self, victim):
        self.pool += victim.area()
        self.add_area(self.eat_pool())

    def can_emit(self,rad):
        return self.rad >= rad

    def can_shoot(self):
        return self.can_emit(self.SHOT_SIZE)

    def can_split(self):
        return self.can_emit(self.MIN_SPLIT)

    def emit(self, angle,speed,rad, ObjClass):
        obj = ObjClass([0,0],rad,self.col, angle,speed)
        self.remove_area(obj.area())
        dist = polar_to_cartesian(angle, self.rad + rad)
        obj.pos = list(map(add, self.pos,dist))
        return obj

    def shoot(self, angle):
        return self.emit(angle, self.SHOOT_SPEED, self.SHOT_SIZE, Cell)

    def split(self,angle):
        return self.emit(angle, self.SPLIT_SPEED, self.rad/2, PlayerCell)

    def run_from(self, cell):
        v = list(map(sub,self.pos, cell.pos))
        angle = cartesian_to_polar(*v)[0]
        intersection = self.rad + cell.rad - self.distance_to(cell)
        dxy = polar_to_cartesian(angle, intersection)
        self.pos = list(map(add,self.pos, dxy))