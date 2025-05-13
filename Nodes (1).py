# Tree nodes definition
class Node:
    def __init__(self, name = None, children = None):
        self.children = children
        self.name = name


    # Transform BinaryExpressionTree into AST
    # + and * only can have Multiple children 
    def linearChildren(self, funcName, badFuncName):
        exprRoot = self
        res = []
        if isinstance(exprRoot, InfixOperatorNode) and (exprRoot.name == funcName or exprRoot.name == badFuncName):
            res.extend(exprRoot.children[0].linearChildren(funcName, badFuncName))
            if exprRoot.name == funcName:
                res.extend(exprRoot.children[1].linearChildren(funcName, badFuncName))

            else:
                badRes = exprRoot.children[1].linearChildren(funcName, badFuncName)

                if badFuncName == '-':
                    goodRes = [-child for child in badRes]
                elif badFuncName == '/':
                    goodRes = [NumberNode(1)/child for child in badRes]

                res.extend(goodRes)

        else:
            res.append(exprRoot)
        return res

    def linearize(self):
        exprRoot = self
        if exprRoot.children == None:
            return

        if exprRoot.name == "+":
            exprRoot.children = self.linearChildren(exprRoot.name, "-")
        elif exprRoot.name == "*":
            exprRoot.children = self.linearChildren(exprRoot.name, "/")

        for child in exprRoot.children:
            child.linearize()
        
    def hash(self):
        if isinstance(self, FunctionNode):
            return str(self.name) + "_" + "_".join(child.hash() for child in self.children)
        elif isinstance(self, VarNode):
            return "v_" + str(self.name)
        elif isinstance(self, NumberNode):
            return str(self.name) + " "
        else:
            return str(self.name) + "_" + "_".join(child.hash() for child in self.children)

    def nodeSort(self):
        if self.children == None:
            return self
        
        for child in self.children:
            child = child.nodeSort()

        if self.name != "+" and self.name == "*" and self.name == "-" and self.name == "/":
            return self

        linearCh = []
        operator = ""
        if self.name == "+":
            operator = self.name
            linearCh = self.linearChildren(self.name, "-")
        elif self.name == "*":
            operator = self.name
            linearCh = self.linearChildren(self.name, "/")
        

        groups = self.groupByHash(linearCh)
        grouppedChildren = []

        for ls in groups:
            print(groups)
            grouppedChildren.extend(ls)
        
        return grouppedChildren

    def groupByHash(self, nodes):
        nodesDict = {}
        for node in nodes:
            nodeHash = node.hash()
            if nodesDict.get(nodeHash) is None:
                nodesDict[nodeHash] = []
            else:
                nodesDict[nodeHash].append(node)
        
        res = []
        keys = list(nodesDict.keys())
        sorted(keys)
        for key in keys:
            res.append(nodesDict[key])
        return res

    # Operator overloading for simple manipulations with nodes
    # Precedence remains the same
    def __add__(self, other):
        return InfixOperatorNode("+", [self, other])
    
    def __sub__(self, other):
        return InfixOperatorNode("-", [self, other])
    
    def __neg__(self):
        return PrefixOperatorNode("-", [self])

    def __mul__(self, other):
        return InfixOperatorNode("*", [self, other])
    
    def __truediv__(self, other):
        return InfixOperatorNode("/", [self, other])

    def __pow__(self, other):
        return InfixOperatorNode("^", [self, other])
    
    def __eq__(self, other):
        if type(self) == type(other) and self.name == other.name:
            return True
        else:
            return False

    #-------------
    def __lt__(self, other):
        return str(self.name) < str(other.name)
    
    def __gt__(self, other):
        return str(self.name) > str(other.name)

class VarNode(Node):
    def __init__(self, var):
        super().__init__(name = var)

    def __str__(self):
        return str(self.name)

class FunctionNode(Node):
    def __init__(self, func, children):
        super().__init__(func, children)
    
    def __str__(self):
        return str(self.name) + "(" + str(self.children[0]) + ")"

class NumberNode(Node):
    def __init__(self, number):
        super().__init__(name = number)
        
    def __str__(self):
        return str(self.name)

class InfixOperatorNode(Node): # node with multiple children, mainly to flatten the exprRoot in simplification process.
    def __init__(self, operator, children):
        super().__init__(operator, children)
        
    def __str__(self):
        resStr = "("
        for child in self.children:
            if child.name == '-' and self.name == "+":
                resStr = resStr[:-1]
            resStr += str(child) + str(self.name)
        resStr = resStr[:-1] + ")"
        return resStr

class PrefixOperatorNode(Node):
    def __init__(self, operator, children):
        super().__init__(operator, children)

    def __str__(self):
        return str(self.name) + "(" + str(self.children[0]) + ")"