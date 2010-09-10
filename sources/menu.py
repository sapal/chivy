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
import colors
import pyglet
import rabbyt
import re
import os

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
    def __init__(self):
        super(GameMenu, self).__init__('Game Options')

        items = []

        items.append(IntegerMenuItem('Items: ', self.onItemsChange, config.minItemNumber, config.maxItemNumber, 1, config.itemNumber))

        items.append(IntegerMenuItem('Bots: ', self.onBotsChange, config.minBots, config.maxBots, 1, config.bots))

        items.append(IntegerMenuItem('Bot speed: ', self.onBotSpeedChange, config.minBotSpeed, config.maxBotSpeed, 1, config.botSpeed))

        self.createBoardMenu()
        items.append(self.boardMenu)

        self.teleports = IntegerMenuItem('    Teleports: ', self.onTeleportsChange, config.minTeleports, config.maxTeleports, 1, config.teleports)
        items.append(self.teleports)

        self.tilesNumber = IntegerMenuItem('    Tiles: ', self.onTileNumberChange, config.minTileNumber, config.maxTileNumber, 10, config.tileNumber)
        items.append(self.tilesNumber)

        self.tilesMenu = EntryMenuItem('    Tiles kinds: ', self.onTilesChange, config.tiles)
        items.append(self.tilesMenu)

        items.append(MenuItem('Back', self.on_quit))

        createMenuLook(self, items)

    def onBotSpeedChange(self, value):
        config.botSpeed = value
    def onBotsChange(self, value):
        config.bots = value

    def createBoardMenu(self):
        self.boardList = [ "Generate Board" ]
        for f in sorted(os.listdir(config.levelsDir)):
            if re.match(".*\\.brd$", f):
                self.boardList.append(f[:-4])
        idx = 0
        if config.boardFilename:
            try:
                idx = self.boardList.find(config.boardFilename)
            except:
                config.boardFilename = None
        self.boardMenu = MultipleMenuItem("Board: ", self.onBoardChange, self.boardList, idx)

    def onBoardChange(self, idx):
        genBoardItems = (self.teleports, self.tilesNumber, self.tilesMenu)
        for it in genBoardItems:
            if idx == 0:
                activateItem(it)
            else:
                deactivateItem(it)
        if idx == 0:
            config.boardFilename = None
        else:
            config.boardFilename = config.levelsDir + self.boardList[idx] + ".brd"
    
    def onItemsChange(self, value):
        config.itemNumber = value

    def onTilesChange(self, tiles):
        #print("Change {0} {1}".format(tiles, self.tilesMenu.value))
        if not tiles:
            return
        for c in tiles:
            if c not in "TIUL+":
                self.tilesMenu.value = config.tiles
                return
        config.tiles = tiles

    def onTileNumberChange(self, value):
        config.tileNumber = value

    def onTeleportsChange(self, value):
        config.teleports = value

    def on_quit(self):
        self.parent.switch_to(0)

class ConnectingMenu(menu.Menu):
    def __init__(self):
        super(ConnectingMenu, self).__init__('Connecting...')
        self.button = MenuItem("Back",self.on_quit)
        createMenuLook(self, [self.button])
        self.ctrl = None

    def on_enter(self):
        super(ConnectingMenu, self).on_enter()
        self.title_label.text='Connecting...'
        self.ctrl = controller.NetworkedController(onFail=self.onFail,onSuccess=self.onSuccess)
        clock.schedule(self.ctrl.update)

    def onSuccess(self):
        clock.unschedule(self.ctrl.update)
        self.parent.switch_to(0)
        director.push(Client(self.ctrl))

    def onFail(self):
        if self.ctrl:
            clock.unschedule(self.ctrl.update)
            self.ctrl = None
        self.title_label.text = "Failed to connect." 

    def on_quit(self):
        self.parent.switch_to(3)

class NetworkGameClientMenu(menu.Menu):
    def __init__(self):
        super(NetworkGameClientMenu, self).__init__('Join Network Game')
        items = []

        items.append(MenuItem("Join", self.onJoin))
        items.append(EntryMenuItem("Host: ",self.onHostChange, config.host))
        items.append(MenuItem("Back", self.on_quit))
        createMenuLook(self, items)

    def onHostChange(self,value):
        config.host = value

    def on_quit(self):
        self.parent.switch_to(0)

    def onJoin(self):
        self.parent.switch_to(5)

