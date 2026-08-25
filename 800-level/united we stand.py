# Problem: 1859A - United We Stand
# Description: Split the array into two non-empty groups with the required divisibility property.
# Pattern: Constructive partition; separate all maximum values from the smaller values.
# Test case: n=4, a=[1, 2, 2, 3] -> b=[1, 2, 2], c=[3]

count_cases = int(input())
for _ in range(count_cases):
    arr_len = int(input())
    arr = list(map(int, input().strip().split()))
    arr_2 = []
    arr_3 = []

    if len(set(arr)) == 1:
        print(-1)
        continue

    maximum = max(arr)
    for i in range(len(arr)):
        if arr[i] == maximum:
            arr_3.append(arr[i])

    for i in range(len(arr)):
        if arr[i] != maximum:
            arr_2.append(arr[i])

    print(len(arr_2), len(arr_3), sep=' ')
    print(*arr_2)
    print(*arr_3)
