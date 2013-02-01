# -*- coding: utf-8 -*-

#-------------------------------------------------------------------------------
# Name:        
# Purpose:
#
# Author:      Arakuma
#
# Created:     17/01/2013
#-------------------------------------------------------------------------------

from naivere.regex import *

def main():
    testMatch("ap+[lmn]*e","apppppple",True)
    testMatch("a[a-c]d","dfsdfasdfsabdsdfsdf")
    testMatch("no+[k-o]*k","noooooooooooooknook",False)
    testMatch("no+[k-o]*k","noooooooooooooknook",True)
    testMatches("no+[k-o]*k","noooooooooooooknook")
    testMatch("p.*n","python", True)

def testMatch(pattern,string,isGreedy):
    re = Regex(pattern,isGreedy)
    print(re.log)
    m = re.match(string)
    if m.matched:
        print("match found from %d to %d, result: %s" % (m.begin, m.end, m.result))
    else:
        print("no match found")

def testMatches(pattern,string):
    re = Regex(pattern,False)
    print(re.log)
    if re.validationResult.error == ERR_NONE:
        matches = re.matches(string)
        if len(matches) > 0:
            print("matches found:")
            for match in matches:
                print("\tfrom %d to %d, result: %s" % (match.begin, match.end, match.result))
        else:
            print("no match found")

if __name__ == '__main__':
    main()
