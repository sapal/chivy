# coding=utf-8

from __future__ import division,print_function
import random
import game
import config
import cocos
import sys
import os
import pyglet
import re
import controller
import keyBindings
import colors
import rabbyt 
from pyglet import gl, clock, font
from pyglet.window import Window,key
from pyglet.text import Label,HTMLLabel
from optparse import OptionParser

def initialize():
    w,h = config.screenSize
    if not config.fullScreen:
        cocos.director.director.init(width=w, height=h)
    else:
        cocos.director.director.init(fullscreen=True)
        w,h = cocos.director.director.get_window_size()
        config.screenSize = w,h
    pyglet.font.add_directory(config.fontsDir)
    BoardSprite.loadSprites(["glow", "cheatSheet", "speedBoots", "shield", "masterSword"])
    BoardSprite.loadSpritesRegex("tile.*")
    BoardSprite.loadSpritesRegex("teleport.*")
    BoardSprite.loadSpritesRegex("OooMan.*")
    BoardSprite.loadSpritesRegex("action.*")
    clock.set_fps_limit(50)
    #rabbyt.set_default_attribs()
    #gl.glEnable(gl.GL_MULTISAMPLE)

class BoardSprite(game.GameObject):
    """This sprite's size and position is in game.Board units (1 == tile size)."""
    """Dictionary of loaded sprites:"""
    sprites = {} 
    sizes = {}

    @staticmethod
    def loadSpritesRegex(regexString):
        end = str(config.spriteSize)+".png"
        r = re.compile(regexString+end)
        BoardSprite.loadSprites([ f[:f.rfind(end)] for f in os.listdir(config.imagesDir) if r.match(f)])

    @staticmethod
    def loadSprites(spriteList):
        for f in spriteList:
            BoardSprite.loadSprite(f)

    @staticmethod
    def loadSprite(spriteName):
        path = config.imagesDir+spriteName+str(config.spriteSize)+".png"
        pic = pyglet.image.load(path)
        pic.anchor_x = int(pic.width/2)
        pic.anchor_y = int(pic.height/2)
        #BoardSprite.sprites[spriteName] = pyglet.sprite.Sprite(pic)
        BoardSprite.sprites[spriteName] = rabbyt.Sprite(path)
        BoardSprite.sizes[spriteName] =  (pic.width/config.spriteSize, pic.height/config.spriteSize)
        
    def __init__(self, name):
        super(BoardSprite, self).__init__()
        self.name = name

    def clear(self):
        self.position = (0,0)
        self.rotation = 0
        self.color = (255, 255, 255)
        self.opacity = 1.0
        self.scale = 1
        self.visible = True

    def draw(self): 
        s = BoardSprite.sprites[self.name]
        size = config.spriteSize
        #s.set_position(self.x*size, self.y*size)
        #s.rotation = self.rotation
        #s.color = self.color

        #s.opacity = self.opacity
        #s.scale = self.scale
        #s.draw()
        s.xy = self.x*size, self.y*size
        s.rot = -self.rotation
        r, g, b = self.color
        s.rgb = r/255, g/255, b/255
        s.scale = self.scale
        s.alpha = self.opacity
        s.render()

    @property
    def size(self):
        return BoardSprite.sizes[self.name]

    @property
    def height(self):
        return self.size[1]
    @property
    def widht(self):
        return self.size[0]

class HudLayer(cocos.layer.Layer):
    def __init__(self, client):
        super(HudLayer, self).__init__()
        self.client = client
        self.fps = clock.ClockDisplay(font=font.load('Edmunds',bold=True,dpi=200),format='FPS: %(fps).2f')
        self.scores = HTMLLabel(multiline=True, width=2*config.spriteSize, anchor_y='top', x=10, y=config.screenSize[1])

    def drawScores(self):
        txt = ["<b><font face='Edmunds' size=6>Scores</font><br/></b>"]
        for p in self.client.game.players.values():
            txt.append(u"<b><font face='Edmunds' size=5 color='{color}'>{name}: {score}</font><br/></b>".format(color=colors.htmlColor(p.color), name=unicode(p.name,"utf-8"), score=p.score))
        txt = u"".join(txt)
        if self.scores.text != txt:
            self.scores.text = unicode(txt)
        self.scores.draw()

    def draw(self):
        gl.glPushMatrix()
        self.transform()

        self.fps.draw()
        self.drawScores()

        gl.glPopMatrix()

