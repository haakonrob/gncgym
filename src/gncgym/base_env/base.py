import os
import gym
import numpy as np
import pyglet
from pyglet import gl
from gym import spaces
from numpy import pi, sin, cos, arctan2
from collections import namedtuple

from gncgym import simulator as sim
from gncgym.definitions import State6DOF, EnvSnapshot, ModuleSnapshot
from . import rendering
from .objects import Vessel2D # , MAX_SURGE
from gncgym.utils import distance, rotate, angwrap
from gym.utils import seeding, EzPickle

from types import SimpleNamespace
from numpy.random import random

from .indicators import Dashboard, VerticalIndicator, TextLabel, ObstacleVectorsIndicator

"""
    
"""

# TODO make window resizable
STATE_W = 96   # less than Atari 160x192
STATE_H = 96
VIDEO_W = 600
VIDEO_H = 400
WINDOW_W = 1200
WINDOW_H = 1000

s = WINDOW_W / 80.0  # Basic unit of window width
h = WINDOW_H / 40.0  # Basic unit of window height

SCALE       = 5.0        # Track scale
PLAYFIELD   = 3000/SCALE # Game over boundary
FPS         = 50
ZOOM        = 1          # Camera zoom
ZOOM_FOLLOW = True       # Set to False for fixed view (don't use zoom)

LOS_DISTANCE = 75
OBST_RANGE = 150
OBST_PENALTY = 25
DETECTED_OBST_COLOR = (0.1, 0.7, 0.2)

# TODO Try alternative observation methods
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


