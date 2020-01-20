from .objective import ControlObjective
from gncgym.utils import distance, rotate, angwrap
from gncgym.definitions import Position, Orientation, LinVel, AngVel, State6DOF, EnvSnapshot


class TrajectoryTracking(ControlObjective):
    def reset_objective(self, waypoints):
        raise NotImplementedError("ControlObjective.reset_objective() has not been implemented.")

    def eval_objective(self, measured_env: State6DOF, real_env: State6DOF):
        raise NotImplementedError("ControlObjective.eval_objective() has not been implemented.")

    def render_objective(self, measured_env: State6DOF, real_env: State6DOF):
        raise NotImplementedError("ControlObjective.render_objective() has not been implemented.")