class BoardLayer(cocos.layer.Layer):
    def __init__(self, client):
        super(BoardLayer, self).__init__()
        self.client = client
        bw, bh = self.game.board.width, self.game.board.height
        self.cameraPosition = bw/2, bh/2
        w,h = config.screenSize
        s = config.spriteSize
        self.cameraZoom = min(w/(bw*s),h/(bh*s))*0.95

    @property
    def game(self):
        return self.client.game

    def toScreenCoords(self,pos):
        x, y = pos
        cx, cy = self.cameraPosition
        w,h = config.screenSize
        s = config.spriteSize
        return (x-cx+0.5)*self.cameraZoom+w/s/2, (y-cy+0.5)*self.cameraZoom+h/s/2
    
    def renderSprite(self, sprite):
        x, y = sprite.position
        scale = sprite.scale

        sprite.position = self.toScreenCoords((x,y))
        sprite.scale *= self.cameraZoom
        sprite.draw()

        sprite.position = x, y
        sprite.scale = scale

    def drawTile(self,tile):
        s = BoardSprite("tile{0}".format(tile.kind))
        s.clear()
        s.position = tile.position
        s.rotation = tile.rotation
        self.renderSprite(s)
    
    def drawItem(self, item):
        s = BoardSprite(item.kind)
        s.clear()
        s.position = item.position
        s.rotation = -item.rotation
        self.renderSprite(s)

    def drawBoard(self):
        tiles = self.game.board.tiles
        for t in tiles.values():
            self.drawTile(t)
        for i in self.game.board.items:
            self.drawItem(i)

    def drawOooMan(self, player, oooMan):
        s = BoardSprite("OooMan-"+player.color+"-"+oooMan.kind)
        s.clear()
        s.position = oooMan.position
        s.rot = oooMan.rotation
        if not oooMan.alive:
            s.opacity = s.scale = 1.0 - oooMan.dieProgress
        if oooMan.actionList and oooMan.actionList[0].kind == game.ActionFactory.TELEPORT:
            a = oooMan.actionList[0]
            if a.started and not a.ended:
                s.opacity = s.scale = 2* (abs(0.5 - a.progress))
        if oooMan is player.activeOooMan:
            g = BoardSprite("glow")
            g.clear()
            g.position = s.position
            g.rotation = s.rotation
            g.scale = s.scale
            self.renderSprite(g)
        self.renderSprite(s)

        sA = BoardSprite("action0")
        sA.clear()
        height, width = sA.size
        w = len(oooMan.actionList)*width
        for a in oooMan.actionList:
            if a.started:
                w += width*a.progress
        for i in range(len(oooMan.actionList)):
            a = oooMan.actionList[i]
            sA = BoardSprite("action{0}".format(a.kind))
            sA.clear()
            sA.position = s.x - w/2 + width/2 + i*width, s.y+ oooMan.size/2 + 0.03
            sA.scale = s.scale
            sA.opacity = (1.0 - a.progress)*s.opacity
            if a.started and (not a.canPerform() or a.discarded):
                sA.color = (255,0,0)
            self.renderSprite(sA)

        width, height = 2*width, 2*height
        w = len(oooMan.items)*width
        for i in range(len(oooMan.items)):
            it = oooMan.items[i]
            sI = BoardSprite(it.kind)
            sI.clear()
            sI.position = s.x - w/2 + width/2 + i*width, s.y - oooMan.size/2 - height/2 - 0.03
            sI.scale = s.scale * height / (sI.height)
            sI.opacity = s.opacity
            self.renderSprite(sI)

        #kills = game.OooMan.kinds[oooMan.kind]
        kills = oooMan.killsKinds()
        scale = 0.5*s.scale
        width = scale*oooMan.size*(1.2)
        w = len(kills)*width
        for i in range(len(kills)):
            k = kills[i]
            sK = BoardSprite("OooMan-white-"+k)
            sK.clear()
            sK.position = s.x - w/2 + width*(i+0.5), s.y - scale/2
            sK.opacity = 0.8*s.opacity
            sK.scale = scale
            self.renderSprite(sK)

    def drawOooMen(self):
        for p in self.game.players.values():
            for o in p.oooMen:
                if o is not p.activeOooMan:
                    self.drawOooMan(p,o)
            if p.activeOooMan:
                self.drawOooMan(p,p.activeOooMan)

    def draw(self):
        gl.glPushMatrix()
        self.transform()

        rabbyt.clear((1,1,1))
        self.drawBoard()
        self.drawOooMen()

        gl.glPopMatrix()

class InputLayer(cocos.layer.Layer):
    is_event_handler = True
    def __init__(self, client):
        super(InputLayer, self).__init__()
        self.client = client
        self.playersInput = {}
        self.controlPlayers = client.controller.controlPlayers

    def getControlPlayers(self):
        return self.playersInput.keys()

    def setControlPlayers(self,controls):
        rem = [ k for k in self.playersInput.keys() if k not in controls]
        for k in rem:
            del self.playersInput[k]
        bindings = [ b for b in keyBindings.preconfigured if self.bindingOk(b) ]
        idx = 0
        for p in controls:
            if p not in self.playersInput and idx < len(bindings):
                self.playersInput[p] = PlayerControl(self.client.controller, p, bindings[idx])
                idx += 1

    controlPlayers = property(getControlPlayers,setControlPlayers)

    def bindingOk(self,binding):
        for i in self.playersInput.values():
            b = i.keyBinding
            for k in b:
                if k in binding:
                    return False
        return True

    def on_key_press(self, key, modyfiers):
        for i in self.playersInput.values():
            i.on_key_press(key, modyfiers)

class Client(cocos.scene.Scene):
    """Client for viewing game."""

    def __init__(self, controller, players = None):
        w,h = config.screenSize

        self.controller = controller
        controller.clients.append(self)
        #super(Client, self).__init__(cocos.layer.util_layers.ColorLayer(255,255,255,255),BoardLayer(self),HudLayer(self),InputLayer(self))
        super(Client, self).__init__(BoardLayer(self),HudLayer(self),InputLayer(self))
        self.schedule(self.update)

    def update(self, dt):
        self.controller.update(dt)

    @property
    def game(self):
        return self.controller.game

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
