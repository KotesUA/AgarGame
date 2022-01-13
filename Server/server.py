import logging
import pickle
import socketserver

import pygame

from AgarLib import Model, Player, PlayerCell

bounds = (5000, 5000)
model = Model(list(), bounds=bounds)
model.spawn_cells(5000)
clients = dict()


class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        msg = pickle.loads(self.request[0])
        code = msg['type']
        data = msg['data']

        if code == 1:
            nick = data
            print(f'Received connection {nick}')
            new_player = Player.spawn(nick, bounds)
            data = pickle.dumps(new_player.id)
            socket = self.request[1]
            socket.sendto(data, self.client_address)
            print(f'Sent {nick} client info')

            clients[self.client_address] = new_player
            model.add_player(new_player)
        elif code == 2:
            mouse = data['mouse_pos']
            keys = data['keys']

            player = clients[self.client_address]

            for key in keys:
                if key == pygame.K_SPACE:
                    model.split(player, mouse[0])
                elif key == pygame.K_w:
                    model.shoot(player, mouse)

            model.update_velocity(player, *mouse)
            model.update()

            data = pickle.dumps(model.get_info(player.center()))
            socket = self.request[1]
            socket.sendto(data, self.client_address)


def start(host='localhost', port=9999):
    with socketserver.UDPServer((host, port), Handler) as server:
        print(f'Started server {host}:{port}')
        server.serve_forever()


if __name__ == '__main__':
    start()
