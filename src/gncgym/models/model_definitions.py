import gym
import logging
import gncgym.definitions as gnc


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
        """
        This function initialises an instance of a Model to be in the state x0, as well as specifying the
        input_space, output_map, and (optionally) the disturbance_space.
        :param x0: initial state of the system.
        :return Model:
        """
        raise NotImplementedError('The __init__() method must be defined by any subclass of Model.')

    def step(self, u, v=None):
        """
        Steps the model forward one time step. The time step used is defined by the model, or the simulator
        module that is used.
        :param u: The input to the model. Must lie within the input_space for the model.
        :param v: The disturbance at this timestep. Optional. If included, must lied within the disturbance
                  space of the model.
        :return:  State6DOF
        """
        if not self.input_space.contains(u):
            logging.warning("Input {} is out of input_space.")

        if self.supports_disturbances():
            state = self._step(u, v)
        else:
            state = self._step(u)

        # Convert the state into a namedtuple form by using the output_map
        return gnc.State6DOF(**{self.output_map[i]: value for i, value in state})

    def _step(self, u, v=None):
        raise NotImplementedError('The _step() method must be defined by any subclass of Model.')

    @property
    def input_space(self):
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
        if '_input_space' not in self.__dict__:
            raise NotImplementedError("The input_space attribute has not been set by the subclass of Model.")
        else:
            return self._input_space

    @input_space.setter
    def input_space(self, u_space: gym.Space):
        """
        Verifies the type of Model.input_space when trying to set the attribute. This method is called when
        input_space is assigned to, for example:
            >>> m = Model()                 # Subclass of Model
            >>> m.input_space = my_space    # The input_space.setter is called here
        """
        if not issubclass(u_space, gym.Space):
            raise TypeError("The input_space attribute must be of type gym.Space")

    @property
    def output_map(self):
        """
        MANDATORY property of a Model. Must be set by the subclass definition before the class
        can be used with the rest of the code. This should be done in the __init__() method of
        any class subclassing Model.
        :return: gym.Space
        """
        if 'output_map' not in self.__dict__:
            raise NotImplementedError("The output_map must be set by the subclass of Model.")
        else:
            return self._disturbance_space

    @output_map.setter
    def output_map(self, o_map: tuple):
        """
        Verifies the type of Model.output_map when trying to set the attribute. This method is
        called when output_map is assigned to, for example:
            >>> m = Model()                 # Subclass of Model
            >>> m.output_map = my_tuple     # output_map.setter is called here
        The output map is just a tuple or list that assigns a text label to each index in
        """
        if type(o_map) is list:
            o_map = tuple(o_map)
        if not type(o_map) is tuple:
            raise TypeError("The output_map attribute must be of type tuple")
        if not all(key in gnc.State6DOF._fields for key in o_map):
            raise ValueError('One of the values in given output_map {} does not match'
                             'one of the state fields: {}'.format(o_map, gnc.State6DOF._fields))
        if len(set(o_map)) != len(o_map):
            raise ValueError('The output map does not specify unique keys.')

    def supports_disturbances(self):
        """
        Used by other modules to detect whether or not the model supports disturbances like waves,
        wind, currents.
        :return:
        """
        return '_disturbance_space' not in self.__dict__

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


