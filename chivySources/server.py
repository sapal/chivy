# coding=utf-8
import sys
import game
from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from time import sleep, localtime
from pyglet import clock
from optparse import OptionParser
from multiprocessing import Queue
import random
import colors
import pickle
import methodPickle
from translation import gettext as _

class ClientChannel(Channel):
    def Close(self):
        players = self.playerMap[self]
        print(_("Connection end (disconnected players: {0})").format(u", ".join([ unicode(self.game.players[p].name,"utf-8") for p in players])))
        for p in players:
            del self.game.players[p]

    def Network(self,data):
        #print()
        pass

    def Network_sendInput(self,data):
        #print("{0:.2f}:{1}".format(self.game.time, data))
        data["time"] = self.game.time
        self.server.sendToAll(data,True)
        self.game.sendInput(data["playerId"],data["inputAction"])

    def Network_requestPlayers(self,data):
        players = data["players"]
        print(_(u"New players: {0}").format(u", ".join([unicode(p["name"],"utf-8") for p in players])))
        playersId = []
        for p in players:
            try:
                playerId = self.game.addPlayer(name=p["name"], color=p["color"], isBot=data["bots"], speed=p["speed"])
                self.playerMap[self].append(playerId)
                playersId.append(playerId)
            except Exception,e:
                print(repr(e))
                break
        self.Send({"action":"controlPlayers", "players":playersId, "bots":data["bots"]})
        self.server.sendToAll(self.server.gameUpdate(),True)

class OooServer(Server):
    channelClass = ClientChannel
    NIL = -1
    def __init__(self, *args, **kwargs):
        """Possible kwargs:
        game
        inQueue - queue for input commands
        """
        if "game" not in kwargs:
            board = game.Board()
            board.generateBoard("TT++LI"*10,random.randint(0,123123))
            self.game = game.Game(board=board)
        else:
            self.game = kwargs["game"]
            del kwargs["game"]
        if "inQueue" in kwargs:
            self.inQueue = kwargs["inQueue"]
            del kwargs["inQueue"]
        else:
            self.inQueue = None
        Server.__init__(self, *args, **kwargs)
        self.clients = {}
        self.dt = 0
        self.endPlease = False

    def Connected(self, channel, addr):
        print("{0} connected".format(addr))
        channel.__dict__["game"] = self.game
        channel.__dict__["server"] = self
        channel.__dict__["playerMap"] = self.clients
        channel.Send(self.gameUpdate())
        channel.Pump()
        self.clients[channel] = []

    def updateDt(self,dt):
        self.dt = dt

    def sendToAll(self,data,force=False):
        clients = list(self.clients.keys())
        random.shuffle(clients)
        for c in clients:
            if force or not c.producer_fifo:
                #print("send")
                c.Send(data)
                c.Pump()
            #else:print("not send")
            
    def gameUpdate(self):
        #print("{0:.2f}".format(self.game.time))
        return {"action":"gameUpdate", "game":pickle.dumps(self.game,-1)}

    def lightGameUpdate(self):
        return {"action":"lightGameUpdate", "game":self.game.lightPickle()}

    def Launch(self):
        if not self.endPlease:print(_("Server started"))
        clock.set_fps_limit(100)
        clock.schedule(self.updateDt)
        clicks = 0
        while not self.endPlease:
            if self.inQueue and not self.inQueue.empty():
                a = self.inQueue.get()
                if a == "endPlease":
                    break
            clicks += 1
            clock.tick()
            self.game.update(self.dt)
            #print("update({0:.2f})".format(self.game.time))
            if clicks+1 >= clock.get_fps()*0.5:
                self.sendToAll(self.gameUpdate(),True)
                clicks = 0
                #print(clock.get_fps())
            #else:
            #    self.sendToAll(self.lightGameUpdate())
            self.Pump()
    
if __name__=="__main__":
    import start
    start.startServer(sys.argv[1:])

