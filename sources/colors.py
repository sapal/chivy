# coding=utf-8
colors = {
        "red":(255,0,0),
        "green":(0,255,0),
        "blue":(0,36,219),
        "yellow":(255,255,0),
        "white":(255,255,255),
        "black":(0,0,0),
        "purple":(160,32,240),
        "cyan":(0,255,255)}
def htmlColor(colorName):
    r,g,b = colors[colorName]
    return "#{0:x}{1:x}{2:x}".format(r,g,b)


