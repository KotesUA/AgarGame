class Chunk:
    def __init__(self, players=None, cells=None):
        players = list() if players is None else players

        cells = list() if cells is None else cells
        self.players = players
        self.cells = cells
