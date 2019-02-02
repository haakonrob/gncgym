import numpy as np
from copy import deepcopy
# from . import base_env
from . import env
from .env import declare_block


@declare_block
def make_integrator_block(initial_value):
    buffer = deepcopy(initial_value)

    def integrate(val):
        nonlocal buffer
        buffer += val * env.dt
        return buffer

    return integrate


@declare_block
def make_derivative_block(n=3):
    buffer = [0]*n

    def update(val):
        nonlocal buffer
        buffer = buffer[1:] + [float(val)]
        return np.mean(np.diff(buffer) / env.dt)

    return update


@declare_block
def make_saturation_block(max_bound, min_bound=None):

    if min_bound is None:
        min_bound = -max_bound
    assert (max_bound > min_bound)

    def saturate(x):
        nonlocal max_bound, min_bound
        if x > max_bound:
            x = max_bound
        elif x < min_bound:
            x = min_bound
        return x

    return saturate


@declare_block
def make_rate_limiting_block(rising_bound, falling_bound=None):
    if falling_bound is None:
        falling_bound = -rising_bound

    assert ((rising_bound > 0) and (falling_bound < 0))

    prev_x = 0

    def rate_limit(x):
        nonlocal prev_x
        if x - prev_x > rising_bound:
            x = prev_x + rising_bound
        elif x - prev_x < falling_bound:
            x = prev_x + falling_bound

        prev_x = x
        return x

    return rate_limit
