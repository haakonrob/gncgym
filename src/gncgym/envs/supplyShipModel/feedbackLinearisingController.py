import numpy as np
from .gncUtilities import angdiff
from simulator.blocks import \
    make_derivative_block, \
    make_saturation_block, \
    make_rate_limiting_block


def make_feedback_linearising_controller_block():
    from .modelConstants import K1, K2, M_p, D_p

    # Controller constants (uses the supply ship model parameters)
    P_u = 0.1
    P_r = 0.04
    D_r = 0.9

    # Create derivative blocks for each signal
    der_u_r_dot = make_derivative_block()
    der_psi_r_dot = make_derivative_block()
    der_psi_r_dot_dot = make_derivative_block()

    # Create saturation and rate-limiting blocks
    saturate_rudder_angle = make_saturation_block(np.pi)
    saturate_thruster_force = make_saturation_block(100000000)
    rate_limit_thruster_force = make_rate_limiting_block(500000)

    def feedback_linearizing_controller(state, nu_r, reference):
        _, _, psi, _, _, r = state.flatten()
        u_r, v_r, _ = nu_r.flatten()
        u_r_des, psi_des = reference

        u_des_r_dot = der_u_r_dot(u_r_des)
        psi_des_dot = der_psi_r_dot(psi_des)
        psi_des_dot_dot = der_psi_r_dot_dot(psi_des_dot)

        F_u = (r/M_p[0, 0]) * (M_p[1, 2] * r + M_p[1, 1] * v_r)
        F_r = (1/(M_p[1, 1] * M_p[2, 2] - M_p[1, 2] * M_p[1, 2])) * \
              (v_r * (D_p[1, 1] * M_p[1, 2] - D_p[2, 1] * M_p[1, 1] + u_r * (M_p[0,0] * M_p[1,1] - M_p[1,1] * M_p[1,1])) +
               r * (D_p[1, 2] * M_p[1, 2] - D_p[2, 2] * M_p[1, 1] + u_r * (M_p[0,0] * M_p[1,2] - M_p[1,1] * M_p[1,2])))

        tau_u = -F_u + u_des_r_dot + (D_p[0, 0] / M_p[0, 0]) * u_r_des + P_u * (u_r_des - u_r)
        tau_r = -F_r + psi_des_dot_dot - P_r * angdiff(psi, psi_des) - D_r * (r - psi_des_dot)

        return np.vstack([
            rate_limit_thruster_force(
                saturate_thruster_force(tau_u/K1)
            ),
            saturate_rudder_angle(tau_r/K2)
        ])

    return feedback_linearizing_controller



