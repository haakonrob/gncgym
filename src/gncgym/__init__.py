import logging
from gym.envs.registration import register
from gym.error import Error as GymError
from gncgym.envs.scenarios import *


"""
Wrap in a try-catch block because gym complians about re-registering 
environments when running tests.
"""
try:
    register(
        id='shipExampleScenario-v0',
        entry_point='gncgym.envs:ExampleScenario',
    )

    register(
        id='shipStraightPathFollowing-v0',
        entry_point='gncgym.envs:StraightPathScenario',
    )

    register(
        id='shipCurvedPathFollowing-v0',
        entry_point='gncgym.envs:CurvedPathScenario',
    )

    register(
        id='shipStraightPathFollowingWithOvertaking-v0',
        entry_point='gncgym.envs:StraightPathOvertakingScenario',
    )

    register(
        id='shipCurvedPathFollowingWithOvertaking-v0',
        entry_point='gncgym.envs:CurvedPathOvertakingScenario',
    )

    register(
        id='shipCurvedPathFollowingWithShipCollision-v0',
        entry_point='gncgym.envs:CurvedPathShipCollisionScenario',
    )

    register(
        id='shipCurvedPathStaticObstacles-v0',
        entry_point='gncgym.envs:CurvedPathStaticObstacles',
    )

    register(
        id='shipCurvedPathStaticDynamicObstacles-v0',
        entry_point='gncgym.envs:CurvedPathStaticDynamicObstacles',
    )

except GymError as e:
    print(e)

