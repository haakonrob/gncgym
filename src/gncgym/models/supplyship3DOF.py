import numpy as np
from numpy import pi, vstack
from gym.spaces import Box
from gncgym.models import Model
from gncgym.simulator.blocks import make_integrator_block

from gncgym.utils import angwrap
from numpy.linalg import inv
from .gncUtilities import m2c, Rzyx


"""
####### Constants #######
"""


THRUST_MIN = 0
THRUST_MAX = 10000000
RUDDER_MIN = pi
RUDDER_MAX = -pi


M = np.array([
        [7.22e6, 0, 0],
        [0, 1.21e7, -3.63e7],
        [0, -3.63e7, 4.75e9]
    ])

D = np.array([
    [95070, 0, 0],
    [0, 4.34e6, -2.27e6],
    [0, -1.88e7, 7.57e8]
])

B = np.array([
    [1, 0],
    [0, -1.13e6],
    [0, 9.63e7]
])

eps = -(M[2, 2]*B[1, 1] - M[1, 2]*B[2, 1]) / (M[1, 1]*B[2, 1] - M[1, 2]*B[1, 1])

H = np.eye(3)
H[1, 2] = -eps

M_p = np.transpose(H).dot(M).dot(H)
D_p = np.transpose(H).dot(D).dot(H)
B_p = np.transpose(H).dot(B)

K1 = B[0, 0]/M[0, 0]
K2 = (M[1, 1]*B[2, 1]-M[1, 2]*B[1, 1])/(M[1, 1]*M[2, 2]-M[1, 2]*M[1, 2])

M_6DOF = np.zeros([6, 6])
M_6DOF[0:2, 0:2] = M_p[0:2, 0:2]
M_6DOF[1, 5] = M_p[1, 2]
M_6DOF[5, 1] = M_p[1, 2]
M_6DOF[5, 5] = M_p[2, 2]

M_p_inv = inv(M_p)


"""
####### Model #######
"""


class SupplyShip3DOF(Model):
    _model_state = None
    _model_integrate = None

    def reset_model(self, x0):
        # Initialise the integrator and the model dynamics
        x0 = np.vstack(x0)  # Column vector
        self._model_state = x0
        self._model_integrate = make_integrator_block(x0)

    def step_model(self, u, v=None):
        f = vstack(u)  # f is always a column vector, no matter if u is either a row or column vector
        # TODO move rescaling inside model equations
        f[0, :] *= THRUST_MAX  # Rescale thrust
        f[1, :] = f[1,:] * pi  # Rescale angle
        state_dot = self._dynamics(self._model_state, f)
        self._model_state = self._model_integrate(state_dot)
        return self._model_state

    def _dynamics(self, state, f):
        """
        The dynamic model of the supply ship.
        :param state: [eta, nu] = [x,y,psi,u,v,r]
        :param f: [u_des, delta_r]
        :return: state_dot
        """

        # Unpack state values and construct the velocity vector nu
        _, _, psi, u, v, r = state
        nu = np.array([u, v, r])

        # Express nu in the 6 DOF system
        nu_6DOF = np.array([u, v, 0, 0, 0, r])

        # Calculate Coriolis matrix
        C_6DOF = m2c(M_6DOF, nu_6DOF)

        # Transform back to the 3 DOF representation
        C_p = C_6DOF
        C_p = np.delete(C_p, [3, 4, 5], axis=0)
        C_p = np.delete(C_p, [3, 4, 5], axis=1)

        eta_dot = Rzyx(0, 0, angwrap(psi)).dot(nu)
        nu_dot = M_p_inv.dot(B_p.dot(f) - C_p.dot(nu) - D_p.dot(nu))
        return np.concatenate([eta_dot, nu_dot])

    @property
    def model_input_space(self):
        return Box(low=np.array([0, -1]), high=np.array([+1, +1]), dtype=np.float32)

    @property
    def state_map(self):
        return ('x','y','yaw','surge','sway','yawrate')

