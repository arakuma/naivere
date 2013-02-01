# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        Patter Validator
# Purpose:     Pattern validator, also modify the patter to a
#              possible well-formatted version
#
# Author:      Arakuma
#
# Created:     17/01/2013
#-------------------------------------------------------------------------------

from common_defs import *
from utils import BaseObject
from collections import deque

class ValidationResult(BaseObject):
    '''Presents a result of a time of validation'''
    def __init__(self):
        self.error = ERR_NONE
        self.error_at = 0
        self.error_len = 0
        self.formatted_parttern = ""
        self.match_start = False
        self.match_end = False

class Validator():
    def __init__(self):
        self._isConcat     = False
        self._isAlternate  = False
        self._pattern      = ""
        self._patternLen   = 0
        self._finalPattern = ""
        self._curPos       = -1
        self._curChr       = CHR_NULL
        self._result       = ValidationResult()

        self._POST_OPS = [SYM_0_OR_1, SYM_0_OR_MORE, SYM_1_OR_MORE]
        self._ESCAPABLE_IN_RANGE_SYMBOLS = [SYM_ALTERNATE, SYM_ANY_CHAR, SYM_PAREN_LEFT,\
            SYM_PAREN_RIGHT, SYM_EXCLUDE, SYM_0_OR_1, SYM_0_OR_MORE, SYM_1_OR_MORE,\
            SYM_CONCAT]
        self._ESCAPABLE_SYMBOLS = [SYM_ALTERNATE, SYM_RANGE_START, SYM_PAREN_LEFT,\
            SYM_PAREN_RIGHT, SYM_ESCAPE, SYM_0_OR_1, SYM_0_OR_MORE, SYM_1_OR_MORE,\
            SYM_CONCAT, CHR_NULL]

    def validate(self,pattern):
        self._pattern = pattern
        self._patternLen = len(self._pattern)

        self._result = ValidationResult()
        if self._patternLen == 0:
            #empty pattern treated as invalid input
            self._result.error = ERR_INVALID_STR
            return self._result

        self._moveNext()

        #Try to find the whole match symbols'''
        wholeMatchSymbol = SYM_MATCH_START + SYM_MATCH_END
        if wholeMatchSymbol == self._pattern or SYM_MATCH_START == self._pattern or SYM_MATCH_END == self._pattern:
            if self._pattern[0] == SYM_MATCH_START:
                self._result.match_start = True
                self._accept(SYM_MATCH_START)
            elif self._pattern[self._patternLen-1] == SYM_MATCH_END:
                self._result.match_end = True
                self._patternLen = self._patternLen - 1

        invalidSymbols = [SYM_0_OR_1, SYM_0_OR_MORE, SYM_1_OR_MORE, SYM_ALTERNATE]
        try:
            while self._curPos < self._patternLen:
                if self._curChr in invalidSymbols:
                    #symbols that will be processed with other chars, should not be here
                    self._error(ERR_MISSING_OP, self._curPos, 1)
                    break
                if self._curChr == SYM_PAREN_RIGHT:
                    #only right parenthese is not enough
                    self._error(ERR_MISMATCH_PAREN, self._curPos, 1)
                    break
                #everything fine, start to go through all chars in pattern
                self._process()
        except Exception:
            pass

        self._result.formatted_parttern = self._finalPattern
        return self._result

    def postFix(self, pattern):
        opStack = []
        postFixQueue = deque([])
        isEscape = False
        for char in pattern:
            if not isEscape and char == SYM_ESCAPE:
                postFixQueue.append(char)
                isEscape = True
                continue
            if isEscape:
                postFixQueue.append(char)
                isEscape = False
                continue
            if char == SYM_PAREN_LEFT:
                opStack.append(char)
            elif char == SYM_PAREN_RIGHT:
                while len(opStack) > 0 and not opStack[-1] == SYM_PAREN_LEFT:
                    postFixQueue.append(opStack.pop())
                opStack.pop()
            else:
                while len(opStack) > 0:
                    if self._getOpPriority(opStack[-1]) >= self._getOpPriority(char):
                        postFixQueue.append(opStack.pop())
                    else:
                        break
                opStack.append(char)
        while len(opStack) > 0:
            postFixQueue.append(opStack.pop())
        return "".join(postFixQueue)

    def _getOpPriority(self,op):
        if op == SYM_PAREN_LEFT:
            return 0
        elif op == SYM_ALTERNATE:
            return 1
        elif op == SYM_CONCAT:
            return 2
        elif op in self._POST_OPS:
            return 3
        elif op == SYM_EXCLUDE:
            return 4
        else:
            return 5

    def _moveNext(self):
        self._curPos += 1
        if self._curPos < self._patternLen:
            self._curChr = self._pattern[self._curPos]
        else:
            self._curChr = CHR_NULL

    def _process(self):
        self._processEscapable()
        self._processConcat()
        self._processExclude()
        self._processNonEscapable()
        self._processParenthese()
        self._processRange()
        self._processAlternate()

    def _processEscapable(self):
        while self._accept(SYM_ESCAPE):
            if not self._testEscapable(self._curChr):
                self._error(ERR_INVALID_ESCAPE, self._curPos - 1, 1)
            self._acceptPostOps()
            self._isConcat = True

    def _processConcat(self):
        while self._accept(SYM_CONCAT):
            self._appendConcatAnd(SYM_CONCAT)
        while self._accept(SYM_EXCLUDE):
            self._appendConcatAnd(SYM_EXCLUDE)

    def _processExclude(self):
        while self._accept(SYM_EXCLUDE):
            _appendConcat()
            _finalPattern += SYM_ESCAPE
            _finalPattern += SYM_EXCLUDE
            _acceptPostOps()
            _isConcat = True

    def _processNonEscapable(self):
        while self._acceptNonEscapable():
            self._acceptPostOps()
            self._isConcat = True
            self._process()

    def _processParenthese(self):
        if self._accept(SYM_PAREN_LEFT):
            startPos = self._curPos - 1
            self._appendConcat()
            self._finalPattern += SYM_PAREN_LEFT
            self._process()
            if not self._test(SYM_PAREN_RIGHT):
                self._error(ERR_MISMATCH_PAREN, startPos, contentLength)
            self._finalPattern += SYM_PAREN_RIGHT

            contentLength = self._curPos - startPos
            if contentLength == 2:
                self._error(ERR_EMPTY_PAREN, startPos, contentLength)

            self._acceptPostOps()
            self._isConcat = True
            self._process()

    def _processRange(self):
        if self._accept(SYM_RANGE_START):
            startPos = self._curPos - 1
            isExclude = False
            self._appendConcat()
            if self._accept(SYM_EXCLUDE):
                isExclude = True
            charsetStr = self._getCharset()

            if not self._test(SYM_RANGE_END):
                self._error(ERR_MISMATCH_BRACKET, startPos, self._curPos - startPos)

            contentLength = self._curPos - startPos
            if contentLength == 2:
                self._error(ERR_INVALID_RANGE, startPos, contentLength)
            elif contentLength == 3 and isExclude:
                self._finalPattern += SYM_PAREN_LEFT + SYM_ESCAPE + SYM_EXCLUDE + SYM_PAREN_RIGHT
            else:
                if isExclude:
                    self._finalPattern += SYM_EXCLUDE
                self._finalPattern += SYM_PAREN_LEFT + charsetStr + SYM_PAREN_RIGHT
            self._acceptPostOps()
            self._isConcat = True
            self._process()

    def _processAlternate(self):
        if self._accept(SYM_ALTERNATE):
            startPos = self._curPos - 1
            self._isConcat = False
            self._appendAlternate()
            self._process()
            if self._curPos - startPos == 1:
                self._error(ERR_MISSING_OP, startPos, 1 )
            self._process()

    def _getCharset(self):
        charset = ""
        rangeStart, start, length = -1,-1,-1
        left, right, rangeStr, tmp = "","","",""
        isFirstChar = True
        while(True):
            tmp = ""
            start = self._curPos
            if self._accept(SYM_ESCAPE):
                tmp = self._testEscapableInBracket()
                if tmp == '':
                    self._error(ERR_INVALID_ESCAPE, start - 1, 1)
                length = 2
            if tmp == '':
                tmp = self._acceptNonEscapableInRange()
                length = 1
            if tmp == '':
                break

            if left == '':
                rangeStart = start
                left = tmp
                if not isFirstChar:
                    charset += SYM_ALTERNATE
                    isFirstChar = False
                charset += tmp
                continue
            if rangeStr == '':
                if not SYM_RANGE == tmp:
                    rangeStart = start
                    left = tmp
                    charset += SYM_ALTERNATE
                    charset += tmp
                else:
                    rangeStr = tmp
                continue
            right = tmp

            expanedRangeStr = self._expandRange(left,right)
            if expanedRangeStr == "":
                self._error(ERR_INVALID_RANGE, rangeStart, start + length - rangeStart)
            charset += expanedRangeStr

        #if not rangeStr == "":
        #    charset += SYM_ALTERNATE
        #    charset += rangeStr
        return charset

    def _expandRange(self,start,end):
        rangeStr = ""
        if len(start) > 1:
            startChar = start[1]
        else:
            startChar = start[0]
        if len(end) > 1:
            endChar = end[1]
        else:
            endChar = end[0]
        if startChar > endChar:
            return ""
        startChar = chr(ord(startChar) + 1)
        while startChar <= endChar:
            rangeStr += SYM_ALTERNATE
            if startChar in self._ESCAPABLE_IN_RANGE_SYMBOLS:
                rangeStr += SYM_ESCAPE
            rangeStr += startChar
            startChar = chr(ord(startChar) + 1)
        return rangeStr

    def _accept(self,char):
        if char == self._curChr:
            self._moveNext()
            return True
        return False

    def _acceptPostOps(self):
        if self._curChr in self._POST_OPS:
            self._finalPattern += self._curChr
            return self._accept(self._curChr)
        return False

    def _acceptNonEscapable(self):
        if not self._curChr in self._ESCAPABLE_SYMBOLS:
            self._appendConcat()
            self._finalPattern += self._curChr
            self._accept(self._curChr)
            return True
        return False

    def _acceptNonEscapableInRange(self):
        lastChar = self._curChr
        if self._curChr in self._ESCAPABLE_IN_RANGE_SYMBOLS:
            self._accept(self._curChr)
            return SYM_ESCAPE + lastChar
        elif SYM_ESCAPE == self._curChr or SYM_RANGE_END == self._curChr or CHR_NULL == self._curChr:
            return ''
        else:
            self._accept(self._curChr)
            return lastChar

    def _appendConcat(self):
        if self._isConcat:
            self._finalPattern += SYM_CONCAT
            self._isConcat = False

    def _appendAlternate(self):
        if self._isAlternate:
            self._finalPattern += SYM_ALTERNATE
            self._isAlternate = False

    def _appendConcatAnd(self,char):
        self._appendConcat()
        self._finalPattern += SYM_ESCAPE
        self._finalPattern += char
        self._acceptPostOps()
        self._isConcat = True

    def _testEscapable(self):
        if self._curChr in self._ESCAPABLE_SYMBOLS:
            self._finalPattern += SYM_ESCAPE
            self._finalPattern += self._curChr
            self._accept(self._curChr)
            return True
        elif self._curChr == SYM_NEWLINE:
            self._finalPattern += '\n'
            self._accept(self._curChr)
            return True
        elif self._curChr == SYM_TAB:
            self._finalPattern += '\t'
            self._accept(self._curChr)
            return True
        return False

    def _testEscapableInBracket(self):
        lastChar = self._curChr;
        if SYM_RANGE_END == lastChar or SYM_ESCAPE == lastChar:
            self._accept(lastChar)
            return SYM_ESCAPE + lastChar
        elif SYM_NEWLINE:
            self._accept(lastChar)
            return '\n'
        elif SYM_TAB:
            self._accept(lastChar)
            return '\t'
        return ''

    def _test(self,char):
        return self._accept(char)

    def _error(self,error, errorAt, errorLen):
        self._result.error = error
        self._result.error_at = errorAt
        self._result.error_len = errorLen
        raise Exception("validation failed")
