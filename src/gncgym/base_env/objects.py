import numpy as np
from numpy import pi, sin, cos

from gncgym.definitions import State6DOF
from gncgym.utils import distance,angwrap
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

    def update(self, *args):
        raise NotImplemented

    def draw(self, viewer):
        raise NotImplemented

    def destroy(self):
        pass


class StaticObstacle(EnvObject):
    def __init__(self, position, radius, color=(0.6,0,0)):
        self.color = color
        super().__init__(radius=radius, position=position)

    def update(self):
        pass

    def draw(self, viewer, color=None):
        viewer.draw_circle(self.position, self.radius, color=self.color if color is None else color)


# TODO Replace path, speed, and init_s with Trajectory object
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

    def update(self):
        self.s += self.speed * sim.env.dt
        self.position = self.path(self.s).flatten()
        self.angle = self.path.get_angle(self.s)

    def draw(self, viewer, color=None):
        viewer.draw_shape(self.vertices, self.position, self.angle, self.color if color is None else color)


class Vessel2D(EnvObject):
    def __init__(self, state: State6DOF, width=4):
        self.ref = [0, 0]  # surge, heading

        self.state = state

        self.path_taken = []
        self.color = (0.6, 0.6, 0.6)
        self.vertices = [
            (-width, -width),
            (-width, width),
            (2 * width, width),
            (3 * width, 0),
            (2 * width, -width),
        ]

        super().__init__(radius=width, angle=state.orientation.yaw, position=(state.position.x, state.position.y))

    def update(self, state, ref):
        self.state = state
        self.ref = ref

    def draw(self, viewer):
        position = self.state.position[0:2]
        orientation = self.state.orientation
        # print(orientation)
        viewer.draw_polyline(self.path_taken, linewidth=3, color=(0.8, 0, 0))  # previous positions
        viewer.draw_shape(self.vertices, position, orientation.yaw, self.color)  # ship
        viewer.draw_arrow(position, orientation.yaw + pi + self.ref[1]/2, length=2)