class ServerMenu(menu.Menu):
    def __init__(self):
        super(ServerMenu, self).__init__('Start Server')
        self.serverProcess = None
        self.server = None
        self.queue = None
        self.statusQueue = None
        items = []

        self.startItem = MenuItem("Start", self.onStart)
        items.append(self.startItem)

        items.append(EntryMenuItem("Host address: ", self.onAddressChange, config.serverAddress))

        items.append(MenuItem("Back", self.on_quit))

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
            self.startItem.label = "Start (server already running)"
        except Exception,e:
            self.startItem.label = "Start (failed to start server)"
            print(e)
        self.startItem.update()

    def onAddressChange(self, value):
        config.serverAddress = value

class PlayerMenu(menu.Menu):
    def __init__(self):
        super(PlayerMenu, self).__init__('Players')
        items = []

        self.choosePlayer = MultipleMenuItem("", self.onPlayerChange, ["Player {0}".format(i+1) for i in range(len(config.players)) ], 0)
        items.append(self.choosePlayer)

        self.playerName = EntryMenuItem("    Name: ", self.onPlayerNameChange, unicode(config.players[0]["name"],"utf-8"))
        items.append(self.playerName)

        self.colors = list(colors.colors.keys())
        self.playerColor = MultipleMenuItem("    Color: ", self.onPlayerColorChange, self.colors, self.colors.index(config.players[0]["color"]))
        items.append(self.playerColor)

        self.playerPlaying = MultipleMenuItem("    Playing: ", self.onPlayerPlayingChange, ["False", "True"], 1)
        items.append(self.playerPlaying)

        items.append(MenuItem("Back", self.on_quit))

        createMenuLook(self, items)

    def onPlayerChange(self, idx):
        self.playerName.value = unicode(config.players[idx]["name"],"utf-8")
        self.playerColor.idx = self.colors.index(config.players[idx]["color"])
        self.playerColor.update()
        if config.players[idx]["playing"]:
            self.playerPlaying.idx = 1
        else:
            self.playerPlaying.idx = 0
        self.playerPlaying.update()

    def onPlayerNameChange(self, value):
        config.players[self.choosePlayer.idx]["name"] = value.encode("utf-8")

    def onPlayerColorChange(self, idx):
        config.players[self.choosePlayer.idx]["color"] = self.colors[idx]

    def onPlayerPlayingChange(self, idx):
        value = (idx == 1)
        config.players[self.choosePlayer.idx]["playing"] = value
    
    def on_quit(self):
        self.parent.switch_to(0)

class MainMenu(menu.Menu):
    def __init__(self):
        super(MainMenu, self).__init__('NoTitle')
        items = []
        items.append(MenuItem('Start Local Game', self.onLocalGame))
        items.append(MenuItem('Join Network Game', self.onNetworkGame))
        items.append(MenuItem('Start Server', self.onStartServer))
        items.append(MenuItem('Players', self.onPlayers))
        items.append(MenuItem('Game Options', self.onGameOptions))
        items.append(MenuItem('Quit', self.on_quit))
        createMenuLook(self, items)

    def onLocalGame(self):
        g = game.Game.gameFromConfig()
        ctrl = controller.Controller(g)
        director.push( Client(ctrl))

    def onStartServer(self):
        self.parent.switch_to(4)

    def on_quit(self):
        pyglet.app.exit()

    def onPlayers(self):
        self.parent.switch_to(1)

    def onNetworkGame(self):
        self.parent.switch_to(3)

    def onGameOptions(self):
        self.parent.switch_to(2)

class BackgroundLayer(layer.base_layers.Layer):
    def draw(self):
        gl.glPushMatrix()
        self.transform()
        rabbyt.clear((1,1,1))
        gl.glPopMatrix()

def getMenuScene():
    s = scene.Scene()
    s.add(BackgroundLayer())
    s.add(layer.base_layers.MultiplexLayer(MainMenu(), PlayerMenu(), GameMenu(), NetworkGameClientMenu(), ServerMenu(), ConnectingMenu()), z=1)
    return s
