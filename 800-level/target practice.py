# Problem: 1873C - Target Practice
# Description: Calculate the total score of all arrows on the target.
# Pattern: Grid simulation; each X scores one plus its minimum distance from an edge.
# Test case: one X at grid[0][0], all other cells are dots -> 1

count_cases = int(input())

for _ in range(count_cases):
    total_score = 0

    for i in range(10):
        row_str = input().strip()
        for j in range(10):
            if row_str[j] == 'X':
                distance_from_edge = min(i, j, 9 - i, 9 - j)
                total_score += distance_from_edge + 1

    print(total_score)
