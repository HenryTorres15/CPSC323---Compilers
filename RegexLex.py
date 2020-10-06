# This file is not used in the compiler.
# This file is for testing correctness of regular expressions.
# More simplified versions of these regex's are used to create
# the NFSMs through Thompson's Construction.
# The resulting FSM is used in the compiler

import re

def is_int_regex(str):
    result = re.match('^[ \t]*[+-]?((0x[0-9a-fA-F]+)|(0[0-7]*)|([0-9]+))[ \t]*$', str)
    return result != None

def is_dec_int_regex(str):
    result = re.match('^[ \t]*[+-]?[0-9]+[ \t]*$', str)
    return result != None

def is_dec_uns_int_regex(str):
    result = re.match('^[ \t]*[0-9]+[ \t]*$', str)
    return result != None

def is_identifier_regex(str):
    result = re.match('^[ \t]*[a-zA-Z][a-zA-Z_]*[ \t]*$', str)
    return result != None