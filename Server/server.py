import pickle
import socketserver
import time
from typing import Dict, Tuple

import pygame

from AgarLib import Model, Player

bounds = (5000, 5000)
model = Model(list(), bounds=bounds)
model.spawn_cells(5000)
clients: Dict[str, Player] = dict()


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
            mouse: Tuple[float, float] = data['mouse_pos']
            keys = data['keys']

            player = clients[self.client_address]
            model.leaderboard[player.id] = {'nick': player.nick, 'score': player.score()}

            top_10 = sorted(model.leaderboard.items(), key=lambda p: p[1]['score'], reverse=True)[:10]
            leaderboard = [{'nick': p['nick'], 'score': p['score'], 'you': player.id == id_} for id_, p in top_10]

            if player.alive and player.end_time < time.time():
                player.alive = False
                model.players.remove(player)

            if player.alive:
                for key in keys:
                    if key == pygame.K_SPACE:
                        model.split(player, mouse[0])
                    elif key == pygame.K_w:
                        model.shoot(player, mouse[0])

                model.update_velocity(player, *mouse)
                model.update()
                model_info = model.get_info(player.center())
                data = pickle.dumps({'model': model_info, 'leader_board': leaderboard})
                socket = self.request[1]
                socket.sendto(data, self.client_address)
            else:
                model.remove_player(player)
                socket = self.request[1]
                data = pickle.dumps({'model': None, 'leader_board': leaderboard})
                socket.sendto(data, self.client_address)


def start(host='localhost', port=9999):
    with socketserver.UDPServer((host, port), Handler) as server:
        print(f'Started server {host}:{port}')
        server.serve_forever()


if __name__ == '__main__':
    start()
