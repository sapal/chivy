# coding=utf-8

from __future__ import division,print_function
import game
import config
import rabbyt
import sys
import os
import pyglet
import re
from pyglet import gl, clock, font
from pyglet.window import Window,key
from pyglet.text import Label,HTMLLabel

class MySprite(rabbyt.Sprite):
    def clear(self):
        self.rot = 0
        self.x = 0
        self.y = 0
        self.red = 1
        self.green = 1
        self.blue = 1
        self.alpha = 1
        self.scale = 1


class Camera(object):

    def __init__(self, win, position=(0,0), zoom = 1.0, follow=None):
        self.win = win
        self.zoom = zoom
        self.follow = follow
        self.position = position
        self.dimensions = (0,0,0,0)

    @property
    def x(self):
        s = config.spriteSize*self.zoom
        return self.position[0]*s

    @property
    def y(self):
        s = config.spriteSize*self.zoom
        return self.position[1]*s

    def update(self):
        if self.follow:
            self.position = self.follow.position

    def worldProjection(self):
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        w,h = config.screenSize
        gl.gluOrtho2D(
            (self.x - w/2)/self.zoom,
            (self.x + w/2)/self.zoom,
            (self.y - h/2)/self.zoom,
            (self.y + h/2)/self.zoom)
        x,y = self.position
        s = 2*config.spriteSize/self.zoom
        self.dimensions = (x-w/s, x+w/s, y-h/s, y+h/s)

    @property
    def left(self):
        return self.dimensions[0]
    @property
    def right(self):
        return self.dimensions[1]
    @property
    def bottom(self):
        return self.dimensions[2]
    @property
    def top(self):
        return self.dimensions[3]

    def hudProjection(self):
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.gluOrtho2D(0, self.win.width, 0, self.win.height)

class Client(object):
    """Client for viewing game."""
    def loadSpritesRegex(self,regexString):
        end = str(config.spriteSize)+".png"
        r = re.compile(regexString+end)
        self.loadSprites([ f[:f.rfind(end)] for f in os.listdir(config.imagesDir) if r.match(f)])
    def loadSprites(self,spriteList):
        for f in spriteList:
            self.sprites[f] = MySprite(config.imagesDir+os.sep+f+str(config.spriteSize)+".png")
            #print(f)

    def __init__(self,game):
        self.sprites = {}
        self.loadSprites(["tile.","tile+","tileL","tileI","tileT"])
        self.loadSprites(["glow"])
        self.loadSpritesRegex("OooMan.*")
        self.loadSpritesRegex("action.*")
        self.game = game
        clock.set_fps_limit(50)
        w,h = config.screenSize
        self.window = Window(width=w,height=h)
        self.window.set_caption("NoTitle!")
        self.window.on_close = sys.exit
        self.inputListener = InputListener()
        self.addKeyBindings()
        self.window.push_handlers(self.inputListener)
        rabbyt.set_default_attribs()
        bw,bh = self.game.board.dimensions
        self.camera = Camera(self.window, position=(bw/2,bh/2), zoom=0.3)
        self.time = 0
        clock.schedule(self.addTime)
        self.fps = clock.ClockDisplay()

    def addKeyBindings(self):
        pass
        

    def addTime(self,dt):
        self.time += dt

    def toScreenCoords(self,pos):
        x,y = pos
        b = self.game.board
        size = config.spriteSize
        #return ((x-b.width/2+0.5)*size, (y-b.height/2+0.5)*size)
        return x*size, y*size


    def drawTile(self,tile):
        s = self.sprites["tile{0}".format(tile.kind)]
        s.clear()
        size = s.top-s.bottom
        s.x,s.y = self.toScreenCoords(tile.position)
        s.rot = -tile.rotation
        s.render()

    def drawBoard(self):
        tiles = self.game.board.tiles
        for x,y in tiles.keys():
            self.drawTile(tiles[x,y])

    def drawOooMan(self, player, oooMan):
        s = self.sprites["OooMan-"+player.color+"-"+oooMan.kind]
        s.clear()
        s.xy = self.toScreenCoords(oooMan.position)
        s.rot = oooMan.rotation
        if oooMan is player.activeOooMan:
            g = self.sprites["glow"]
            g.clear()
            g.xy = s.xy
            g.render()
        if not oooMan.alive:
            s.alpha = 1.0 - oooMan.dieProgress
        if oooMan.canDie:
            s.red = s.green = s.blue = 0.5

        s.render()
        sA = self.sprites["action0"]
        height = sA.top-sA.bottom
        width = sA.right-sA.left
        w = len(oooMan.actionList)*width
        for a in oooMan.actionList:
            if a.started:
                w += width*a.progress
        for i in range(len(oooMan.actionList)):
            a = oooMan.actionList[i]
            sA = self.sprites["action{0}".format(a.kind)]
            sA.clear()
            sA.x = s.x - w/2 + width/2 + i*width
            sA.y = s.y+config.spriteSize/3+height
            sA.rot = 0
            sA.alpha = 1.0 - a.progress
            if a.started and (not a.canPerform() or a.discarded):
                sA.green = 0
                sA.blue = 0
                #print((a.direction,a.startPosition,a.getEndPosition()))
            sA.render()
    def drawOooMen(self):
        for p in self.game.players:
            for o in p.oooMen:
                if o is not p.activeOooMan:
                    self.drawOooMan(p,o)
            self.drawOooMan(p,p.activeOooMan)

    def draw(self):
        self.camera.worldProjection()
        rabbyt.clear((1,1,1,1))
        self.drawBoard()
        self.drawOooMen()
        self.camera.hudProjection()
        self.fps.draw()

    def loop(self):
        clock.tick()
        self.window.dispatch_events()
        rabbyt.set_time(self.time)
        self.game.update(self.time)
        #self.camera.follow = self.game.players[0].activeOooMan
        self.camera.update()
        self.draw()
        self.window.flip()

    def run(self):
        while True:
            self.loop()

