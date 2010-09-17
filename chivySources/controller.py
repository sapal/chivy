# coding=utf-8

import ai
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
from translation import gettext as _

class Controller(object):
    def __init__(self,game=game.Game.simpleGame()):
        self._game = game
        self.clients = []
        self.controlPlayers = list(game.players.keys())
        self.bots = []
        for name in self.randomBotNames(config.bots):
            self.addBot(name)

    def randomBotNames(self, count):
        return random.sample([name for name in config.botNames if name not in [p.name for p in self.game.players.values()]], count)

    def addBot(self, name=None, color=None):
        """Passing None for name or color will result in random one."""
        if name is None:
            name = self.randomBotNames(1)[0]
        id = self.game.addPlayer(name,color, isBot=True)
        self.bots.append(ai.ProximityAI(self, id))

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
        self.bots[:] = [ b for b in self.bots if b.playerID in self._game.players ]
        for b in self.bots:
            b.update(dt)

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
        self.onFail = onFail
        self.onSuccess = onSuccess
        self.gameReady = False
        self.playersReady = False
        self.Connect((host, port))
        print(_("Connecting..."))
        super(NetworkedController, self).__init__()
        self._game = game.Game(players=[],board=game.Board((1,1),""))
        self.controlPlayers = []
        self.lastUpdate = time()
        self.lastGameUpdate = time()
        connection.Send({"action":"requestPlayers", "players":players, "bots":False})
        connection.Pump()
        self.Pump()

    def addBot(self, name=None, color=None):
        if name is None:
            name = self.randomBotNames(1)[0]
        connection.Send({"action":"requestPlayers", "players":[{"name":name, "color":color}], "bots":True})

    @property
    def ready(self):
        return self.playersReady and self.gameReady

    def sendInput(self,playerId,action):
        #Controller.sendInput(self,playerId,action)
        connection.Send({"action":"sendInput", "playerId":playerId, "inputAction":action})
        connection.Pump()
        self.Pump()

    def Network_error(self,data):
        print(_("error: {0}").format(data['error'][1]))
        connection.Close()
        
    def Network_disconnected(self,data):
        print(_("Disconnected."))
        self.onFail()

    def Network_controlPlayers(self,data):
        print(_("Controlling players: {0}").format(data["players"]))
        if data["bots"]:
            print(_("Adding bot"))
            self.bots.extend([ ai.ProximityAI(self, id) for id in data["players"]])
        else:
            self.controlPlayers.extend(data["players"])
            for c in self.clients:
                c.controlPlayers = self.controlPlayers
            #if self.gameReady and not self.playersReady and self.onSuccess:
            #    self.onSuccess()
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
            super(NetworkedController, self).update(t - self.lastUpdate)
            self.lastUpdate = t
            #print("update({0:.2f})".format(self._game.time))
        connection.Pump()
        self.Pump()

    def Network_gameUpdate(self,data):
        t = self._game.time
        self._game = pickle.loads(data['game'])
        if abs(t-self._game.time) > 0.1: 
            print(_("lag:{0:.2f}s").format(t - self._game.time))
        self.lastUpdate = time()
        self.lastGameUpdate = time()
        if not self.gameReady and self.playersReady and self.onSuccess:
            self.onSuccess()
            self.gameReady = True

    def Network_lightGameUpdate(self,data):
        self._game.lightUnpickle(data['game'])

    def end(self):
        connection.Close()

if __name__=="__main__":
    import start
    start.startClient(sys.argv[1:])
    
