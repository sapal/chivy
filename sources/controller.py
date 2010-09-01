# coding=utf-8

import game
import random
import sys
import pickle
import methodPickle
from PodSixNet.Connection import connection, ConnectionListener

class Controller(object):
    def __init__(self,game=game.Game.simpleGame()):
        self._game = game
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
        self.Connect((host, port))
        #connection.Send("hello!")
        print("hello!")

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

    def update(self):
        connection.Pump()
        self.Pump()

    def Network_update(self,data):
        print("update")
        self._game = pickle.loads(data['game'])

if __name__=="__main__":
    ctrl = NetworkedController()
    import gui
    c = gui.Client(ctrl)
    c.run()
