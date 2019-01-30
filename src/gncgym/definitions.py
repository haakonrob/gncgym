from math import sqrt
from collections import namedtuple

"""
Use Named Tuples to represent the various 'types' used in the environment.
This is done instead of just using arrays because of the variety of models
that the environment has to accommodate. Using named tuples instead allows
us to do things like:
    state.position.x
which is more resusable and clear when compared to numeric indexing. 
"""

Position = namedtuple('Position', ['x', 'y', 'z'])
Orientation = namedtuple('Orientation', ['roll', 'pitch', 'yaw'])
LinVel = namedtuple('LinVelocity', ['u', 'v', 'w'])
AngVel = namedtuple('AngVelocity', ['p', 'q', 'r'])
State6DOF = namedtuple('State', ['position', 'orientation', 'linVelocity', 'angVelocity'])

aliases = {
    'heading': 'yaw',
    'surge': 'u',
    'sway': 'v',
    'heave': 'w',
    'rollrate': 'p',
    'pitchrate': 'q',
    'yawrate': 'r',
}


def add(v1, v2):
    return Position(v1.x + v2.x, v1.y + v2.y, v1.z + v2.z)


def sub(v1, v2):
    return Position(v1.x - v2.x, v1.y - v2.y, v1.z - v2.z)


def dot(v1, v2):
    return (v1.x * v2.x) + (v1.y * v2.y) + (v1.z * v2.z)


def norm(v):
    return sqrt(dot(v, v))


def distance(v1, v2):
    return (v1.x - v2.x) ** 2 + (v1.y - v2.y) ** 2 + (v1.z - v2.z) ** 2


def normalise(v):
    L = norm(v)
    return Position(v.x / L, v.y / L, v.z / L)
