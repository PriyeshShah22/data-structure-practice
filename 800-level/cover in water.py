# Problem: 1900A - Cover in Water
# Description: Find the minimum water placements needed to fill every empty cell.
# Pattern: Greedy; three consecutive empty cells need only 2, otherwise count all dots.
# Test case: n=7, cells=..#.#.. -> 5

count = int(input())
for i in range(count):
    n = int(input())
    string = input()
    count = 0
    if '...' in string:
        print(2)   
    else:
        for i in string:
            if i == '.':
                count += 1
        print(count)
        # string.count('.')
