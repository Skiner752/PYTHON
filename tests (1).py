from psevdoCalc import *
from Parser import *
from Nodes import *
from dalembert import *

pc = psevdoCalc()

# derivative test
e1 = Parser("x^x + y*x").parse()
print(pc.derivative(e1)) 

# eval test
e2 = Parser("cos(x)^2 + 3*x + y").parse()
print(pc.eval(e2, {"x": 2}))

# simplify test
e3 = Parser("3 - 2 +5*(-7-2)^3 + x  + x*0 + y").parse()
print(pc.simplify(e3))

# Roots of function
e4 = Parser("x^2 - 1").parse()
print(f'Roots - {pc.findRootsOfFunction(e4, -100, 100)}')

# limit test
e5 = Parser("(1-cos(x))/x^2").parse() 
print(f'Limit of the function - {pc.limit(e5, 0, "x")}')

# function analysis
# e6 = Parser("(x^2 + 8)/(1 + x)").parse()
# print(f'{pc.functionAnalysis(e6)}')

# Vector Calculus
e7 = Parser("y^3 + 5*x + 3*x^4 + z^2").parse() # grad test
e8 = Parser("(3*x*y)*i + (2*z)*j + (x^3)*k").parse() # div test
e9 = Parser("(2*y + z)*i + (x + z)*j + (y + x)*k ").parse() # curl test
print(pc.vectorCalculus(e7, e8, e9))

# Definite integral approximation
e11 = Parser("2*x^2 + 1 - x^3").parse()
print(f'Approximate value of the Integral: {pc.numericalIntegration(e11, 2, -2,8)}')

# Closed path integral of complex variable
e12 = Parser("(x^2 + 6*x + 2)/((x+3)*(x-5)*(x+3))").parse()
print(f'Integral of function = {pc.eval(pc.CauchyIntegral(e12, 3))}')

# Complex number descriptor
print(pc.complexDescr("2-3i"))

print(pc.root_test('((7*n+1)/(8*n-2))^(3*n+2)')) 
print(pc.root_test('((8*n-1)/(7*n+7))^((n+1)*(n+1))')) 
print(pc.leibniz_test('(-1)^(n)*(n+1)/(n+5)*7^n')) 
print(pc.leibniz_test('(-1)^(n)*(1/n)')) 
series1 = '(n+1)!/(n+5)*7^n' 
series2 = '(n+1)!/(n+5)' 
print(ratio_test(series1)) 
print(ratio_test(series2))