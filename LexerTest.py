import unittest

from Lexer import *
from LexerConstants import *
from RegexLex import *

class LexerUnitTests(unittest.TestCase):

    # Test is_int_regex()
    def test_is_int_regex_dec(self):
        # Test is_int_regex() for valid decimal acceptance
        self.assertTrue(is_int_regex('0'))
        self.assertTrue(is_int_regex('  +0  '))
        self.assertTrue(is_int_regex('  -0  '))
        self.assertTrue(is_int_regex('  -1398  '))
        self.assertTrue(is_int_regex('  +8013  '))
        self.assertTrue(is_int_regex('  318 '))

        # Test is_int_regex() for valid hexadecimal acceptance
        self.assertTrue(is_int_regex(' +0x0 '))
        self.assertTrue(is_int_regex(' -0x0 '))
        self.assertTrue(is_int_regex(' -0xFAB '))
        self.assertTrue(is_int_regex(' 0x111A3B4 '))
        self.assertTrue(is_int_regex(' -0x0A '))
        self.assertTrue(is_int_regex(' 0x0A '))

        # Test is_int_regex() for invalid inputs
        self.assertFalse(is_int_regex('+'))
        self.assertFalse(is_int_regex('-'))
        self.assertFalse(is_int_regex('0x'))
        self.assertFalse(is_int_regex('130ab'))
        self.assertFalse(is_int_regex('0130ab'))
        self.assertFalse(is_int_regex('0x130ghi'))

    # Test is_dec_int_regex()
    def test_is_dec_int_regex(self):
        # Do not allow hexadecimal for is_dec_int_regex()
        self.assertFalse(is_dec_int_regex(' +0x0 '))
        self.assertFalse(is_dec_int_regex(' -0xFAB '))

        # Allow valid yet unusual inputs for is_dec_int_regex()
        self.assertTrue(is_dec_int_regex('+0'))
        self.assertTrue(is_dec_int_regex('-0'))
        self.assertTrue(is_dec_int_regex(' 0000000001 '))

        # Allow normal inputs for is_dec_int_regex()
        self.assertTrue(is_dec_int_regex('3189999'))
        self.assertTrue(is_dec_int_regex('-9139813'))
    
    # Test is_uns_int_dec_regex()
    def test_is_dec_uns_int_regex(self):
        self.assertTrue(is_dec_uns_int_regex('0'))
        self.assertTrue(is_dec_uns_int_regex('   123'))
        self.assertTrue(is_dec_uns_int_regex('321   '))
        self.assertTrue(is_dec_uns_int_regex(' 00123'))

        self.assertFalse(is_dec_uns_int_regex(' 0xabc  '))

    # Test is_identifier_regex()
    def test_is_identifier_regex(self):
        self.assertTrue(is_identifier_regex('var_'))
        self.assertTrue(is_identifier_regex('Var_iable'))
        self.assertTrue(is_identifier_regex('e'))

        self.assertFalse(is_identifier_regex('_underscore_first'))
        self.assertFalse(is_identifier_regex('numb3r5'))
        self.assertFalse(is_identifier_regex('$ymbol$'))
        self.assertFalse(is_identifier_regex('unî∂en†iƒie∂'))

    # Test Lexer.lexer()
    def test_lexer(self):
        tokens = []
        lx = Lexer("original_sample.txt")
        tok = lx.lexer()
        while (tok):
            tokens.append(tok)
            tok = lx.lexer()

        type_ans = [
            TokenSeparator, # $$
            TokenKeyword, TokenIdentifier, TokenSeparator, # int       i;
            TokenKeyword, TokenIdentifier, TokenSeparator, # int      max;
            TokenKeyword, TokenIdentifier, TokenSeparator, # int      sum;
            TokenIdentifier, TokenOperator, TokenInteger, TokenSeparator, # sum = 0;
            TokenIdentifier, TokenOperator, TokenInteger, TokenSeparator, # i = 1;
            TokenKeyword, TokenSeparator, TokenIdentifier, TokenSeparator, TokenSeparator, # get ( max);
            TokenKeyword, TokenSeparator, TokenIdentifier, TokenOperator, # while (i <
            TokenIdentifier, TokenSeparator, TokenSeparator, # max)  {
            TokenIdentifier, TokenOperator, TokenIdentifier, # sum = sum
            TokenOperator, TokenIdentifier, TokenSeparator, # + i;
            TokenIdentifier, TokenOperator, TokenIdentifier, # i  =i
            TokenOperator, TokenInteger, TokenSeparator, # + 1;
            TokenSeparator, # }
            TokenIdentifier, TokenOperator, TokenIdentifier, # sum = sum
            TokenOperator, TokenIdentifier, TokenSeparator, # + max;
            TokenKeyword, TokenSeparator, TokenIdentifier, TokenSeparator, TokenSeparator, # put (sum);
            TokenSeparator, # $$
        ]
        val_ans = [
            "$$",
            "int", "i", ";",
            "int", "max", ";",
            "int", "sum", ";",
            "sum", "=", "0", ";",
            "i", "=", "1", ";",
            "get", "(", "max", ")", ";",
            "while", "(", "i", "<", "max", ")", "{",
            "sum", "=", "sum", "+", "i", ";",
            "i", "=", "i", "+", "1", ";",
            "}",
            "sum", "=", "sum", "+", "max", ";",
            "put", "(", "sum", ")", ";",
            "$$"
        ]
        for i in range (len(type_ans)):
            self.assertEqual(type_ans[i], tokens[i].type)
            self.assertEqual(val_ans[i], tokens[i].value)

if __name__ == '__main__':
    unittest.main()