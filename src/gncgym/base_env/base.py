import gym
from gym import spaces
import numpy as np
from numpy import pi, sin, cos, arctan2
from gncgym import simulator as sim

from . import rendering
from .objects import MAX_SURGE
from .utils import distance, rotate
from gym.utils import seeding, EzPickle
from gncgym.simulator.angle import Angle
import pyglet
from pyglet import gl

from numpy.random import random

"""
    
"""


STATE_W = 96   # less than Atari 160x192
STATE_H = 96
VIDEO_W = 600
VIDEO_H = 400
WINDOW_W = 1200
WINDOW_H = 1000

SCALE       = 5.0        # Track scale
PLAYFIELD   = 3000/SCALE # Game over boundary
FPS         = 50
ZOOM        = 1          # Camera zoom
ZOOM_FOLLOW = True       # Set to False for fixed view (don't use zoom)

LOS_DISTANCE = 75
OBST_RANGE = 150
OBST_PENALTY = 25
DETECTED_OBST_COLOR = (0.1, 0.7, 0.2)

NR = 0  # Number of elements in reference obs
NS = 4  # Number of elements in state obs
STATIC_OBST_SLOTS = 4
DYNAMIC_OBST_SLOTS = 0

REF_SPACE = np.array([[-1, 0], [1, 1]])
STATE_SPACE = np.array([[-1]*NS, [1]*NS])
STATIC_OBST_SPACE = np.tile(np.array([[-1, 0], [1, 1]]), (1, STATIC_OBST_SLOTS))
DYNAMIC_OBST_SPACE = np.tile(np.array([[-1, 0, -1, 0], [1, 1, 1, 1]]), (1, DYNAMIC_OBST_SLOTS))

# OBS_SPACE = np.concatenate([STATE_SPACE, STATIC_OBST_SPACE, DYNAMIC_OBST_SPACE], axis=1)

if NR == 2:
    OBS_SPACE = np.concatenate([REF_SPACE, STATE_SPACE, STATIC_OBST_SPACE, DYNAMIC_OBST_SPACE], axis=1)
else:
    OBS_SPACE = np.concatenate([STATE_SPACE, STATIC_OBST_SPACE, DYNAMIC_OBST_SPACE], axis=1)


