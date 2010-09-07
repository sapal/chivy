# coding=utf-8
from __future__ import division,print_function
import random
import random as rand
import kinds
import pickle
import colors
import config

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
    items - list of Item
    itemNumber - target number of items (excluding teleports)
    teleports - number of teleports
    """
    def __init__(self, dimensions=(1,1), tiles="", itemNumber=4, seed=random.random()):
        """Creates board."""
        self.seed = seed
        self.dimensions = dimensions
        self.tilesFromString(tiles)
        self.items = []
        self.itemNumber = itemNumber

    @property
    def random(self):
        #random.setstate(self.randomState)
        random.seed(self.seed)
        self.seed = random.random()
        return random

    @property
    def teleportsPositions(self):
        return [t.position for t in self.items if t.kind[0:8] == "teleport"]
    @property
    def teleports(self):
        return len(self.teleportsPositions)

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
                    
    def generateBoard(self,tiles,seed=rand.random(),tileNumber=None, teleports=3):
        """If tileNumber is positive number, tiles is repeated
        to build a string which is tileNumber long."""
        if tileNumber and tileNumber>0:
            n = tileNumber
            l = len(tiles)
            t = [tiles for i in range(0,n,l)]
            tiles = ("".join(t))[:n]
        que = [(0,0)]
        self.tiles = {}
        self.seed = seed
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
        self.items[:] = []
        self.addAllTeleports(teleports)

    def addTeleports(self, kind, count):
        count = min(len(self.getNormalTiles()),count)
        pos = self.randomPositions(count, self.teleportsPositions)
        for p in pos:
            self.items.append(Teleport(p,kind))
        tel = [ t for t in self.items if t.kind == "teleport-"+kind]
        if tel:
            for i in range(len(tel)):
                tel[i-1].target = tel[i].position

    def addAllTeleports(self, count=3):
        while count*6 > len(self.getNormalTiles()):
            count -= 1
        for k in OooMan.kinds.keys():
            self.addTeleports(k, count)

    def update(self,time):
        for i in self.items:
            i.update(time)
        self.items[:] = [ i for i in self.items if not i.deleteMe ]
        if len(self.items) < self.teleports + self.itemNumber:
            self.items.extend(self.randomItems(self.teleports + self.itemNumber - len(self.items)))

    def randomItems(self, count):
        disallowed = set([t.position for t in self.items if t.kind[0:8] == "teleport"])
        if len(disallowed) >= len(self.getNormalTiles()):
            return []
        return [ ItemFactory.createItem(self.randomPosition(disallowed), self.random.choice(ItemFactory.kinds)) for i in range(count) ]

    def randomPosition(self, disallowed=[]):
        return self.randomPositions(1, disallowed)[0]

    def randomPositions(self, count, disallowed=[]):
        pos = [ p for p in self.tiles.keys() if not self.tiles[p].border and p not in disallowed]
        return self.random.sample(pos, count)

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

    def getNormalTiles(self):
        """Returns normal tiles (all but border tiles)"""
        return [ p for p in self.tiles.values() if not p.border ]

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

class Item(GameObject):
    def __init__(self, position):
        GameObject.__init__(self, position)
        self.size = 0.6
        self.kind = "item"
        self.deleteMe = False

    def update(self, time):
        pass

    def use(self, oooMan):
        pass

    def canUse(self,oooMan):
        return not self.deleteMe and oooMan.actionList and oooMan.actionList[0].kind == ActionFactory.USE_ITEM and oooMan.collide(self)

class Teleport(Item):
    def __init__(self, position, oooManKind):
        Item.__init__(self, position)
        self.oooManKind = oooManKind
        self.target = None
        self.kind = "teleport-"+oooManKind

    def canUse(self, oooMan):
        return self.oooManKind == oooMan.kind and Item.canUse(self,oooMan)

    def use(self, oooMan):
        if self.target:
            t = ActionFactory.createAction(oooMan, ActionFactory.TELEPORT)
            t.target = self.target
            oooMan.actionList[0] = t

class OwnedItem(Item):
    """Item that can be owned by player."""
    def __init__(self, position, activeTime=30, owner=None, *args, **kwargs):
        """All derived classes should have constructor like this."""
        Item.__init__(self, position)
        self.kind = "ownedItem"
        self.owner = owner
        self.activeTime = activeTime
        self.startTime = None
        self.args = args
        self.kwargs = kwargs

    def canUse(self, oooMan):
        return self.owner is None and Item.canUse(self, oooMan)
    
    def update(self, time):
        if self.startTime is None:
            self.startTime = time
        if self.startTime + self.activeTime <= time:
            #print("{0} + {1} >= {2}".format(self.startTime, self.activeTime, time))
            self.deleteMe = True

    def use(self, oooMan):
        oooMan.items.append(self.__class__(None, 10, oooMan, *(self.args), **(self.kwargs)))
        self.deleteMe = True

class SpeedBoots(OwnedItem):
    def __init__(self, position, activeTime=30, owner=None, *args, **kwargs):
        """possible kwargs:
        speed = 2 - player new speed
        """
        OwnedItem.__init__(self, position, activeTime, owner, *args, **kwargs)
        self.speed = 1.5
        self.kind = "speedBoots"
        if "speed" in kwargs:
            self.speed = kwargs["speed"]

    def owner_update(self, update, *args, **kwargs):
        a = self.owner.actionList
        if a and "speed" in dir(a[0]):
            s = a[0].speed
            a[0].speed= self.speed
        res = update(*args, **kwargs)
        if a and "speed" in dir(a[0]):
            a[0].speed = s
        return res

class Shield(OwnedItem):
    def __init__(self, position, activeTime=30, owner=None, *args, **kwargs):
        OwnedItem.__init__(self, position, activeTime, owner, *args, **kwargs)
        self.kind = "shield"

    def owner_die(self, die, *args, **kwargs):
        return False

class MasterSword(OwnedItem):
    def __init__(self, position, activeTime=30, owner=None, *args, **kwargs):
        OwnedItem.__init__(self, position, activeTime, owner, *args, **kwargs)
        self.kind = "masterSword"

    def owner_killsKinds(self, killsKinds, *args, **kwargs):
        return OooMan.kinds.keys()

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

    def start(self,time):
        self.startTime = time
        self.started = True
        if OooManAction.discardImpossible and not self.canPerform():
            self.discard()

    def update(self,time):
        """This method should return if update was performed."""
        if self.started:
            dt = time - self.startTime
            self.progress = min(1.0,dt*self.speed)
        if self.progress == 1.0 and not self.ended:
            self.end(time)
        if (not self.started) or self.ended or (not self.canPerform()):
            return False
        else:
            return True

    def discard(self):
        self.discarded = True

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
        self.startRotation = None
        self.relative = relative

    def start(self,time):
        self.startPosition = self.oooMan.position
        self.startRotation = self.oooMan.rotation
        self.direction =  (4+int(round(self.oooMan.rotation/90.0))%4)%4
        OooManAction.start(self,time)

    def discard(self):
        OooManAction.discard(self)
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

    def end(self, time):
        self.oooMan.position = self.getEndPosition()
        self.oooMan.rotation = self.rotate
        OooManAction.end(self, time)

class OooManUseItem(OooManAction):
    def canPerform(self):
        for i in self.oooMan.board.items:
            if i.canUse(self.oooMan):
                return True
        return False

    def start(self, time):
        OooManAction.start(self, time)
        for i in self.oooMan.board.items:
            if i.canUse(self.oooMan):
                i.use(self.oooMan)
                break

class OooManTeleport(OooManAction):
    def __init__(self, oooMan, kind, target=None):
        OooManAction.__init__(self, oooMan, kind)
        self.target = target

    def start(self, time):
        self.startPosition = self.oooMan.position
        OooManAction.start(self, time)

    def update(self, time):
        OooManAction.update(self, time)
        if self.target:
            if self.progress <=0.5:
                self.oooMan.position = self.startPosition
            else:
                self.oooMan.position = self.target

class ActionFactory(object):
    """Object used for creating actions."""
    """Kinds of actions:"""
    kinds = (MOVE,ROTATE_CW,ROTATE_CCW,GO_NORTH,GO_WEST,GO_SOUTH,GO_EAST,USE_ITEM,TELEPORT) = range(9)
    """Actions arguments:"""
    actionsConstructors = {
                MOVE: (OooManMoveRotate,{'move':True,'rotate':0,'relative':True}),
                ROTATE_CW: (OooManMoveRotate,{'move':False,'rotate':-90,'relative':True}), ROTATE_CCW: (OooManMoveRotate,{'move':False,'rotate':+90,'relative':True}), GO_NORTH: (OooManMoveRotate,{'move':BoardTile.NORTH,'rotate':0,'relative':False}), GO_WEST: (OooManMoveRotate,{'move':BoardTile.WEST,'rotate':0,'relative':False}),
                GO_SOUTH: (OooManMoveRotate,{'move':BoardTile.SOUTH,'rotate':0,'relative':False}),
                GO_EAST: (OooManMoveRotate,{'move':BoardTile.EAST,'rotate':0,'relative':False}),
                USE_ITEM: (OooManUseItem,{}),
                TELEPORT: (OooManTeleport,{})
            }

    @staticmethod
    def createAction(oooMan,kind):
        actionC,kargs = ActionFactory.actionsConstructors[kind]
        return actionC(oooMan,kind,**kargs)

class ItemFactory(object):
    """Object used for creating items."""
    """Kinds of items:"""
    kinds = ("speedBoots","shield","masterSword")
    itemsConstructors = {
            "speedBoots": (SpeedBoots, {'activeTime':30, 'speed':1.5}),
            "shield": (Shield, {}),
            "masterSword": (MasterSword, {})
            }
    @staticmethod
    def createItem(position, kind):
        itemC,kwargs = ItemFactory.itemsConstructors[kind]
        return itemC(position, **kwargs)

def itemAffected(f, *args, **kwargs):
    def wrapped(*args, **kwargs):
        #print("{0}({1},{2})".format(f, args, kwargs))
        items = args[0].items
        for i in items:
            try:
                return  getattr(i,"owner_"+f.__name__)(f, *args, **kwargs)
            except Exception,e:
                pass
        return f(*args, **kwargs)
    return wrapped

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
        self.items = []

    def __str__(self):
        return str(self.position)+" "+self.kind
    
    @itemAffected
    def collide(self,gameObject):
        if gameObject is self:
            return False
        x,y = self.position
        ox,oy = gameObject.position
        #print("{0}\t{1}\t{2}".format(self,gameObject,(self.size**2, (ox-x)**2 , (oy-y)**2)))
        return (((self.size+gameObject.size)/2)**2 >= (ox-x)**2+(oy-y)**2)
    
    @itemAffected
    def collideOooMan(self,other,time):
        if not self.collide(other):
            return
        if (other.player is not self.player) and other.kind in self.killsKinds():
            if other.die(time):
                self.kill()

    @itemAffected
    def killsKinds(self):
        return OooMan.kinds[self.kind]

    @itemAffected
    def kill(self):
        self.player.score += 2

    @itemAffected
    def die(self,time):
        self.dieStartTime = time
        self.alive = False
        self.player.score -= 1
        return True

    @itemAffected
    def actionEnded(self,time):
        if self.actionList:
            self.actionList.pop(0)
            self.update(time)

    @itemAffected
    def addAction(self,kind):
        """kind should be one fo OooMan.actionKinds"""
        if len(self.actionList) >= OooMan.maxActions:
            return
        action = ActionFactory.createAction(self,kind)
        self.actionList.append(action)

    @itemAffected
    def update(self,time):
        if not self.alive:
            self.actionList[:] = []
            self.items[:] = []
            self.dieProgress += self.dieSpeed*(time - self.dieStartTime)
        if self.actionList:
            a = self.actionList[0]
            if not a.started:
                a.start(time)
            a.update(time)
        for i in self.items:
            i.update(time)
        self.items[:] = [ i for i in self.items if not i.deleteMe ]

    @itemAffected
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
                "switchActive": (self.switchActiveOooMan, {}),
                "useItem": (self.addAction, {'kind':ActionFactory.USE_ITEM})
                }

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

    def __init__(self, **kwargs):
        """Creates new Game.
        Possible kwargs:
        board - Board to be used in this game.
        players - Players to play the game (list of Players)."""
        self.time = 0
        self._setAttr(kwargs,"board",Board())
        self._setAttr(kwargs,"players",{})

    def update(self,dt):
        self.time += dt
        self.board.update(self.time)
        for p in self.players.values():
            p.update(self.time)
        oooMen = [o for p in self.players.values() for o in p.alive ]
        for man in oooMen:
            for other in oooMen:
                man.collideOooMan(other,self.time)

    def sendInput(self,playerId,action):
        self.players[playerId].sendInput(action)

    def addPlayer(self, name=None, color=None):
        """Returns created player id.
        name = None or color = None indicates that a random one
        should be used."""
        playerId = 0
        while playerId in self.players:
            playerId += 1
        if color is None or color in [p.color for p in self.players.values()]:
            color = random.choice([ k for k in colors.colors.keys() if k not in [p.color for p in self.players.values()] ])
        if name is None:
            name = random.choice([ n for n in config.samplePlayerNames if n not in [p.name for p in self.players.values()] ])
        self.players[playerId] = Player(self.board, color, name)
        return playerId

    @staticmethod
    def simpleGame(players=2, seed=random.randint(1,10000)):
        random.seed(seed)
        b = Board()
        b.generateBoard("T+LI"*10*players,seed)
        col = list(colors.colors.keys())
        random.shuffle(col)
        playerDict = {} 
        for i in range(players):
            playerDict[i] = Player(b,col[i],"Player {0}".format(i)) 
        return Game(board=b, players=playerDict)

    @staticmethod
    def gameFromConfig(board=None, players=None):
        """Passing non-None argument will override config"""
        if board is None:
            board = Board(itemNumber=config.itemNumber)
            board.generateBoard(config.tiles, tileNumber=config.tileNumber, teleports=config.teleports)
        g = Game(board=board)
        if players is None:
            players = config.players
        for p in players:
            if p.playing:
                g.addPlayer(p.name, p.color)
        return g

if __name__ == "__main__":
    Board._test()

