# coding=utf-8
from __future__ import division,print_function
import random
import kinds
import pickle

class GameObject(object):
    """Base class for other objects in game."""
    def __init__(self,position=(0,0),rotation=0):
        self.position = position
        self.rotation = rotation
    @property
    def x(self):
        return self.position[0]
    @property
    def y(self):
        return self.position[1]


class BoardTile(GameObject):
    """Class descripting single board-tile.
    
    position - position on board (x,y) - (0,0) is lower left corner
    upSide - rotation of tile (witch of the sides is facing NORTH - one of BoardTile.directions)
    kind - one of BoardTile.kinds
    border - True means that this BoardTile is on border of the board and nothing should be placed here.
    """
    """Directions:"""
    directions = (NORTH,WEST,SOUTH,EAST) = range(4)
    """Deltas (dx,dy) for each direction:"""
    delta = [(0,1), (-1,0), (0,-1), (1,0)]
    """ Kind description: (canGo [NORTH,WEST,SOUTH,EAST] for tile with rotation == NORTH)"""
    kinds = {"I":[True,False,True,False], 
            "T":[False,True,True,True], 
            "+":[True,]*4, 
            "L":[True,False,False,True],
            ".":[False,]*4,
            "U":[True,False,False,False]}
    @staticmethod
    def reverseDirection(dir):
        return (dir+2)%4
    
    def __init__(self,position=(0,0),upSide=0,kind=".",border=False):
        GameObject.__init__(self,position)
        self.kind = kind
        self.upSide = upSide
        self.border = border

    def lightPickle(self):
        return pickle.dumps((self.position, self.upSide, self.kind, self.border),-1)
    @staticmethod
    def lightUnpickle(pickleString):
        pos, up, kind, border = pickle.loads(pickleString)
        return BoardTile(pos, up, kind, border)

    def canGo(self,direction):
        """Checks if it is possible to move in "direction" from this tile."""
        return BoardTile.kinds[self.kind][(direction+self.upSide)%4]

    def getRotation(self):
        return 90*self.upSide
    def setRotation(self,rotation):
        self.upSide = int(round(rotation/90))%4
    rotation = property(getRotation,setRotation)

