# ------------------------------------------------------
# We have 2 options to parse mathematical expression:
#   1. Stack. Similar project that uses stack:
#      https://www.codeproject.com/Articles/13731/Symbolic-Differentiation
#
#   2. Tree. 
#
# Both options are viable, but we are going to use Tree, as it is easier.
# Ideally, we should be able to have String <-> Tree relationship.
# ------------------------------------------------------
#
# ------------------------------------------------------
# Sources used to learn about parsing, languages, and grammar:
#   1. https://www.youtube.com/watch?v=SToUyjAsaFk -- video about Code parsing of mathematical expression
#
#   2. https://www.youtube.com/watch?v=bxpc9Pp5pZM -- video about fundamentals of parsing
#
#   3. https://users.monash.edu/~lloyd/tildeProgLang/Grammar/ -- formal definiton of grammar
#
#   4. http://cogitolearning.co.uk/2013/04/writing-a-parser-in-java-a-grammar-for-mathematical-expressions/
#
#   5. https://www.engr.mun.ca/~theo/Misc/exp_parsing.htm
#
#   6. https://itnext.io/writing-a-mathematical-expression-parser-35b0b78f869e
#
# ------------------------------------------------------ 
#
# ------------------------------------------------------
# First, we need to implement parser in our code.
# Grammar Rules for our language:
# Based on sources: https://habr.com/ru/articles/150043/,
#                   https://inspirnathan.com/posts/162-recursive-descent-parser-for-math-expressions-in-javascript/
#
# Number = {Digit}+('.'{Digit}*) -> allows for 2.22 
# Id = {Letter}{AlphaNumeric}* -> variable, function     
#                                                         
# <Expression> ::= <Addition>
#              
# <Addition> ::= <Multiplication> {('+' | '-') <Multiplication>}*
#
# <Multiplication> ::= <Exponentiation> {('*' | '/') <Exponentiation>}*
#                
# <Exponentiation> ::= <Primary> {'^' <Exponentiation>}*
#
# <Primary> ::= Id
#           | Number
#           | '(' <Expression> ')'
#           | - <Exponentiation>
#           | <Call>
# 
# <Call> ::= Id '(' <Expression> ')'
#
# ------------------------------------------------------

from Nodes import *
from Parser import *
import math
import re
from CoolProgressBar import *