class BaseScenario(gym.Env, EzPickle):
    """BaseShipScenario"""

    """Default values"""
    sim_t = 0                       # Time
    bg = None                       # Background
    objective = SimpleNamespace()   # Namespace for variables related to the objective
    viewer = None                   # Renderer, draw shapes
    last_obs = None                 # Last observation made
    np_random = None                # Random number generator used for generation, ensures reproducibility with seed()
    objects = []                    # Contains objects in the environment
    vessel = None                   # Object for visualising the model state
    indicators = []                 # List of Indicators that display custom information
    base_initialised = False        # Flag to check that the user initialises the env using env.reset()

    metadata = {
        'render.modes': ['human', 'rgb_array', 'state_pixels'],
        'video.frames_per_second': FPS
    }

    """
    ### User defined functions ###
    
    The only required function is generate_scenario, which allows
    the user to customise variables freely, such as adding obstacles to env.objects, or initialising
    the objective in a certain way. 
    """

    def generate_scenario(self, rng):
        raise NotImplemented("Generate() must be implemented. It must at least set the self.ship variable.")

    """
    ### Mix-in functions ###
    These functions must be implemented by subclasses. Some are mandatory, like the Model and objective functions,
    but others have suitable defaults.
    """
    def _reset_model(self, initial_state):
        raise NotImplementedError

    def _model(self, action):
        raise NotImplementedError

    def reset_objective(self, namespace, rng):
        raise NotImplementedError

    def eval_objective(self, namespace, action, state_est, state):
        raise NotImplementedError

    def render_objective(self, namespace, viewer):
        raise NotImplementedError

    def navigate(self, state):
        pass

    def disturbance(self, rng):
        pass


    """
    ### OpenAI Gym API ###
        reset()
        step()
        render()
        seed()
        close()
    """

    def reset(self):
        """
        initial_state = self.generate(self.np_random)
        self.model_init(initial_state)
        :return:
        """
        sim.init(
            solver='fixed_step',
            step_size=0.05,
        )

        if self.np_random is None:
            self.seed()

        # Generate scenario using the seeded RNG
        # self.generate(self.np_random)

        # Initialise the objective
        action = np.zeros(self._model_input_space.shape)
        initial_state = self.reset_objective(self.objective, self.np_random)

        # Initialise the model and get initial observation
        self._reset_model(initial_state)
        state = self._model(action)
        state_est = self.navigate(state)
        self.last_obs, _, _ = self.eval_objective(self.objective, action, state_est, state)

        # Create Vessel object for drawing
        self.vessel = Vessel2D(state)

        # Create indicators
        # TODO Fix scaling issues, need max surge 
        self.obs_indicator = ObstacleVectorsIndicator(position=(20 * s, h), dim=(s, h), veclen=1)
        self.indicators = [
            Dashboard(width=WINDOW_W, height=h),
            TextLabel((20, WINDOW_H * 2.5 / 40.00), fontsize=36,
                      color=(255, 255, 255, 255), val_fn=lambda: self.objective.reward),
            VerticalIndicator(position=(s * 14, 1.6 * h),
                              dim=(1.5 * s, 1.5 * h),
                              val_range=(0, 1),
                              goal_val=4,
                              color_range=((0, 0.6, 0.1), (1, 0.6, 0.1)),
                              val_fn=lambda: self.vessel.state.surge)]

        # One time setups
        if self.viewer is None:
            self._init_viewer()

        if self.bg is None:
            self._init_background()

        self.base_initialised = True
        return self.last_obs

    def step(self, action):
        # TODO Reshape step() into a simple control loop with various modules
        """
        v = self.disturbance()
        x = self.model(u, v)
        y = self.observe(xn)
        obs = self.objective(xn, yn)  # e = (obs, step_r, done, info)
        self.objects = []
        for o in self.objects:
            o.step()
        snapshot = EnvSnapshot(timestamp=t, vessel=x, objects=self.objects.copy(), disturbances=v}
        history.add(snapshot)
        return obs

        """

        # Step the simulation
        sim.env.step()  # Updates dt
        state = self._model(action)

        # Get a state estimate using the Navigator
        state_est = self.navigate(state)

        # Evaluate the current state and the action taken according to the Objective
        self.last_obs, sr, done = self.eval_objective(self.objective, action, state_est, state)

        # Update drawing objects
        self.vessel.update(state, action)
        for o in self.objects:
            o.update()

        # TODO After updating, put all of the objects into a snapshot that the render function will take in

        return self.last_obs, sr, done, {}

    def close(self):
        self.destroy()
        if self.viewer is not None:
            self.viewer.close()
            self.viewer = None

    def destroy(self):
        pass

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def render(self, mode='human'):
        if not self.base_initialised:
            raise AttributeError('The environment has not been initialised. '
                                 'Call env.reset() before running the environment')

        zoom = 0.1 * SCALE * max(1 - sim.env.time, 0) + ZOOM * SCALE * min(sim.env.time, 1)   # Animate zoom first second

        scroll_x = self.vessel.state.position.x
        scroll_y = self.vessel.state.position.y
        angle = -self.vessel.angle
        vel = self.vessel.linearVelocity

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

            self._render_objects()

            image_data = pyglet.image.get_buffer_manager().get_color_buffer().get_image_data()
            arr = np.fromstring(image_data.data, dtype=np.uint8, sep='')
            arr = arr.reshape(VP_H, VP_W, 4)
            arr = arr[::-1, :, 0:3]

        if mode=="rgb_array" and not self.human_render: # agent can call or not call env.render() itself when recording video.
            win.flip()

        if mode=='human':
            self.human_render = True
            win.clear()
            gl.glViewport(0, 0, WINDOW_W, WINDOW_H)

            self._render_objects()

            win.flip()

        self.viewer.onetime_geoms = []
        return arr

    def _render_objects(self):
        # Draw objects with coordinate transform
        self.transform.enable()

        self.bg.draw()
        self.render_objective(self.objective, self.viewer)
        self.vessel.draw(self.viewer)

        for o in self.objects:
            o.draw()

        for geom in self.viewer.onetime_geoms:
            geom.render()

        self.transform.disable()

        # Draw indicators without coordinate transform
        self.obs_indicator.draw()
        for i in self.indicators:
            i.draw()

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
            if not os.path.exists('.tmp/'):
                os.mkdir('./tmp')
            bg.save('./tmp/bg.png')
            self.bg = pyglet.sprite.Sprite(bg, x=-self.bg_w/2, y=-self.bg_h/2)
            self.bg.scale = 1

        self.bg.draw()

    # def _render_progress(self):
    #     # self.viewer.draw_circle(self.path(self.ideal_s), radius=1, res=30, color=(0.3, 0.8, 0.3))
    #     p = self.path(self.s).flatten()
    #     self.viewer.draw_circle(origin=p, radius=1, res=30, color=(0.8, 0.3, 0.3))

    # # TODO remove, objects should just be drawn as is. To get the color I can use a callback
    # def _render_obstacles(self):
    #     for i, o in enumerate(self.static_obstacles):
    #         o.draw(self.viewer, color=DETECTED_OBST_COLOR if i in self.active_static else None)
    #
    #     for i, o in enumerate(self.dynamic_obstacles):
    #         o.draw(self.viewer, color=DETECTED_OBST_COLOR if i in self.active_dynamic else None)

    def _init_background(self):
        """ Generate background texture so that we can see that the vessel is moving"""
        from pyglet.gl.gl import GLubyte
        # TODO make background texture tiling
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

    # TODO Move obstacle indicators to objective.py
    def _render_indicators(self, W, H):

        s = W/40.0
        h = H/40.0
        boatw = 1.3*25

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

        # Visualise the obstacles as seen by the ship
        obst_ind(place=20)


class EnvHistory:
    Snapshots = namedtuple('Snapshots', ['env', 'modules'])

    def __init__(self):
        self.timestamps = []
        self.snapshots = []
        self.modules = []
        self.metadata = {}

    def add(self, env_snapshot, module_snapshot):
        assert env_snapshot.timestamp == module_snapshot.timestamp
        self.timestamps.append(env_snapshot.timestamp)
        self.snapshots.append(type(self).Snapshots(env=env_snapshot, modules=module_snapshot))
