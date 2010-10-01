# coding=utf-8
import re
import sys
import os

menuItems = []

def generateMenu(output):
    outputFile = output[:output.rfind('.')]
    outputName = os.path.split(output)[1]
    outputName = outputName[:outputName.rfind('.')]
    s = u"""<table class="border">
        <tr><td class="borderLT"></td><td class="borderH"></td><td class="borderRT"></td></tr>
        <tr><td class="borderV"></td>
            <td class="menu"><table width="100%"><tr>"""
    items = []
    prc=100.0/len(menuItems)
    for name, href in menuItems:
        cls = "menu"
        if href == outputName:
            cls = "menuSelf"
        items.append(u'<td width="{prc}%" class="{cls}Td"><a class="{cls}Href" href="{href}.html">{name}</a></td>'.format(cls=cls, href=href, name=unicode(name,"utf-8"), prc=prc))
    s += u"\n".join(items) + u"""</tr></table></td>
            <td class="borderV"></td></tr>
        <tr><td class="borderLB"></td><td class="borderH"></td><td class="borderRB"></td></tr></table>"""
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

    
    