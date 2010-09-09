# coding=utf-8

import game
import random
class BaseAI(object):
    """Base class fo AI."""
   
    def __init__(self, controller,playerID):
        self.controller = controller
        self.playerID = playerID
        self.speed = 2+2*random.random()
        self.time = 0

    def update(self,dt):
        self.time += dt
        while self.time >= 1.0/self.speed:
            self.time -= 1.0/self.speed
            action = self.chooseAction()
            if action:
                self.sendInput(action)


    def chooseAction(self):
        """This method should return action that should be performed (one
        of Player().actions.keys()) or None if no action should be performed."""
        return None


    def goAction(self, direction):
        return ["goNorth", "goWest", "goSouth", "goEast"][direction]

    @property
    def activeOooMan(self):
        return self.controller.game.players[self.playerID].activeOooMan

    @property
    def board(self):
        return self.controller.game.board

    def intPosition(self, gameObject):
        x,y = gameObject.position
        return (int(round(x)), int(round(y)))

    def sendInput(self, action):
        self.controller.sendInput(self.playerID, action)

class RandomAI(BaseAI):
    """Random walk AI."""
    
    def chooseAction(self):
        r = random.random()
        if r<0.2:
            return None
        elif r<0.4:
            return "switchActive"
        elif r<0.6:
            return "useItem"
        else:
            d = int(10*(r-0.6))
            return self.goAction(d)

