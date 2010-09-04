# coding=utf-8

from __future__ import division,print_function
import random
import game
import config
import rabbyt
import sys
import os
import pyglet
import re
import controller
import keyBindings
import colors
from pyglet import gl, clock, font
from pyglet.window import Window,key
from pyglet.text import Label,HTMLLabel
from optparse import OptionParser

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
        #gl.glScissor(100,100,400,400)
        #gl.glEnable(gl.GL_SCISSOR_TEST)

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
        #gl.glDisable(gl.GL_SCISSOR_TEST)
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

    def __init__(self,controller,players = None):
        pyglet.font.add_directory(config.fontsDir)
        self.sprites = {}
        self.loadSprites(["glow", "cheatSheet", "speedBoots", "shield", "masterSword"])
        self.loadSpritesRegex("tile.*")
        self.loadSpritesRegex("teleport.*")
        self.loadSpritesRegex("OooMan.*")
        self.loadSpritesRegex("action.*")
        self.controller = controller
        controller.clients.append(self)
        self.game = self.controller.game
        clock.set_fps_limit(50)
        w,h = config.screenSize
        if not config.fullScreen:
            self.window = Window(width=w, height=h)
        else:
            self.window = Window(fullscreen=True)
            w,h = self.window.width,self.window.height
            config.screenSize = w,h
        rabbyt.set_default_attribs()
        self.window.set_caption("NoTitle!")
        self.window.on_close = sys.exit
        self.playersInput = {}
        self.controlPlayers = controller.controlPlayers
        bw,bh = self.game.board.dimensions
        gl.glEnable(gl.GL_MULTISAMPLE)
        zoom = min( w/(config.spriteSize*bw), h/(config.spriteSize*bh))*0.95
        self.camera = Camera(self.window, position=((bw-1)/2,(bh-1)/2), zoom=zoom)
        self.fps = clock.ClockDisplay(font=font.load('Edmunds',bold=True,dpi=200),format='FPS: %(fps).2f')
        self.scores = HTMLLabel(multiline=True, width=2*config.spriteSize, anchor_y='top', x=10, y=h)

    def bindingOk(self,binding):
        for i in self.playersInput.values():
            b = i.keyBinding
            for k in b:
                if k in binding:
                    return False
        return True

    def getControlPlayers(self):
        return self.playersInput.keys()

    def setControlPlayers(self,controls):
        rem = [ k for k in self.playersInput.keys() if k not in controls]
        for k in rem:
            self.window.remove_handlers(self.playersInput[k])
            del self.playersInput[k]
        bindings = [ b for b in keyBindings.preconfigured if self.bindingOk(b) ]
        idx = 0
        for p in controls:
            if p not in self.playersInput and idx < len(bindings):
                self.playersInput[p] = PlayerControl(self.controller, p, bindings[idx])
                self.window.push_handlers(self.playersInput[p])
                idx += 1
                
    controlPlayers = property(getControlPlayers,setControlPlayers)

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
    
    def drawItem(self, item):
        s = self.sprites[item.kind]
        s.clear()
        s.x,s.y = self.toScreenCoords(item.position)
        s.rot = -item.rotation
        s.render()

    def drawBoard(self):
        tiles = self.game.board.tiles
        for x,y in tiles.keys():
            self.drawTile(tiles[x,y])
        for i in self.game.board.items:
            self.drawItem(i)

    def drawOooMan(self, player, oooMan):
        s = self.sprites["OooMan-"+player.color+"-"+oooMan.kind]
        s.clear()
        s.xy = self.toScreenCoords(oooMan.position)
        s.rot = oooMan.rotation
            #print(oooMan.position)
        if not oooMan.alive:
            s.alpha = s.scale = 1.0 - oooMan.dieProgress
        if oooMan.actionList and oooMan.actionList[0].kind == game.ActionFactory.TELEPORT:
            a = oooMan.actionList[0]
            if a.started and not a.ended:
                s.alpha = s.scale = 2* (abs(0.5 - a.progress))
        if oooMan is player.activeOooMan:
            g = self.sprites["glow"]
            g.clear()
            g.xy = s.xy
            g.scale = s.scale
            g.render()
        s.render()

        sA = self.sprites["action0"]
        sA.clear()
        height = (sA.top-sA.bottom)  
        width = (sA.right-sA.left) 
        w = len(oooMan.actionList)*width
        for a in oooMan.actionList:
            if a.started:
                w += width*a.progress
        for i in range(len(oooMan.actionList)):
            a = oooMan.actionList[i]
            sA = self.sprites["action{0}".format(a.kind)]
            sA.clear()
            sA.x = s.x - w/2 + width/2 + i*width
            sA.y = s.y+ oooMan.size*config.spriteSize/2 + height
            sA.scale = s.scale
            sA.alpha = (1.0 - a.progress)*s.alpha
            if a.started and (not a.canPerform() or a.discarded):
                sA.green = 0
                sA.blue = 0
                #print((a.direction,a.startPosition,a.getEndPosition()))
            sA.render()

        width, height = 2*width, 2*height
        w = len(oooMan.items)*width
        for i in range(len(oooMan.items)):
            it = oooMan.items[i]
            sI = self.sprites[it.kind]
            sI.clear()
            sI.x = s.x - w/2 + width/2 + i*width
            sI.y = s.y - oooMan.size * config.spriteSize/2 - height/2 - 5
            sI.scale = s.scale * height / (sI.top - sI.bottom)
            sI.alpha = s.alpha
            sI.render()

        #kills = game.OooMan.kinds[oooMan.kind]
        kills = oooMan.killsKinds()
        scale = 0.5*s.scale
        width = scale * config.spriteSize*oooMan.size*(1.2)
        w = len(kills)*width
        for i in range(len(kills)):
            k = kills[i]
            sK = self.sprites["OooMan-white-"+k]
            sK.clear()
            sK.x = s.x - w/2 + width*(i+0.5)
            #sK.y = s.y - oooMan.size*config.spriteSize/2 -config.spriteSize*scale/2
            sK.y = s.y - config.spriteSize*scale/2
            sK.alpha = 0.8*s.alpha
            sK.scale = scale
            sK.render()
    def drawOooMen(self):
        for p in self.game.players.values():
            for o in p.oooMen:
                if o is not p.activeOooMan:
                    self.drawOooMan(p,o)
            if p.activeOooMan:
                self.drawOooMan(p,p.activeOooMan)

    def drawScores(self):
        txt = ["<b><font face='Edmunds' size=6>Scores</font><br/></b>"]
        for p in self.game.players.values():
            txt.append(u"<b><font face='Edmunds' size=5 color='{color}'>{name}: {score}</font><br/></b>".format(color=colors.htmlColor(p.color), name=unicode(p.name,"utf-8"), score=p.score))
        txt = u"".join(txt)
        if self.scores.text != txt:
            self.scores.text = unicode(txt)
        self.scores.draw()
        """s = self.sprites["cheatSheet"]
        s.x = 256
        s.y = 512
        s.alpha = 0.5
        s.render()"""


    def draw(self):
        rabbyt.clear((1,1,1,1))
        self.camera.worldProjection()
        self.drawBoard()
        self.drawOooMen()
        self.camera.hudProjection()
        self.drawScores()
        self.fps.draw()

    def loop(self):
        dt = clock.tick()
        self.window.dispatch_events()
        self.controller.update()
        self.game = self.controller.game
        self.game.update(dt)
        rabbyt.set_time(self.game.time)
        #self.camera.follow = self.game.players[0].activeOooMan
        self.camera.update()
        self.draw()
        self.window.flip()

    def run(self):
        while True:
            self.loop()


class PlayerControl(pyglet.event.EventDispatcher):
    def __init__(self, controller, playerId, keyBindings):
        """keyBindings is a dictionary key -> action (string)"""
        self.controller = controller
        self.playerId = playerId
        self.keyBindings = keyBindings
    def on_key_press(self, symbol, modifiers):
        if symbol in self.keyBindings:
            self.controller.sendInput(self.playerId, self.keyBindings[symbol])

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
    import start
    start.startLocalGame(sys.argv[1:])
