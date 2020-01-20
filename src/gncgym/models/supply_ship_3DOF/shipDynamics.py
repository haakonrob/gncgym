import numpy as np
from gncgym.utils import angwrap
from numpy.linalg import inv
from .gncUtilities import m2c, Rzyx


def make_supply_ship_dynamics_block():
    from .modelConstants import M_p, D_p, B_p, M_6DOF

    M_p_inv = inv(M_p)

    def model_dynamics(state, f):
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

    # Returns a reference to the dynamics function, that can be called to
    # obtain the time-derivative of the state.
    return model_dynamics


