#!/usr/bin/env python
# coding=utf-8
import sys
from optparse import OptionParser
import config
import game
import server
import random

def startClient(argv):
    import controller
    import gui
    parser = OptionParser()
    parser.add_option("-n", "--player-name", action="append", help="Specify player name.", dest="players")
    parser.add_option("-a", "--address", default="localhost", help="Server address.")
    parser.add_option("-p", "--port", default=9999, type="int", help="Server port.")
    options, args = parser.parse_args()
    if not options.players:
        options.players = [random.choice(config.samplePlayerNames)]
    ctrl = controller.NetworkedController(options.address, options.port, options.players)
    c = gui.Client(ctrl)
    c.run()

def startLocalGame(argv):
    import controller
    import gui
    import cocos
    parser = OptionParser()
    parser.add_option("-n", "--player-name", action="append", help="Specify player name.", dest="players")
    parser.add_option("-t", "--teleports", default=3, type="int", help="Number of teleports of each kind")
    parser.add_option("-b", "--board", default="TT++LI", help="Tiles used to create board.")
    parser.add_option("-o", "--number-of-tiles", default=100, type="int", help="Number of tiles on board", dest="number")
    parser.add_option("-s", "--random-seed", default=random.randint(0,100000), help="Random seed used to generate board", dest="seed")
    options, args = parser.parse_args(argv)
    if not options.players:
        options.players = random.sample(config.samplePlayerNames,2)

    board = game.Board()
    board.generateBoard(options.board, options.seed, options.number)
    g = game.Game(board=board, players={}, teleports=options.teleports)
    for name in options.players:
        g.addPlayer(name=name)

    gui.initialize()
    ctrl = controller.Controller(g)
    c = gui.Client(ctrl)
    cocos.director.director.run(cocos.scene.Scene(c))


def startServer(argv):
    parser = OptionParser()
    parser.add_option("-a", "--address", default="localhost", help="Server address.")
    parser.add_option("-p", "--port", default=9999, type="int", help="Server port.")
    parser.add_option("-t", "--teleports", default=3, type="int", help="Number of teleports of each kind")
    parser.add_option("-b", "--board", default="TT++LI", help="Tiles used to create board.")
    parser.add_option("-n", "--number-of-tiles", default=100, type="int", help="Number of tiles on board", dest="number")
    parser.add_option("-s", "--random-seed", type="int", default=random.randint(0,100000), help="Random seed used to generate board", dest="seed")
    options, args = parser.parse_args(argv)

    board = game.Board()
    board.generateBoard(options.board, options.seed, options.number)
    g = game.Game(board=board, players={}, teleports=options.teleports)

    s = server.OooServer(localaddr=(options.address, options.port), game=g)
    s.Launch()

def printHelp():
    print("""Usage:
    start.py (server|client|local) [options]""")

if __name__=="__main__":
    call = {"server":startServer,
            "client":startClient,
            "local":startLocalGame}
    if len(sys.argv) < 2 or sys.argv[1] not in call.keys():
        printHelp()
        sys.exit()
    call[sys.argv[1]](sys.argv[2:])

    
