import numpy as np
from gym import Space


def shape(v):
    try:
        return v.shape  # NumPy arrays and PyTorch Tensors
    except AttributeError:
        return (len(v), 1)


class Model:
    """
    Standard interface for models for use in the gncgym. Requires that the shape of the state, inputs (optional), and
    disturbances (optional) be specified in subclasses, along with a function to initialise/reset a model and a step
    function that returns the next state according to the inputs.
    Notation for the variables is standard:
        x: state
        u: input
        v: disturbances
        y: measurement
    """

    def __init__(self, state, input_space=None, output_space=None, disturbance_space=None):
        self._input_space = None
        self._output_space = None
        self._disturbance_space = None
        self._step = None
        self._output_map = dict()

    def init(self, x0=None):
        raise NotImplementedError

    def step(self, u, v):
        if not callable(self._step):
            raise NotImplementedError
        else:
            return self._step(u, v)

    """
    Mandatory properties of a model. The spaces of the inputs must be defined explicitly to
    ensure that agents and controllers can assign inputs to the model properly. Additionally,
    the output of the model code must be mapped to keys used in the namedtuple representation
    of the state.   
    """
    @property
    def input_space(self):
        if self._input_space is None or not issubclass(self._input_space, Space):
            raise NotImplementedError
        else:
            return self._input_space

    @property
    def disturbance_space(self):
        if self._disturbance_space is None or not issubclass(self._disturbance_space, Space):
            raise NotImplementedError
        else:
            return self._disturbance_space

    @property
    def output_map(self):
        if type(self._output_map) is not dict:
            raise NotImplementedError
        else:
            return self._output_map

