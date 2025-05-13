from series_plus_one import *
import math
from psevdoCalc import *

pc = psevdoCalc()

def ratio_test(series):

    def extract_substring(input_string, name):
        index = input_string.find('/')
        if name == 'num':
            if index != -1:
                result = input_string[:index].strip()
                multipliers = result.split('*')
                list_of_multipliers = [m.strip() for m in multipliers]
            return list_of_multipliers
        else:
            if index != -1:
                result = input_string[index+1:].strip()
                multipliers = re.split(r'\*', result)
                list_of_multipliers = [m.strip() for m in multipliers]
            return list_of_multipliers
    
    def remove_first_duplicates(list1, list2):
        for element in list1:
            if element in list2:
                list1.remove(element)
                list2.remove(element)
        return list1, list2

    numerator1 = extract_substring(series, 'num')
    denominator1 = extract_substring(series, 'den')
    numerator1 = series_plus(numerator1)
    denominator1 = series_plus(denominator1)

    numerator2 = extract_substring(series, 'num')
    denominator2 = extract_substring(series, 'den')

    numerator = []
    numerator.extend(remove_first_duplicates(numerator1, numerator2)[0])
    numerator.extend(remove_first_duplicates(denominator2, denominator1)[0])
    denominator = []
    denominator.extend(remove_first_duplicates(denominator1, denominator2)[0])
    denominator.extend(remove_first_duplicates(numerator1, numerator2)[1])

    num = "*".join(numerator)
    den = "*".join(denominator)

    q = pc.limit_inf(num,den)
    if isinstance(q,int) and q > 1:
        return 'A divergent series'
    elif isinstance(q,int) and q < 1:
        return 'A convergent series'
    elif q == 'infinity':
        return 'A divergent series'
    else:
        return 'Use another method'





# series1 = '(n+1)!/(n+5)*7^n'
# series2 = '(n+1)!/(n+5)'

# print(ratio_test(series1))
# print(ratio_test(series2))
    




