from Nodes import *

class Token:
    # ------------------------------------------------------
    # Tokenization. Takes the input string and transforms it 
    # into tokens that our grammar can understand.
    # Since, it should be Recursive Descent algorithm, it would be better, if we used generators with yield.
    # However, at this point, it adds complexity, as we must implement iterable class Token. Probably,
    # in the future, we can change it.
    # 
    # Right now it has some limitations.
    #
    # TO DO:
    # 1. Add regex to identify IDs and NUMBERs as it is done in python parser.
    # 2. Add different types of brackets.
    # 3. Implicit multiplication.
    # 4. Improve error handling. As for now, it is descent.
    # 5. Add iterable class Token.
    #
    # ------------------------------------------------------

    def __init__(self):
        pass

    def _tokenType(self, c):
        if c.isdigit() or c == '.':
            return "NUMBER"
        elif (c == "+" or c == "-" or c == "*" or c == "/" or c == "^"):
            return "OPERATOR"
        elif c.isalnum() or c == "_":
            return "ID"
        elif c == '(':
            return "R_BRACKET"
        elif c == ')':
            return "L_BRACKET"
        else:
            raise Exception(f"Token {c} is not valid!")

    def _nextToken(self, expr, start_idx):
        token = ''
        buffer = ''
        idx = start_idx
        tokenType = self._tokenType(expr[idx])

        if(tokenType == "NUMBER"):
            decimalPointCnt = 0
            while idx < len(expr) and (self._tokenType(expr[idx]) == "NUMBER"):
                token = expr[idx]
                if token == '.':
                    decimalPointCnt += 1
                    if decimalPointCnt > 1:
                        break
                buffer += token
                idx += 1
        
        elif(tokenType == "ID"):
            underscoreCnt = 0
            while idx < len(expr) and (self._tokenType(expr[idx]) == "ID" or self._tokenType(expr[idx]) == "NUMBER"):
                token = expr[idx]
                if token == '_':
                    underscoreCnt += 1
                    if underscoreCnt > 1:
                        break
                buffer += token
                idx += 1

        elif(tokenType == "OPERATOR" or tokenType == "R_BRACKET" or tokenType == "L_BRACKET"):
            buffer = expr[idx]
            idx += 1

        return ((tokenType, buffer), idx)

    def tokenize(self, expr):
        idx = 0
        tokens = []
        exprUpd = expr.replace(' ', '')

        while idx < len(exprUpd):
            token, next_idx = self._nextToken(exprUpd, idx)
            if not token:
                raise Exception(f"expression is not valid. the problem occured at {idx} with {token}")
            idx = next_idx
            tokens.append(token)

        return tokens

class Parser:

    # ------------------------------------------------------
    # Parser. Takes string and transforms it into binary expression tree.
    # The input is expression string. The input should be in the format of
    # 3*x + sin(x) + x^5, for example.
    #
    # The rules for input:
    #   1. Tokens can be separated by 0 or more whitespaces
    #   2. Function arguments have to be in parentheses
    #
    # Limitations (yet):
    #   1. Only one type of brackets are allowed -> "()"
    #   2. No modulus (i.e. ||) implemented
    #   3. No rational fractions implemented
    #   4. Implicit multiplication only allowed between literals 
    #      and arguments (in that order)
    # ------------------------------------------------------

    FUNCTIONS = ['sin', 'cos', 'tan', 'cot', 'sec', 'csc',
                 'cosh', 'sinh', 'tanh', 'coth', 'sech', 'csch',
                 'arcsin', 'arccos', 'arctan', 'arccot', 'arcsec', 'arccsc',
                 'arccosh', 'arcsinh', 'arctanh', 'arccoth', 'arcsech', 'arccsch',
                 'ln']

    def __init__(self, exprString):
        self.__tokenIdx = 0
        self.__curToken = None
        self.__tokens = Token().tokenize(exprString)
    
    def parse(self): # string -> tree
        if not self.__tokens:
            raise Exception("expression is not valid.")
        
        self.__curToken = self.__tokens[0]

        return self._parseExpr()
    
    def _parseExpr(self):
        return self._parseAddition()

    def _parseAddition(self):
        left = self._parseMultiplication()

        while self.__curToken[1] == "+" or self.__curToken[1] == "-":
            op = self.__curToken[1]
            self._consume()
            right = self._parseMultiplication()
            left = InfixOperatorNode(op, [left, right])

        return left
    
    def _parseMultiplication(self):
        left = self._parseExponentiation()

        while self.__curToken[1] == "*" or self.__curToken[1] == "/":
            op = self.__curToken[1]
            self._consume()
            right = self._parseExponentiation()
            left = InfixOperatorNode(op, [left, right])

        return left

    # '^' is Right Associative Binary Operator
    def _parseExponentiation(self):
        left = self._parseValue()

        if self.__curToken[1] == '^':
            op = self.__curToken[1]
            self._consume()
            right = self._parseExponentiation()
            left = InfixOperatorNode(op, [left, right])
            return left
        else:
            return left

    def _parseValue(self):
        # number
        if self.__curToken[0] == 'NUMBER':
            node = self.__curToken[1]
            self._consume()
            return NumberNode(float(node))
        # variable and functions
        elif self.__curToken[0] == "ID":
            node = self.__curToken[1]
            if node in Parser.FUNCTIONS:
                return self._parseCall()
            else:
                self._consume()
                return VarNode(node)
        elif self.__curToken[1] == "(":
            self._consume()
            expr = self._parseExpr()
            if self.__curToken[1] != ")":
                raise Exception("The brackets are not balanced!")
            else:
                self._consume()
            return expr
        elif self.__curToken[1] == '-':
            op = self.__curToken[1]
            self._consume()
            left = self._parseExponentiation()
            return PrefixOperatorNode(op, [left])
        else:
            raise Exception("Expression is not valid!")
    
    def _parseCall(self):
        fn = self.__curToken[1]
        self._consume()
        if self.__curToken[1] == "(":
            self._consume()
            expr = self._parseExpr()
            if self.__curToken[1] != ")":
                raise Exception("The brackets are not balanced!")
            else:
                self._consume()
            return FunctionNode(fn, [expr])
        else:
            raise Exception("Function must be followed by brackets!")
            

    def _consume(self):
        self.__tokenIdx += 1
        if self.__tokenIdx < len(self.__tokens):
            self.__curToken = self.__tokens[self.__tokenIdx]

