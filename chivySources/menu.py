# coding=utf-8

from cocos import menu,layer,scene,actions
from cocos.actions.interval_actions import *
from cocos.actions.base_actions import *
from cocos.director import director
from cocos.scenes.transitions import *
from gui import Client
from pyglet import gl,clock
from cocos.menu import Menu, MenuItem, EntryMenuItem, MultipleMenuItem, ToggleMenuItem, IntegerMenuItem
from multiprocessing import Process,Queue
from config import Config as config
import server
import keyBindings
import controller
import game
import gui
import colors
import kinds
import pyglet
import rabbyt
import re
import os
import random
from translation import gettext as _

def deactivateItem(item):
    item.item.color = item.item_selected.color = (128,128,128,255)
    item.update()

def activateItem(item):
    item.item.color = item.parent.font_item['color']
    item.item_selected.color = item.parent.font_item_selected['color']
    item.update()

def createMenuLook(myMenu,items):
    myMenu.font_title['font_name'] = 'Edmunds'
    myMenu.font_title['color'] = colors.rgba("black")

    myMenu.font_item['font_name'] = 'Edmunds'
    myMenu.font_item['color'] = colors.rgba("black")

    myMenu.font_item_selected['font_name'] = 'Edmunds'
    #myMenu.font_item_selected['color'] = colors.rgba("green")
    myMenu.font_item_selected['color'] = (255, 158, 19, 255)

    myMenu.menu_halign = menu.LEFT
    myMenu.menu_anchor_x = menu.CENTER
    myMenu.menu_anchor_y = menu.CENTER

    #myMenu.create_menu(items, menu.zoom_in(), menu.zoom_out())
    myMenu.create_menu(items, menu.shake(), menu.shake_back())


class GameMenu(menu.Menu):
    def __init__(self, background):
        super(GameMenu, self).__init__(_('Game Options'))
        self.background = background

        items = []

        items.append(IntegerMenuItem(_('Point limit: '), self.onPointsChange, config.minPoints, config.maxPoints, 10, config.points))

        items.append(IntegerMenuItem(_('Items: '), self.onItemsChange, config.minItemNumber, config.maxItemNumber, 1, config.itemNumber))

        self.createBoardMenu()
        items.append(self.boardMenu)

        self.teleports = IntegerMenuItem(_('    Teleports: '), self.onTeleportsChange, config.minTeleports, config.maxTeleports, 1, config.teleports)
        items.append(self.teleports)

        self.tilesNumber = IntegerMenuItem(_('    Tiles: '), self.onTileNumberChange, config.minTileNumber, config.maxTileNumber, 10, config.tileNumber)
        items.append(self.tilesNumber)

        self.createWallsMenu()
        items.append(self.wallsMenu)

        items.append(MenuItem(_('Back'), self.on_quit))

        createMenuLook(self, items)
        self.onBoardChange(self.boardMenu.idx)

    def onPointsChange(self, value):
        config.points = value

    def addBoardFiles(self, directory):
        try:
            for f in sorted(os.listdir(directory)):
                if re.match(".*\\.brd$", f):
                    self.boardList.append(f[:-4])
                    self.boardFilenames.append(directory+f)
        except OSError,e:
            print(e)

    def createWallsMenu(self):
        self.tilesKindsNames = [ _("None"), _("Few"), _("Average"), _("Many") ]
        self.tilesKinds = [ "+", "+T", "++TTIL", "+T+TILIL" ]
        try:
            idx = self.tilesKinds.index(config.tiles)
        except:
            idx = 0
        self.wallsMenu = MultipleMenuItem(_("    Walls: "), self.onWallsChange, self.tilesKindsNames, idx)

    def createBoardMenu(self):
        self.boardFilenames = [None]
        self.boardList = [ _("Generate Board") ]
        self.addBoardFiles(config.levelsDir)
        self.addBoardFiles(config.userLevelsDir)
        try:
            idx = self.boardFilenames.index(config.boardFilename)
        except:
            idx = 0
        self.boardMenu = MultipleMenuItem(_("Board: "), self.onBoardChange, self.boardList, idx)

    def updateBoard(self):
        g = game.Game.gameFromConfig()
        g.players = {}
        g.board.items = g.board.teleports
        g.board.itemNumber = 0
        self.background.setBoard(g.board)

    def onBoardChange(self, idx):
        genBoardItems = (self.teleports, self.tilesNumber, self.wallsMenu)
        for it in genBoardItems:
            if idx == 0:
                activateItem(it)
            else:
                deactivateItem(it)
        config.boardFilename = self.boardFilenames[idx]
        self.updateBoard()
    
    def onItemsChange(self, value):
        config.itemNumber = value

    def onWallsChange(self, idx):
        config.tiles = self.tilesKinds[idx]
        self.updateBoard()

    def onTileNumberChange(self, value):
        config.tileNumber = value
        self.updateBoard()

    def onTeleportsChange(self, value):
        config.teleports = value
        self.updateBoard()

    def on_enter(self):
        self.updateBoard()
        super(GameMenu, self).on_enter()

    def on_quit(self):
        self.background.setImage(None)
        self.parent.switch_to(0)

