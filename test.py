def f(s):
    if s is None:
        return
    deep = len(s)
    k = 0
    result = recurrent(s, deep, k)
    print(result)


def recurrent(s, deep, k):
    print('s:{}'.format(s))
    if not s:
        print(k)
        return k
    if deep == 1:
        k = k + ishuiwei(s)
        print(k)
    recurrent(s, deep-1, k)
    recurrent(s[1:], deep-1, k)


def ishuiwei(s):
    print('dd')
    n = len(s)
    for i in range(n//2):
        if s[i] != s[i-1]:
            return 0
    return 1