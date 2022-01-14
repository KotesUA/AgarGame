import logging
import time
import itertools

from AgarLib.cell import Cell
from AgarLib.chunk import Chunk


class Model:
    ROUND_TIME = 600

    def __init__(self, players=None, cells=None, bounds=(5000, 5000), chunk_size=500):
        players = list() if players is None else players
        cells = list() if cells is None else cells

        self.bounds = bounds
        self.chunk_size = chunk_size
        self.chunks = list()

        for i in range((self.bounds[0] * 2) // chunk_size + 1):
            self.chunks.append(list())
            for j in range((self.bounds[1] * 2) // chunk_size + 1):
                self.chunks[-1].append(Chunk())

        for player in players:
            self.add_player(player)

        for cell in cells:
            self.add_cell(cell)

        self.round_start = time.time()

    @property
    def cells(self):
        cells = list()
        for line in self.chunks:
            for chunk in line:
                cells.extend(chunk.cells)
        return cells

    @property
    def players(self):
        players = list()
        for line in self.chunks:
            for chunk in line:
                players.extend(chunk.players)
        return players

    def update_velocity(self, player, angle, speed):
        player.update_velocity(angle, speed)

    def shoot(self, player, angle):
        emitted_cells = player.shoot(angle)
        for cell in emitted_cells:
            self.add_cell(cell)
        logging.debug(f'{player} shot') if emitted_cells else logging.debug(f'{player} tried to shoot, but he cant')

    def split(self, player, angle):
        self.remove_player(player)
        new_cells = player.split(angle)
        self.add_player(player)
        logging.debug(f'{player} split') if new_cells else logging.debug(f'{player} tried to split, but he cant')

    def update(self):
        self.update_round()
        self.update_cells()
        self.update_players()

    def update_round(self):
        if time.time() - self.round_start >= self.ROUND_TIME:
            logging.debug(f'New round started')
            self.reset()
            self.round_start = time.time()

    def update_cells(self):
        for cell in self.cells:
            self.remove_cell(cell)
            self.bound_cell(cell)
            self.add_cell(cell)

    def update_players(self):
        seen_players = self.players
        for player in seen_players:
            self.remove_player(player)
            player.move()
            self.bound_player(player)
            self.add_player(player)

            chunks = self._seen_chunks(player.center())
            players = list()
            cells = list()
            for chunk in chunks:
                players.extend(chunk.players)
                cells.extend(chunk.cells)

            for cell in cells:
                killed = player.murder(cell)
                if killed:
                    logging.debug(f'{player} ate {killed}')
                    self.remove_cell(killed)
                    self.spawn_cells(1)

            for another_player in players:
                if player == another_player:
                    continue
                killed = player.murder(another_player)
                if killed:
                    if len(another_player.cells) == 1:
                        logging.debug(f'{player}ate {another_player}')
                        self.remove_player(another_player)
                        seen_players.remove(another_player)
                        another_player.remove_part(killed)
                    else:
                        logging.debug(f'{player} ate {another_player} part {killed}')

    def spawn_cells(self, amount):
        for _ in range(amount):
            self.add_cell(Cell.random_cell(self.bounds))

    def bound_cell(self, cell):
        cell.pos[0] = self.bounds[0] if cell.pos[0] > self.bounds[0] else cell.pos[0]
        cell.pos[0] = -self.bounds[0] if cell.pos[0] < -self.bounds[0] else cell.pos[0]
        cell.pos[1] = self.bounds[1] if cell.pos[1] > self.bounds[1] else cell.pos[1]
        cell.pos[1] = -self.bounds[1] if cell.pos[1] < -self.bounds[1] else cell.pos[1]

    def bound_player(self, player):
        for cell in player.cells:
            self.bound_cell(cell)

    def add_player(self, player):
        self._pos_to_chunk(player.center()).players.append(player)
        print(f'added player {player}')

    def add_cell(self, cell):
        self._pos_to_chunk(cell.pos).cells.append(cell)

    def remove_player(self, player):
        self._pos_to_chunk(player.center()).players.remove(player)

    def remove_cell(self, cell):
        self._pos_to_chunk(cell.pos).cells.remove(cell)

    def get_info(self, pos):
        chunks = self._seen_chunks(pos)
        players = list()
        cells = list()

        for chunk in chunks:
            players.extend(chunk.players)
            cells.extend(chunk.cells)

        model = Model(players, cells, self.bounds, self.chunk_size)
        model.round_start = self.round_start
        return model

    def reset(self):
        for player in self.players:
            player.reset()

    def _pos_to_chunk(self, pos):
        chunk_pos = self._chunk_pos(pos)
        return self.chunks[chunk_pos[0]][chunk_pos[1]]

    def _chunk_pos(self, pos):
        return [int((pos[0] + self.bounds[0]) // self.chunk_size), int((pos[1] + self.bounds[1]) // self.chunk_size)]

    def _seen_chunks(self, pos):
        chunks = list()
        chunk_pos = self._chunk_pos(pos)
        for diff in itertools.product([-1, 0, 1], repeat=2):
            pos = [chunk_pos[0] + diff[0], chunk_pos[1] + diff[1]]
            if 0 <= pos[0] < len(self.chunks) and 0 <= pos[1] < len(self.chunks[0]):
                chunks.append(self.chunks[pos[0]][pos[1]])
        return chunks