class ConnectingMenu(menu.Menu):
    def __init__(self):
        super(ConnectingMenu, self).__init__(_('Connecting...'))
        self.button = MenuItem("Back",self.on_quit)
        createMenuLook(self, [self.button])
        self.ctrl = None

    def on_enter(self):
        super(ConnectingMenu, self).on_enter()
        self.title_label.text = _('Connecting...')
        self.ctrl = controller.NetworkedController(onFail=self.onFail,onSuccess=self.onSuccess)
        clock.schedule(self.ctrl.update)

    def onSuccess(self):
        clock.unschedule(self.ctrl.update)
        self.parent.switch_to(0)
        director.push(Client(self.ctrl, killController=True))

    def onFail(self):
        if self.ctrl:
            clock.unschedule(self.ctrl.update)
            self.ctrl = None
        self.title_label.text = _("Failed to connect.")

    def on_quit(self):
        self.parent.switch_to(3)

class NetworkGameClientMenu(menu.Menu):
    def __init__(self):
        super(NetworkGameClientMenu, self).__init__(_('Join Network Game'))
        items = []

        items.append(MenuItem(_("Join"), self.onJoin))
        items.append(EntryMenuItem(_("Host: "),self.onHostChange, config.host))
        items.append(MenuItem(_("Back"), self.on_quit))
        createMenuLook(self, items)

    def onHostChange(self,value):
        config.host = value

    def on_quit(self):
        self.parent.switch_to(0)

    def onJoin(self):
        self.parent.switch_to(5)

class ServerMenu(menu.Menu):
    def __init__(self):
        super(ServerMenu, self).__init__(_('Start Server'))
        self.serverProcess = None
        self.server = None
        self.queue = None
        self.statusQueue = None
        items = []

        self.startItem = MenuItem(_("Start"), self.onStart)
        items.append(self.startItem)

        items.append(EntryMenuItem(_("Host address: "), self.onAddressChange, config.serverAddress))

        items.append(MenuItem(_("Back"), self.on_quit))

        createMenuLook(self, items)

    def on_quit(self):
        self.parent.switch_to(0)

    def onStart(self):
        if self.serverProcess:
            self.queue.put("endPlease")
            self.serverProcess.join(0.5)
            if self.serverProcess.is_alive(): self.serverProcess.terminate()
        g = game.Game.gameFromConfig(players={})
        self.queue = Queue()
        self.statusQueue = Queue()
        try:
            self.server = server.OooServer(localaddr=(config.serverAddress, 9999), game=g, inQueue=self.queue)
            self.serverProcess = Process(target=self.server.Launch)
            self.serverProcess.daemon = True
            self.serverProcess.start()
            self.startItem.label = _("Start (server already running)")
        except Exception,e:
            self.startItem.label = _("Start (failed to start server)")
            print(e)
        self.startItem.update()

    def onAddressChange(self, value):
        config.serverAddress = value

