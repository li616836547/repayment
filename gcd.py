import sys
def gcd(a, b):
    if b == 0:
        return a
    else:
        return gcd(b, a%b)


def solution(n):
    a = 1
    for i in range(1, n+1):
        now = int(i / gcd(a, i))
        a *= now
    return a

