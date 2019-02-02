import numpy as np


def distance(p1, p2):
    return np.sqrt((float(p1[0]) - float(p2[0]))**2 + (float(p1[1]) - float(p2[1]))**2)


def rotate(vec, angle):
    if isinstance(vec, np.ndarray):
        vec = vec.flatten()
    angle = float(angle)
    return (vec[0]*np.cos(angle) - vec[1]*np.sin(angle), vec[1]*np.cos(angle) + vec[0]*np.sin(angle))


def flatten(li):
    return [i for i in dfs(li)] if not isinstance(li, np.ndarray) else li.flatten()


def between(x, a, b):
    return (a > b and a > x > b) or (a < b and a < x < b)


def sign(x):
    # No zero on purpose
    return 1 if x > 0 else -1


def dfs(li):
    for i in li:
        if type(li) is not list and type(li) is not tuple:
            yield i
        else:
            for j in dfs(i):
                yield j
