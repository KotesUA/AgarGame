import math
import time
import pygame


class Camera(object):
    def __init__(self, x, y, width, height):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.scale = 1

    def set_center(self, pos):
        self.x = pos[0] - self.width / 2
        self.y = pos[1] + self.height / 2

    def adjust(self, pos):
        return pos[0] * self.scale - self.x, self.y - pos[1] * self.scale


class View:
    BLACK = (0, 0, 0)
    GRAY = (50, 50, 50)
    LIGHT_GRAY = (128, 128, 128)
    PADDING = 5
    EXPIRE = 10

    def __init__(self, screen, model, player, leaderboard=None):
        self.screen = screen
        self.width, self.height = self.screen.get_size()
        self.model = model
        self.leaderboard = leaderboard or []
        self.player = player

        self.camera = Camera(0, 0, self.width, self.height)
        self.fps = 30
        self.clock = pygame.time.Clock()

        self.screen = pygame.display.set_mode((self.width, self.height))
        self.surface = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.surface.fill(View.LIGHT_GRAY)
        self.font = pygame.font.Font(pygame.font.get_default_font(), 20)

    def redraw(self):
        self.camera.set_center(self.player.center())
        self.screen.fill(View.BLACK)
        self.draw_grid()

        for cell in self.model.cells:
            self.draw_cell(cell)

        for player in self.model.players:
            self.draw_player(player)

        self.draw_hud((10, 10))
        self.draw_message()
        pygame.display.flip()

    def draw_grid(self, step=50):
        size = self.model.bounds[0]
        for i in range(-size, size + step, step):
            start = (-size, i)
            end = (size, i)
            pygame.draw.line(self.screen, View.GRAY, self.camera.adjust(start), self.camera.adjust(end), 2)
            pygame.draw.line(self.screen, View.GRAY, self.camera.adjust(start[::-1]), self.camera.adjust(end[::-1]), 2)

    def draw_cell(self, cell):
        pygame.draw.circle(self.screen, cell.col, self.camera.adjust(cell.pos), cell.rad)

    def draw_player(self, player):
        for cell in player.cells:
            self.draw_cell(cell)
            self.draw_text(self.screen, player.nick, self.camera.adjust(cell.pos), align_center=True)

    def draw_hud(self, padding):
        lines = list()
        lines.append(f'Time: {round(self.player.end_time - time.time(), 2)}')
        lines.append('')
        lines.append('Top players: ')
        for i, player in enumerate(self.leaderboard, 1):
            lines.append(f'{">" if player["you"] else ""}{i:02}. {player["nick"]}: {player["score"]:05.2f}')
        self.draw_item((self.width - 200, 15), lines, 10, padding)

    def draw_item(self, pos, lines, maxlength, padding):
        maxlength = max(map(lambda line: self.font.size(line)[0], lines))
        h = self.font.get_height()
        size = (maxlength + 2 * padding[0], h * len(lines) + 2 * padding[1])

        surface = pygame.transform.scale(self.surface, size)
        for i, line in enumerate(lines):
            self.draw_text(surface, line, (padding[0], padding[1] + h * i))
            self.screen.blit(surface, pos)

    def draw_message(self):
        if time.time() - self.model.round_start <= self.EXPIRE:
            self.draw_text(self.screen, "New round starting now!", [self.width // 2, self.height // 2*0.2], self.BLACK, align_center = True)

    def draw_text(self, surface, text, pos, col=BLACK, align_center=False):
        text_surface = self.font.render(text, True, col)
        pos = list(pos)
        if align_center:
            pos[0] -= text_surface.get_width() // 2
            pos[1] -= text_surface.get_height() // 2
        surface.blit(text_surface, pos)

    def start(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        self.model.shoot(self.player, self.mouse_polar()[0])
                    elif event.key == pygame.K_SPACE:
                        self.model.split(self.player, self.mouse_polar()[0])
                elif event.type == pygame.QUIT:
                    exit()
            self.model.update_velocity(self.player, *(self.mouse_polar()))
            self.model.update()
            self.redraw()
            self.clock.tick(5)

    def mouse_polar(self):
        x, y = pygame.mouse.get_pos()
        x -= self.width / 2
        y = self.height / 2 - y
        angle = math.atan2(y, x)
        speed = math.sqrt(x**2 + y**2)

        speed_bound = 0.8 * min(self.width / 2, self.height / 2)
        speed = 1 if speed >= speed_bound else speed / speed_bound
        return angle, speed

