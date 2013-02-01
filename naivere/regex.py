# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:        Regex
# Purpose:
#
# Author:      Arakuma
#
# Created:     17/01/2013
#-------------------------------------------------------------------------------

from validator import *
from common_defs import *
from state_machine import *
from os import linesep

class Match(BaseObject):
    def __init__(self):
        self.matched = False
        self.begin = -1
        self.end = -1
        self.result = ""

class Regex:
    def __init__(self, pattern, isGreedy = False):
        self.log = ""
        self._isGreedy = isGreedy
        self._dfaStateTable = {}
        self._validator = Validator()
        self._reducedDfaState = None
        # pattern validation
        self.validationResult = self._validator.validate(pattern)
        if not self.validationResult.error == ERR_NONE:
            self._writeLog("Pattern error %s at %d with length %d" % (self.validationResult.error, self.validationResult.error_at, self.validationResult.error_len) )
        else:
            self._writeLog("Formatted pattern: %s" % self.validationResult.formatted_parttern)
            # pattern post-fixed
            postFixedPatter = self._validator.postFix(self.validationResult.formatted_parttern)
            self._writeLog("Post fixed pattern: %s" % postFixedPatter)
            # nfa
            State.resetIdCounter()
            nfaState = self._createNfa(postFixedPatter)
            self._writeLog("NFA states table:")
            self._printStateTable(nfaState)
            # dfa
            self._writeLog( "*" * 80 )
            State.resetIdCounter()
            dfaState = self._createDfa(nfaState)
            self._writeLog("DFA states table:")
            self._printStateTable(dfaState)
            # reduced dfa
            self._writeLog( "*" * 80 )
            State.resetIdCounter()
            self._reducedDfaState = self._reduceDfa(dfaState)
            self._writeLog("DFA states table:")
            self._printStateTable(self._reducedDfaState)

    def _writeLog(self, log):
        self.log += log + "\n"

    def _createNfa(self, pattern):
        nfaStack = []
        isEscape = False
        for char in pattern:
            if not isEscape and char == SYM_ESCAPE:
                isEscape = True
                continue
            if isEscape:
                exp = NfaExp()
                exp.stateFrom.addNextState(char, exp.stateTo)
                nfaStack.append(exp)
                isEscape = False
                continue

            if char == SYM_0_OR_MORE:
                # a*
                expA = nfaStack.pop()
                exp = NfaExp()
                expA.stateTo.addNextState(SYM_EPSILON, expA.stateFrom)
                expA.stateTo.addNextState(SYM_EPSILON, exp.stateTo)
                exp.stateFrom.addNextState(SYM_EPSILON, expA.stateFrom)
                exp.stateFrom.addNextState(SYM_EPSILON, exp.stateTo)
                nfaStack.append(exp)
            elif char == SYM_1_OR_MORE:
                # a+ = a.a*
                expA = nfaStack.pop()
                exp = NfaExp()
                exp.stateFrom.addNextState(SYM_EPSILON, expA.stateFrom)
                exp.stateTo.addNextState(SYM_EPSILON, expA.stateFrom)
                expA.stateTo.addNextState(SYM_EPSILON, exp.stateTo)
                nfaStack.append(exp)
            elif char == SYM_0_OR_1:
                # a? = a|ep
                expA = nfaStack.pop()
                exp = NfaExp()
                exp.stateFrom.addNextState(SYM_EPSILON, expA.stateFrom)
                exp.stateFrom.addNextState(SYM_EPSILON, exp.stateTo)
                expA.stateTo.addNextState(SYM_EPSILON, exp.stateTo)
                nfaStack.append(exp)
            elif char == SYM_ALTERNATE:
                # a|b
                expB = nfaStack.pop()
                expA = nfaStack.pop()
                exp = NfaExp()
                expA.stateTo.addNextState(SYM_EPSILON, exp.stateTo)
                expB.stateTo.addNextState(SYM_EPSILON, exp.stateTo)
                exp.stateFrom.addNextState(SYM_EPSILON, expA.stateFrom)
                exp.stateFrom.addNextState(SYM_EPSILON, expB.stateFrom)
                nfaStack.append(exp)
            elif char == SYM_CONCAT:
                # a.b
                expB = nfaStack.pop()
                expA = nfaStack.pop()
                expA.stateTo.addNextState(SYM_EPSILON, expB.stateFrom)
                exp = NfaExp(False)
                exp.stateFrom = expA.stateFrom
                exp.stateTo = expB.stateTo
                nfaStack.append(exp)
            elif char == SYM_ONE_CHAR:
                exp = NfaExp()
                exp.stateFrom.addNextState(SYM_ANY_CHAR, exp.stateTo)
                nfaStack.append(exp)
            elif char == SYM_EXCLUDE:
                expA = nfaStack.pop()
                expDummy = NfaExp()
                expDummy.stateFrom.addNextState(SYM_DUMMY, expDummy.stateTo)
                expA.stateTo.addNextState(SYM_EPSILON, expDummy.stateFrom)
                expAny = NfaExp()
                expAny.stateFrom.addNextState(SYM_ANY_CHAR, expAny.stateTo)
                exp = NfaExp()
                exp.stateFrom.addNextState(SYM_EPSILON, expA.stateFrom)
                exp.stateFrom.addNextState(SYM_EPSILON, expAny.stateFrom)
                expA.stateTo.addNextState(SYM_EPSILON, exp.stateTo)
                expAny.stateTo.addNextState(SYM_EPSILON, exp.stateTo)
                nfaStack.append(exp)
            else:
                exp = NfaExp()
                exp.stateFrom.addNextState(char, exp.stateTo)
                nfaStack.append(exp)
        # the final express should be the answer here
        assert len(nfaStack) == 1
        finalExp = nfaStack.pop()
        finalExp.stateTo.isFinal = True
        return finalExp.stateFrom

    def _createDfa(self,nfaState):
        allStates = []
        allSymbols = []
        self._getAllSymbolsAndStates(nfaState,allSymbols,allStates)
        allSymbols.remove(SYM_EPSILON)

        closure = self._getEpsilonClosure(nfaState)
        dfaStartState = State()
        if self._isFinalGroup(closure):
            dfaStartState.isFinal = True

        self._addDfaRecord(dfaStartState,closure)
        tClosures = []
        while not self._getNextUnmarkedDfaState() == None:
            tState = self._getNextUnmarkedDfaState()
            self._markDfaState(tState)
            tClosures = self._getClosuresByDfaState(tState)
            for symbol in allSymbols:
                moves = self._getMovesFromStates(symbol,tClosures)
                if not len(moves) == 0:
                    closure = self._getEpsilonClosureForStates(moves)
                    uState = self._getDfaStateByClosure(closure)
                    if uState is None:
                        uState = State()
                        if self._isFinalGroup(closure):
                            uState.isFinal = True
                        self._addDfaRecord(uState,closure)
                    tState.addNextState(symbol,uState)
        return dfaStartState

    def _reduceDfa(self,dfaState):
        allStates = []
        allSymbols = []
        self._getAllSymbolsAndStates(dfaState,allSymbols,allStates)

        reducedDfaState = None
        #1 group partition
        statesGroups = self._partitionDfaStates(allSymbols,allStates)
        #2 select start and final states
        for group in statesGroups:
            firstStateInGroup = group[0]
            if dfaState in group:
                reducedDfaState = firstStateInGroup
            if self._isFinalGroup(group):
                firstStateInGroup.isFinal = True
            if len(group) == 1:
                continue
            #3 remove the selected state
            group.remove(firstStateInGroup)
            replaceCount = 0
            for replacedState in group:
                allStates.remove(replacedState)
                for state in allStates:
                    replaceCount += state.replaceState(replacedState,firstStateInGroup)
        #4 clear dead states
        allStates = [state for state in allStates if not state.isDead()]
        return reducedDfaState

    def _partitionDfaStates(self,symbols,states):
        allGroups = []
        statesMapping = Map()
        finalStates = []
        nonFinalStates = []
        for state in states:
            if state.isFinal:
                finalStates.append(state)
            else:
                nonFinalStates.append(state)
        if len(nonFinalStates) > 0:
            allGroups.append(nonFinalStates)
        allGroups.append(finalStates)
        enumIndex = 0
        while enumIndex < len(symbols):
            symbol = symbols[enumIndex]
            enumIndex += 1
            partitionIndex = 0
            while partitionIndex < len(allGroups):
                toPartition = allGroups[partitionIndex]
                partitionIndex += 1
                if len(toPartition) == 0 or len(toPartition) == 1:
                    continue
                for state in toPartition:
                    nextStates = state.getNextStates(symbol)
                    if not nextStates == None:
                        assert(len(nextStates) == 1)
                        statesMapping.add( tuple(self._findGroup(allGroups, nextStates[0])), state )
                    else:
                        statesMapping.add( None, state )
                if len(statesMapping) > 1:
                    allGroups[:] = (group for group in allGroups if group != toPartition)
                    for key in statesMapping:
                        allGroups.append(statesMapping[key])
                    partitionIndex = 0
                    enumIndex = 0
                statesMapping.clear()
        return allGroups

    def _findGroup(self, groups, state):
        for group in groups:
            if state in group:
                return group
        return None

    def _getMovesFromStates(self,symbol,states):
        allMoves = []
        for state in states:
            moves = state.getNextStates(symbol)
            if not moves == None:
                allMoves = list(set(allMoves)|set(moves))
        return allMoves

    def _addDfaRecord(self,dfaState,closure):
        record = DfaStateRecord()
        record.closure = closure
        self._dfaStateTable[dfaState] = record

    def _getDfaStateByClosure(self,closure):
        for state in self._dfaStateTable:
            if self._dfaStateTable[state].closure == closure:
                return state
        return None

    def _getClosuresByDfaState(self,dfaState):
        if self._dfaStateTable.has_key(dfaState):
            return self._dfaStateTable[dfaState].closure
        return None

    def _getNextUnmarkedDfaState(self):
        for state in self._dfaStateTable:
            if not self._dfaStateTable[state].marked:
                return state
        return None

    def _markDfaState(self,dfaState):
        self._dfaStateTable[dfaState].marked = True

    def _getAllDfaStates(self):
        return list(self._dfaStateTable.keys())

    def _isFinalGroup(self,stateGroup):
        for state in stateGroup:
            if state.isFinal:
                return True
        return False

    def _getEpsilonClosure(self,nfaState):
        processed = []
        unprocessed = []
        unprocessed.append(nfaState)
        while len(unprocessed) > 0:
            state = unprocessed[0]
            epsilonStates = state.getNextStates(SYM_EPSILON)
            processed.append(state)
            unprocessed[:] = (item for item in unprocessed if item != state)
            if not epsilonStates == None:
                for epsilonState in epsilonStates:
                    if not epsilonState in processed:
                        unprocessed.append(epsilonState)
        return processed

    def _getEpsilonClosureForStates(self,states):
        closure = []
        for state in states:
            stateClosure = self._getEpsilonClosure(state)
            closure = list(set(closure)|set(stateClosure))
        return closure

    def _getAllSymbolsAndStates(self,startState,allSymbols,allStates):
        toCheckedStates = []
        toCheckedStates.append(startState)
        while len(toCheckedStates) > 0:
            state = toCheckedStates[0]
            allStates.append(state)
            toCheckedStates[:] = (item for item in toCheckedStates if item != state)
            for symbol in state.getAllKeys():
                if not symbol in allSymbols:
                    allSymbols.append(symbol)
                nextStates = state.getNextStates(symbol)
                for nextState in nextStates:
                    if not nextState in allStates:
                        toCheckedStates.append(nextState)

    def _printStateTable(self,startState):
        allStates = []
        allSymbols = []
        self._getAllSymbolsAndStates(startState,allSymbols,allStates)
        if SYM_EPSILON in allSymbols:
            allSymbols.remove(SYM_EPSILON)
            allSymbols.append(SYM_EPSILON)

        cellWidth = 11
        lineWidth = cellWidth * ( len(allSymbols) + 1 )
        self._writeLog( "|" + "-" * lineWidth + "|" )
        header = "| %-9s" % " "
        for symbol in allSymbols:
            header += "|" + " %-9s" % symbol
        self._writeLog( header + " |" )
        self._writeLog( "|" + "-" * lineWidth + "|" )

        for state in allStates:
            row = "|" + " %-9s" % ( {True:">",False:""}[state==startState] + str(state) )
            for symbol in allSymbols:
                nextStates = state.getNextStates(symbol)
                statesStr = ""
                if nextStates == None:
                    statesStr = "-"
                else:
                    for nextState in nextStates:
                        statesStr += str(nextState) + ","
                row += "|" + " %-9s" % statesStr
            row += " |"
            self._writeLog( row )

        self._writeLog( "|" + "-" * lineWidth + "|" )

    def matches(self,stringToMatch):
        matches = []
        index = 0
        while index < len(stringToMatch):
            match = self.match(stringToMatch[index:])
            if match.matched:
                match.begin += index
                match.end += index
                index = match.end + 1
                matches.append(match)
            else:
                break
        return matches

    def match(self,stringToMatch):
        m = Match()
        if stringToMatch == None or self._reducedDfaState == None:
            return m
        matchIndex = 0
        searchRange = len(stringToMatch) - 1
        currentState = self._reducedDfaState
        while matchIndex <= searchRange:
            if self._isGreedy and self._isWildcard(currentState):
                if m.begin == -1:
                    m.begin = matchIndex
                matchIndex = self._getWildcardIndex(currentState,stringToMatch,matchIndex,searchRange)
            nextState = currentState.getNextState(stringToMatch[matchIndex])
            if nextState == None:
                nextState = currentState.getNextState(SYM_ANY_CHAR)
            if not nextState == None:
                if m.begin == -1:
                    m.begin = matchIndex
                if nextState.isFinal:
                    if not self.validationResult.match_end or matchIndex == searchRange:
                        m.matched = True
                        m.end = matchIndex
                        if not self._isGreedy:
                            break
                currentState = nextState
                matchIndex += 1
            else:
                if not self.validationResult.match_start and not m.matched:
                    if m.begin == -1:
                        matchIndex += 1
                    else:
                        matchIndex = m.begin + 1
                    m.begin = -1
                    m.end = -1
                    currentState = self._reducedDfaState
                else:
                    break
        if not m.matched:
            if not self._reducedDfaState.isFinal:
                m.begin = -1
                m.end = -1
            else:
                m.matched = True
                m.begin = 0
                m.end = -1
        else:
            m.result = stringToMatch[m.begin:m.end+1]
        return m

    def _isWildcard(self,state):
        return not None == state.getNextState(SYM_ANY_CHAR)

    def _getWildcardIndex(self,state,string,index,searchRange):
        wildCardIndex = 0
        while index <= searchRange:
            nextState = state.getNextState(string[index])
            if not nextState == None:
                wildCardIndex = index
            index += 1
        return wildCardIndex
