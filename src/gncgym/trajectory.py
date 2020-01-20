import math
from copy import deepcopy
import numpy as np
from numpy import pi

# import matplotlib.pyplot as plt
from scipy import interpolate
from scipy.optimize import fminbound
from gncgym.utils import angwrap


class Trajectory:
    def __init__(self, t,
                 x, y, z=None, u=None, v=None, w=None,
                 roll=None, pitch=None, yaw=None, rollrate=None, pitchrate=None, yawrate=None):
        pass

    def __call__(self, *args, **kwargs):
        pass

class ParamLine():
    def __init__(self, startpoint, endpoint):
        self.startpoint = startpoint
        self.endpoint = endpoint
        x1, y1 = startpoint
        x2, y2 = endpoint
        dx = x2 - x1
        dy = y2 - y1
        L = math.sqrt(dx ** 2 + dy ** 2)
        a_x = dx/L
        a_y = dy/L

        self.A = np.array([[a_x], [a_y]])
        self.p0 = np.array([[x1], [y1]])
        self.length = L
        self.angle = angwrap(np.arctan2(dy, dx))

    def __call__(self, s):
        s = np.array(s)
        return self.p0 + self.A * np.vstack([s,s])

    def get_angle(self, s=None):
        if s is None:
            return self.angle
        s = np.array(s)
        if s.shape == ():
            s = np.array([s])
        return np.array([self.angle for i in s])

    def get_endpoint(self):
        return self(self.length)

    def get_closest_s(self, p):
        p = np.vstack(p)
        # if p.shape != 2:
        #     p = np.transpose(p)
        return fminbound(lambda s: np.linalg.norm(self(s) - p), 0, self.length, xtol=1e-2)

    def plot(self, ax, s, *opts):

        z = self(s)
        ax.plot(-z[1,:], z[0,:], *opts)

    def __reversed__(self):
        return ParamLine(self.endpoint, self.startpoint)


class ParamCurve():
    def __init__(self, waypoints):
        waypoints = np.array(waypoints)
        if waypoints.shape[0] != 2:
            waypoints = np.transpose(waypoints)

        Z = waypoints
        for i in range(3):
            S = arc_len(Z)
            C = interpolate.pchip(x=S, y=Z, axis=1)
            Z = C(np.linspace(S[0], S[-1], 1000))

        self.C = C
        self.s_min = S[0]
        self.s_max = S[-1]
        self.length = self.s_max

    def __call__(self, s, check_domain=False):
        s = np.array(s)
        if check_domain and s.min() < self.s_min or s.max() > self.s_max:
            pass
            # logging.warning('Argument s outside of curve domain: {}'.format((self.s_min, self.s_max)))
        return self.C(s)

    def get_angle(self, s, check_domain=False):
        s = np.array(s)
        if check_domain and s.min() < self.s_min or s.max() > self.s_max:
            pass
            # logging.warning('Argument s outside of curve domain: {}'.format((self.s_min, self.s_max)))

        if s.shape == ():
            s = np.array([s])
        output = []
        for ss in s:
            dx, dy = (self.C(ss + 0.05) - self.C(ss - 0.05)).flatten()
            output.append(angwrap(np.arctan2(dy, dx)))
        return np.array(output)

    def get_endpoint(self):
        return self(self.s_max)

    def get_closest_s(self, p):
        # p = np.vstack(p)
        # if p.shape != 2:
        #     p = np.transpose(p)

        def distance(p1, p2):
            return np.sqrt((float(p1[0]) - float(p2[0]))**2 + (float(p1[1]) - float(p2[1]))**2)

        return fminbound(lambda s: distance(self(s), p), x1=0, x2=self.length, xtol=1e-6, maxfun=10000)

    def __reversed__(self):
        curve = deepcopy(self)
        C = curve.C
        curve.C = lambda s: C(curve.length-s)
        return curve

    def plot(self, ax, s, *opts):
        s = np.array(s)
        z = self(s)
        ax.plot(-z[1,:],z[0,:], *opts)


class ParamCircle:
    def __init__(self, center, radius):
        self.R = radius
        self.center = np.array(center)
        if self.center.shape == (2,):
            self.center = np.transpose([self.center])
        self.length = 2*pi*self.R

    def __call__(self, s):
        p = np.vstack([self.R*np.cos(s/self.R), self.R*np.sin(s/self.R)])
        return p + self.center

    def get_angle(self, s):
        s = np.array(s)
        if s.shape == ():
            s = np.array([s])
        return np.array([angwrap(pi/2 + ss/self.R) for ss in s])

    def get_endpoint(self):
        return self(self.length-100)

    def get_closest_s(self, p):
        # p = np.vstack(p)
        # if p.shape != 2:
        #     p = np.transpose(p)

        def distance(p1, p2):
            return np.sqrt((float(p1[0]) - float(p2[0]))**2 + (float(p1[1]) - float(p2[1]))**2)

        return fminbound(lambda s: distance(self(s), p), x1=0, x2=self.length, xtol=1e-3, maxfun=10000)

    def plot(self, ax, s, *opts):
        s = np.array(s)
        z = self(s)
        ax.plot(-z[1, :], z[0, :], *opts)


class RandomLineThroughOrigin(ParamLine):
    def __init__(self,  rng, length=100, origin=(0,0)):
        angle = math.pi*rng.randint(0, 360)/180
        x1, y1 = math.cos(angle)*length/2 + origin[0], math.sin(angle)*length/2 + origin[1]
        x2, y2 = -x1, -y1
        super().__init__([x1, y1], [x2, y2])


class RandomCurveThroughOrigin(ParamCurve):
    def __init__(self, rng, start, end=None):
        p = []
        if end is None:
            end = -np.array(start)

        for vec in [start, end]:
            vec = np.array(vec)
            L = np.sqrt(np.sum(vec ** 2))
            p.append(vec/2.0 + L/4*(rng.rand()-0.5))

        super().__init__([start, p[0], [0, 0], p[1], end])


def arc_len(Z):
    Z = np.array(Z)
    diffZ = np.diff(Z, axis=1)
    dZ = np.sqrt(np.sum(diffZ ** 2, axis=0))
    return np.concatenate([[0], np.cumsum(dZ)])


if __name__ == '__main__':
    from random import random
    import matplotlib.pyplot as plt
    fig, (ax11, ax12) = plt.subplots(1, 2)

    start = 10*(random()-0.5), 10*(random()-0.5)
    end = -start[0] + 3*(random()-0.5), -start[1] + 3*(random()-0.5)

    C = ParamCircle((0,1), 5)
    s = np.linspace(0, C.length, 500)
    z = C(s)
    a = C.get_angle(s)
    ax11.plot(z[0, :], z[1, :], 'b')
    ax11.plot([0], [1], 'ro')
    ax11.axis('equal')

    # ax11.plot(start[0], start[1], 'go')

    ax12.plot(s, a, 'g')
    ax12.axis([min(s), max(s), -pi, pi])



    plt.show()
