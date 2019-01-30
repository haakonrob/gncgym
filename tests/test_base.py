import gym
from gncgym.envs.scenarios import ExampleScenario
import numpy as np



class TestBase:
    def test_env(self):
        env = ExampleScenario()
        action = [0, 0]
        first_obs = env.reset()
        assert(type(first_obs) is np.ndarray)
        for _ in range(100):
            obs, sr, done, info = env.step(action)
        assert(type(first_obs) == type(obs))
        assert(first_obs.shape == obs.shape)
        assert(type(float(sr)) is float)  # Just make sure that you can interpret the output as float
        assert (type(done) is bool)
