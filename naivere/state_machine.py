# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        State Machines
# Purpose:
#
# Author:      Arakuma
#
# Created:     17/01/2013
#-------------------------------------------------------------------------------

from utils import BaseObject, Map

class State(BaseObject):
    idCounter = 0

    def __init__(self):
        self.id = State.idCounter
        State.idCounter += 1
        self.map = Map()
        self.isFinal = False

    def __str__(self):
        stateName = "S" + str(self.id)
        if self.isFinal:
            stateName = "{%s}" % stateName
        return stateName

    def addNextState(self, symbol, state):
        self.map.add(symbol, state)

    def getNextStates(self, symbol):
        if symbol in self.map:
            return self.map[symbol]
        else:
            return None

    def getNextState(self, symbol):
        if self.map.has_key(symbol):
            return self.map[symbol][0]
        return None

    def removeNextStates(self, symbol):
        del(self.map[symbol])

    def replaceState(self, oldState, newState):
        replacementCount = 0
        for key in self.map.keys():
            states = self.map[key]
            for index,state in enumerate(states):
                if state == oldState:
                    states[index] = newState
                    replacementCount += 1
        return replacementCount

    def isDead(self):
        if self.isFinal or len(self.map) == 0:
            return False
        for key in self.map.keys():
            states = self.map[key]
            for state in states:
                if state == self:
                    return False
        return True

    def getAllKeys(self):
        return self.map.keys()

    @staticmethod
    def resetIdCounter():
        State.idCounter = 0

class NfaExp(BaseObject):
    def __init__(self, createStates = True):
        if createStates:
            self.stateFrom = State()
            self.stateTo = State()
        else:
            self.stateFrom = None
            self.stateTo = None

class DfaStateRecord(BaseObject):
    def __init__(self):
        self.closure = []
        self.marked = False
