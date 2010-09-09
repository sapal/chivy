# coding=utf-8
import os
import os.path
import sys
from ast import literal_eval
"""Game config."""

class Config(object):
    """Class for storing config"""

    """Configuration, that should be saved and loaded:"""
    userConfig = ['locale', 'imagesDir', 'fontsDir', 'levelsDir', 'spriteSize', 'samplePlayerNames',
            'screenSize', 'fullScreen',  'players', 'host', 'serverAddress',
            'boardFilename', 'minTileNumber', 'maxTileNumber', 'tileNumber', 
            'tiles', 'minTeleports', 'maxTeleports', 'teleports', 'minItemNumber',
            'maxItemNumber', 'itemNumber']

    """Localization:"""
    locale = "pl_PL"

    """Code directory:"""
    codeDir = os.path.dirname(os.path.abspath(sys.argv[0]))+os.sep
    """Images directory:"""
    imagesDir = codeDir+".."+os.sep+"images"+os.sep
    """Fonts directory:"""
    fontsDir = codeDir+".."+os.sep+"fonts"+os.sep
    """Levels directory:"""
    levelsDir = codeDir+".."+os.sep+"levels"+os.sep
    """Fonts directory:"""
    fontsDir = codeDir+".."+os.sep+"fonts"+os.sep
    """User directory:"""
    userDir = os.path.expanduser("~"+os.sep+".NoName"+os.sep)

    """Tiled directory:"""
    tiledDir = codeDir+".."+os.sep+"tiled"+os.sep

    """Sprite size:"""
    spriteSize = 128

    """Sample player names:"""
    samplePlayerNames = ["Michał", "Ewa", "Szymon", "Bob", "Alice", "Jacek", "Placek", "Luna", "Hermiona", "Ginny"]

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
    players = [ {"name":"Michał", "color":"green", "playing":True}, 
                {"name":"Ewa", "color":"red", "playing":True}, 
                {"name":"Szymon", "color":"blue", "playing":False}, 
                {"name":"Bob", "color":"black", "playing":False}]

    """Host:"""
    host = "localhost"

    """Server address:"""
    serverAddress = "localhost"

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
        config = {}
        userDir = Config.userDir
        for c in Config.userConfig:
            config[c] = Config.__dict__[c]
        try:
            if not os.path.isdir(userDir):
                os.makedirs(userDir)
            f = open(userDir+"config.py", 'w')
            f.write(str(config))
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
