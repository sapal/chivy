#!/usr/bin/env python
# coding=utf-8
from PIL import Image, ImageMath
from PIL.ImageColor import getrgb
import os
import config
import re

def difference1(source, color):
    """When source is bigger than color"""
    return (source - color) / (255.0 - color)

def difference2(source, color):
    """When color is bigger than source"""
    return (color - source) / color


def color_to_alpha(image, color=None):
    image = image.convert('RGBA')
    width, height = image.size

    color = map(float, color)
    img_bands = [band.convert("F") for band in image.split()]

    # Find the maximum difference rate between source and color. I had to use two
    # difference functions because ImageMath.eval only evaluates the expression
    # once.
    alpha = ImageMath.eval(
        """float(
            max(
                max(
                    max(
                        difference1(red_band, cred_band),
                        difference1(green_band, cgreen_band)
                    ),
                    difference1(blue_band, cblue_band)
                ),
                max(
                    max(
                        difference2(red_band, cred_band),
                        difference2(green_band, cgreen_band)
                    ),
                    difference2(blue_band, cblue_band)
                )
            )
        )""",
        difference1=difference1,
        difference2=difference2,
        red_band = img_bands[0],
        green_band = img_bands[1],
        blue_band = img_bands[2],
        cred_band = color[0],
        cgreen_band = color[1],
        cblue_band = color[2]
    )

    # Calculate the new image colors after the removal of the selected color
    new_bands = [
        ImageMath.eval(
            "convert((image - color) / alpha + color, 'L')",
            image = img_bands[i],
            color = color[i],
            alpha = alpha
        )
        for i in xrange(3)
    ]

    # Add the new alpha band
    new_bands.append(ImageMath.eval(
        "convert(alpha_band * alpha, 'L')",
        alpha = alpha,
        alpha_band = img_bands[3]
    ))

    return Image.merge('RGBA', new_bands)

def whiteAlpha(color,alpha):
    if alpha >= 200.0:
        return color
    return 255.0

def replaceColor(image,color,imageOut,colorOut):
    image = Image.open(image)
    image = image.convert("RGBA")
    background = Image.new('RGBA', image.size, colorOut)
    bands = background.split()
    alpha = (image.split())[3]
    alpha = ImageMath.eval("convert(255.0 * max(alpha-254.0,0.0), 'L')",
            alpha = alpha)
    bands = [
            ImageMath.eval("convert( min(255-alpha + color,255.0), 'L')",
                color = bands[i],
                alpha = alpha) for i in range(3)
            ]
    bands = (bands[0],bands[1],bands[2],alpha)
    background = Image.merge('RGBA', bands)
    #background = background.convert('RGB')
    image = color_to_alpha(image, color)
    background.paste(image.convert('RGB'),mask=image)
    background.save(imageOut)

if __name__ == "__main__":
    r = re.compile(r"OooMan-red-.*128\.png")
    colors = {"green":(0,255,0,0),
            "blue":(0,0,255,0),
            "yellow":(255,255,0,0)}
    for s in [128]:
        for c in colors.keys():
            for f in os.listdir(config.imagesDir):
                if r.match(f):
                    nf = "OooMan-"+c+f[10:]
                    replaceColor(config.imagesDir+os.sep+f,getrgb("red"),config.imagesDir+os.sep+nf,colors[c])
