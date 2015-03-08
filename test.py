__author__ = 'zephyryin'

import copy


def getPermutations(a):
    result = []
    temp = []
    height = len(a)
    print height
    permutations(a, result, temp, 0, height)
    return result


def permutations(a, result, temp, depth, height):
    if depth >= height:
        result.append(copy.deepcopy(temp))
        return
    for r in a[depth]:
        temp.append(r)
        permutations(a, result, temp, depth+1, height)
        temp.pop(-1)



a = [[1,2,3],[4,5],[6]]
result = getPermutations(a)
for r in result:
    print r