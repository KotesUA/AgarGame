import time
from typing import List, Tuple

import AgarLib
from AgarLib.instruments import get_velocity
from AgarLib.interfaces import Killer, Victim
from AgarLib.player_cell import PlayerCell


class Player(Killer, Victim):
    START_SIZE = 40
    LAST_ID = -1

    def __init__(self, nick: str, player_cell: PlayerCell, life_time: int = 300):
        self.id: int = self.create_id()
        self.nick: str = nick
        self.cells: List[PlayerCell] = [player_cell]
        self.alive: bool = True
        self.end_time: float = time.time() + life_time
        self.life_time: int = life_time

    def __repr__(self):
        return f'{self.__class__.__name__} || nick = {self.nick} || id = {self.id}'

    def move(self):
        for i, player_cell in enumerate(self.cells):
            player_cell.move()

            for another_cell in self.cells[i+1:]:
                if player_cell == another_cell or not player_cell.intersects(another_cell):
                    continue
                if player_cell.cooldown == 0 and another_cell.cooldown == 0:
                    player_cell.eat(another_cell)
                    self.cells.remove(another_cell)
                else:
                    player_cell.run_from(another_cell)

    def update_velocity(self, angle: float, speed: float):
        center = self.center()
        for cell in self.cells:
            rel_velocity = get_velocity(center, angle, speed, cell.pos)
            cell.update_velocity(*rel_velocity)

    def shoot(self, angle: float) -> List['AgarLib.Cell']:
        emitted = list()
        for cell in self.cells:
            if cell.can_shoot():
                emitted.append(cell.shoot(angle))
        return emitted

    def split(self, angle: float):
        emitted = list()
        for cell in self.cells:
            if cell.can_split():
                emitted.append(cell.split(angle))
        self.cells.extend(emitted)
        return emitted

    def center(self) -> Tuple[float, float]:
        x: float = sum(cell.pos[0] for cell in self.cells)
        y: float = sum(cell.pos[1] for cell in self.cells)
        center = (x/len(self.cells), y/len(self.cells))
        return center

    def score(self):
        return round(sum(cell.rad for cell in self.cells), 2)

    def die(self, killer):
        for cell in self.cells:
            killed = killer.murder(cell)
        return killed if killed else None

    def murder(self, victim: 'AgarLib.Cell'):
        for cell in self.cells:
            if not victim.vulnerable_time:
                killed = victim.die(cell)
                if killed:
                    cell.eat(killed)
                    return killed
            elif victim.vulnerable_time < time.time():
                victim.vulnerable_time = 0
        return None

    def reset(self):
        self.cells = self.cells[:1]
        self.cells[0].poll = 0
        self.cells[0].rad = self.START_SIZE

    @classmethod
    def create_id(cls) -> int:
        cls.LAST_ID += 1
        return cls.LAST_ID

    @classmethod
    def spawn(cls, nick, bounds) -> 'Player':
        player_cell = PlayerCell.random_cell(bounds)
        player_cell.rad = cls.START_SIZE
        return cls(nick, player_cell)
