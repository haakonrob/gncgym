import numpy as np
import simulator as sim

from copy import deepcopy
from simulator.blocks import make_integrator_block

from .gncUtilities import Rzyx
from .feedbackLinearisingController import make_feedback_linearising_controller_block
from .shipDynamics import make_supply_ship_dynamics_block


@sim.declare_block
def make_supply_ship_block(initial_state=np.vstack([0, 0, 0, 0, 0, 0]), linearising_feedback=True):
    # Make sure that the given state is not changed
    state = deepcopy(initial_state)

    # Blocks
    integrate = make_integrator_block(initial_state)
    model = make_supply_ship_dynamics_block()
    if linearising_feedback:
        controller = make_feedback_linearising_controller_block()

    def supply_ship(reference, disturbances=None):
        nonlocal state, integrate, model, controller

        if disturbances is not None:
            raise NotImplemented("Disturbances not implemented yet.")
        else:
            Vc = np.vstack([0, 0, 0])

        reference[0] = max(reference[0], 0)  # cannot have a negative surge reference
        if linearising_feedback:
            nu_r = state[3:, :] - Rzyx(-state[2], 0, 0).dot(Vc)
            f = controller(state, nu_r, reference)
        else:
            f = np.vstack(reference)

        state_dot = model(state, f)
        state = integrate(state_dot)

        return state

    return supply_ship
