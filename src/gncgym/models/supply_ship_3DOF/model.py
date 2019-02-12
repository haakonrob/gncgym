import numpy as np
from numpy import pi, vstack
from gym.spaces import Box
from gncgym.models import Model
from gncgym.simulator.blocks import make_integrator_block
from .shipDynamics import make_supply_ship_dynamics_block


THRUST_MIN = 0
THRUST_MAX = 10000000
RUDDER_MIN = pi
RUDDER_MAX = -pi


class SupplyShip3DOF(Model):
    def __init__(self, x0):
        # Mandatory Model definitions
        self.input_space = Box(low=np.array([0, -1]), high=np.array([1, 1]))
        self.output_map = ['x', 'y', 'yaw', 'surge', 'sway', 'yawrate']

        # Initialise the integrator and the model dynamics
        self.state = x0.copy()
        self.integrate = make_integrator_block(x0)
        self.ship_dynamics = make_supply_ship_dynamics_block()

    def _step(self, u, v=None):
        f = vstack(u)  # f is always a column vector, no matter if u is either a row or column vector
        f[0, :] *= THRUST_MAX  # Rescale
        f[1, :] = f[1,:] * pi
        state_dot = self.ship_dynamics(self.state, f)
        self.state = self.integrate(state_dot)
        return self.state

