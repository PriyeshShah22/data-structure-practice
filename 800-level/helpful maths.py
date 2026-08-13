# Problem: 339A - Helpful Maths
# Description: Rearrange the summands into non-decreasing order.
# Pattern: Split the string, sort the numbers, then join them again.
# Test case: 3+2+1 -> 1+2+3

numbers = input().split('+')
number = list(map(int, numbers))
number.sort()
print('+'.join(list(map(str,number))))
