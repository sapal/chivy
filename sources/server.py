# coding=utf-8
import game
from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from time import sleep, localtime
from pyglet import clock
import random
import colors
import pickle
import methodPickle

class ClientChannel(Channel):
    def Close(self):
        players = self.playerMap[self]
        for p in players:
            del self.game.players[p]
        print("Connection end (players {0})".format(players))

    def Network(self,data):
        print(self.game.time)
        print(data)
        print()

    def Network_sendInput(self,data):
        self.server.sendToAll(data,True)
        self.game.sendInput(data["playerId"],data["inputAction"])

    def Network_requestPlayers(self,data):
        players = data["players"]
        print("requestPlayers({0})".format(players))
        for name in players:
            playerId = 0
            while playerId in self.game.players:
                playerId += 1
            color = random.choice([ k for k in colors.colors.keys() if k not in [p.color for p in self.game.players.values()] ])
            self.game.players[playerId] = game.Player(self.game.board, color, name)
            self.playerMap[self].append(playerId)
        self.Send({"action":"controlPlayers", "players":self.playerMap[self]})
        self.server.sendToAll(self.server.gameUpdate(),True)

class OooServer(Server):
    channelClass = ClientChannel
    NIL = -1
    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.clients = {}
        self.dt = 0
        board = game.Board()
        board.generateBoard("TT++LI"*10,random.randint(0,123123))
        self.game = game.Game(board=board)

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
        #print("gameUpdate")
        return {"action":"gameUpdate", "game":pickle.dumps(self.game,-1)}

    def lightGameUpdate(self):
        return {"action":"lightGameUpdate", "game":self.game.lightPickle()}

    def Launch(self):
        print("Server started")
        clock.set_fps_limit(100)
        clock.schedule(self.updateDt)
        clicks = 0
        while True:
            clicks += 1
            clock.tick()
            self.game.update(self.dt)
            if clicks+1 >= clock.get_fps():
                self.sendToAll(self.gameUpdate(),True)
                clicks = 0
                #print(clock.get_fps())
            #else:
            #    self.sendToAll(self.lightGameUpdate())
            self.Pump()
    
if __name__=="__main__":
    s = OooServer(localaddr=("localhost",9999))
    s.Launch()


