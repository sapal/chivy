# coding=utf-8
import os
import os.path
import sys
from ast import literal_eval
import re
"""Game config."""

class Config(object):
    """Class for storing config"""

    """Game title:"""
    title = "Chivy"

    """Game version:"""
    version = "0.3"

    """Configuration, that should be saved and loaded:"""
    userConfig = ['locale', 'samplePlayerNames', 'userLevelsDir',
            'screenSize', 'fullScreen',  'players', 'host', 'serverAddress', 'botNames',
            'minBots', 'maxBots', 'bots', 'minBotSpeed', 'maxBotSpeed', 'botSpeed',
            'minPoints', 'maxPoints', 'points',
            'boardFilename', 'minTileNumber', 'maxTileNumber', 'tileNumber', 
            'tiles', 'minTeleports', 'maxTeleports', 'teleports', 'minItemNumber',
            'maxItemNumber', 'itemNumber']

    """Localization:"""
    locale = "pl_PL"

    """Entry directory:"""
    entryDir = os.path.dirname(os.path.abspath(sys.argv[0]))+os.sep
    """Code directory:"""
    codeDir = os.path.abspath(__file__)[:-10]
    sys.path[0] = codeDir
    codeDir += os.sep

    """Images directory:"""
    imagesDir = codeDir+".."+os.sep+"images"+os.sep
    """Fonts directory:"""
    fontsDir = codeDir+".."+os.sep+"fonts"+os.sep
    """Levels directory:"""
    levelsDir = codeDir+".."+os.sep+"levels"+os.sep
    """Fonts directory:"""
    fontsDir = codeDir+".."+os.sep+"fonts"+os.sep
    """User's directory:"""
    userDir = os.path.expanduser("~"+os.sep+".Chivy"+os.sep)
    """User's levels directory:"""
    userLevelsDir = userDir + "levels" + os.sep

    """Tiled directory:"""
    tiledDir = codeDir+".."+os.sep+"tiled"+os.sep
    """Translations directory:"""
    translationsDir = codeDir+".."+os.sep+"translations"+os.sep

    """Sprite size:"""
    spriteSize = 128

    """Sample player names:"""
    samplePlayerNames = ["Michał", "Ewa", "Szymon", "Bob", "Alice", "Jacek", "Placek", "Luna", "Hermiona", "Ginny"]

    """Bot names:"""
    botNames = [".:^LoL bOt^:.", "c_style_bot", "camelCaseBot", "h^bot", "#@$!!&^*", "CONSTANT_BOT" ]

    """Screen size:"""
    #screenSize = 1280,800
    #screenSize = 1024,756
    screenSize = 800,600
    #screenSize = 640,480

    """Full screen mode:"""
    fullScreen = True
    #fullScreen = False

    """Debug:"""
    dbg = False
    #dbg = True

    class PlayerConfig(object):
        def __init__(self, name="Player", color="red", playing=True):
            self.name = name
            self.color = color
            self.playing = playing

    """Players: (list of dict with keys: name(stirng), color(string), playing(bool) )"""
    players = [ {"name":"Michał", "color":"green", "prefferedKeybindings":0, "playing":True}, 
                {"name":"Ewa", "color":"red", "prefferedKeybindings":1, "playing":True}, 
                {"name":"Szymon", "color":"blue", "prefferedKeybindings":2, "playing":False}, 
                {"name":"Bob", "color":"black", "prefferedKeybindings":3, "playing":False}]

    """Host:"""
    host = "localhost"

    """Server address:"""
    serverAddress = "localhost"

    """Point limit:"""
    minPoints = 10
    maxPoints = 400
    points = 100

    """Number of bots:"""
    minBots = 0
    maxBots = 6
    bots = 3

    """Bot speed:"""
    minBotSpeed = 1
    maxBotSpeed = 6
    botSpeed = 3

    """Board filename: (None value indicates that board should be generated)"""
    boardFilename = None

    """Number of tiles:"""
    minTileNumber = 10
    maxTileNumber = 500
    tileNumber = 100

    """Tiles:"""
    tiles = "TT++LI"

    """Number of teleports:"""
    minTeleports = 0
    maxTeleports = 10
    teleports=3

    """Number of non-teleport items on board:"""
    minItemNumber = 0
    maxItemNumber = 50
    itemNumber = 4

    @staticmethod
    def saveConfig():
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        config = {}
        userDir = Config.userDir
        for c in Config.userConfig:
            config[c] = Config.__dict__[c]
        try:
            if not os.path.isdir(userDir):
                os.makedirs(userDir)
            f = open(userDir+"config.py", 'w')
            f.write(pp.pformat(config))
            f.close()
        except Exception,e:
            print(e)

    @staticmethod
    def loadConfig(fileName=None):
        """Passing None for fileName will use default userDir+"config.py". """
        if not fileName:
            fileName = Config.userDir + "config.py"
        try:
            config = literal_eval( (open(fileName).read()) )
        except Exception,e:
            print(e)
            return
        for c in Config.userConfig:
            if c in config:
                setattr(Config, c, config[c])
    #print(codeDir)

Config.loadConfig()
