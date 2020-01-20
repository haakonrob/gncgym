import numpy as np
from gym.spaces import Box
from .gncUtilities import m2c, Rzyx
from gncgym.utils import angwrap
from gncgym.models import Model
from gncgym.simulator.blocks import make_integrator_block

"""
Originally made by Camilla Sterud.
"""

"""
####### Model Constants #######
"""

M = 18.82
I_zz = 1.77
X_udot = 0.421
Y_vdot = -27.2
Y_rdot = -1.83
N_rdot = -4.34
X_uu = -3.11
Y_vv = -3.01
N_rr = -2
Y_rr = 0.632
N_vv = -3.18
N_uudr = -6.08

THRUST_MIN_AUV = 0
THRUST_MAX_AUV = 10
RUDDER_MAX_AUV = 0.1
MAX_SPEED = 1.8

M_RB = np.diag([M, M, I_zz])

M_A = -np.array([
    [X_udot, 0, 0],
    [0, Y_vdot, Y_rdot],
    [0, Y_rdot, N_rdot]
    ])

M_inv = np.linalg.inv(M_RB + M_A)

D_quad = -np.diag([X_uu, Y_vv, N_rr])


def D(u, v, r):
    return D_quad @ np.diag(np.reshape(np.absolute([u, v, r]), (3,)))


def B(u):
    return np.array([
        [1, 0],
        [0, 0],
        [0, float(N_uudr*u*u)],
    ])


"""
####### Model #######
"""


class AUV2D(Model):
    _model_state = None
    _model_integrate = None

    def reset_model(self, x0):
        # Initialise the integrator and the model dynamics
        x0 = np.vstack(x0)  # Column vector
        self._model_state = x0
        self._model_integrate = make_integrator_block(x0)

    def step_model(self, u, v=None):
        f = np.vstack(u)  # f is always a column vector, no matter if u is either a row or column vector
        # TODO move rescaling inside model equations
        f[0, :] *= THRUST_MAX_AUV  # Rescale thrust
        f[1, :] = f[1,:] * RUDDER_MAX_AUV  # Rescale angle
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
        _D = D(u, v, r) @ nu
        _B = B(u) @ f
        eta_dot = Rzyx(0, 0, angwrap(psi)).dot(nu)
        nu_dot = M_inv @ (B(u) @ f - D(u, v, r) @ nu)
        return np.concatenate([eta_dot, nu_dot])

    @property
    def model_input_space(self):
        return Box(low=np.array([0, -1]), high=np.array([+1, +1]), dtype=np.float32)

    @property
    def state_map(self):
        return ('x','y','yaw','surge','sway','yawrate')
