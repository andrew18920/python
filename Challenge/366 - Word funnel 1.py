# https://www.reddit.com/r/dailyprogrammer/comments/98ufvz/20180820_challenge_366_easy_word_funnel_1/

funnelExamples = [
  ['leave', 'eave'],
  ['reset', 'rest'],
  ['dragoon', 'dragon'],
  ['eave', 'leave'],
  ['sleet', 'lets'],
  ['skiff', 'ski'],
]

bonusExamples = ["dragoon", "boats", "affidavit"]

def substrings(word):
    results = set()
    for x in range(len(word)):
        results.add(word[:x] + word[x+1:])
    return results

def funnel(word1, word2):
    if len(word1) != len(word2)+1:
        return False
    elif word2 in substrings(word1):
        return True
    return False

words = set(open('enable1.txt','r').read().split('\n'))

def funnelList(word):
    results = []
    candidates = substrings(word)
    for candidate in candidates:
        if candidate in words:
            results.append(candidate)
    return results

def fiveOptions():
    results = []
    for word in words:
        if len(word)>4:
            if len(funnelList(word))==5:
                results.append(word)
    return results
            
    

print('\nFunnel:')
[print(funnel(set[0], set[1])) for set in funnelExamples]

print('\nBonus 1:')
[print(funnelList(set)) for set in bonusExamples]

print('\nBonus 2:')
print(fiveOptions())


