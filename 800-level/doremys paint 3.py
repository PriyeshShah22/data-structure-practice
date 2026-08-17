# Problem: 1890A - Doremy's Paint 3
# Description: Check whether the array can be rearranged so every adjacent pair has the same sum.
# Pattern: Frequency counting; use at most two values whose frequencies differ by at most one.

from collections import Counter

count = int(input())

for _ in range(count):
    n = int(input())
    a = list(map(int, input().split()))

    freq = Counter(a)
    Values = list(freq.values())

    if len(Values) > 2:
        print("NO")
    elif len(Values) == 1:
        print("YES")
    else:
        freq1 = Values[0]
        freq2 = Values[1]
        diff = abs(freq1 - freq2)

        if diff <= 1:
            print("YES")
        else:
            print("NO")

# Worked test case: n=3, a=[1, 1, 2]
# The values have frequencies 2 and 1, whose difference is 1, so they can alternate.
# Rearrange the array as [1, 2, 1]: 1+2=3 and 2+1=3, so every adjacent sum is equal.
# Therefore, the answer is YES.
