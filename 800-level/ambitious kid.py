# Problem: 1866A - Ambitious Kid
# Description: Find the minimum number of moves needed to make the product of the array zero.
# Pattern: Minimum absolute value; changing the closest element to zero takes the fewest moves.
# Test case: n=5, a=[1, 2, 3, 4, 5] -> 1

n = int(input())
a = list(map(int, input().split()))

closest = min(map(abs, a))
print(closest)
