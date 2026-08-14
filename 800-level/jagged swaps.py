# Problem: 1896A - Jagged Swaps
# Description: Decide whether the allowed peak swaps can sort the permutation.
# Pattern: Invariant; the first value never moves, so it must already be 1.
# Test case: n=3, permutation=[3, 1, 2] -> NO

count = int(input())
for i in range(count):
    second_input = list(map(int, input().split()))
    third_input = list(map(int, input().split()))
    
    if third_input[0] == 1:
        print("YES")   
    else:
        print("NO")
