# coding=utf-8
from __future__ import division,print_function
import random

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
            ".":[False,]*4}
    @staticmethod
    def reverseDirection(dir):
        return (dir+2)%4
    
    def __init__(self,position=(0,0),upSide=0,kind="."):
        GameObject.__init__(self,position)
        self.kind = kind
        self.upSide = upSide

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
    def __init__(self, dimensions=(8,8),tiles=""):
        """Creates board."""

        self.dimensions = dimensions
        self.tilesFromString(tiles)

    def tilesFromString(self,s):
        """Creates array of tiles (self.tiles) from string s.
        Board description string is height lines with 2*width characters each.
        Each tile is represented by 2 characters: kind and upSide (0,1,2,3)."""
        if not s:
            s = ((".0"*self.width)+'\n')*self.height
        rows = list(reversed(s.split()))
        self.dimensions = (len(rows[0])//2,len(rows))
        self.tiles = {}
        for x in range(self.width):
            for y in range(self.height):
                self.tiles[(x,y)] = BoardTile((x,y),int(rows[y][2*x+1]),rows[y][2*x])
    def generateBoard(self,tiles,seed=0):
        que = [(0,0)]
        self.tiles = {}
        random.seed(seed)
        tiles = list(tiles)
        random.shuffle(tiles)
        for t in tiles:
            random.shuffle(que)
            while que:
                if que[-1] in self.tiles.keys():
                    que.pop()
                else:break
            if not que:break
            pos = que.pop()
            dirs = list(BoardTile.directions)
            random.shuffle(dirs)
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
                self.tiles[x,y] = BoardTile((x,y),0,'.')
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
            nTiles[nx,ny] = BoardTile((nx,ny),t.upSide,t.kind)
        self.tiles = nTiles

    def randomPosition(self):
        pos = [ p for p in self.tiles.keys() if self.tiles[p].kind != '.']
        return random.choice(pos)
    def __repr__(self):
        resLst = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                if (x,y) in self.tiles:
                    row.append(self.tiles[(x,y)].kind+str(self.tiles[(x,y)].upSide))
                else:
                    row.append('.0')
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
        print(b)

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
        self.relative = relative
        self.discarded = False
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
        self.oooMan.position = (sx*(1.0-p) + ex*p, sy*(1.0-p) + ey*p)
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
                ROTATE_CW: (OooManMoveRotate,{'move':False,'rotate':-90,'relative':True}),
                ROTATE_CCW: (OooManMoveRotate,{'move':False,'rotate':+90,'relative':True}),
                GO_NORTH: (OooManMoveRotate,{'move':BoardTile.NORTH,'rotate':0,'relative':False}),
                GO_WEST: (OooManMoveRotate,{'move':BoardTile.WEST,'rotate':0,'relative':False}),
                GO_SOUTH: (OooManMoveRotate,{'move':BoardTile.SOUTH,'rotate':0,'relative':False}),
                GO_EAST: (OooManMoveRotate,{'move':BoardTile.EAST,'rotate':0,'relative':False})
            }
    def createAction(oooMan,kind):
        actionC,kargs = ActionFactory.actionsConstructors[kind]
        return actionC(oooMan,kind,**kargs)
    createAction = staticmethod(createAction)


class OooMan(GameObject):
    """Class representing OooMan - player's character.

    kind - type of OooMan
    board - board on wich OooMan is
    """
    """Maximum number of queued actions:"""
    maxActions = 8
    """Types of OooMen: (dictionary: string->list of stirngs - OooMen eaten by this one)"""
    kinds = {}
    @staticmethod
    def create(player):
        kinds = list(OooMan.kinds.keys())
        for o in player.oooMen:
            if o.kind in kinds:
                kinds.remove(o.kind)
        return OooMan(player.board.randomPosition(),0,random.choice(kinds),player)
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

class Game(object):
    """Class representing game
    
    board - Board
    players - list of Players
    """
    def _setAttr(self,kwargs,attrName,default):
        if attrName in kwargs.keys():
            self.__dict__[attrName] = kwargs[attrName]
        else:
            self.__dict__[attrName] = default
    def __init__(self,**kwargs):
        """Creates new Game.
        Possible kwargs:
        board - Board to be used in this game.
        players - Players to play the game (list of Players)."""
        self._setAttr(kwargs,"board",Board())
        self._setAttr(kwargs,"players",[])

    def update(self,time):
        for p in self.players:
            p.update(time)
        oooMen = [o for p in self.players for o in p.alive ]
        for man in oooMen:
            for other in oooMen:
                man.collideOooMan(other,time)
        activeOooMen = [p.activeOooMan for p in self.players]
        for man in oooMen:
            man.updateCanDie(activeOooMen)

if __name__ == "__main__":
    Board._test()

