import numpy as np


def shape(v):
    try:
        return v.shape  # NumPy arrays and PyTorch Tensors
    except AttributeError:
        return (1, len(v))


class Model:
    """
    Standard interface for models for use in the gncgym. Requires that the shape of the state, inputs (optional), and
    disturbances (optional) be specified in subclasses, along with a function to initialise/reset a model and a step
    function that returns the next state according to the inputs.
    Notation for the variables is standard:
        x: state
        u: input
        w: disturbances
        y: measurement
    """

    def __init__(self, state, input=None, disturbances=None):
        self.shape_x = shape(state)
        self.shape_u = shape(input)
        self.shape_w = shape(disturbances)

    def init(self, x=None, u=None, w=None):
        raise NotImplementedError

    def input(self, u):
        if shape_u is None:
            raise ValueError('Model.input() was called without declaring the input shape.')
        if shape(u) != self.shape_u:
            raise ValueError('Shape of argument is wrong.')
        self.u = u

    def disturbance(self, w):
        self.w = w

    def step(self):
        raise NotImplementedError

    def measure(self):
        """
        Implement this function if you want
        :return:
        """
        return self.x
