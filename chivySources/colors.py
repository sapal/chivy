# coding=utf-8
colors = {
        "red":(255,0,0),
        "green":(0,255,0),
        "blue":(0,36,219),
        "yellow":(255,255,0),
        "white":(255,255,255),
        "black":(0,0,0),
        "purple":(160,32,240),
        "cyan":(0,255,255),
        "pink":(255,75,253),
        "darkgreen":(39,92,0)}

def htmlColor(colorName):
    r,g,b = colors[colorName]
    if colorName == "white":
        r,g,b = 190,190,190
    return "#{0:02x}{1:02x}{2:02x}".format(r,g,b)

def rgba(colorName, alpha=255):
    r,g,b = colors[colorName]
    return (r,g,b,alpha)