class Board(object):
    """Class representing board.
    
    dimensions = (width,height)
    tiles - dictionary: (x,y) -> BoardTile
    """
    def __init__(self, dimensions=(1,1),tiles=""):
        """Creates board."""
        self.randomState = random.getstate()
        self.dimensions = dimensions
        self.tilesFromString(tiles)

    @property
    def random(self):
        random.setstate(self.randomState)
        random.randint(0,1)
        self.randomState = random.getstate()
        return random

    def lightPickle(self):
        return pickle.dumps((self.randomState, self.tiles, self.dimensions),-1)

    @staticmethod
    def lightUnpickle(pickleString):
        b = Board()
        b.randomState, b.tiles, b.dimensions = pickle.loads(pickleString)
        return b

    def tilesFromString(self,s):
        """Creates array of tiles (self.tiles) from string s.
        Board description string is height lines with 2*width characters each.
        Each tile is represented by 2 characters: kind and upSide (0,1,2,3).
        Kind = '_' means that there is no tile on that position.
        If upSide is > 3 then tile is on border
        """
        if not s:
            s = ((".0"*self.width)+'\n')*self.height
        rows = list(reversed(s.split()))
        self.dimensions = (len(rows[0])//2,len(rows))
        self.tiles = {}
        for x in range(self.width):
            for y in range(self.height):
                k,u = rows[y][2*x],int(rows[y][2*x+1])
                b = (u>3)
                u %= 4
                if k != '_':
                    self.tiles[(x,y)] = BoardTile((x,y),u,k,b)
    def generateBoard(self,tiles,seed=0):
        que = [(0,0)]
        self.tiles = {}
        self.random.seed(seed)
        tiles = list(tiles)
        self.random.shuffle(tiles)
        for t in tiles:
            self.random.shuffle(que)
            while que:
                if que[-1] in self.tiles.keys():
                    que.pop()
                else:break
            if not que:break
            pos = que.pop()
            dirs = list(BoardTile.directions)
            self.random.shuffle(dirs)
            for d in dirs:
                self.tiles[pos] = BoardTile(pos,0,'+')
                if self.getTile(pos,d) or pos == (0,0):
                    for up in dirs:
                        self.tiles[pos] = BoardTile(pos,up,t)
                        if self.getTile(pos,d):
                            break
                    break
            for d in dirs:
                if self.getTile(pos,d) is None:
                    x,y = pos
                    dx,dy = BoardTile.delta[d]
                    #print("dodaję d({0},{1})".format(dx,dy))
                    que.append((x+dx,y+dy))
            #print("t:{t},kind:{k} pos:{pos} up:{up}".format(t=t,pos=pos,up=self.tiles[pos].upSide,k=self.tiles[pos].kind))
        for (x,y) in que:
            if (x,y) not in self.tiles:
                for k in ("T","I","L","U","."):
                    okKind = False
                    for u in BoardTile.directions:
                        self.tiles[x,y] = BoardTile((x,y),u,k,True)
                        okUp = True
                        for d in BoardTile.directions:
                            t = self.getTile((x,y),d)
                            if t and not t.border:
                                okUp = False
                                break
                        if okUp:
                            okKind = True
                            break
                    if okKind:
                        break
                            
        left = len(tiles)
        right = -left
        top = -left
        bottom = left
        for (x,y) in self.tiles.keys():
            left = min(left,x)
            right = max(right,x)
            top = max(top,y)
            bottom = min(bottom,y)
        #print("[{0},{1}] x [{2},{3}]".format(left,right,bottom,top))
        self.dimensions = max(0,1+right-left),max(0,1+top-bottom)
        nTiles = {}
        for (x,y),t in self.tiles.items():
            nx,ny = x-left,y-bottom
            nTiles[nx,ny] = BoardTile((nx,ny),t.upSide,t.kind,t.border)
        self.tiles = nTiles

    def randomPosition(self):
        pos = [ p for p in self.tiles.keys() if not self.tiles[p].border]
        return self.random.choice(pos)
    def __repr__(self):
        resLst = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                if (x,y) in self.tiles:
                    t = self.tiles[x,y]
                    row.append(t.kind+str(t.upSide + 4*int(t.border)))
                else:
                    row.append('_0')
            resLst.append("".join(row))
        return "\n".join(reversed(resLst))

    def getTile(self,position,direction):
        """Returns tile at position = (x,y) if direction is None,
        or tile NORTH/WEST/SOUTH/EAST (according to direction) from this tile.

        Returns None if no such tile exists, and False if it cannot be reached from tile (x,y)."""
        try:
            x,y = position
            if direction is None:
                return self.tiles[x,y]
            dx,dy = BoardTile.delta[direction]
            #if x+dx < 0 or y+dy <0:
            #    return None
            if self.tiles[x,y].canGo(direction) and self.tiles[dx+x,dy+y].canGo(BoardTile.reverseDirection(direction)):
                return self.tiles[dx+x,dy+y]
            else:
                return False
        except BaseException,e:
            return None

    @property
    def width(self):
        return self.dimensions[0]
    @property
    def height(self):
        return self.dimensions[1]
    @staticmethod
    def _test():
        #print(Board(tiles="T1L2I1\n.0+4I2"))
        b = Board()
        b.generateBoard("T"*10+"+"*3)
        #print(b)
        import copy
        a = copy.deepcopy(b)
        a.tilesFromString(str(b))
        print(str(b) == str(a))
        #print(a)

class OooManAction(object):
    """ Base class for various actions.
    kind - one of ActionFactory.kinds
    """
    discardImpossible = True
    def __init__(self,oooMan,kind):
        """All derived classes should have constructor with this three parameters first."""
        self.startTime = 0
        self.progress = 0.0
        self.speed = 1.0
        self.oooMan = oooMan
        self.ended = False
        self.started = False
        self.kind = kind
        self.discarded = False

    def lightPickle(self):
        return pickle.dumps((self.startTime, self.progress, self.speed, self.ended, self.started, self.kind, self.discarded), -1)

    @staticmethod
    def lightUnpickle(pickleString,oooMan):
        a = OooManAction(oooMan,"")
        a.startTime, a.progress, a.speed, a.ended, a.started, a.kind, a.discarded = pickle.loads(pickleString)
        return a

    def start(self,time):
        self.startTime = time
        self.started = True
    def update(self,time):
        """This method should return if update was performed."""
        dt = time - self.startTime
        if (not self.started) or self.ended or (not self.canPerform()):
            return False
        else:
            self.progress = min(1.0,dt*self.speed)
        dt = time - self.startTime
        if self.progress == 1.0:
            self.end(time)
        return True
    def canPerform(self):
        return True
    def end(self,time):
        self.ended = True
        self.oooMan.position = self.getEndPosition()
        self.oooMan.rotation = self.rotate
        self.oooMan.actionEnded(time)

class OooManMoveRotate(OooManAction):
    """Move and rotate OooMan."""
    def __init__(self,oooMan,kind,move,rotate,relative):
        """
        if relative is True:
            move - True if oooMan should be moved forward, False otherwise
            rotate - rotation in degrees, ccw
        else:
            move - direction (NORTH, WEST, SOUTH, EAST)
            rotate - absolute rotation
        """
        OooManAction.__init__(self,oooMan,kind)
        self.move = move
        self.rotate = rotate
        self.startPosition = None
        self.startRotation = None
        self.relative = relative

    def lightPickle(self):
        return pickle.dumps((OooManAction.lightPickle(self), self.move, self.rotate, self.startPosition, self.startRotation, self.relative), -1)

    @staticmethod
    def lightUnpickle(pickleString,oooMan):
        atr = pickle.loads(pickleString)
        a = OooManAction.lightUnpickle(atr[0],oooMan)
        a.__class__ = OooManMoveRotate
        s, a.move, a.rotate, a.startPosition, a.startRotation, a.relative = atr
        return a

    def start(self,time):
        OooManAction.start(self,time)
        self.startPosition = self.oooMan.position
        self.startRotation = self.oooMan.rotation
        self.direction =  (4+int(round(self.oooMan.rotation/90.0))%4)%4
        if OooManAction.discardImpossible and not self.canPerform():
            self.discard()

    def discard(self):
        self.discarded = True
        self.roatate = 0
        self.relative = True
        self.move = None

    def update(self,time):
        #print((self.started,self.ended,self.canPerform(),self.getEndPosition()))
        if not OooManAction.update(self,time):
            return False
        sx,sy = self.startPosition
        ex,ey = self.getEndPosition()
        p = self.progress
        x,y = sx,sy
        if abs(ex-sx) > 0.01: x = sx*(1.0-p) + ex*p
        if abs(ey-sy) > 0.01: y = sy*(1.0-p) + ey*p
        self.oooMan.position = (x,y)
        r = self.startRotation + self.rotate
        self.oooMan.rotation = self.startRotation*(1.0-p) + r*p
        #print((self.startTime,time,self.progress))
        return True

    def getEndPosition(self):
        if not self.started:
            return self.startPosition
        x,y = self.startPosition
        x,y = int(round(x)),int(round(y))
        if self.relative:
            if not self.move:
                return self.startPosition
            tile = self.oooMan.board.getTile((x,y), self.direction)
            if not tile:
                return None
            return tile.position
        else:
            tile = self.oooMan.board.getTile((x,y), self.move)
            if not tile:
                return None
            return tile.position

    def canPerform(self):
        return not (self.getEndPosition() is None)

class ActionFactory(object):
    """Object used to create actions."""
    """Kinds of actions:"""
    kinds = (MOVE,ROTATE_CW,ROTATE_CCW,GO_NORTH,GO_WEST,GO_SOUTH,GO_EAST) = range(7)
    """Actions arguments:"""
    actionsConstructors = {
                MOVE: (OooManMoveRotate,{'move':True,'rotate':0,'relative':True}),
                ROTATE_CW: (OooManMoveRotate,{'move':False,'rotate':-90,'relative':True}), ROTATE_CCW: (OooManMoveRotate,{'move':False,'rotate':+90,'relative':True}), GO_NORTH: (OooManMoveRotate,{'move':BoardTile.NORTH,'rotate':0,'relative':False}), GO_WEST: (OooManMoveRotate,{'move':BoardTile.WEST,'rotate':0,'relative':False}),
                GO_SOUTH: (OooManMoveRotate,{'move':BoardTile.SOUTH,'rotate':0,'relative':False}),
                GO_EAST: (OooManMoveRotate,{'move':BoardTile.EAST,'rotate':0,'relative':False})
            }

    @staticmethod
    def createAction(oooMan,kind):
        actionC,kargs = ActionFactory.actionsConstructors[kind]
        return actionC(oooMan,kind,**kargs)


class OooMan(GameObject):
    """Class representing OooMan - player's character.

    kind - type of OooMan
    board - board on wich OooMan is
    """
    """Maximum number of queued actions:"""
    maxActions = 8
    """Types of OooMen: (dictionary: string->list of stirngs - OooMen eaten by this one)"""
    kinds = kinds.CLASSIC
    @staticmethod
    def create(player):
        kinds = list(OooMan.kinds.keys())
        for o in player.oooMen:
            if o.kind in kinds:
                kinds.remove(o.kind)
        k = player.board.random.choice(kinds)
        return OooMan(player.board.randomPosition(), 0, k, player)
    def __init__(self,position,rotation,kind,player):
        GameObject.__init__(self,position,rotation)
        self.kind = kind
        self.player = player
        self.board = player.board
        self.actionList = []
        self.size = 0.66
        self.alive = True
        self.dieProgress = 0
        self.dieStartTime = 0
        self.dieSpeed = 0.1
        self.canDie = False
    
    def lightPickle(self):
        s = self
        return pickle.dumps((s.position, s.rotation, s.kind, [(a.__class__, a.lightPickle()) for a in s.actionList], s.size, s.alive, s.dieProgress, s.dieStartTime, s.dieSpeed, s.canDie ), -1)
    @staticmethod

    def lightUnpickle(pickleString,player):
        arg = pickle.loads(pickleString)
        o = OooMan(arg[0], arg[1], arg[2], player)
        o.actionList = [ c.lightUnpickle(s,o) for c,s in arg[3] ]
        o.size, o.alive, o.dieProgress, o.dieStartTime, o.dieSpeed, o.canDie = arg[4:]
        return o

    def __str__(self):
        return str(self.position)+" "+self.kind

    def collide(self,gameObject):
        if gameObject is self:
            return False
        x,y = self.position
        ox,oy = gameObject.position
        #print("{0}\t{1}\t{2}".format(self,gameObject,(self.size**2, (ox-x)**2 , (oy-y)**2)))
        return (self.size**2 >= (ox-x)**2+(oy-y)**2)

    def collideOooMan(self,other,time):
        if not self.collide(other):
            return
        #print("COLLIDE!")
        if (other.player is not self.player) and other.kind in OooMan.kinds[self.kind]:
            other.die(time)
            self.player.score += 2

    def die(self,time):
        self.dieStartTime = time
        self.alive = False
        self.player.score -= 1

    def actionEnded(self,time):
        if self.actionList:
            self.actionList.pop(0)
            self.update(time)

    def addAction(self,kind):
        """kind should be one fo OooMan.actionKinds"""
        if len(self.actionList) >= OooMan.maxActions:
            return
        action = ActionFactory.createAction(self,kind)
        self.actionList.append(action)

    def update(self,time):
        if not self.alive:
            self.actionList = []
            self.dieProgress += self.dieSpeed*(time - self.dieStartTime)
        if self.actionList:
            a = self.actionList[0]
            if not a.started:
                a.start(time)
            a.update(time)

    def updateCanDie(self,activeOooMen):
        self.canDie = False
        for a in activeOooMen:
            if not a or a is self.player.activeOooMan:
                continue
            if self.kind in OooMan.kinds[a.kind]:
                self.canDie = True

    def removeAction(self):
        if self.actionList:
            self.actionList.pop()

class Player(object):
    """Class representing single player.
    
    name - player's name
    oooMen - list of player's OooMans
    activeOooMan
    color - player's color (string)
    """
    def __init__(self,board,color="red",name=""):
        self.name = name
        self.board = board
        self.oooMen = []
        self.color = color
        self.activeOooMan = None
        self.score = 0
        self.actions = {
                "goNorth": (self.addAction, {'kind':ActionFactory.GO_NORTH}),
                "goWest": (self.addAction, {'kind':ActionFactory.GO_WEST}),
                "goSouth": (self.addAction, {'kind':ActionFactory.GO_SOUTH}),
                "goEast": (self.addAction, {'kind':ActionFactory.GO_EAST}),
                "move": (self.addAction, {'kind':ActionFactory.MOVE}),
                "rotateCW": (self.addAction, {'kind':ActionFactory.ROTATE_CW}),
                "rotateCCW": (self.addAction, {'kind':ActionFactory.ROTATE_CCW}),
                "switchActive": (self.switchActiveOooMan, {})
                }

    def lightPickle(self):
        "Returns lightweight pickle of this player"
        activeIdx = -1
        if self.activeOooMan in self.oooMen:
            activeIdx = self.oooMen.index(self.activeOooMan)
        return pickle.dumps((self.name, [ o.lightPickle() for o in self.oooMen ], self.color, activeIdx, self.score), -1)

    @staticmethod
    def lightUnpickle(pickleString, board):
        arg = pickle.loads(pickleString)
        p = Player(board, arg[2], arg[0])
        p.oooMen = [ OooMan.lightUnpickle(o, p) for o in arg[1] ] 
        if arg[3] != -1:
            p.activeOooMan = p.oooMen[arg[3]]
        p.score = arg[4]
        return p

    @property
    def alive(self):
        return [o for o in self.oooMen if o.alive]

    def addOooMan(self):
        o = OooMan.create(self)
        self.oooMen.append(o)
        self.updateActiveOooMan()

    def updateActiveOooMan(self):
        if self.activeOooMan not in self.alive:
            self.activeOooMan = None
        if self.alive and not self.activeOooMan: 
            self.activeOooMan = self.alive[0]

    def removeOooMan(self,oooMan):
        self.oooMen.remove(oooMan)
        self.updateActiveOooMan()

    def switchActiveOooMan(self):
        self.updateActiveOooMan()
        if not self.activeOooMan:
            return
        alive = self.alive
        idx = alive.index(self.activeOooMan)
        self.activeOooMan = alive[(idx+1)%len(alive)]

    def update(self,time):
        for o in self.oooMen:
            o.update(time)
        self.oooMen[:] = [o for o in self.oooMen if not o.dieProgress >=1]
        self.updateActiveOooMan()
        while len(self.oooMen) < 3:
            self.addOooMan()

    def addAction(self,kind):
        """Adds action to active oooMan"""
        if self.activeOooMan:
            self.activeOooMan.addAction(kind)

    def removeAction(self):
        if self.activeOooMan:
            self.activeOooMan.removeAction()

    def sendInput(self,action):
        f,kwargs = self.actions[action]
        f(**kwargs)

class Game(object):
    """Class representing game
    
    board - Board
    players - dictionary  id -> Player
    time - in-game time
    """
    def _setAttr(self,kwargs,attrName,default):
        if attrName in kwargs.keys():
            self.__dict__[attrName] = kwargs[attrName]
        else:
            self.__dict__[attrName] = default

    def lightPickle(self):
        return pickle.dumps((self.time, [ (i, p.lightPickle()) for i, p in self.players.items()], self.board.lightPickle()), -1)

    def lightUnpickle(self,pickleString):
        print("Unpickle")
        self.time, pl , self.board = pickle.loads(pickleString)
        self.board = Board.lightUnpickle(self.board)
        self.players = {}
        for k,v in pl:
            self.players[k] = Player.lightUnpickle(v,self.board)

    def __init__(self,**kwargs):
        """Creates new Game.
        Possible kwargs:
        board - Board to be used in this game.
        players - Players to play the game (list of Players)."""
        self.time = 0
        self._setAttr(kwargs,"board",Board())
        self._setAttr(kwargs,"players",{})

    def update(self,dt):
        self.time += dt
        for p in self.players.values():
            p.update(self.time)
        oooMen = [o for p in self.players.values() for o in p.alive ]
        for man in oooMen:
            for other in oooMen:
                man.collideOooMan(other,self.time)
        activeOooMen = [p.activeOooMan for p in self.players.values()]
        for man in oooMen:
            man.updateCanDie(activeOooMen)

    def sendInput(self,playerId,action):
        self.players[playerId].sendInput(action)

    @staticmethod
    def simpleGame(players=2, seed=random.randint(1,10000)):
        b = Board()
        b.generateBoard("T+LI"*10*players,seed)
        colors = ["red","blue","green","cyan","black","white","purple"]
        random.seed(seed)
        random.shuffle(colors)
        playerDict = {} 
        for i in range(players):
            playerDict[i] = Player(b,colors[i],"Player {0}".format(i)) 
        return Game(board=b, players=playerDict)

if __name__ == "__main__":
    Board._test()

