# Problem: 1858A - Buttons
# Description: Determine who wins when both players use their own and shared buttons.
# Pattern: Game + parity; shared pairs cancel, so only c % 2 can give Anna one extra move.
# Test case: a=1, b=1, c=1 -> First

count = int(input())
for _ in range(count):
    a, b, c = map(int, input().split())

    # c % 2 tells us if there is a leftover common move.
    # Anna wins if her base moves plus that leftover move beats b.
    if a + (c % 2) > b:
        print("First")
    else:
        print("Second")
