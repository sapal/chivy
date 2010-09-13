# coding=utf-8

import game
import random
from config import Config as config
class BaseAI(object):
    """Base class fo AI."""
   
    def __init__(self, controller,playerID):
        self.controller = controller
        self.playerID = playerID
        self.speed = 0.5+config.botSpeed*(1+0.2*(random.random()-0.5))
        self.time = 0

    def getTarget(self, oooMan):
        """Returns ending position of oooMan, if all movement actions are performed correctly.
        Note that this method doesn't check if actions are possible and dosen't include teleport actions."""
        x,y = oooMan.position
        for a in oooMan.actionList:
            #print("\t{0} ".format(a.kind))
            dKinds = {game.ActionFactory.GO_NORTH: game.BoardTile.delta[game.BoardTile.NORTH],
                game.ActionFactory.GO_WEST: game.BoardTile.delta[game.BoardTile.WEST],
                game.ActionFactory.GO_SOUTH: game.BoardTile.delta[game.BoardTile.SOUTH],
                game.ActionFactory.GO_EAST: game.BoardTile.delta[game.BoardTile.EAST]}
            if a.kind in dKinds:
                dx,dy = dKinds[a.kind]
                x,y = x+dx,y+dy
        #print((x,y))
        return x,y

    def update(self,dt):
        self.time += dt
        while self.time >= 1.0/self.speed:
            self.time -= 1.0/self.speed
            action = self.chooseAction()
            if action:
                self.sendInput(action)


    def chooseAction(self):
        """This method should return action that should be performed (one
        of Player().actions.keys()) or None if no action should be performed."""
        return None


    def goAction(self, direction):
        return ["goNorth", "goWest", "goSouth", "goEast"][direction]

    @property
    def player(self):
        return self.controller.game.players[self.playerID]
    @property
    def oooMen(self):
        return self.player.oooMen
    @property
    def activeOooMan(self):
        return self.player.activeOooMan

    @property
    def board(self):
        return self.controller.game.board

    def pos2int(self, pos):
        x,y = pos
        return (int(round(x)), int(round(y)))

    def intPosition(self, gameObject):
        return self.pos2int(gameObject.position)

    def sendInput(self, action):
        self.controller.sendInput(self.playerID, action)

class RandomAI(BaseAI):
    """Random walk AI."""
    
    def chooseAction(self):
        r = random.random()
        if r<0.2:
            return None
        elif r<0.4:
            return "switchActive"
        elif r<0.6:
            return "useItem"
        else:
            d = int(10*(r-0.6))
            return self.goAction(d)

class ProximityAI(BaseAI):
    """AI that chooses path based on how close oooMan is to other oooMen/items."""

    def __init__(self, controller, playerID):
        super(ProximityAI, self).__init__(controller, playerID)
        self.dist = {}
        self.distSource = None
        self.maxDist = 10

    def precomputeDist(self, start):
        self.distSource = start
        que = [start]
        self.dist = {start:0}
        teleports = {}
        for t in self.board.teleports:
            if t.oooManKind == self.activeOooMan.kind:
                teleports[t.position] = t
        #print("precomputeDist({0})".format(start))
        while que:
            p = que.pop(0)
            #print(p)
            if self.dist[p] >= self.maxDist:
                continue
            if p in teleports:
                t = teleports[p].target
                if t not in self.dist:
                    self.dist[t] = self.dist[p] +1
                    que.append(t)
            for d in game.BoardTile.directions:
                t = self.board.getTile(p, d)
                if t and t.position not in self.dist:
                    self.dist[t.position] = self.dist[p] +1
                    que.append(t.position)

    def getDistance(self, pos1, pos2):
        """The distance is computed for activeOooMan (only this kind of teleports is used)."""
        if pos2 == self.distSource:
            pos1, pos2 = pos2, pos1
        if pos1 != self.distSource:
            self.precomputeDist(pos1)
        if pos2 not in self.dist.keys():
            x1, y1 = pos1
            x2, y2 = pos2
            return abs(x1-x2) + abs(y1-y2)
        return self.dist[pos2]

    def scoreDist(self, position, gameObject):
        return 1.5**-self.getDistance(position, gameObject.position)

    def scoreOooMan(self, position, oooMan, otherOooMan):
        if otherOooMan.player is self.player:
            return 0.0
        if otherOooMan.kind in oooMan.killsKinds():
            #print("\tI will kill him.")
            return 2*self.scoreDist(position, otherOooMan)
        if oooMan.kind in otherOooMan.killsKinds():
            #print("\tHe will kill me.")
            return -self.scoreDist(position, otherOooMan)
        return 0.0

    def scoreItem(self, position, oooMan, item):
        if game.isTeleport(item):
            kind = item.oooManKind
            if kind == oooMan.kind:
                return 0.2*self.scoreDist(position, item)
            elif kind in oooMan.killsKinds():
                return 0.1*self.scoreDist(position, item)
            else: return -0.05*self.scoreDist(position, item)
        else: return 0.3*self.scoreDist(position, item)

    def score(self, position):
        #s = random.random()*0.5
        s = 0.0
        #print("position: {0} kind:{1}".format(position, self.activeOooMan.kind))
        for oooMan in [o for p in self.controller.game.players.values() for o in p.oooMen ]:
            s += self.scoreOooMan( position, self.activeOooMan, oooMan)
            #print("\tscore:{0} lastMan:{1}".format(s,oooMan.kind))
        for i in self.board.items:
            s += self.scoreItem(position, self.activeOooMan, i)
            #print("\tscore:{0} item:{1}".format(s, i.kind))
        return s


    def chooseAction(self):
        if not self.activeOooMan:
            return None
        if self.activeOooMan.actionList and [ m for m in self.oooMen if not m.actionList]:
            return "switchActive"
        elif len(self.activeOooMan.actionList)<3:
            bestScore = self.score(self.getTarget(self.activeOooMan))
            best = "useItem"
            pos = self.pos2int(self.getTarget(self.activeOooMan))
            for d in game.BoardTile.directions:
                t = self.board.getTile(pos, d)
                #print((d,t))
                if t:
                    s = self.score(t.position)
                    if s > bestScore:
                        best = self.goAction(d)
                        bestScore = s
            return best
        elif [ m for m in self.oooMen if len(m.actionList)<2]:
            return "switchActive"
        else:
            return None



