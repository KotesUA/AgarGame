from AgarLib.instruments import get_velocity
from AgarLib.interfaces import Killer, Victim
from AgarLib.player_cell import PlayerCell


class Player(Killer, Victim):
    START_SIZE = 40
    LAST_ID = -1

    def __init__(self, nick, player_cell):
        self.id = self.create_id()
        self.nick = nick
        self.cells = [player_cell]

    def __repr__(self):
        return f'{self.__class__.__name__} || nick = {self.nick} || id = {self.id}'

    def move(self):
        for i, player_cell in enumerate(self.cells):
            player_cell.move()

            for another_cell in self.cells[:i+1]:
                if player_cell == another_cell or not player_cell.intersects(another_cell):
                    continue
                if player_cell.cooldown == 0 and another_cell.cooldown == 0:
                    player_cell.eat(another_cell)
                    self.cells.remove(another_cell)
                else:
                    player_cell.run_from(another_cell)

    def update_velocity(self, angle, speed):
        center = self.center()
        for cell in self.cells:
            rel_velocity = get_velocity(center, angle, speed, cell.pos)
            cell.update_velocity(*rel_velocity)

    def shoot(self, angle):
        emitted = list()
        for cell in self.cells:
            if cell.can_shoot():
                emitted.append(cell.shoot(angle))
            return emitted

    def split(self, angle):
        emitted = list()
        for cell in self.cells:
            if cell.can_split():
                emitted.append(cell.split(angle))
            return emitted

    def center(self):
        x = sum(cell.pos[0] for cell in self.cells)
        y = sum(cell.pos[1] for cell in self.cells)
        center = [x/len(self.cells), y/len(self.cells)]
        return center

    def score(self):
        return sum(cell.rad for cell in self.cells)

    def die(self, killer):
        for cell in self.cells:
            killed = killer.murder(cell)
            return killed if killed else None

    def murder(self, victim):
        for cell in self.cells:
            killed = victim.die(cell)
            if killed:
                cell.eat(killed)
                return killed
            return None

    def reset(self):
        self.cells = self.cells[:1]
        self.cells[0].poll = 0
        self.cells[0].rad = self.START_SIZE

    @classmethod
    def create_id(cls):
        cls.LAST_ID += 1
        return cls.LAST_ID

    @classmethod
    def spawn(cls, nick, bounds):
        player_cell = PlayerCell.random_cell(bounds)
        player_cell.rad = cls.START_SIZE
        return cls(nick, player_cell)
