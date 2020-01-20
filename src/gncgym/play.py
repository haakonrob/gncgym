import inspect
import numpy as np
from time import time
from gncgym.base_env.base import BaseScenario
import gncgym.scenarios as scenarios


def play_scenario(game):
    scenarios.autoload()  # Auto-imports all Scenario classes found in the scenarios directory.

    if game not in scenarios.available_scenarios:
        raise Exception('The scenario {} has not been implemented.'.format(game))
    else:
        env = scenarios.available_scenarios[game]()

    from pyglet.window import key

    def key_press(k, mod):
        if k == key.LEFT:  a[1] = 1
        if k == key.RIGHT: a[1] = -1
        if k == key.UP:    a[0] = 1
        if k == key.DOWN:  a[0] = -1

    def key_release(k, mod):
        nonlocal restart, quit
        if k == key.R:
            restart = True
            print('Restart')
        if k == key.Q:
            quit = True
            print('quit')
        if k == key.LEFT and a[1] != 0: a[1] = 0
        if k == key.RIGHT and a[1] != 0: a[1] = 0
        if k == key.UP:    a[0] = 0
        if k == key.DOWN:  a[0] = 0

    env.reset()
    env.render()
    record_video = False
    if record_video:
        env.monitor.start('/tmp/video-test', force=True)
    env.viewer.window.on_key_press = key_press
    env.viewer.window.on_key_release = key_release

    try:
        while True:
            a = np.array([0.0, 0.0])
            total_reward = 0.0
            steps = 0
            t = time()
            restart = False
            quit = False
            while True:
                t, dt = time(), time()-t
                a[0] = np.clip(a[0], 0, 1)
                a[1] = np.clip(a[1], -1, 1)
                obs, r, done, info = env.step(a)
                total_reward += r

                if False and steps % 200 == 0 or done:
                    print("\nObservation: {}".format(obs))
                    print("action " + str(["{:0.2f}".format(x) for x in a]))
                    print("step {} total_reward {:+0.2f}".format(steps, total_reward))
                steps += 1
                env.render()

                if quit: raise KeyboardInterrupt
                if done or restart: break

            env.reset()

    except KeyboardInterrupt:
        pass

    env.close()


if __name__ == '__main__':
    # choice = 'CurvedPathShipCollisionScenario'
    # choice = 'CircularPathScenario'
    # choice = 'StraightPathManyStaticObstaclesScenario'
    # choice = 'ExampleScenario'
    choice = 'CurvedPathStaticObstacles'
    # choice = 'CurvedPathStaticDynamicObstacles'
    play_scenario(choice)