class PlayerMenu(menu.Menu):
    def __init__(self, background):
        super(PlayerMenu, self).__init__(_('Players'))
        self.background = background
        items = []

        self.choosePlayer = MultipleMenuItem("", self.onPlayerChange, [_("Player {0}").format(i+1) for i in range(len(config.players)) ], 0)
        items.append(self.choosePlayer)

        self.playerName = EntryMenuItem(_("    Name: "), self.onPlayerNameChange, unicode(config.players[0]["name"],"utf-8"))
        items.append(self.playerName)

        self.colors = list(colors.colors.keys())
        self.colorNames = [ _(c) for c in self.colors ]
        self.playerColor = MultipleMenuItem(_("    Color: "), self.onPlayerColorChange, self.colorNames, self.colors.index(config.players[0]["color"]))
        items.append(self.playerColor)

        self.playerSpeed = IntegerMenuItem(_("    Speed: "), self.onPlayerSpeedChange, 0.3, 3, 0.1, config.players[0]["speed"])
        items.append(self.playerSpeed)

        self.playerPlaying = MultipleMenuItem(_("    Playing: "), self.onPlayerPlayingChange, [_("No"), _("Yes")], int(config.players[0]["playing"]))
        items.append(self.playerPlaying)

        items.append(IntegerMenuItem(_('Bots: '), self.onBotsChange, config.minBots, config.maxBots, 1, config.bots))

        items.append(IntegerMenuItem(_('Bot level: '), self.onBotSpeedChange, config.minBotSpeed, config.maxBotSpeed, 1, config.botSpeed))

        items.append(MenuItem(_("Back"), self.on_quit))

        createMenuLook(self, items)

    def updateImage(self):
        idx = self.choosePlayer.idx
        self.background.setImage("player{0}controls-base".format(config.players[idx]["prefferedKeybindings"]))

    def onPlayerSpeedChange(self, value):
        config.players[self.choosePlayer.idx]["speed"] = value

    def onBotSpeedChange(self, value):
        config.botSpeed = value

    def onBotsChange(self, value):
        config.bots = value

    def onPlayerChange(self, idx):
        self.playerName.value = unicode(config.players[idx]["name"],"utf-8")
        self.playerColor.idx = self.colors.index(config.players[idx]["color"])
        self.playerColor.update()
        if config.players[idx]["playing"]:
            self.playerPlaying.idx = 1
        else:
            self.playerPlaying.idx = 0
        self.playerPlaying.update()
        self.updateImage()

    def onPlayerNameChange(self, value):
        config.players[self.choosePlayer.idx]["name"] = value.encode("utf-8")

    def onPlayerColorChange(self, idx):
        config.players[self.choosePlayer.idx]["color"] = self.colors[idx]

    def onPlayerPlayingChange(self, idx):
        value = (idx == 1)
        config.players[self.choosePlayer.idx]["playing"] = value
    
    def on_enter(self):
        super(PlayerMenu, self).on_enter()
        self.updateImage()

    def on_quit(self):
        self.background.setImage(None)
        self.parent.switch_to(0)

class MainMenu(menu.Menu):
    def __init__(self, background):
        super(MainMenu, self).__init__(_('Chivy'))
        self.background = background
        items = []
        items.append(MenuItem(_('Start Local Game'), self.onLocalGame))
        items.append(MenuItem(_('Join Network Game'), self.onNetworkGame))
        items.append(MenuItem(_('Start Server'), self.onStartServer))
        items.append(MenuItem(_('Players'), self.onPlayers))
        items.append(MenuItem(_('Game Options'), self.onGameOptions))
        items.append(MenuItem(_('Quit'), self.on_quit))
        createMenuLook(self, items)

    def onLocalGame(self):
        g = game.Game.gameFromConfig()
        ctrl = controller.Controller(g)
        director.push( Client(ctrl))

    def onStartServer(self):
        self.parent.switch_to(4)

    def on_enter(self):
        super(MainMenu, self).on_enter()
        #self.background.setImage("OooMan-{color}-{kind}".format(color=random.choice(colors.colors.keys()), kind=random.choice(kinds.CLASSIC.keys())))
        b = game.Board()
        b.generateBoard("TT++LI", tileNumber=30)
        g = game.Game.gameFromConfig(board=b, players=[])
        self.background.setGame(g, bots=4)

    def on_quit(self):
        pyglet.app.exit()

    def onPlayers(self):
        self.parent.switch_to(1)

    def onNetworkGame(self):
        self.parent.switch_to(3)

    def onGameOptions(self):
        self.parent.switch_to(2)

class BackgroundLayer(layer.base_layers.Layer):
    def __init__(self):
        super(BackgroundLayer, self).__init__()
        self.image = None
        self.boardLayer = None
        self.controller = controller.Controller(game.Game())
        self.schedule(self.controller.update)

    def setGame(self, game, bots=0):
        self.controller.setGame(game)
        self.updateBoardLayer()
        for b in range(bots):
            self.controller.addBot()

    def updateBoardLayer(self):
        if not self.boardLayer:
            w,h = config.screenSize
            lw,lh = w/2,h/2
            self.boardLayer = gui.BoardLayer(self.controller,(lw,lh))
            self.boardLayer.position = (w-lw,(h-lh)/2)

    def setBoard(self, board):
        self.setGame(game.Game())
        self.controller.game.board = board
        self.updateBoardLayer()

    def setImage(self, image):
        self.boardLayer = None
        self.image = image

    def draw(self):
        gl.glPushMatrix()
        self.transform()

        if self.boardLayer:
            self.boardLayer.draw()
        else:
            rabbyt.clear((1,1,1))
            if self.image:
                sprite = gui.BoardSprite(self.image)
                w,h = config.screenSize
                sprite.scaleToScreenHeight(h/3)
                sw,sh = sprite.screenSize
                sprite.setScreenPosition((w*3/4, h/2))
                sprite.draw()

        gl.glPopMatrix()

def getMenuScene():
    s = scene.Scene()
    b = BackgroundLayer()
    s.add(b)
    s.add(layer.base_layers.MultiplexLayer(MainMenu(b), PlayerMenu(b), GameMenu(b), NetworkGameClientMenu(), ServerMenu(), ConnectingMenu()), z=1)
    return s
