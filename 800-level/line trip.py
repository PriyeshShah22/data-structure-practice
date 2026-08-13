# Problem: 1901A - Line Trip
# Description: Find the smallest fuel tank that supports the round trip.
# Pattern: Greedy maximum gap; double the final gap because x has no station.
# Test case: n=3, x=7, stations=[1, 2, 5] -> 4

count = int(input())
for i in range(count):
    second_input = list(map(int, input().split()))
    third_input = list(map(int, input().split()))
    n = second_input[0]
    x = second_input[1]
    final_max = third_input[0]
    
    for i in range(len(third_input)- 1):
        max = third_input[i + 1] - third_input[i]
        if max > final_max:
            final_max = max
    
    final_calc = (x - third_input[-1])* 2
    if final_max <= final_calc:
        final_max = final_calc
        
    print(final_max)
