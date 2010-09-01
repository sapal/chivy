# coding=utf-8

import game
import random

class Controller(object):
    def __init__(self,game=None):
        if game:
            self._game = game
        else:
            self.simpleGame()
    def simpleGame(self, players=2, seed=random.randint(1,10000)):
        b = game.Board()
        b.generateBoard("T+LI"*10*players,seed)
        colors = ["red","blue","green","cyan","black","white","purple"]
        random.shuffle(colors)
        playerList = [ game.Player(b,colors[i],"Player {0}".format(i)) for i in range(players)]
        self._game = game.Game(board=b, players=playerList)
    def setGame(self,game):
        self._game = game
    @property
    def game(self):
        return self._game
    def sendInput(self,playerId,action):
        self._game.sendInput(playerId,action)
