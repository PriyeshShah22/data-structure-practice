# Problem: 1899A - Game with Integers
# Description: Determine which player wins while changing the integer by one.
# Pattern: Game + modulo 3; First wins unless the starting number is divisible by 3.
# Test case: n=3 -> Second

count = int(input())
for i in range(count):
    second_input = list(map(int, input().split()))
    
    if second_input[0] == 1:
        print("First")
    elif second_input[0] % 3 == 0:
        print("Second")
    else:
        print("First")
