# coding=utf-8

import game
import gui
import random
import colors
import sys
import pickle
import methodPickle
from config import Config as config
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
    def __init__(self, host=None, port=9999, players=None, onFail=sys.exit, onSuccess=None):
        """Passing None for host or players defaults to 
        config.host and config.players.
        onFail is executed if it was impossible to estabilish connection.
        If connection has been successfully estabilished onSuccess is called."""
        if not host:
            host = config.host
        if players is None:
            players = [ {"name":p["name"], "color":p["color"]} for p in config.players if p["playing"]]
        Controller.__init__(self)
        self._game = game.Game(players=[],board=game.Board((1,1),""))
        self.onFail = onFail
        self.onSuccess = onSuccess
        self.Connect((host, port))
        self.controlPlayers = []
        self.gameReady = False
        self.playersReady = False
        self.lastUpdate = time()
        self.lastGameUpdate = time()
        print("Connecting...")
        connection.Send({"action":"requestPlayers", "players":players})
        connection.Pump()
        self.Pump()

    @property
    def ready(self):
        return self.playersReady and self.gameReady

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
        self.onFail()

    def Network_controlPlayers(self,data):
        print("Controling players:{0}".format(data["players"]))
        self.controlPlayers = data["players"]
        for c in self.clients:
            c.controlPlayers = self.controlPlayers
        if self.gameReady and not self.playersReady and self.onSuccess:
            self.onSuccess()
        self.playersReady = True

    def sendInputDt(self, dt, data, time):
        if time > self.lastGameUpdate:
            self._game.sendInput(data["playerId"], data["inputAction"])

    def Network_sendInput(self,data):
        #print("{0:.2f}:{1}".format(self._game.time, data))
        t = time()
        dt = t - self.lastUpdate
        gameT = self._game.time + dt
        if gameT < data["time"]:
            clock.schedule_once(self.sendInputDt, data["time"] - gameT, data=data, time=t+(data["time"] -gameT))
        else:
            self.sendInputDt(0, data,t)

    def update(self,dt):
        if self.ready:
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
        self.lastGameUpdate = time()
        if not self.gameReady and self.playersReady and self.onSuccess:
            self.onSuccess()
        self.gameReady = True

    def Network_lightGameUpdate(self,data):
        self._game.lightUnpickle(data['game'])

if __name__=="__main__":
    import start
    start.startClient(sys.argv[1:])
    
