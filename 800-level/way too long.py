# Problem: 71A - Way Too Long Words
# Description: Abbreviate words longer than ten characters.
# Pattern: String length check + first/count/last construction.
# Test case: localization -> l10n

count = int(input())
words =[]
for i in range(count):
    words.append(input().strip())
for word in words:
    if(len(word) > 10):
        short = word[0] + str(len(word)-2) + word[-1]
        print(short)
    else: 
        print(word)
