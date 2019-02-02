import numpy as np
from math import atan2


def straightLineGuidance(state, surge_des=4, lookahead=75):
    # Unpack the state
    x, y, _, _, _, _ = state

    # Standard Line-of-sight for straight line path following
    heading_des = atan2(-y, lookahead)

    return np.array([surge_des, heading_des])
