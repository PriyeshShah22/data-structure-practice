# Problem: 1877A - Goals of Victory
# Description: Find the missing team's efficiency from the efficiencies of all other teams.
# Pattern: Math invariant; every team's efficiency sums to zero, so negate the known sum.
# Test case: n=4, efficiencies=[3, -4, 5] -> -(3-4+5) = -4

count = int(input())

for _ in range(count):
    n = input()
    a = list(map(int, input().split()))

    final = -(sum(a))
    print(final)