class psevdoCalc:
    DERIVATIVES = {'sin(x)':'cos(x)', 'cos(x)':'-sin(x)', 'tan(x)':'sec(x)^2',
                    'cosec(x)':'-cosec(x)*cot(x)', 'sec(x)':'sec(x)*tan(x)', 'cot(x)':'-cosec(x)^2',
                    'sinh(x)':'cosh(x)', 'cosh(x)':'-sinh(x)', 'tanh(x)':'sech(x)^2',
                    'cosech(x)':'-cosech(x)*coth(x)','sech(x)':'sech(x)*tanh(x)', 'coth(x)':'-cosech(x)^2',
                    'ln(x)': '1/x'}
    
    FUNCTIONS = ['sin', 'cos', 'tan', 'cot', 'sec', 'csc',
                 'cosh', 'sinh', 'tanh', 'coth', 'sech', 'csch',
                 'arcsin', 'arccos', 'arctan', 'arccot', 'arcsec', 'arccsc',
                 'arccosh', 'arcsinh', 'arctanh', 'arccoth', 'arcsech', 'arccsch',
                 'ln']


    CONSTS = {
            'pi' : math.pi,
            'e' : math.e
        }
    
    # ------------------------------------------------------
    # Traverses the tree and calculates the derivative according to the rules:
    #   1. f(x) = c => f'(x) = 0
    #   2. (f +- g)' = f' +- g'
    #   3. (f*g)' = f'*g + f*g'
    #   4. (f/g)' = (f'*g - f*g')/(g^2)
    #   5. f(g)' = f'(g)*g'
    #   6. (f^g)' = f^g(f'*(g/f) + g'*ln(f))
    # ------------------------------------------------------
    def _innerDerivative(self, dx, dy):
        if self._isLeaf(dx):
            if isinstance(dx, VarNode) and dx.name == dy:
                return NumberNode(1)
            else:
                return NumberNode(0)
                
        else:
            if isinstance(dx, InfixOperatorNode):
                if dx.name == '+':
                    return self._innerDerivative(dx.children[0], dy) + self._innerDerivative(dx.children[1], dy)
                elif dx.name == '-':
                    return self._innerDerivative(dx.children[0], dy) - self._innerDerivative(dx.children[1], dy)
                elif dx.name == '*':
                    return self._innerDerivative(dx.children[0], dy)*dx.children[1] + dx.children[0] * self._innerDerivative(dx.children[1], dy)
                elif dx.name == '/':
                    return (self._innerDerivative(dx.children[0], dy) * dx.children[1] - dx.children[0]*self._innerDerivative(dx.children[1], dy))/(dx.children[1]*dx.children[1])
                elif dx.name == '^':
                    return dx.children[0]**dx.children[1] * (self._innerDerivative(dx.children[0], dy) * (dx.children[1]/dx.children[0]) + self._innerDerivative(dx.children[1], dy) * FunctionNode("ln", [dx.children[0]]))
            
            elif isinstance(dx, PrefixOperatorNode):
                return -self._innerDerivative(dx.children[0], dy)
            
            elif isinstance(dx, FunctionNode):
                if dx.name in psevdoCalc.FUNCTIONS:
                    newFuncNode = Parser(self.DERIVATIVES[dx.name + "(x)"].replace("x", str(dx.children[0]))).parse()
                    return newFuncNode*self._innerDerivative(dx.children[0], dy)
                
                elif dx.name not in psevdoCalc.FUNCTIONS:
                    return FunctionNode(dx.name + "'", [dx.children[0]])*self._innerDerivative(dx.children[0], dy)
    
    def derivative(self, dx, dy = "x"):
        return self.simplify(self._innerDerivative(dx, dy))

    # takes expression and values --> evaluated expression
    def eval(self, dx, vals = {}):
        if self._isLeaf(dx):
            if isinstance(dx, VarNode):
                if dx.name == 'pi' or dx.name == 'e':
                    return NumberNode(psevdoCalc.CONSTS[dx.name])
                elif dx.name in vals.keys():
                    return NumberNode(vals[dx.name])
                else:
                    return dx
            else:
                return dx
        else:
            if isinstance(dx, InfixOperatorNode):
                if dx.name == '+':
                    left = self.eval(dx.children[0], vals)
                    right = self.eval(dx.children[1], vals)
                    if isinstance(left, NumberNode) and isinstance(right, NumberNode):
                        return NumberNode(float(left.name) + float(right.name))
                    else:
                        return left + right

                elif dx.name == '-':
                    left = self.eval(dx.children[0], vals)
                    right = self.eval(dx.children[1], vals)
                    if isinstance(left, NumberNode) and isinstance(right, NumberNode):
                        return NumberNode(float(left.name) - float(right.name))
                    else:
                        return left - right

                elif dx.name == '*':
                    left = self.eval(dx.children[0], vals)
                    right = self.eval(dx.children[1], vals)
                    if isinstance(left, NumberNode) and isinstance(right, NumberNode):
                        return NumberNode(float(left.name) * float(right.name))
                    else:
                        return left * right

                elif dx.name == '/':
                    left = self.eval(dx.children[0], vals)
                    right = self.eval(dx.children[1], vals)
                    if isinstance(left, NumberNode) and isinstance(right, NumberNode):
                        return NumberNode(float(left.name)/float(right.name))
                    else:
                        return left/right

                elif dx.name == '^':
                    left = self.eval(dx.children[0], vals)
                    right = self.eval(dx.children[1], vals)
                    if isinstance(left, NumberNode) and isinstance(right, NumberNode):
                        return NumberNode(float(left.name)**float(right.name))
                    else:
                        return left**right
            
            elif isinstance(dx, PrefixOperatorNode):
                left = self.eval(dx.children[0], vals)
                if isinstance(left, NumberNode):
                    return NumberNode(-left.name)
                else:
                    return -left
            
            elif isinstance(dx, FunctionNode):
                left = self.eval(dx.children[0], vals)
                
                if dx.name in psevdoCalc.FUNCTIONS:
                    if isinstance(left, NumberNode):
                        if dx.name == "ln":
                            dx.name = "log"
                        if dx.name[:3] == "arc":
                            dx.name = dx.name[0] + dx.name[3:]
                        mathFunctionAttr = getattr(math, dx.name)
                        return NumberNode(mathFunctionAttr(float(left.name)))
                    else:
                        return FunctionNode(dx.name, [left])
                else:
                    return FunctionNode(dx.name, [left])

    # Trim expression. The function performs basic simplification before normalization and pattern matching
    # It is performed on BinaryExpressionTree
    def _trimExpression(self, dx):
        if self._isLeaf(dx):
            return dx
        
        # 0 + exp = exp
        # exp + 0 = exp
        elif dx == InfixOperatorNode("+", []):
            left = self._trimExpression(dx.children[0])
            right = self._trimExpression(dx.children[1])
            if left == NumberNode(0):
                return right
            elif right == NumberNode(0):
                return left
            return left + right

        # exp - 0 = exp
        # 0 - exp = -exp
        elif dx == InfixOperatorNode("-", []):
            left = self._trimExpression(dx.children[0])
            right = self._trimExpression(dx.children[1])
            if left == NumberNode(0):
                return -right
            elif right == NumberNode(0):
                return left
            return left - right

        # exp*0 = 0
        # 0*exp = 0
        # exp*1 = exp
        # 1*exp = exp
        elif dx == InfixOperatorNode("*", []):
            left = self._trimExpression(dx.children[0])
            right = self._trimExpression(dx.children[1])
            if left == NumberNode(0) or right == NumberNode(0):
                return NumberNode(0)
            elif left == NumberNode(1):
                return right
            elif right == NumberNode(1):
                return left
            return left * right
        
        # exp^1 = exp
        # 1^exp = 1
        # exp^0 = 1
        # 0^exp = 0
        elif dx == InfixOperatorNode("^", []):
            left = self._trimExpression(dx.children[0])
            right = self._trimExpression(dx.children[1])
            if right == NumberNode(1):
                return left
            elif left == NumberNode(1):
                return NumberNode(1)
            elif left == NumberNode(0):
                return NumberNode(0)
            elif right == NumberNode(0):
                return NumberNode(1)
            return left ** right
        
        # 0/exp = 0
        # exp/1 = exp
        elif dx == InfixOperatorNode("/", []):
            left = self._trimExpression(dx.children[0])
            right = self._trimExpression(dx.children[1])
            if right == NumberNode(1):
                return left
            elif left == NumberNode(0):
                return NumberNode(0)
            return left/right
        
        elif dx == PrefixOperatorNode("-", []):
            return -dx.children[0]
        
        elif isinstance(dx, FunctionNode):
            return FunctionNode(dx.name, [dx.children[0]])

    def simplify(self, dx):
        dx = self.eval(dx)
        return self._trimExpression(dx)

    def _isLeaf(self, node):
        if node.children == None:
            return True
        else:
            return False

    #----------------------------------------
    def findRootsOfFunction(self, expr, leftBound, rightBound, step = 0.1):
        #x0 - initial guess, epsilon - error, max_iter - max # of iterations
        solutions = []
        i = 0
        cpb = ProgressBar()
        while leftBound <= rightBound and i <= 2000:
            # cpb.displayProgressBar(i, 2000)
            solution = self._innerRoot(expr, leftBound, 1e-10, 1000)
            if solution is not None and (solution <100 and solution > -100):
                solution = round(solution, 6)
                if solution not in solutions:
                    solutions.append(solution)
            leftBound += step
            i += 1
        print()
        solutions = sorted(solutions)
        return solutions

    def _numDerivative(self, expr, x):
        h = 1e-8
        # print(type(self.eval(expr, {"x": x + h}).children[0]))
        return (self.eval(expr, {"x": x + h}).name - self.eval(expr, {"x": x}).name)/h

    def _innerRoot(self, expr, x0, epsilon, maxIter):
        xn = x0
        for _ in range(0, maxIter):
            try:
                y = self.eval(expr, {"x": xn}).name
                if abs(y) < epsilon:
                    return xn
                slope = self._numDerivative(expr, xn)
                if slope == 0:
                    return None
                xn = xn - y / slope
            except:
                return None
        return None

    def limit(self, expr, limit, dx):
        try:
            return self.eval(expr, {dx: limit})

        except:
            # inf^0, 0/0, inf/inf, 0^inf, 0/inf, inf/0
            l = limit
            leftStep = l - 0.1
            rightStep = l + 0.1
            epsilon = 0.0000001
            step = 0.00001
            rightLimit, leftLimit = 0, 0
            i = 1
            while (rightStep - leftStep) > epsilon:
                leftStep += (step) * i
                leftLimit = self.eval(expr, {dx: leftStep })
                rightStep -= (step) * i
                rightLimit = self.eval(expr, {dx: rightStep })
                i += 1       
            if leftLimit.name > 9000:
                return math.inf
            else:
                return round(leftLimit.name, 3)
    
    #---------------------------------------------

    def functionAnalysis(self, func):
        #  Determine points of intersections with abscissas
        Oy = self.eval(func, {"x" : 0}).name
        print(f'{Oy} - point of intersection with Oy')
        
        Ox = self.findRootsOfFunction(func,-100,100 )

        if Ox == []:
            print('Equation does not have any roots, so no intersection')
        else:
            print(f'{Ox} - point of intersection with Ox')

        # Extremas 
        der_y = self.derivative(func, "x")
        # return der_y
        roots_der_y = self.findRootsOfFunction(der_y,-100,100)
        # print(roots_der_y)
        number_of_seg = len(roots_der_y) + 1
        # return number_of_seg 
        point_bet = roots_der_y[0] + roots_der_y[1]
        der_point_bet = self.eval(der_y, {"x":point_bet}).name
        der_in_points = []
        for i in range(len(roots_der_y)):
            point = roots_der_y[i]
            if point < 0:
                point -= 1
                der_y_point = self.eval(der_y, {"x":point}).name
                der_in_points.append(der_y_point)
                # print(der_y_point)
                # print(f"Since the derivative is positive for x < {point +1}")
            else:
                point += 1
                der_y_point = self.eval(der_y, {"x":point}).name
                der_in_points.append(der_y_point)
                # print(der_y_point)
            if i < len(roots_der_y)-1:
                der_in_points.append(der_point_bet)
            point = 1e-18
            der_y_point = 1e-19
        for i in range(len(der_in_points)-1):
            
            if der_in_points[i] > der_in_points[i+1]:
                a = self.eval(func, {"x": roots_der_y[i]})
                print(f'Local max {a} in the point x = {roots_der_y[i]}')
            else:
                b = self.eval(func, {"x": roots_der_y[i]})
                print(f'Local min {b} in the point x = {roots_der_y[i]}')
            a, b = 0, 0


    def numericalIntegration(self, expr, b, a, n = 1000):
        delta_x = (b-a)/n
        ans = 0
        p = n // 2
        for i in range(1,p+1):
            x_st = a + (2*i - 2)*delta_x
            x_con = a + (2*i - 1)*delta_x
            x_l = a + (2*i)*delta_x
            ans += (self.eval(expr, {"x": x_st}).name + 4*self.eval(expr,{"x":x_con}).name + self.eval(expr, {"x": x_l}).name)
        ans *= delta_x/3
        return ans

    def vectorCalculus(self, func_g, func_d, func_c):
        # gradient
        i_g = self.derivative(func_g, "x") * VarNode('i')
        j_g = self.derivative(func_g, "y" ) * VarNode('j')
        k_g = self.derivative(func_g, "z") * VarNode('k')

        gradient = f'Gradient {i_g + j_g + k_g}'
        
        # Divergence
        i_d = self.derivative(self.derivative(func_d, "i"), "x")
        j_d = self.derivative(self.derivative(func_d, "j"), "y")
        k_d = self.derivative(self.derivative(func_d, "k"), "z")
        
        divergence = f'Divergence {i_d + j_d + k_d}'

        # Curl
        i_c = self.derivative(self.derivative(func_c, "k"), "y") - self.derivative(self.derivative(func_c, "j"), "z")
        j_c = self.derivative(self.derivative(func_c, "i"), "x") - self.derivative(self.derivative(func_c, "k"), "z")
        k_c = self.derivative(self.derivative(func_c, "j"), "x") - self.derivative(self.derivative(func_c, "i"), "y")

        curl = f'Curl {i_c - j_c + k_c}'

        return gradient, divergence, curl

    def taylorExpansion(self, expr, numOfTerms, center):
        val = self.eval(expr, {"x": center})
        result = str(val)
        der = expr
        fact = 1

        for i in range(1, numOfTerms):
            fact *= i
            der = self.derivative(der)
            val = self.eval(der, {"x": center})
            result += f"+ {val}*(x-{center})^{i}/{fact}"

        return Parser(result).parse()

    def _findNode(self, expr, nodeName):
        if expr.name == nodeName:
            return expr
        else:
            return self._findNode(expr, nodeName)

    # since complex number are not implemented works for real number mainly
    # also (any)/(any) only
    def CauchyIntegral(self, expr, radius):
        f_z, g_z = self._findNode(expr, "/").children
        var = VarNode("x")
        
        singularPoints = self.findRootsOfFunction(g_z, -radius, radius)
        singularPointsInsideCircle = []

        for point in singularPoints:
            if abs(point) < radius and self.eval(f_z, {var.name: point}).name != 0:
                singularPointsInsideCircle.append(point)
        
        res = NumberNode(0)

        for point in singularPointsInsideCircle:
            g_zUpd = self.limit(g_z/(var - NumberNode(point)), point, "x")
            res += NumberNode(2*self.eval(f_z, {var.name: point}).name / g_zUpd)*VarNode("pi")

        return res

    def complexDescr(self, cmplx):
        if '-' in cmplx:
            re, im = cmplx.split('-')
            im = '-'+im[:-1]
            re, im = float(re), float(im)
        elif '+' in cmplx:
            re, im = cmplx.split('+')
            im = im[:-1]
            re, im = float(re), float(im)

        radius = (re ** 2 + im ** 2) ** 0.5
        argument = 0
        ratio = re/im
        arcTanVal = self.eval(FunctionNode("arctan", [NumberNode(ratio)])).name
        if re > 0:
            argument = arcTanVal
        elif re < 0:
            if im>=0:
                argument = arcTanVal + self.CONSTS["pi"]
            else:
                argument = arcTanVal - self.CONSTS["pi"]
        elif re == 0:
            if im > 0:
                argument = self.CONSTS["pi"]/2
            if im < 0:
                argument = -self.CONSTS["pi"]/2

        if argument < 0:
            argument += 2*self.CONSTS["pi"]
            
        polarForm = NumberNode(radius)*(FunctionNode("cos", [argument]) + VarNode("i")*FunctionNode("sin", [argument]))
        quadrant = -1
        if argument <= 0.5 * self.CONSTS["pi"]:
            quadrant = 1

        elif argument <= self.CONSTS["pi"]:
            quadrant = 2

        elif argument <= 3/2 * self.CONSTS["pi"]:
            quadrant = 1
            
        else:
            quadrant = 4
        
        return {"modul": radius, "arg": argument, "polarForm": polarForm, "quarter": quadrant}
