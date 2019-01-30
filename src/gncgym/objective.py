from .definitions import Vec, State6DOF

class ControlObjective:
    def __init__(self, state_trajectory: State6DOF):
        """
        This class accepts a state trajectory specifying the desired state of the vessel.
        The fields
        :param state_trajectory:
        """
