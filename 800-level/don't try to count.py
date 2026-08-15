# Problem: 1881A - Don't Try to Count
# Description: Find the fewest string doublings needed to contain the target.
# Pattern: Brute force + strings; repeatedly double x and check for the substring.
# Test case: n=1, m=5, x=a, s=aaaaa -> 3

count_cases = int(input())

for _ in range(count_cases):
    n = list(map(int, input().split())) 
    x = input()
    s = input()
    
    op_count = 0
    found = False
    
    for i in range(7): #n.m <=25 so 6 is enough to cover all cases
        if s in x:
            print(op_count)
            found = True
            break
        x =  x + x
        op_count += 1
        
    if not found:
        print(-1)
