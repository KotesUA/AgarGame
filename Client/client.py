import time
import pickle
import socket


import pygame

from AgarLib import View, Player, PlayerCell
from Client.client_menu import ClientMenu


class GameConnection:
    def __init__(self, screen):
        self.screen = screen
        self.player_id = None
        self.is_in_lobby = False
        self.host = None
        self.port = None
        self.address = None

    def connect(self, get_attributes):
        attributes = get_attributes
        self.address = attributes['addr']
        nick = attributes['nick']
        self.host, self.port = self.address.split(':')
        self.port = int(self.port)

        try:
            msg = pickle.dumps({
                'type': 1,
                'data': nick
            })
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(msg, (self.host, self.port))
            print(f'Sending {msg} to {self.address}')

            data = sock.recv(2**13)
            self.player_id = pickle.loads(data)
            print(f'Received {self.player_id} from {self.address}')

            view = View(self.screen, None, None)
            while True:
                keys = list()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        exit()
                    elif event.type == pygame.KEYDOWN:
                        keys.append(event.key)
                mouse_pos = view.mouse_polar()
                msg = pickle.dumps({
                    'type': 2,
                    'data': {
                        'mouse_pos': mouse_pos,
                        'keys': keys,
                    },
                })
                sock.sendto(msg, (self.host, self.port))

                data = sock.recv(2**16)
                msg = pickle.loads(data)

                view.player = None
                view.model = msg
                for pl in view.model.players:
                    if pl.id == self.player_id:
                        view.player = pl
                        break
                    if view.player is None:
                        print("Player was killed!")
                        return
                view.redraw()
            time.sleep(1/30)
        except socket.timeout:
            print('Server not responding')


def start(width=1920, height=1080):
    socket.setdefaulttimeout(2)

    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('agar.io clone by @kotes, @andreeewleonov, @FBISpy')

    connection = GameConnection(screen)
    menu = ClientMenu(width, height)
    menu.update_menu(connection.connect)
    clock = pygame.time.Clock()

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                exit()

            if menu.get_menu().is_enabled():
                menu.get_menu().draw(screen)
            menu.get_menu().update(events)
            pygame.display.flip()
            clock.tick(30)


if __name__ == '__main__':
    start()

