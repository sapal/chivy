#!/usr/bin/env python
# coding=utf-8

import game
import xml.dom.minidom
import re
import kinds
import sys
from translation import gettext as _

def parseDimensions(domMap, board):
    w = int(domMap.getAttribute("width"))
    h = int(domMap.getAttribute("height"))
    board.dimensions = w,h

def parseTileset(tileset, tilesets):
    first = int(tileset.getAttribute("firstgid"))
    if re.match(".*Teleports.tsx$", tileset.getAttribute("source")):
        for kind in sorted(kinds.CLASSIC.keys()):
            tilesets[first] = ("teleport", kind)
            first += 1
    elif re.match(".*Tiles.tsx$", tileset.getAttribute("source")):
        for kind in sorted(game.BoardTile.kinds.keys()):
            for d in (0,3,2,1):
                tilesets[first] = ("tile", kind, d)
                first += 1
    elif re.match(".*Border.tsx$", tileset.getAttribute("source")):
        tilesets[first] = ("border",)

def parseLayer(layer, layers, tilesets, dimensions):
    w, h = dimensions
    name = layer.getAttribute("name")
    data = layer.getElementsByTagName("data")[0]
    x, y = 0, h-1
    layer = {}
    for tile in data.getElementsByTagName("tile"):
        gid = int(tile.getAttribute("gid"))
        if gid > 0:
            layer[(x,y)] = tilesets[gid]
        x += 1
        if x == w:
            x = 0
            y -= 1
    if re.match("Teleports", name):
        if "Teleports" not in layers:
            layers["Teleports"] = {}
        layers["Teleports"][name] = layer
    else:
        layers[name] = layer

def generateBoard(board, layers):
    for pos,tile in layers["Map"].items():
        if tile[0] != "tile":
            continue
        board.tiles[pos] = game.BoardTile(pos, tile[2], tile[1], False)
    if "Border" in layers:
        for pos,tile in layers["Border"].items():
            if tile[0] != "border" or pos not in board.tiles:
                continue
            board.tiles[pos].border = True
    teleports = {}
    if "Teleports" in layers:
        for layerName in sorted(layers["Teleports"].keys()):
            telLayer = layers["Teleports"][layerName]
            for pos,tile in telLayer.items():
                if tile[0] != "teleport" or pos not in board.tiles:
                    continue
                kind = tile[1]
                if kind not in teleports:
                    teleports[kind] = []
                teleports[kind].append(pos)
    for k,tel in teleports.items():
        for i in range(len(tel)):
            teleport = game.Teleport(tel[i-1], k)
            teleport.target = tel[i]
            board.items.append(teleport)

def getBoard(tmxFile):
    b = game.Board()
    b.tiles = {}
    b.items = []
    tilesets = {}
    layers = {}
    dom = xml.dom.minidom.parse(tmxFile)
    parseDimensions(dom.getElementsByTagName("map")[0], b)
    for t in dom.getElementsByTagName("tileset"):
        parseTileset(t, tilesets)
    for l in dom.getElementsByTagName("layer"):
        parseLayer(l, layers, tilesets, b.dimensions)
    #print("layers:{0}, tilesets:{1}".format(layers, tilesets))
    generateBoard(b, layers)
    return b

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(_("Usage: {0} someBoard.tmx").format(sys.argv[0]))
        sys.exit()
    tmxFile = sys.argv[1]
    outFile = tmxFile[0:-3] + "brd"
    getBoard(tmxFile).saveAsXml(outFile)
