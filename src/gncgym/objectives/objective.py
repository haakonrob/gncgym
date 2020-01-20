from types import SimpleNamespace
from numpy import ndarray
from gncgym.definitions import Position, Orientation, LinVel, AngVel, State6DOF, EnvSnapshot


class ControlObjective:
    def reset_objective(self, waypoints):
        """
        This class accepts a state trajectory specifying the desired state of the vessel.
        Returns the initial state of the vessel, and an objective object.
        :param waypoints:
        """
        raise NotImplementedError("ControlObjective.reset_objective() has not been implemented.")

    def eval_objective(self, obj: SimpleNamespace, action: ndarray, measured_env: State6DOF, real_env: State6DOF):
        raise NotImplementedError("ControlObjective.eval_objective() has not been implemented.")

    def render_objective(self, obj: SimpleNamespace, viewer):
        raise NotImplementedError("ControlObjective.render_objective() has not been implemented.")
