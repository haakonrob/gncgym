from gym.envs.registration import register
from gym.error import Error as GymError
from gncgym.scenarios.example_scenarios import *


"""
Wrap in a try-catch block because gym complians about re-registering 
environments when running tests.
"""
try:
    register(
        id='shipExampleScenario-v0',
        entry_point='gncgym.env:ExampleScenario',
    )

    register(
        id='shipStraightPathFollowing-v0',
        entry_point='gncgym.env:StraightPathScenario',
    )

    register(
        id='shipCurvedPathFollowing-v0',
        entry_point='gncgym.env:CurvedPathScenario',
    )

    register(
        id='shipStraightPathFollowingWithOvertaking-v0',
        entry_point='gncgym.env:StraightPathOvertakingScenario',
    )

    register(
        id='shipCurvedPathFollowingWithOvertaking-v0',
        entry_point='gncgym.env:CurvedPathOvertakingScenario',
    )

    register(
        id='shipCurvedPathFollowingWithShipCollision-v0',
        entry_point='gncgym.env:CurvedPathShipCollisionScenario',
    )

    register(
        id='shipCurvedPathStaticObstacles-v0',
        entry_point='gncgym.env:CurvedPathStaticObstacles',
    )

    register(
        id='shipCurvedPathStaticDynamicObstacles-v0',
        entry_point='gncgym.env:CurvedPathStaticDynamicObstacles',
    )

except GymError as e:
    print(e)

