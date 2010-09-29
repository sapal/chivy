# coding=utf-8
from pyglet.window import key

def createAbsoluteBindings(goNorth=key.UP, goWest=key.LEFT, goSouth=key.DOWN, goEast=key.RIGHT, switchActive=key.RCTRL, useItem=key.RSHIFT):
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

def createAbsoulteTextBindings(goNorth=None, goWest=None, goSouth=None, goEast=None, switchActive=None, useItem=None):
    bindings = createAbsoluteBindings(goNorth, goWest, goSouth, goEast, switchActive, useItem)
    if None in bindings:
        del bindings[None]
    return bindings

def add(bindings, action, key):
    """Adds binding action - key.
    Returns True on success and False otherwise"""
    if key in bindings and bindings[key] != action:
        return False
    else:
        bindings[key] = action
        return True


preconfigured = (ARROWS,WSAD,IJKL,NUMPAD) = (
        (createAbsoluteBindings(), {}),
        (createAbsoluteBindings(key.W, key.A, key.S, key.D, key.Q, key.E), createAbsoulteTextBindings("W","A","S","D","Q","E")),
        (createAbsoluteBindings(key.I, key.J, key.K, key.L, key.U, key.O), createAbsoulteTextBindings("I","J","K","L","U","O")),
        (createAbsoluteBindings(key.NUM_8, key.NUM_4, key.NUM_5, key.NUM_6, key.NUM_7, key.NUM_9), {}) )

