# coding=utf-8
from pyglet.window import key

def createAbsoluteBindings(goNorth=key.UP, goWest=key.LEFT, goSouth=key.DOWN, goEast=key.RIGHT, switchActive=key.RCTRL, useItem=key.SLASH):
    return {goNorth:"goNorth", 
        goWest:"goWest",
        goSouth:"goSouth",
        goEast:"goEast",
        switchActive:"switchActive",
        useItem:"useItem"}

def createRelativeBindings(switchActive=key.RCTRL, move=key.UP, rotateCW=key.RIGHT, rotateCCW=key.LEFT):
    return {switchActive:"switchActive",
        move:"move",
        rotateCW:"rotateCW",
        rotateCCW:"rotateCCW"}

def add(bindings, action, key):
    """Adds binding action - key.
    Returns True on success and False otherwise"""
    if key in bindings and bindings[key] != action:
        return False
    else:
        bindings[key] = action
        return True

preconfigured = (ARROWS,WSAD,IJKL) = (
        createAbsoluteBindings(),
        createAbsoluteBindings(key.W, key.A, key.S, key.D, key.Q, key.E),
        createAbsoluteBindings(key.I, key.J, key.K, key.L, key.U, key.O))

