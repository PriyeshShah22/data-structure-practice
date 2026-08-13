# Problem: 1903A - Halloumi Boxes
# Description: Decide whether limited subarray reversals can sort the boxes.
# Pattern: Greedy + sorting; k >= 2 permits sorting, otherwise it must already be sorted.
# Test case: n=2, k=1, boxes=[3, 1] -> NO

count = int(input())
for i in range(count):
    second_input = list(map(int, input().split()))
    third_input = list(map(int, input().split()))
    
    n = second_input[0]
    k = second_input[1]
    
    if third_input == sorted(third_input) or k >= 2:
        print("YES")   
    else:
        print("NO")
