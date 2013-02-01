#-------------------------------------------------------------------------------
# Name:        Common Definitions
# Purpose:
#
# Author:      Arakuma
#
# Created:     17/01/2013
#-------------------------------------------------------------------------------

#Enumeration simulation
def Enum( *sequential, **named ):
    enums = dict( zip( sequential, range( len( sequential ) ) ), **named )
    return type( "Enum", (), enums )

#Error definitions, all error value are below zero
ERR_NONE              = 0
ERR_MISMATCH_PAREN    = -1
ERR_MISMATCH_BRACKET  = -2
ERR_EMPTY_PAREN       = -10
ERR_EMPTY_BRACKET     = -11
ERR_MISSING_OP        = -12
ERR_INVALID_ESCAPE    = -20
ERR_INVALID_RANGE     = -21
ERR_INVALID_STR       = -22

#internal symbol for patterns
SYM_CONCAT            = "~"
SYM_ALTERNATE         = "|"
SYM_0_OR_MORE         = "*"
SYM_1_OR_MORE         = "+"
SYM_0_OR_1            = "?"
SYM_PAREN_LEFT        = "("
SYM_PAREN_RIGHT       = ")"
SYM_EXCLUDE           = "^"
SYM_ONE_CHAR          = "."
SYM_ANY_CHAR          = "anyone"
SYM_ESCAPE            = "\\"
SYM_RANGE_START       = "["
SYM_RANGE_END         = "]"
SYM_RANGE             = "-"
SYM_DUMMY             = "DUMMY"
SYM_MATCH_START       = "^"
SYM_MATCH_END         = "$"
SYM_NEWLINE           = "n"
SYM_TAB               = "t"
SYM_EPSILON           = "epsilon"

CHR_NULL              = "\0"
