import re

def expand_factorial(expression):

    match1 = re.match(r'\((\d+)\((\w)([-+]\d+)\)\)!', expression)   # the form like (3*(n+1)!)
    if match1:
        coefficient, variable, constant = match1.groups()
        if int(constant) > 0:
            output_string = f"({coefficient}*{variable})!"
            for i in range(1, int(coefficient)*int(constant) + 1):
                output_string += f"*({coefficient}*{variable}+{i})"
        elif int(constant) < 0:
            output_string = f"({coefficient}*{variable}{str(int(constant)*int(coefficient)-int(coefficient))})!"
            for i in range(1, int(coefficient) + 1):
                output_string += f"*({coefficient}*{variable}{int(constant)*int(coefficient)-int(coefficient)+i})"
        return output_string

    match2 = re.match(r'\((\w+)([-+]\d+)\)!', expression)   # the form like (n+1)! or (n-1)!
    if match2:
        variable, offset = match2.groups()
        offset = int(offset)
        if offset > 0:
            output_string = f"({variable}+{offset-1})!*({variable}+{offset})"
        elif offset < 0:
            if offset == -1:
                output_string = f"({variable}{offset})!*({variable})"
            else:
                output_string = f"({variable}{offset-1})!*({variable}{offset})"
        return output_string

def plus_one(expression):
    if not '))' in expression:
        if '(n-1)' in expression:
            return '(n)!'
        elif '+' in expression:
            result = expression.replace('n','n+1')
            index = result.find('+')
            result = result[:index] + '+' + str(eval(result[index:-2]))+ ')!'
            return result
        elif '-' in expression:
            result = expression.replace('n','n+1')
            index = result.find('+')
            result = result[:index] + str(eval(result[index:-2]))+ ')!'
            return result
        elif expression[1] == 'n':
            return expression.replace('(n)','(n+1)')
        else:
            return expression.replace('n','(n+1)')
    else:
        if '(n-1)' in expression:
            index = result.find('n')
            return result[:index+1] + '))!'
        elif '+' in expression:
            result = expression.replace('n','n+1')
            index = result.find('+')
            result = result[:index] + '+' + str(eval(result[index:-3]))+ '))!'
            return result
        else:
            result = expression.replace('n','n+1')
            index = result.find('+')
            result = result[:index] + str(eval(result[index:-3]))+ '))!'
            return result

def series_plus(expr):
    idx = 0
    for m in expr:
        if 'n' in m and not "!" in m and not "^" in m:
            m = m.replace('n','(n+1)')
            expr[idx] = m
        idx += 1
    idx = 0
    for m in expr:
        if '!' in m:
            m = plus_one(m)
            multi = expand_factorial(m)
            list_multi = multi.split('*')
            expr.pop(idx)
            expr.extend(list_multi)
        idx += 1
    idx = 0
    for m in expr:
        if '^n' in m:
            index = m.find('^')
            m = m.replace('n','(n+1)')
            multi = m[:index+1] + m[index+2] + '*' + m[:index+1] + f'({int(m[index+3:-1])})'
            list_multi = multi.split('*')
            expr.pop(idx)
            expr.extend(list_multi)
        idx += 1
    return expr



