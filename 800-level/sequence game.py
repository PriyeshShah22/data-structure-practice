# Problem: 1862B - Sequence Game
# Description: Construct a valid original sequence that produces the given sequence.
# Pattern: Constructive insertion; duplicate a value whenever it follows a decrease.
# Test case: b=[1, 3, 2] -> a=[1, 3, 2, 2]

count_cases = int(input())
for _ in range(count_cases):
    arr_len = int(input())
    arr = list(map(int, input().strip().split()))
    arr_2 = []
    arr_2.append(arr[0])
    for i in range(1, arr_len):
        if arr[i - 1] <= arr[i]:
            arr_2.append(arr[i])
        else:
            arr_2.extend([arr[i], arr[i]])

    print(len(arr_2))
    print(*arr_2)