class BaseShipScenario(gym.Env, EzPickle):
    metadata = {
        'render.modes': ['human', 'rgb_array', 'state_pixels'],
        'video.frames_per_second': FPS
    }

    def __init__(self):
        sim.init(
            solver='fixed_step',
            step_size=0.05,
        )

        self.viewer = None
        self.bg = None

        self.path = None
        self.s = None

        self.speed = None
        self.ship = None
        self.last_obs = None

        self.static_obstacles = None
        self.dynamic_obstacles = None
        self.active_static = None
        self.active_dynamic = None
        self.viewer = None

        self.reward = None
        self.np_random = None

        self.reset()

        # TODO change the action space to match the boat actions
        # TODO create a reasonable observation space, current is image related
        self.action_space = gym.spaces.Box(low=np.array([-1, 0]), high=np.array([+1, +1]), dtype=np.float32)
        self.observation_space = gym.spaces.Box(low=OBS_SPACE[0, :], high=OBS_SPACE[1, :], dtype=np.float32)

    def step(self, action):
        self.ship.steer(action[0])
        self.ship.surge(action[1])

        # TODO Reshape this into a simple control loop with various modules
        """
        w = self.disturbances()
        x = self.ship.step(u, w)
        y = self.observer(xn)
        e = self.objective(xn, yn)  # e = (obs, step_r, done, info)
        return e
        
        """
        self.ship.step()
        s = self.path.get_closest_s(self.ship.position)
        ds, self.s = s - self.s, s

        for o in self.dynamic_obstacles:
            o.step()

        obs = self.navigate()
        self.last_obs = obs
        done, sr = self.step_reward(action, obs, ds)
        info = {}
        self.reward += sr

        sim.env.step()  # Updates dt

        return obs, sr, done, info

    # TODO move to observer or objective module
    def navigate(self, state=None):
        if state is None:
            state = self.ship.state.flatten()

        self.update_closest_obstacles()

        # TODO Try lookahead vector instead of closest point
        closest_point = self.path(self.s).flatten()
        closest_angle = self.path.get_angle(self.s)
        target = self.path(self.s + LOS_DISTANCE).flatten()
        target_angle = self.path.get_angle(self.s + LOS_DISTANCE)

        # Ref error
        surge_ref_error = self.speed - self.ship.ref[0]
        heading_ref_error = float(Angle(target_angle - self.ship.ref[1]*pi))

        # State and path errors
        surge_error = self.speed - state[3]
        heading_error = float(Angle(target_angle - state[2]))
        cross_track_error = rotate(closest_point - self.ship.position, -closest_angle)[1]
        target_dist = distance(self.ship.position, target)

        # Construct observation vector
        obs = np.zeros((NR + NS + 2 * STATIC_OBST_SLOTS + 4 * DYNAMIC_OBST_SLOTS,))

        if NR == 2:
            # obs[0] = np.clip(surge_ref_error / MAX_SURGE, -1, 1)
            obs[1] = np.clip(heading_ref_error / pi, -1, 1)

        obs[NR+0] = np.clip(surge_error / MAX_SURGE, -1, 1)
        obs[NR+1] = np.clip(heading_error / pi, -1, 1)
        obs[NR+2] = np.clip(cross_track_error / OBST_RANGE, -1, 1)
        obs[NR+3] = np.clip(target_dist / OBST_RANGE, 0, 1)

        if False:
            state_error = np.array([target[0], target[1], target_angle, self.speed, 0, 0]) - state  # plus obstacles
            state_error[0:2] = rotate(state_error[0:2], self.ship.angle)  # Rotate to body frame
            state_error[2] = float(Angle(state_error[2]))  # Bring back into -pi, pi range

            # Reference error
            obs[0] = np.clip(ref_error[0] / MAX_SURGE, -1, 1)
            obs[1] = np.clip(ref_error[0] / pi, -1, 1)

            # Path errors
            obs[2] = np.clip(state_error[0] / LOS_DISTANCE, -1, 1)
            obs[3] = np.clip(state_error[1] / LOS_DISTANCE, -1, 1)
            obs[4] = np.clip((((state_error[2] + pi) % (2*pi)) - pi) / pi, -1, 1)
            obs[5] = np.clip(state_error[3] / MAX_SURGE, -1, 1)
            obs[6] = np.clip(state_error[4] / MAX_SURGE, -1, 1)
            obs[7] = np.clip(state_error[5] / MAX_SURGE, -1, 1)

        # Write static obstacle data into observation
        for i, slot in self.active_static.items():
            obst = self.static_obstacles[i]
            vec = obst.position - self.ship.position
            obs[NS + NR + 2*slot] = float(Angle(arctan2(vec[1], vec[0]) - self.ship.angle))/pi
            obs[NS + NR + 2*slot + 1] = 1 - np.clip((np.linalg.norm(vec) - self.ship.radius - obst.radius) / LOS_DISTANCE, 0, 1)

        # Write dynamic obstacle data into observation
        for i, slot in self.active_dynamic.items():
            obst = self.dynamic_obstacles[i]
            vec = obst.position - self.ship.position
            obs[NS + NR + STATIC_OBST_SLOTS * 2 + 4*slot] = float(Angle(arctan2(vec[1], vec[0]) - self.ship.angle))/pi
            obs[NS + NR + STATIC_OBST_SLOTS * 2 + 4*slot + 1] = 1 - np.clip(
                (np.linalg.norm(vec) - self.ship.radius - obst.radius) / LOS_DISTANCE, 0, 1)
            vel = rotate(obst.linearVelocity, self.ship.angle)
            obs[NS + NR + STATIC_OBST_SLOTS * 2 + 4*slot + 2] = vel[0]
            obs[NS + NR + STATIC_OBST_SLOTS * 2 + 4*slot + 3] = vel[1]

        return obs

    def update_closest_obstacles(self):
        # Deallocate static obstacles that are out of range
        for i, slot in self.active_static.copy().items():
            if distance(self.ship.position, self.static_obstacles[i].position) > OBST_RANGE * 1.05:
                self.active_static.pop(i)

        # Deallocate dynamic obstacles that are out of range
        for i, slot in self.active_dynamic.copy().items():
            if distance(self.ship.position, self.dynamic_obstacles[i].position) > OBST_RANGE * 1.05:
                self.active_dynamic.pop(i)

        if STATIC_OBST_SLOTS > 0:
            # Allocate static obstacles
            distances = {i: distance(self.ship.position, obst.position) for i, obst in enumerate(self.static_obstacles)}
            for obsti, obst in enumerate(self.static_obstacles):
                dist = distances[obsti]
                if dist < OBST_RANGE and obsti not in self.active_static:
                    available_slots = tuple(set(range(STATIC_OBST_SLOTS)) - set(self.active_static.values()))
                    if len(available_slots) > 0:
                        slot = np.random.choice(available_slots)
                        self.active_static[obsti] = slot
                    else:
                        active_distances = {k: distances[k] for k in self.active_static.keys()}
                        i_max = max(active_distances, key=active_distances.get)
                        if dist < active_distances[i_max]:
                            slot_max = self.active_static[i_max]
                            self.active_static.pop(i_max)
                            self.active_static[obsti] = slot_max

        if DYNAMIC_OBST_SLOTS > 0:
            # Allocate dynamic obstacles
            distances = {i: distance(self.ship.position, obst.position) for i, obst in enumerate(self.dynamic_obstacles)}
            for obsti, obst in enumerate(self.dynamic_obstacles):
                dist = distances[obsti]
                if dist < OBST_RANGE and obsti not in self.active_dynamic:
                    available_slots = tuple(set(range(DYNAMIC_OBST_SLOTS)) - set(self.active_dynamic.values()))
                    if len(available_slots) > 0:
                        slot = np.random.choice(available_slots)
                        self.active_dynamic[obsti] = slot
                    else:
                        active_distances = {k: distances[k] for k in self.active_dynamic.keys()}
                        i_max = max(active_distances, key=active_distances.get)
                        if dist < active_distances[i_max]:
                            slot_max = self.active_dynamic[i_max]
                            self.active_dynamic.pop(i_max)
                            self.active_dynamic[obsti] = slot_max

    def step_reward(self, action, obs, ds):
        done = False
        x, y = self.ship.position
        step_reward = 0

        # Living penalty
        # step_reward -= 0.001  # TODO Increase living penalty

        if not done and self.reward < -50:
            done = True

        if not done and abs(self.s - self.path.length) < 1:
            done = True

        for o in self.static_obstacles + self.dynamic_obstacles:
            if not done and distance(self.ship.position, o.position) < self.ship.radius + o.radius:
                done = True
                step_reward -= OBST_PENALTY
                break

        if not done and abs(x) > PLAYFIELD or abs(y) > PLAYFIELD:
            done = True
            step_reward -= 50

        if not done and distance(self.ship.position, self.path.get_endpoint()) < 20:
            done = True
            # step_reward += 50

        if not done:  # Reward progress along path, penalise backwards progress
            step_reward += ds/4

        if not done:  # Penalise cross track error if too far away from path
            # state_error = obs[:6]
            # step_reward += (0.2 - np.clip(np.linalg.norm(state_error), 0, 0.4))/100
            # heading_err = state_error[2]
            # surge_err = state_error[3]
            # TODO Punish for facing wrong way / Reward for advancing along path

            surge_error = obs[NR+0]
            cross_track_error = obs[NR+2]

            # step_reward -= abs(cross_track_error)*0.1
            # step_reward -= max(0, -surge_error)*0.1

            step_reward -= abs(cross_track_error)*0.5 + max(0, -surge_error)*0.5

            # step_reward -= (max(0.1, -obs[0]) - 0.1)*0.3
            # dist_from_path = np.sqrt(x_err ** 2 + y_err ** 2)
            # path_angle = self.path.get_angle(self.s)
            # If the reference is pointing towards the path, don't penalise
            # if dist_from_path > 0.25 and sign(float(Angle(path_angle - self.ship.ref[1]))) == sign(y_err):
            #     step_reward -= 0.1*(dist_from_path - 0.25)

        return done, step_reward

    def reset(self):
        if self.ship is not None:
            self.ship.destroy()
            self.ship = None
        if self.np_random is None:
            self.seed()
        self.static_obstacles = []
        self.dynamic_obstacles = []
        self.active_static = dict()
        self.active_dynamic = dict()
        self.reward = 0
        self.s = 0

        self.path_rendered = False

        self.generate(self.np_random)

        if self.speed is None:
            raise NotImplementedError('The self.speed attribute MUST be set.')
        if self.path is None:
            raise NotImplementedError('The self.path attribute MUST be set.')
        if self.ship is None:
            raise NotImplementedError('The self.ship attribute MUST be set.')
        self.last_obs = self.navigate()

        S = np.linspace(0, self.path.length, 1000)
        self.path_points = np.transpose(self.path(S))

        return self.last_obs

    def close(self):
        self.destroy()
        if self.viewer is not None:
            self.viewer.close()
            self.viewer = None

    def generate(self, rng):
        raise NotImplemented("Generate() must be implemented. It must at least set the self.ship variable.")

    def destroy(self):
        pass

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def render(self, mode='human'):
        if self.viewer is None:
            self._init_viewer()

        def render_objects():
            t.enable()
            self._render_path()
            self._render_progress()
            self.ship.draw(self.viewer)
            self._render_tiles(win)
            self._render_obstacles()

            # Visualise path error (DEBUGGING)
            # p = np.array(self.ship.position)
            # dir = rotate(self.last_obs[0:2], self.ship.angle)
            # self.viewer.draw_line(p, p + 10*np.array(dir), color=(0.8, 0.3, 0.3))

            for geom in self.viewer.onetime_geoms:
                geom.render()

            t.disable()

            self._render_indicators(WINDOW_W, WINDOW_H)

        zoom = 0.1 * SCALE * max(1 - sim.env.time, 0) + ZOOM * SCALE * min(sim.env.time, 1)   # Animate zoom first second
        # zoom = 1
        zoom_state  = ZOOM*SCALE*STATE_W/WINDOW_W
        zoom_video  = ZOOM*SCALE*VIDEO_W/WINDOW_W
        scroll_x = self.ship.position[0]
        scroll_y = self.ship.position[1]
        angle = -self.ship.angle
        vel = self.ship.linearVelocity
        if np.linalg.norm(vel) > 0.5:
            angle = arctan2(vel[0], vel[1])
        self.transform.set_scale(zoom, zoom)

        self.transform.set_translation(
            WINDOW_W/2 - (scroll_x*zoom*cos(angle) - scroll_y*zoom*sin(angle)),
            WINDOW_H/2 - (scroll_x*zoom*sin(angle) + scroll_y*zoom*cos(angle))
        )
        self.transform.set_rotation(angle)

        arr = None
        win = self.viewer.window
        if mode != 'state_pixels':
            win.switch_to()
            win.dispatch_events()

        if mode=="rgb_array" or mode=="state_pixels":
            win.clear()
            t = self.transform
            if mode=='rgb_array':
                VP_W = VIDEO_W
                VP_H = VIDEO_H
            else:
                VP_W = STATE_W
                VP_H = STATE_H
            gl.glViewport(0, 0, VP_W, VP_H)
            t.enable()

            render_objects()

            image_data = pyglet.image.get_buffer_manager().get_color_buffer().get_image_data()
            arr = np.fromstring(image_data.data, dtype=np.uint8, sep='')
            arr = arr.reshape(VP_H, VP_W, 4)
            arr = arr[::-1, :, 0:3]

        if mode=="rgb_array" and not self.human_render: # agent can call or not call base_env.render() itself when recording video.
            win.flip()

        if mode=='human':
            self.human_render = True
            win.clear()
            t = self.transform
            gl.glViewport(0, 0, WINDOW_W, WINDOW_H)

            render_objects()

            win.flip()

        self.viewer.onetime_geoms = []
        return arr

    def _init_viewer(self):
        self.viewer = rendering.Viewer(WINDOW_W, WINDOW_H)
        self.score_label = pyglet.text.Label('0000', font_size=36,
                                             x=20, y=WINDOW_H * 2.5 / 40.00, anchor_x='left', anchor_y='center',
                                             color=(255, 255, 255, 255))
        self.transform = rendering.Transform()

    def _render_path(self):
        self.viewer.draw_polyline(self.path_points, linewidth=3, color=(0.3, 0.3, 0.3))

    def _render_progress(self):
        # self.viewer.draw_circle(self.path(self.ideal_s), radius=1, res=30, color=(0.3, 0.8, 0.3))
        p = self.path(self.s).flatten()
        self.viewer.draw_circle(origin=p, radius=1, res=30, color=(0.8, 0.3, 0.3))

    def _render_obstacles(self):
        for i, o in enumerate(self.static_obstacles):
            o.draw(self.viewer, color=DETECTED_OBST_COLOR if i in self.active_static else None)

        for i, o in enumerate(self.dynamic_obstacles):
            o.draw(self.viewer, color=DETECTED_OBST_COLOR if i in self.active_dynamic else None)

    def _render_tiles(self, win):
        if self.bg is None:
            # Initialise background
            from pyglet.gl.gl import GLubyte
            data = np.zeros((int(2*PLAYFIELD), int(2*PLAYFIELD), 3))
            self.bg_h = data.shape[0]
            self.bg_w = data.shape[1]
            k = self.bg_h//100
            for x in range(0, data.shape[0], k):
                for y in range(0, data.shape[1], k):
                    data[x:x+k, y:y+k, :] = np.array((
                        int(255*min(1.0, 0.3 + 0.025 * (random() - 0.5))),
                        int(255*min(1.0, 0.7 + 0.025 * (random() - 0.5))),
                        int(255*min(1.0, 0.8 + 0.025 * (random() - 0.5)))
                    ))

            pixels = data.flatten().astype('int').tolist()
            raw_data = (GLubyte * len(pixels))(*pixels)
            bg = pyglet.image.ImageData(width=self.bg_w, height=self.bg_h, format='RGB', data=raw_data)
            bg.save('/tmp/bg.png')
            self.bg = pyglet.sprite.Sprite(bg, x=-self.bg_w/2, y=-self.bg_h/2)
            self.bg.scale = 1

        self.bg.draw()

    def _render_indicators(self, W, H):

        s = W/40.0
        h = H/40.0
        boatw = 1.3*25
        gl.glBegin(gl.GL_QUADS)
        gl.glColor4f(0,0,0,1)
        gl.glVertex3f(W, 0, 0)
        gl.glVertex3f(W, 5*h, 0)
        gl.glVertex3f(0, 5*h, 0)
        gl.glVertex3f(0, 0, 0)
        gl.glEnd()

        def vertical_ind(place, val, color):
            gl.glBegin(gl.GL_QUADS)
            gl.glColor3f(*color)
            gl.glVertex3f((place+0)*s, 2*h + h*val, 0)
            gl.glVertex3f((place+1)*s, 2*h + h*val, 0)
            gl.glVertex3f((place+1)*s, 2*h, 0)
            gl.glVertex3f((place+0)*s, 2*h, 0)
            gl.glEnd()


        def horiz_ind(place, val, color):
            gl.glBegin(gl.GL_QUADS)
            gl.glColor4f(color[0], color[1], color[2], 1)
            gl.glVertex3f((place+0)*s, 4*h, 0)
            gl.glVertex3f((place+val)*s, 4*h, 0)
            gl.glVertex3f((place+val)*s, 2*h, 0)
            gl.glVertex3f((place+0)*s, 2*h, 0)
            gl.glEnd()

        def gl_boat(x, y):
            # Draw boat shape
            gl.glBegin(gl.GL_LINES)
            gl.glColor3f(0.9, 0.9, 0.9)
            gl.glVertex2f(x, y)
            gl.glVertex2f(x + boatw, y)
            gl.glVertex2f(x + boatw, y)
            gl.glVertex2f(x + boatw, y + 2 * h)
            gl.glVertex2f(x + boatw, y + 2 * h)
            gl.glVertex2f(x + boatw / 2, y + 2.5 * h)
            gl.glVertex2f(x + boatw / 2, y + 2.5 * h)
            gl.glVertex2f(x, y + 2*h)
            gl.glVertex2f(x, y + 2*h)
            gl.glVertex2f(x, y)
            gl.glEnd()

        def gl_arrow(x, y, angle, length, color=(0.9, 0.9, 0.9)):
            L = 50
            T = np.clip(7*length, 0, 7)
            hx, hy = x + length*L*cos(angle), y + length*L*sin(angle)

            gl.glEnable(gl.GL_LINE_SMOOTH)
            gl.glLineWidth(2)
            gl.glBegin(gl.GL_LINES)
            gl.glColor3f(*color)
            gl.glVertex2f(x, y)
            gl.glVertex2f(hx, hy)
            gl.glEnd()

            gl.glBegin(gl.GL_TRIANGLES)
            gl.glVertex2f(hx+T*cos(angle), hy+T*sin(angle))
            gl.glVertex2f(hx + T*cos(angle + 2*pi/3), hy + T*sin(angle + 2*pi/3))
            gl.glVertex2f(hx + T*cos(angle + 4*pi/3), hy + T*sin(angle + 4*pi/3))
            gl.glEnd()

        def obst_ind(place):
            gl_boat(place * s, h)
            static_obstacle_obs = self.last_obs[NS+NR:NS+NR + 2*STATIC_OBST_SLOTS]
            dynamic_obstacle_obs = self.last_obs[NS+NR + 2*STATIC_OBST_SLOTS:NS+NR + 2*STATIC_OBST_SLOTS + 4*DYNAMIC_OBST_SLOTS]

            for i in range(STATIC_OBST_SLOTS):
                heading = pi*static_obstacle_obs[2*i]
                closeness = static_obstacle_obs[2*i+1]
                gl_arrow(place * s + boatw/2, 2*h,
                         angle=heading+pi/2,
                         length=np.clip(closeness, 0.1, 1),
                         color=(np.clip(1.2*closeness, 0, 1), 0.5, 0.1))

            for i in range(DYNAMIC_OBST_SLOTS):
                heading = pi*dynamic_obstacle_obs[4*i]
                closeness = dynamic_obstacle_obs[4*i+1]
                gl_arrow(place * s + boatw/2, 2*h,
                         angle=heading+pi/2,
                         length=np.clip(closeness, 0.1, 1),
                         color=(np.clip(1.2*closeness, 0, 1), 0.5, 0.1))

        scale = 3
        R = self.ship.ref[0]
        true_speed = np.sqrt(np.square(self.ship.linearVelocity[0]) + np.square(self.ship.linearVelocity[1]))
        if NR == 2:
            ref_speed_error = self.last_obs[0]
            vertical_ind(6, -scale*ref_speed_error, color=(np.clip(R/MAX_SURGE, 0, 1), 0.5, 0.1))
        state_speed_error = self.last_obs[NR+0]
        vertical_ind(7, -scale*state_speed_error, color=(np.clip(true_speed/MAX_SURGE, 0, 1), 0.6, 0.1))

        # Visualise the obstacles as seen by the ship
        obst_ind(place=20)

        self.score_label.text = "{:2.2f}".format(self.reward)
        self.score_label.draw()


