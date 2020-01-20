import numpy as np
from .objective import ControlObjective
from types import SimpleNamespace
from gncgym.utils import distance, rotate, angwrap
from gncgym.definitions import State6DOF
from gncgym.reference_generation.parametrised_curves import RandomCurveThroughOrigin

MAX_SURGE = 10
LOS_DISTANCE = 75
OBST_RANGE = 150
OBST_PENALTY = 25
DETECTED_OBST_COLOR = (0.1, 0.7, 0.2)

# TODO Move all obstacle tracking to either Objective or Observer
# TODO Try alternative observation methods
NR = 0  # Number of elements in reference obs
NS = 4  # Number of elements in state obs
STATIC_OBST_SLOTS = 4
DYNAMIC_OBST_SLOTS = 0

REF_SPACE = np.array([[-1, 0], [1, 1]])
STATE_SPACE = np.array([[-1]*NS, [1]*NS])
STATIC_OBST_SPACE = np.tile(np.array([[-1, 0], [1, 1]]), (1, STATIC_OBST_SLOTS))
DYNAMIC_OBST_SPACE = np.tile(np.array([[-1, 0, -1, 0], [1, 1, 1, 1]]), (1, DYNAMIC_OBST_SLOTS))


class PathFollowing(ControlObjective):
    def reset_objective(self, obj: SimpleNamespace, rng, path=None, desired_speed=4, obstacles=None):
        if path is None:
            L = 200
            a = 2 * np.pi * (rng.rand() - 0.5)
            path = RandomCurveThroughOrigin(rng, start=(L * np.cos(a), L * np.sin(a)))

        # Add slight random perturbation to starting point
        init_x, init_y = path(0)
        init_yaw = path.get_angle(0)
        init_x += 2 * (rng.rand() - 0.5)
        init_y += 2 * (rng.rand() - 0.5)
        init_yaw += 0.1 * (rng.rand() - 0.5)
        initial_state = dict(x=init_x, y=init_y, yaw=init_yaw, surge=0, sway=0, yawrate=0)

        obj.path = path
        obj.path_points = np.transpose(obj.path(np.linspace(0, obj.path.length, 500)))
        obj.desired_speed = desired_speed
        obj.static_obstacles = []
        obj.dynamic_obstacles = []
        obj.active_static = dict()
        obj.active_dynamic = dict()
        obj.reward = 0
        obj.s = 0

        return initial_state

    def eval_objective(self, obj: SimpleNamespace, action: np.ndarray, measured_state: State6DOF, real_state: State6DOF):
        s_new = obj.path.get_closest_s(measured_state.position[0:2])
        obj.ds, obj.s = s_new - obj.s, s_new
        obs = self._calculate_errors(obj, real_state)

        sr = self._step_reward(obj, action, obs, real_state)
        obj.reward += sr
        done = self._stop_criterion(obj)

        return obs, sr, done

    def render_objective(self, obj, viewer):
        # Draw path
        viewer.draw_polyline(obj.path_points, linewidth=3, color=(0.3, 0.3, 0.3))

        # Draw closest point on path
        p = obj.path(obj.s).flatten()
        viewer.draw_circle(origin=p, radius=1, res=30, color=(0.8, 0.3, 0.3))

    def _calculate_errors(self, obj, state):

        self._update_closest_obstacles(obj, state)

        closest_point = obj.path(obj.s).flatten()
        closest_angle = obj.path.get_angle(obj.s)
        target = obj.path(obj.s + LOS_DISTANCE).flatten()
        target_angle = obj.path.get_angle(obj.s + LOS_DISTANCE)

        # State and path errors
        velocity = state.velocity
        surge_error = obj.desired_speed - velocity.surge
        heading_error = float(angwrap(target_angle - state.orientation.yaw))
        cross_track_error = rotate(closest_point - np.array(state.position[0:2]), -closest_angle)[1]
        target_dist = distance(state.position[0:2], target)

        # Construct observation vector
        obs = np.zeros((NR + NS + 2 * STATIC_OBST_SLOTS + 4 * DYNAMIC_OBST_SLOTS,))
        obs[NR + 0] = np.clip(surge_error / MAX_SURGE, -1, 1)
        obs[NR + 1] = np.clip(heading_error / np.pi, -1, 1)
        obs[NR + 2] = np.clip(cross_track_error / OBST_RANGE, -1, 1)
        obs[NR + 3] = np.clip(target_dist / OBST_RANGE, 0, 1)

        return obs

    def _update_closest_obstacles(base_env, obj: SimpleNamespace, state):

        # Deallocate static obstacles that are out of range
        for i, slot in obj.active_static.copy().items():
            if distance(state.position, obj.static_obstacles[i].position) > OBST_RANGE * 1.05:
                obj.active_static.pop(i)

        # Deallocate dynamic obstacles that are out of range
        for i, slot in obj.active_dynamic.copy().items():
            if distance(state.position, obj.dynamic_obstacles[i].position) > OBST_RANGE * 1.05:
                obj.active_dynamic.pop(i)

        # TODO Replace duplicated code with something that just iterates through self.objects
        if STATIC_OBST_SLOTS > 0:
            # Allocate static obstacles
            distances = {i: distance(state.position, obst.position) for i, obst in enumerate(obj.static_obstacles)}
            for obsti, obst in enumerate(obj.static_obstacles):
                dist = distances[obsti]
                if dist < OBST_RANGE and obsti not in obj.active_static:
                    available_slots = tuple(set(range(STATIC_OBST_SLOTS)) - set(obj.active_static.values()))
                    if len(available_slots) > 0:
                        slot = np.random.choice(available_slots)
                        obj.active_static[obsti] = slot
                    else:
                        active_distances = {k: distances[k] for k in obj.active_static.keys()}
                        i_max = max(active_distances, key=active_distances.get)
                        if dist < active_distances[i_max]:
                            slot_max = obj.active_static[i_max]
                            obj.active_static.pop(i_max)
                            obj.active_static[obsti] = slot_max

        if DYNAMIC_OBST_SLOTS > 0:
            # Allocate dynamic obstacles
            distances = {i: distance(state.position, obst.position) for i, obst in
                         enumerate(obj.dynamic_obstacles)}
            for obsti, obst in enumerate(obj.dynamic_obstacles):
                dist = distances[obsti]
                if dist < OBST_RANGE and obsti not in obj.active_dynamic:
                    available_slots = tuple(set(range(DYNAMIC_OBST_SLOTS)) - set(obj.active_dynamic.values()))
                    if len(available_slots) > 0:
                        slot = np.random.choice(available_slots)
                        obj.active_dynamic[obsti] = slot
                    else:
                        active_distances = {k: distances[k] for k in obj.active_dynamic.keys()}
                        i_max = max(active_distances, key=active_distances.get)
                        if dist < active_distances[i_max]:
                            slot_max = obj.active_dynamic[i_max]
                            obj.active_dynamic.pop(i_max)
                            obj.active_dynamic[obsti] = slot_max

    def _stop_criterion(base_env, obj: SimpleNamespace):
        done = False

        if not done and obj.reward < -50:
            done = True

        if not done and abs(obj.s - obj.path.length) < 1:
            done = True
            print("done")

        return done

    def _step_reward(base_env, obj: SimpleNamespace, action, obs, state):
        step_reward = 0

        # TODO check why obstacle collision does not work anymore (probably because of numpy)
        for o in base_env.objects:
            if distance(state.position, o.position) < state.radius + o.radius:
                step_reward -= OBST_PENALTY
                break

        step_reward += obj.ds / 4
        # Penalise cross track error if too far away from path
        surge_error = obs[NR + 0]
        cross_track_error = obs[NR + 2]
        step_reward -= abs(cross_track_error) * 0.5 + max(0, -surge_error) * 0.5

        return step_reward
