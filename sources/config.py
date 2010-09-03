# coding=utf-8
import os
import os.path
import sys
"""Game config."""

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
userDir = os.path.expanduser("~"+os.sep+"NoName"+os.sep)
"""Sprite size:"""
spriteSize = 128

"""Sample player names:"""
samplePlayerNames = ["Michał","Ewa","Szymon","Bob","Alice"]

"""Screen size:"""
#screenSize = 1280,800
screenSize = 1024,756
#screenSize = 800,600
#screenSize = 640,480

"""Full screen mode:"""
fullScreen = True
#fullScreen = False

"""Debug:"""
dbg = False
#dbg = True

if os.path.isfile(userDir+os.sep+"config.py"):
    try:
        exec open(userDir+os.sep+"config.py").read()
    except Exception,e:
        print(e)