class InputListener(pyglet.event.EventDispatcher):
    """Class that translates user input to events.
    
    keyBindings - dictionary:
        pyglet.window.key -> (function,kwargs)"""
    def __init__(self):
        self.keyBindings = {}
    def on_key_press(self,symbol,modifiers):
        if symbol in self.keyBindings:
            f,kwargs = self.keyBindings[symbol]
            f(**kwargs)

if __name__ == "__main__":
    game.OooMan.kinds = eval(file(config.levelsDir+"sample.ooo").read())
    #print(game.OooMan.kinds)
    #b = game.Board(tiles=file(config.levelsDir+"sample.lev").read())
    #b = game.Board(tiles="I0L0\nT0T0")
    b = game.Board()
    b.generateBoard("T+LI"*30)
    p = game.Player(b,"red")
    p.addOooMan()
    p.addOooMan()
    q = game.Player(b,"blue")
    q.addOooMan()
    q.addOooMan()

    g = game.Game(board=b, players=[p,q])
    c = Client(g)
    c.inputListener.keyBindings = {
            #key.UP: (p.addAction, {'kind':game.ActionFactory.MOVE}),
            #key.RIGHT: (p.addAction, {'kind':game.ActionFactory.ROTATE_CW}),
            #key.LEFT: (p.addAction, {'kind':game.ActionFactory.ROTATE_CCW}),

            key.UP: (p.addAction, {'kind':game.ActionFactory.GO_NORTH}),
            key.LEFT: (p.addAction, {'kind':game.ActionFactory.GO_WEST}),
            key.DOWN: (p.addAction, {'kind':game.ActionFactory.GO_SOUTH}),
            key.RIGHT: (p.addAction, {'kind':game.ActionFactory.GO_EAST}),
            #key.RSHIFT: (p.removeAction, {}),
            key.RCTRL: (p.switchActiveOooMan,{}),

            key.W: (q.addAction, {'kind':game.ActionFactory.GO_NORTH}),
            key.A: (q.addAction, {'kind':game.ActionFactory.GO_WEST}),
            key.S: (q.addAction, {'kind':game.ActionFactory.GO_SOUTH}),
            key.D: (q.addAction, {'kind':game.ActionFactory.GO_EAST}),
            #key.LSHIFT: (q.removeAction, {}),
            key.LCTRL: (q.switchActiveOooMan,{})}
    c.run()
