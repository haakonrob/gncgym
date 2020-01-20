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


# TODO Numpy has something called Record Arrays, which can be used exactly the same as these named tuples, but based on
#  the power of numpy arrays. This is the next step...

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
    def __init__(self, x=0, y=0, z=0, roll=0, pitch=0, yaw=0, surge=0, sway=0, heave=0, rollrate=0, pitchrate=0, yawrate=0):
        self.x,         self.y,         self.z = x, y, z
        self.roll,      self.pitch,     self.yaw = roll, pitch, yaw
        self.surge,     self.sway,      self.heave = surge, sway, heave
        self.rollrate,  self.pitchrate, self.yawrate = rollrate, pitchrate, yawrate

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
        return Velocity(self.surge, self.sway, self.heave, self.rollrate, self.pitchrate, self.yawrate)

    @velocity.setter
    def velocity(self, surge, sway, heave, rollrate, pitchrate, yawrate):
        self.surge = surge
        self.sway = sway
        self.heave = heave
        self.rollrate = rollrate
        self.pitchrate = pitchrate
        self.yawrate = yawrate


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


# TODO Consider moving to base.py
# TODO Consider calling ENVSnapshot EnvState instead
class EnvSnapshot:
    def __init__(self, timestamp: float, vessel: State6DOF, objects: dict, disturbances: dict, modules: dict):
        self.timestamp = timestamp
        self.vessel = vessel
        self.objects = objects
        self.disturbances = disturbances

    def repr(self):
        return "EnvSnapshot(timestamp={})".format(self.timestamp)


class ModuleSnapshot:
    def __init__(self, timestamp, model, objective, observer=None, controller=None):
        self.timestamp = timestamp
        self.signals = dict(
            model={'in': model.input, 'out': model.output},
            objective={'in': objective.input, 'out': objective.output},
            observer=None if observer is None else {'in': observer.input, 'out':observer.output},
            controller=None if controller is None else {'in': controller.input, 'out': controller.output})

    def repr(self):
        return "ModuleSnapshot(timestamp={})".format(self.timestamp)
