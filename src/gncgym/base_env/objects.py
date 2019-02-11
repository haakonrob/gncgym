import numpy as np
from numpy import pi, sin, cos
from gncgym.simulator.angle import Angle
from gncgym.utils import distance
from gncgym.models.supply_ship_3DOF import make_supply_ship_block
import gncgym.simulator as sim

# Top-down ship dynamics simulation.
#
# This code, and the rest of the ship base_env is heavily based on Oleg Klimov's car_racing environment for the OpenAI
# gym. Oleg did a great job of combining the gym's classical control rendering module and some custom visuals
# by calling the Pyglet gl API directly. This functionality includes camera following, a fancy 'zoom in' on startup,
# and a few indicators for the total reward achieved, the current speed, and the control inputs. I've taken this
# functionality, replaced the Box2D simulation and replaced it with my own ship simulation code,
#
# Created by Haakon Robinson.

MAX_SURGE = 20
CROSS_TRACK_TOL = 10
SURGE_TOL = 0.5

RUDDER_RATE = 0.1
SURGE_RATE = 0.2

THRUST_MIN = 0
THRUST_MAX = 10000000
RUDDER_MIN = pi
RUDDER_MAX = -pi


class EnvObject:
    def __init__(self, radius, angle=0.0, position=(0.0, 0.0), linearVelocity=(0.0, 0.0), angularVelocity=0):
        if not isinstance(position, np.ndarray):
            position = np.array(position)
        if radius < 0:
            raise ValueError
        self.radius = radius
        self.position = position.flatten()
        self.angle = angle
        self.linearVelocity = linearVelocity
        self.angularVelocity = angularVelocity

    def step(self):
        raise NotImplemented

    def draw(self, viewer):
        raise NotImplemented

    def destroy(self):
        pass


class StaticObstacle(EnvObject):
    def __init__(self, position, radius, color=(0.6,0,0)):
        self.color = color
        super().__init__(radius=radius, position=position)

    def step(self):
        pass

    def draw(self, viewer, color=None):
        viewer.draw_circle(self.position, self.radius, color=self.color if color is None else color)


class DynamicObstacle(EnvObject):
    def __init__(self, path, speed, init_s=0, color=(0.6, 0, 0), width=5):
        # Create body
        self.s = init_s
        self.path = path
        self.speed = speed
        self.color = color
        x, y = self.path(0)
        angle = self.path.get_angle(0)
        self.vertices = [
            (-width, -width),
            (-width, width),
            (2 * width, width),
            (3 * width, 0),
            (2 * width, -width),
        ]
        super().__init__(radius=width, angle=angle, position=(x, y), linearVelocity=(speed*cos(angle), speed*sin(angle)))

    def step(self):
        self.s += self.speed * sim.env.dt
        self.position = self.path(self.s).flatten()
        self.angle = self.path.get_angle(self.s)

    def draw(self, viewer, color=None):
        viewer.draw_shape(self.vertices, self.position, self.angle, self.color if color is None else color)


# TODO Step specified model
class Vessel2D(EnvObject):
    def __init__(self, init_angle, init_x, init_y, width=4, linearising_feedback=True):
        self.lin_feedback = linearising_feedback
        self.ref = [0, Angle(init_angle)]  # surge, heading

        self.state = np.vstack((init_x, init_y, init_angle, 0, 0, 0))
        self.model = make_supply_ship_block(self.state, linearising_feedback=linearising_feedback)
        self.path_taken = []
        self.color = (0.6, 0.6, 0.6)
        self.vertices = [
            (-width, -width),
            (-width, width),
            (2 * width, width),
            (3 * width, 0),
            (2 * width, -width),
        ]

        super().__init__(radius=width, angle=init_angle, position=(init_x, init_y))

    def surge(self, surge):
        surge = np.clip(surge, -1, 1)
        if self.lin_feedback:
            self.ref[0] = np.clip(self.ref[0] + surge*SURGE_RATE, 0, MAX_SURGE)
        else:
            self.ref[0] = surge*(THRUST_MAX - THRUST_MIN) + THRUST_MIN

    def steer(self, steer):
        steer = np.clip(steer, -1, 1)
        if self.lin_feedback:
            self.ref[1] = float(Angle(self.ref[1] + steer * RUDDER_RATE))
        else:
            self.ref[1] = steer*RUDDER_MAX

    def step(self):
        self.state = self.model(self.ref)
        self.position = tuple(self.state[0:2, :].flatten())
        self.angle = float(self.state[2])
        self.linearVelocity = tuple(self.state[3:5].flatten())
        self.angularVelocity = float(self.state[5])

        if self.path_taken == [] or distance(self.position, self.path_taken[-1]) > 3:
            self.path_taken.append(self.position)

    def draw(self, viewer):
        viewer.draw_polyline(self.path_taken, linewidth=3, color=(0.8, 0, 0))  # previous positions
        viewer.draw_shape(self.vertices, self.position, self.angle, self.color)  # ship
        if self.lin_feedback:
            viewer.draw_arrow(self.position, self.ref[1], length=5)  # reference
        else:
            viewer.draw_arrow(self.position, self.angle + pi + self.ref[1]/4, length=2)
