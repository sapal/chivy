# coding=utf-8

import game
import random
import colors
import sys
import pickle
import methodPickle
from time import sleep
from PodSixNet.Connection import connection, ConnectionListener

class Controller(object):
    def __init__(self,game=game.Game.simpleGame()):
        self._game = game
        self.clients = []
        self.controlPlayers = list(range(len(game.players)))
    def setGame(self,game):
        self._game = game
    @property
    def game(self):
        return self.getGame()
    def getGame(self):
        return self._game
    def sendInput(self,playerId,action):
        self._game.sendInput(playerId,action)
    def update(self):
        pass

class NetworkedController(Controller,ConnectionListener):
    def __init__(self, host="localhost", port=9999):
        Controller.__init__(self)
        self._game = game.Game(players=[],board=game.Board((1,1),""))
        self.Connect((host, port))
        self.controlPlayers = []
        self.ready = False
        print("Connecting...")
        connection.Send({"action":"requestPlayers", "players":["Bob", "Alice"]})
        while not self.ready:
            connection.Pump()
            self.Pump()
            sleep(0.01)
        print("OK")

    def sendInput(self,playerId,action):
        #Controller.sendInput(self,playerId,action)
        connection.Send({"action":"sendInput", "playerId":playerId, "inputAction":action})
        connection.Pump()
        self.Pump()

    def Network_error(self,data):
        print("error: {0}".format(data['error'][1]))
        connection.Close()
        
    def Network_disconnected(self,data):
        print("Disconnected.")
        sys.exit()

    def Network_controlPlayers(self,data):
        self.controlPlayers = data["players"]
        for c in self.clients:
            c.controlPlayers = self.controlPlayers

    def update(self):
        connection.Pump()
        self.Pump()

    def Network_gameUpdate(self,data):
        self._game = pickle.loads(data['game'])
        self.ready = True

    def Network_lightGameUpdate(self,data):
        self._game.lightUnpickle(data['game'])

if __name__=="__main__":
    ctrl = NetworkedController()
    import gui
    c = gui.Client(ctrl)
    c.run()
