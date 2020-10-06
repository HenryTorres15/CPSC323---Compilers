import sys

from LexerConstants import *

# Character Type treated like an enum:
ALPHA       = 0
ASTERISK    = 1
DIGIT       = 2
DOLLAR      = 3
EQUAL       = 4
INVALID     = 5
LBRACKET    = 6
OP          = 7
RBRACKET    = 8
SEP         = 9
UNDERSCORE  = 10
WHITESPACE  = 11

# State Transition Table:
#      Input character type:
#      0   1   2   3   4   5   6   7   8   9  10  11
T = [[ 1,  8,  2, 10,  7, 12,  3,  8, 12, 11, 12,  0], # 0  Starting
    [  1, 12, 12, 12, 12, 12, 12, 12, 12, 12,  1, 12], # 1  Accepting
    [ 12, 12,  2, 12, 12, 12, 12, 12, 12, 12, 12, 12], # 2  Accepting
    [ 12,  4, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12], # 3
    [  4,  5,  4,  4,  4,  4,  4,  4,  4,  4,  4,  4], # 4
    [  4,  4,  4,  4,  4,  4,  4,  4,  6,  4,  4,  4], # 5
    [  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0], # 6  Final
    [  9,  9,  9,  9,  8,  9,  9,  9,  9,  9,  9,  9], # 7
    [  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0], # 8  Final
    [  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0], # 9  Final Rewind
    [ 12, 12, 12, 11, 12, 12, 12, 12, 12, 12, 12, 12], # 10
    [  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0], # 11 Final
    [ 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12]] # 12 Invalid

# Note:
# All accepting states need some way to preempt the FSA.
# In other words, there must be some way for the FSA to stop processing
# and create a token for every accepting state. Otherwise the FSA would
# never end.
# 
# A solution to this is final states. Final states are a subset of accepting
# states where the FSA will immediately halt once that state is reached.
# This is sufficient for some tokens with a known length such as operators
# and separators, but not for others such as integers and identifiers.
#
# A second solution used to solve the problem for digits and identifiers
# is a set of "distinguishing" characters
# When the FSA is in the accepting state for integers and identifiers,
# it will check the next character to see if it's distinguishing.
# If it's distinguishing, the FSA will stop.
# See LexerConstants.py for the Distinguishing set.
#
# A third and more general solution is to stop on whitespaces.
# The only time a whitespace doesn't stop the FSA is if we're
# in the middle of a comment.


# Accepting states:
# The key represents the accepting state, the value represents the token type to create
Accepting = {
    1: TokenIdentifier, 2: TokenInteger, 6: TokenComment,
    7: TokenOperator, 8: TokenOperator, 9: TokenOperator,
    11: TokenSeparator, 12: TokenInvalid
}

# "Final" states:
# A subset of accepting states. In these states, the FSA should immediately create a token
# rather than waiting for whitespace.
Final = {6, 8, 9, 11}

# "Rewind" states:
# A subset of final states. In these states, the FSA should
# put a character back into the input stream.
Rewind = {9}

class Token:
    def __init__(self, type_=TokenInvalid, value="Error"):
        self.type = type_
        self.value = value

    # The string representation of a token's information
    def __repr__(self):
        return f"{TokenTypeStr[self.type]}".ljust(15) + f"{self.value}"


