# coding=utf-8
import game
from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from time import sleep, localtime
from weakref import WeakKeyDictionary
from pyglet import clock
import pickle
import methodPickle

class ClientChannel(Channel):
    def Close(self):
        print("Connection end")

    def Network(self,data):
        print(data)

    def Network_sendInput(self,data):
        self.game.sendInput(data["playerId"],data["inputAction"])

class OooServer(Server):
    channelClass = ClientChannel
    def __init__(self, *args, **kwargs):
        Server.__init__(self, *args, **kwargs)
        self.clients = []
        self.dt = 0
        self.game = game.Game.simpleGame(1)

    def Connected(self, channel, addr):
        print("{0} connected".format(addr))
        channel.__dict__["game"] = self.game
        self.clients.append(channel)

    def updateDt(self,dt):
        self.dt = dt

    def Launch(self):
        print("Server started")
        clock.set_fps_limit(20)
        clock.schedule(self.updateDt)
        while True:
            clock.tick()
            print(clock.get_fps())
            self.game.update(self.dt)
            sGame = pickle.dumps(self.game,-1)
            m = {"action":"update", "game":sGame}
            for c in self.clients:
                c.Send(m)
                c.Pump()
            self.Pump()
    
if __name__=="__main__":
    s = OooServer(localaddr=("localhost",9999))
    s.Launch()


