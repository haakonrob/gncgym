import numpy as np
import gym
import logging
import gncgym.definitions as gncdefs


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

    def __init__(self, x0=None):
        # Initialise the integrator and the model dynamics
        self._model_state = None
        self._model_integrate = None
        self.ship_dynamics = None

    def reset_model(self, initial_state):
        raise NotImplementedError

    def step_model(self, u, v=None):
        raise NotImplementedError('The _step() method must be defined by any subclass of Model.')

    def _reset_model(self, initial_state):
        if type(initial_state) is dict:
            self.reset_model([initial_state[k] for k in self.state_map])
        elif type(initial_state) is gncdefs.State6DOF:
            self.reset_model(np.array([v for v in initial_state if v is not None]))
        else:
            raise ValueError('Invalid state type passed to _reset_model')

    def _model(self, u, v=None):
        """
        Steps the model forward one time step. The time step used is defined by the model, or the simulator
        module that is used.
        :param u: The input to the model. Must lie within the input_space for the model.
        :param v: The disturbance at this timestep. Optional. If included, must lied within the disturbance
                  space of the model.
        :return:  State6DOF
        """
        u = np.array(u)
        v = np.array(v) if v is not None else v
        if not self._model_input_space.contains(u):
            logging.warning("Input {} is out of input_space.")

        if self.supports_disturbances():
            raw_state = self.step_model(u, v)
        else:
            raw_state = self.step_model(u)

        return gncdefs.State6DOF(**{self.state_map[i]: float(value) for i, value in enumerate(raw_state)})

    @property
    def _model_input_space(self):
        """
        MANDATORY property of a Model. Must be set by the subclass definition before the class
        can be used with the rest of the code. This should be done in the __init__() method of
        any class subclassing Model. This attribute defines the ranges of values that the input
        may take. For example,
            Space(low=[-1, -1], high=[1, 1])
        declares that the input consists of a 2-vector where the elements take values between [-1, 1].
        If an invalid input is given to the model, a warning will be logged. However, it is up to the
        implemented model to decide whether to throw an error or saturate the value.
        :return: gym.Space
        """
        try:
            if not issubclass(type(self.model_input_space), gym.Space):
                raise TypeError("The input_space attribute must be of type gym.Space")
            return self.model_input_space
        except AttributeError:
            raise NotImplementedError("The _model_input_space attribute has not been set by the subclass of Model.")

    @property
    def state_map(self):
        """
        MANDATORY property of a Model. Must be set by the subclass definition before the class
        can be used with the rest of the code. This should be done in the __init__() method of
        any class subclassing Model.
        :return: gym.Space
        """
        if '_output_map' not in self.__dict__:
            raise NotImplementedError("The output_map must be set by the subclass of Model.")
        else:
            return self._output_map

    @state_map.setter
    def state_map(self, o_map: tuple):
        """
        Verifies the type of Model.output_map when trying to set the attribute. This method is
        called when output_map is assigned to, for example:
            >>> m = Model()                 # Subclass of Model
            >>> m.state_map = my_tuple     # output_map.setter is called here
        The output map is just a tuple or list that assigns a text label to each element in the state
        """
        if type(o_map) is list:
            o_map = tuple(o_map)
        if not type(o_map) is tuple:
            raise TypeError("The output_map attribute must be of type tuple")
        if not all(key in gncdefs.variables for key in o_map):
            raise ValueError('One of the values in given output_map {} does not match'
                             'one of the state fields: {}'.format(o_map, gncdefs.State6DOF._fields))
        if len(set(o_map)) != len(o_map):
            raise ValueError('The output map does not specify unique keys.')
        self._output_map = o_map

    def supports_disturbances(self):
        """
        Used by other modules to detect whether or not the model supports disturbances like waves,
        wind, currents.
        :return:
        """
        return '_disturbance_space' in self.__dict__

    @property
    def disturbance_space(self):
        """
        OPTIONAL property of a Model. Other modules will detect whether or not this has been defined.
        This should be done in the __init__() method of any class subclassing Model. If this attribute
        has been set, the model.step() function will be called with the w parameter. This attribute
        defines the ranges of values that the disturbances may take. For example,
            Space(low=[-1, -1], high=[1, 1])
        declares that the input consists of a 2-vector where the elements take values between [-1, 1].
        If an invalid disturbance is given to the model, a warning will be logged. However, it is up
        to the implemented model to decide whether to throw an error or saturate the value.
        :return: gym.Space
        """
        if '_disturbance_space' not in self.__dict__:
            raise NotImplementedError("The disturbance_space has not been set by the subclass of Model.")
        else:
            return self._disturbance_space

    @disturbance_space.setter
    def disturbance_space(self, d_space: gym.Space):
        """
        Verifies the type of Model.output_map when trying to set the attribute. This method is
        called when output_map is assigned to, for example:
            >>> m = Model()                         # Subclass of Model
            >>> m.disturbance_space = my_space      # disturbance_space.setter is called here
        """
        if not issubclass(d_space, gym.Space):
            raise TypeError("The disturbance_space attribute must be of type gym.Space")