class Lexer:

    # Build a dictionary for O(1) determination of column number
    # Some characters are grouped togther because they are functionally equivalent.
    # For example, all letters are treated equally by the transition function
    def char_col_dict_init(self):
        char_col_dict = {}
        # Map separators to column defined by SEP
        for sep in Separators:
            char_col_dict[sep] = SEP
        # Map operators not including asterisk to column defined by OP
        for op in Operators:
            char_col_dict[op] = OP
        # Map letters to column defined by ALPHA
        for i in range(65, 91): # [A, Z]
            char_col_dict[chr(i)] = ALPHA
        for i in range(97, 123): # [a, z]
            char_col_dict[chr(i)] = ALPHA
        # Map digits to column defined by NUM
        for i in range(48, 58): # [0, 9]
            char_col_dict[chr(i)] = DIGIT
        # Map whitespace to column defined by WHITESPACE
        for ws in Whitespaces:
            char_col_dict[ws] = WHITESPACE
        # Map some characters separately
        char_col_dict["_"] = UNDERSCORE
        char_col_dict["$"] = DOLLAR
        char_col_dict["*"] = ASTERISK
        char_col_dict["["] = LBRACKET
        char_col_dict["]"] = RBRACKET
        char_col_dict["="] = EQUAL
        return char_col_dict

    # Find the column that the character maps to in the transition table.
    # This is done by looking the character up in the char_col_dict
    # If the character is not found in the dictionary, it is an invalid character.
    def get_char_col(self, char):
        if char in self.char_col_dict:
            return self.char_col_dict[char]
        return INVALID

    def __init__(self, fname):
        self.file = open(fname, "r")
        self.char_col_dict = self.char_col_dict_init()

    def __del__(self):
        self.file.close()

    # Tries to create a token.
    # If the state indicates an identifier, try to see if it is a keyword.
    def create_token(self, state, lexeme):
        if state in Accepting:
            if Accepting[state] == TokenIdentifier and (lexeme in Keywords):
                return Token(TokenKeyword, lexeme)
            return Token(Accepting[state], lexeme)
        return Token(TokenInvalid, lexeme)

    # Eats up whitespace in the character stream
    # Will return the new character after the whitespaces and also
    # the position of the character just before it
    def skip_whitespace(self, char, prev_pos):
        while char in Whitespaces:
            prev_pos = self.file.tell()
            char = self.file.read(1)
        return (char, prev_pos)

    # Read and return a token object containing information on the retrieved lexeme.
    # This function will advance the file pointer
    def lexer(self):
        state = 0
        lexeme = ""

        # Sometimes we need to go back in the stream, so keep track of previvous location
        prev_pos = self.file.tell()
        char = self.file.read(1)
    
        # Skip whitespace
        char, prev_pos = self.skip_whitespace(char, prev_pos)

        # If EOF, return None
        if char == "":
            return None

        while char != "":
            # ********** STEP 1: **********
            # Look for characters that indicate we should stop the FSA

            # If we're building an identifier or integer and we find a distinguishing char
            # See note on distinguishing characters at the beginning of this file
            if state == 1 or state == 2:
                if char in Distinguishing:
                    self.file.seek(prev_pos) # put a character back
                    return self.create_token(state, lexeme)
            
            # Finding a whitespace always stops the FSA unless we're in comment mode
            if state != 4 and state != 5:
                if char in Whitespaces:
                    return self.create_token(state, lexeme)


            # ********** STEP 2: **********
            # Transition the FSA

            lexeme += char
            input_col = self.get_char_col(char)
            state = T[state][input_col]

            # ********** STEP 3: **********
            # Check if we're now in a final state

            if state in Final:
                # If the token is a comment, skip it and return the next token
                if Accepting[state] == TokenComment:
                    state = 0
                    lexeme = ""
                    prev_pos = self.file.tell()
                    char = self.file.read(1)
                    char, prev_pos = self.skip_whitespace(char, prev_pos)
                    # Handle the corner case where a comment is at the end of file
                    if char == "":
                        return None
                    continue

                # If we had an equal and and now the current character is not an equal sign
                if state == 9:
                    self.file.seek(prev_pos) # put a character back
                    lexeme = lexeme[:len(lexeme)-1] # get rid of the last character
                    return self.create_token(state, lexeme)
                return self.create_token(state, lexeme)

            prev_pos = self.file.tell()
            char = self.file.read(1)

        # Reached end of file
        return self.create_token(state, lexeme)
