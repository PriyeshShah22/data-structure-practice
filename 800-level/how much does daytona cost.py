# Problem: 1878A - How Much Does Daytona Cost?
# Description: Determine whether k can be the most common value in any non-empty subsegment.
# Pattern: Membership check; if k appears, the one-element subsegment [k] is enough.
# Test case: n=4, k=1, a=[2, 3, 4, 4] -> NO because 1 never appears in the array.

count = int(input())

for _ in range(count):
    n = list(map(int, input().split()))
    a = list(map(int, input().split()))

    num = n[1]
    if num in a:
        print("YES")
    else:
        print("NO")
