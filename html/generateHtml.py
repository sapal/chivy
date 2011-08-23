# coding=utf-8
import re
import sys
import os

menuItems = []

def generateMenu(output):
    outputFile = output[:output.rfind('.')]
    outputName = os.path.split(output)[1]
    outputName = outputName[:outputName.rfind('.')]
    items = []
    for name, href in menuItems:
        cls = "menu"
        if href == outputName:
            cls = "menuSelf"
        items.append(u'<div class="menuItem"><a class="{cls}Href" href="{href}.html">{name}</a></div>'.format(cls=cls, href=href, name=unicode(name,"utf-8")))
    s = u"\n\t\t".join(items)+'<br class="clear"/>'
    f = open(outputFile+".menu", "w")
    f.write(s.encode("utf-8"))
    f.close()

def generateHtml(template, output):
    template = open(template).read()
    outputName = output[:output.rfind('.')]
    repl = {}
    for m in re.finditer("<!--([^>]*)-->",template):
        group = m.group(1)
        print(group)
        if group not in repl:
            try:
                repl[group] = open(".".join([outputName, group])).read()
            except Exception,e:
                print(e)
                try:
                    repl[group] = open(".".join(["default", group])).read()
                except Exception,e:
                    print(e)
    for k,v in repl.items():
        template = template.replace("<!--{0}-->".format(k), v.strip())
    f = open(output, 'w')
    f.write(template)
    f.close()

if __name__=="__main__":
    if len(sys.argv) < 3:
        print("Usage: {0} template menu output.html".format(sys.argv[0]))
        sys.exit()
    menuItems = eval(open(sys.argv[2]).read()) 
    generateMenu(sys.argv[3])
    generateHtml(sys.argv[1], sys.argv[3])

    
    
