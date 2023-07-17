from decimal import Decimal
import math

value = "1.1072928695148106e+17"

decial = value.split('e+')
number = decial[0].replace(".", "")
integer_str = int(number)
print(integer_str)
