# coding=utf-8

import game
import gui
import random
import colors
import sys
import config
import pickle
import methodPickle
from pyglet import clock
from time import sleep,time
from optparse import OptionParser
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
    def update(self,dt):
        self._game.update(dt)

class NetworkedController(Controller,ConnectionListener):
    def __init__(self, host="localhost", port=9999, players={random.choice(config.samplePlayerNames):random.choice(colors.colors)}):
        Controller.__init__(self)
        self._game = game.Game(players=[],board=game.Board((1,1),""))
        self.Connect((host, port))
        self.controlPlayers = []
        self.ready = False
        self.lastUpdate = time()
        print("Connecting...")
        connection.Send({"action":"requestPlayers", "players":players})
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

    def sendInputDt(self, dt, data):
        self._game.sendInput(data["playerId"], data["inputAction"])

    def Network_sendInput(self,data):
        #print("{0:.2f}:{1}".format(self._game.time, data))
        t = time()
        if self._game.time + t - self.lastUpdate < data["time"]:
            clock.schedule_once(self.sendInputDt, data["time"] - (self._game.time + t - self.lastUpdate), data=data)
        else:
            self.sendInputDt(0, data)

    def update(self,dt):
        t = time()
        #print((t,dt,t-self.lastUpdate))
        self._game.update(t - self.lastUpdate)
        self.lastUpdate = t
        #print("update({0:.2f})".format(self._game.time))
        connection.Pump()
        self.Pump()

    def Network_gameUpdate(self,data):
        t = self._game.time
        self._game = pickle.loads(data['game'])
        if abs(t-self._game.time) > 0.1: 
            print("lag:{0:.2f}s".format(t - self._game.time))
        self.lastUpdate = time()
        self.ready = True

    def Network_lightGameUpdate(self,data):
        self._game.lightUnpickle(data['game'])

if __name__=="__main__":
    import start
    start.startClient(sys.argv[1:])
    
