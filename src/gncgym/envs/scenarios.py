import numpy as np
from numpy import sin, cos
from .base import BaseShipScenario
from ship_env.parametrisedCurves import RandomLineThroughOrigin, RandomCurveThroughOrigin, ParamCircle, ParamLine
from .objects import Vessel2D, StaticObstacle, DynamicObstacle, distance, MAX_SURGE, CROSS_TRACK_TOL, SURGE_TOL


class ExampleScenario(BaseShipScenario):
    def generate(self, rng):
        self.path = RandomLineThroughOrigin(rng, length=500)
        x, y = self.path(0)
        angle = self.path.get_angle(0)
        self.speed = 4

        self.ship = Vessel2D(angle, x, y)

        self.static_obstacles.append(
            StaticObstacle(position=self.path(100), radius=10, color=(0.6, 0, 0))
        )

        self.dynamic_obstacles.append(
            DynamicObstacle(self.path, speed=4, init_s=50)
        )


class StraightPathScenario(BaseShipScenario):
    def generate(self, rng):
        self.path = RandomLineThroughOrigin(rng, length=500)
        self.speed = 4

        x, y = self.path(0)
        angle = self.path.get_angle(0)
        x += 2*(rng.rand()-0.5)
        y += 2*(rng.rand()-0.5)
        angle += 0.1*(rng.rand()-0.5)
        self.ship = Vessel2D(angle, x, y)


class CurvedPathScenario(BaseShipScenario):
    def __init__(self, linearising_feedback=True):
        self.linFB = linearising_feedback
        super().__init__()

    def generate(self, rng):
        L = 400
        a = 2*np.pi*(rng.rand()-0.5)
        self.path = RandomCurveThroughOrigin(rng, start=((L*cos(a), L*sin(a))))
        self.speed = 4

        x, y = self.path(0)
        angle = self.path.get_angle(0)
        x += 2*(rng.rand()-0.5)
        y += 2*(rng.rand()-0.5)
        angle += 0.1*(rng.rand()-0.5)
        self.ship = Vessel2D(angle, x, y, linearising_feedback=self.linFB)


class CircularPathScenario(BaseShipScenario):
    def generate(self, rng):
        self.path = ParamCircle((0, 0), 300)
        self.speed = 4

        x, y = self.path(0)
        angle = self.path.get_angle(0)
        x += 2*(rng.rand()-0.5)
        y += 2*(rng.rand()-0.5)
        angle += 0.1*(rng.rand()-0.5)
        self.ship = Vessel2D(angle, x, y)


class StraightPathOvertakingScenario(BaseShipScenario):
    def generate(self, rng):
        L = 400
        a = 2*np.pi*(rng.rand()-0.5)
        self.path = RandomLineThroughOrigin(rng, start=((L*cos(a), L*sin(a))))
        self.speed = 4

        x, y = self.path(0)
        angle = self.path.get_angle(0)
        x += 2*(rng.rand()-0.5)
        y += 2*(rng.rand()-0.5)
        angle += 0.1*(rng.rand()-0.5)

        self.dynamic_obstacles.append(DynamicObstacle(self.path, speed=2, init_s=20))
        self.ship = Vessel2D(angle, x, y)


class CurvedPathOvertakingScenario(BaseShipScenario):
    def generate(self, rng):
        L = 400
        a = 2*np.pi*(rng.rand()-0.5)
        self.path = RandomCurveThroughOrigin(rng, start=((L*cos(a), L*sin(a))))
        self.speed = 4

        x, y = self.path(0)
        angle = self.path.get_angle(0)
        x += 2*(rng.rand()-0.5)
        y += 2*(rng.rand()-0.5)
        angle += 0.1*(rng.rand()-0.5)

        self.dynamic_obstacles.append(DynamicObstacle(self.path, speed=2, init_s=20))
        self.ship = Vessel2D(angle, x, y)


class StraightPathShipCollisionScenario(BaseShipScenario):
    def generate(self, rng):
        # L = 400
        # a = 2*np.pi*(rng.rand()-0.5)
        self.path = RandomLineThroughOrigin(rng, length=400)
        self.speed = 4
        x, y = self.path(0)
        angle = self.path.get_angle(0)
        x += 2*(rng.rand()-0.5)
        y += 2*(rng.rand()-0.5)
        angle += 0.1*(rng.rand()-0.5)
        self.ship = Vessel2D(angle, x, y)

        self.dynamic_obstacles.append(DynamicObstacle(reversed(self.path), speed=2, init_s=20))


class CurvedPathShipCollisionScenario(BaseShipScenario):
    def generate(self, rng):
        L = 400
        a = 2*np.pi*(rng.rand()-0.5)
        self.path = RandomCurveThroughOrigin(rng, start=((L*cos(a), L*sin(a))))
        self.speed = 4

        x, y = self.path(0)
        angle = self.path.get_angle(0)
        x += 2*(rng.rand()-0.5)
        y += 2*(rng.rand()-0.5)
        angle += 0.1*(rng.rand()-0.5)
        self.ship = Vessel2D(angle, x, y)

        self.dynamic_obstacles.append(DynamicObstacle(reversed(self.path), speed=2, init_s=20))


class CurvedPathStaticObstacles(BaseShipScenario):
    def generate(self, rng):
        L = 400
        a = 2 * np.pi * (rng.rand() - 0.5)
        self.path = RandomCurveThroughOrigin(rng, start=((L * cos(a), L * sin(a))))
        self.speed = 4

        x, y = self.path(0)
        angle = self.path.get_angle(0)
        x += 2*(rng.rand()-0.5)
        y += 2*(rng.rand()-0.5)
        angle += 0.1*(rng.rand()-0.5)
        self.ship = Vessel2D(angle, x, y, linearising_feedback=False)

        for i in range(10):
            self.static_obstacles.append(StaticObstacle(
                self.path(0.9*self.path.length*(rng.rand() + 0.1)).flatten() + 100*(rng.rand(2)-0.5), radius=10*(rng.rand()+0.5) ))


class CurvedPathStaticDynamicObstacles(BaseShipScenario):
    def generate(self, rng):
        L = 400
        a = 2 * np.pi * (rng.rand() - 0.5)
        self.path = RandomCurveThroughOrigin(rng, start=((L * cos(a), L * sin(a))))
        self.speed = 4

        x, y = self.path(0)
        angle = self.path.get_angle(0)
        x += 2*(rng.rand()-0.5)
        y += 2*(rng.rand()-0.5)
        angle += 0.1*(rng.rand()-0.5)
        self.ship = Vessel2D(angle, x, y)

        straightpath = ParamLine(startpoint=self.path(0).flatten(), endpoint=self.path.get_endpoint().flatten())

        for i in range(rng.randint(5, 20)):
            self.static_obstacles.append(StaticObstacle(
                self.path(0.9*self.path.length*(rng.rand() + 0.1)).flatten() + 100*(rng.rand(2)-0.5), radius=10*(rng.rand()+0.5) ))

        for i in range(rng.randint(-10, 3)):
            init_s = 0.9 * self.path.length * (rng.rand() + 0.1)
            speed = (rng.rand()+1/6)*6
            p = rng.choice([self.path, reversed(self.path), straightpath, reversed(straightpath)])
            self.dynamic_obstacles.append(DynamicObstacle(path=p, speed=speed, init_s=init_s))
