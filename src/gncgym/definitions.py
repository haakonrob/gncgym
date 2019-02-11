import sys
from math import sqrt
from collections import namedtuple

"""
Use Named Tuples to represent the various 'types' used in the environment.
This is done instead of just using arrays because of the variety of models
that the environment has to accommodate. Using named tuples instead allows
us to do things like:
    state.x
or
    distance(state1.position, state2.position)
which is more resusable and clear when compared to numeric indexing.
"""

this = sys.modules[__name__]

position_vars = ['x', 'y', 'z']
orientation_vars = ['roll', 'pitch', 'yaw']
linvel_vars = ['surge', 'sway', 'heave']
angvel_vars = ['rollrate', 'pitchrate', 'yawrate']

this.variables = [*position_vars, *orientation_vars, *linvel_vars, *angvel_vars]

this.aliases = {
    'heading': 'yaw',
    'psi': 'yaw',
    'phi': 'roll',
    'theta': 'pitch',
    'u': 'surge',
    'v': 'sway',
    'w': 'heave',
    'p': 'rollrate',
    'q': 'pitchrate',
    'r': 'yawrate',
    'nu': 'pose',
    'eta': 'velocity',
}

Position = namedtuple('Position', position_vars)
Orientation = namedtuple('Orientation', orientation_vars)
Pose = namedtuple('Pose', [*position_vars, *orientation_vars])

LinVel = namedtuple('LinVelocity', linvel_vars)
AngVel = namedtuple('AngVelocity', angvel_vars)
Velocity = namedtuple('Velocity', [*linvel_vars, *angvel_vars])


class State6DOF:
    def __init__(self, pos, ori, lvel, avel):
        self.x,         self.y,         self.z =        pos
        self.roll,      self.pitch,     self.yaw =      ori
        self.surge,     self.sway,      self.heave =    lvel
        self.rollrate,  self.pitchrate, self.yawrate =  avel

    @property
    def position(self):
        return Position(self.x, self.y, self.z)

    @property
    def orientation(self):
        return Orientation(self.roll, self.pitch, self.yaw)

    @property
    def pose(self):
        return Pose(self.x, self.y, self.z, self.surge, self.sway, self.heave)

    @property
    def linVelocity(self):
        return LinVel(self.surge, self.sway, self.heave)

    @property
    def angVelocity(self):
        return AngVel(self.rollrate, self.pitchrate, self.yawrate)

    @property
    def velocity(self):
        return Orientation(self.surge, self.sway, self.heave, self.rollrate, self.pitchrate, self.yawrate)


def add(v1, v2):
    assert type(v1) is type(v2), "Tried to add different types {} and {}.".format(type(v1), type(v2))
    return type(v1)(*[a + b for a, b in zip(v1, v2)])


def sub(v1, v2):
    assert type(v1) is type(v2), "Tried to sub different types {} and {}.".format(type(v1), type(v2))
    return type(v1)(*[a - b for a, b in zip(v1, v2)])


def dot(v1, v2):
    assert len(v1) == len(v2), "Tried to dot different types {} and {}.".format(type(v1), type(v2))
    return sum(a * b for a, b in zip(v1, v2))


def norm(v):
    return sqrt(dot(v, v))


def distance(v1, v2):
    assert type(v1) is type(v1), "Tried to find distance between different types {} and {}.".format(type(v1), type(v2))
    return sqrt(sum((a - b)**2 for a, b in zip(v1, v2)))


def normalise(v):
    L = norm(v)
    return type(v)(*[p/L for p in v])
