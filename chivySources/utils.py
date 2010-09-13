# coding=utf-8

import random
class RandomQueue(object):
    def __init__(self, random=random):
        self.ques = {}
        self._top = None
        self._topType = None
        self._topOK = False
        self.random = random

    def top(self):
        if not self._topOK:
            self._getTop()
        return self._top

    def pop(self):
        res = self.top()
        #print("{3}\tPOP topOk:{2} res:{0}, resType:{1}".format(res, self._topType,self._topOK,len(self)))
        self.ques[self._topType][0].remove(res)
        self._topOK = False
        return res

    def __nonzero__(self):
        for q,p in self.ques.values():
            if q and p:
                return True
        return False

    def __repr__(self):
        return str(self.ques)

    def newType(self, type, prop):
        if type in self.ques.keys():
            self.ques[type] = (self.ques[type], prop)
        else:
            self.ques[type] = ([], prop)

    def push(self, item, type):
        #print("{2}\tpush({0},{1})".format(item,type,len(self)))
        self.ques[type][0].append(item)

    def _getTop(self):
        prop = 0
        for q, p in self.ques.values():
            prop += p*len(q)
        r = self.random.random()*prop
        #print("r:{0}/{1} ({2})".format(r,prop,self.__nonzero__()))
        for k, (q, p) in self.ques.items():
            if r < p*len(q) and q:
                self._top = self.random.choice(q)
                self._topType = k
                self._topOK = True
                #print("NewTop: [{0}] = {1}".format(self._topType, self._top))
                break
            else:
                r -= p*len(q)
    def __len__(self):
        l = 0
        for q,p in self.ques.values():
            l += len(q)
        return l

def str2tuple(s):
    """Convert tuple-like strings to real tuples.
    eg '(1,2,3,4)' -> (1, 2, 3, 4)
    """
    if s[0] + s[-1] != "()":
        raise ValueError("Badly formatted string (missing brackets).")
    items = s[1:-1] # removes the leading and trailing brackets
    items = items.split(',')
    L = [int(x.strip()) for x in items] # clean up spaces, convert to ints
    return tuple(L)

def str2bool(s):
    return s == "True" or s == "1"
