import inspect
import numpy as np
from time import time
from gncgym.base_env.base import BaseShipScenario
import gncgym.scenarios as scenarios


def play_scenario(game):
    scenarios.autoload()  # Auto-imports all Scenario classes found in the scenarios directory.

    if game not in scenarios.available_scenarios:
        raise Exception('The scenario {} has not been implemented.'.format(game))
    else:
        env = scenarios.available_scenarios[game]()

    from pyglet.window import key

    da = np.array([0.0, 0.0])

    def key_press(k, mod):
        if k == key.LEFT:  da[0] = 1
        if k == key.RIGHT: da[0] = -1
        if k == key.UP:    da[1] = 1
        if k == key.DOWN:  da[1] = -1

    def key_release(k, mod):
        nonlocal restart, quit
        if k == key.R:
            restart = True
            print('Restart')
        if k == key.Q:
            quit = True
            print('quit')
        if k == key.LEFT and da[0] != 0: da[0] = 0
        if k == key.RIGHT and da[0] != 0: da[0] = 0
        if k == key.UP:    da[1] = 0
        if k == key.DOWN:  da[1] = 0

    env.render()
    record_video = False
    if record_video:
        env.monitor.start('/tmp/video-test', force=True)
    env.viewer.window.on_key_press = key_press
    env.viewer.window.on_key_release = key_release

    try:
        while True:
            a = np.array([0.0, 0.0])
            env.reset()
            a[0] = env.ship.angle/np.pi
            total_reward = 0.0
            steps = 0
            t = time()
            restart = False
            quit = False
            while True:
                t, dt = time(), time()-t
                a[0] = ((a[0] + dt*da[0] + 1) % 2) - 1
                a[1] = np.clip(a[1] + dt*da[1], 0, 1)

                obs, r, done, info = env.step(da)
                total_reward += r
                if steps % 200 == 0 or done:
                    print("\nObservation: {}".format(obs))
                    print("action " + str(["{:+0.2f}".format(x) for x in a]))
                    print("step {} total_reward {:+0.2f}".format(steps, total_reward))
                steps += 1
                if not record_video:  # Faster, but you can as well call base_env.render() every time to play full window.
                    env.render()

                if quit: raise KeyboardInterrupt
                if done or restart: break

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