#---------------------------------------------------------------
    def leibniz_test(self, expr): 
        expr1 = Parser(expr).parse()
        num1, num2, num3 = self.eval(expr1, {"n": 1}).name, self.eval(expr1, {"n": 2}).name, self.eval(expr1, {"n": 3}).name
        num100 = self.eval(expr1, {"n": 100}).name
        if num1 > 0 and num2 < 0 and num3 > 0 or num1 < 0 and num2 > 0 and num3 < 0:
            if abs(num1) > abs(num2) and abs(num2) > abs(num100):
                if self.limit(expr1, math.inf, "x").name != 0:
                    return 'The series converges conditionally'
                else:
                    return 'You should use other tests to be sure of absolute convergence of the series'
            else:
                return 'A divergent series'
        else:
            return 'A divergent series'


    
    def root_test(self, series):
        index = series.find('))^')
        part1 = series[1:index+1] 
        part2 = series[index+4:-1]
        index = series.find('/')
        num1, num2 = part1[1:index-2], part1[index+1:-1]
        base = self.limit_inf(num1, num2)
        num1, num2 = part2, 'n'
        degree = self.limit_inf(num1, num2)
        if base == 'infinity' or degree == 'infinity':
            return 'A divergent series'
        else:
            base = float(eval(base))
            degree = float(eval(degree))
            if base < 1 and degree >= 1:
                return 'A convergent series'
            else:
                return 'Use another method'


    def limit_inf(self, num, den):
        num = num.replace('n','x')
        den = den.replace('n','x')
        str1 = Parser(num).parse()
        str2 = Parser(den).parse()
        limit = 'math.inf'
        numerator = self.limit(str1, math.inf, "x").name
        denominator = self.limit(str2, math.inf, "x").name
        if numerator != math.inf:
                num1 = int(numerator)
        num1 = numerator
        if denominator != math.inf:
                num2 = int(denominator)
        num2 = denominator
        while num1 == math.inf and num2 == math.inf:
            str1,str2 = self.derivative(str1), self.derivative(str2)
            numerator = self.limit(str1, math.inf, "x").name
            denominator = self.limit(str2, math.inf, "x").name
            if numerator != math.inf:
                num1 = int(numerator)
            if denominator != math.inf:
                num2 = int(denominator)
        if num1 == 0:
            answer = '0'
        elif isinstance(num1, int) and isinstance(num2, int) and num2 != 0:
            answer = f'{num1}/{num2}'
        else:
            answer = 'infinity'
        return answer