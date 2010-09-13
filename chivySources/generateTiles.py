#!/usr/bin/env python
# coding=utf-8
from PIL import Image, ImageMath
import kinds
import game
from config import Config as config
from generateColors import replaceColor

def concatenate(imageList, rotate=False):
    images = map(Image.open, imageList)
    if rotate:
        w = 2*sum(i.size[0] + i.size[1] for i in images)
        h = max( max(i.size[0],i.size[1]) for i in images)
    else:
        w = sum(i.size[0] for i in images)
        h = max(i.size[1] for i in images)
    result = Image.new("RGBA", (w,h))
    x = 0
    for i in images:
        if rotate:
            for r in range(4):
                img = i.rotate(90*r)
                result.paste(img, (x,0))
                x += i.size[0]
        else:
            result.paste(i, (x, 0))
            x += i.size[0]
    return result

def tile(nameList, output, rotate=False):
    imageList = [ config.imagesDir + name for name in nameList]
    concatenate(imageList, rotate).save(config.tiledDir + output)

if __name__ == "__main__":
    tile(["teleport-{0}128.png".format(kind) for kind in sorted(kinds.CLASSIC.keys())], "teleport-tiles.png" )
    replaceColor(config.tiledDir + "teleport-tiles.png", (96,96,96), config.tiledDir + "teleport-tiles.png", (255,0,0))
    tile(["tile{0}128.png".format(kind) for kind in sorted(game.BoardTile.kinds.keys())], "tile-tiles.png", True )




