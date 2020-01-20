from gncgym.base_env.base import BaseScenario

from gncgym.objectives.pathfollowing import PathFollowing
from gncgym.models.supplyship3DOF import SupplyShip3DOF
from gncgym.models.auv import AUV2D
from gncgym.navigators.navigator import IdentityNavigator


class ExampleScenario(PathFollowing, SupplyShip3DOF, IdentityNavigator, BaseScenario):
    def generate(self, rng):
        # self.path = RandomLineThroughOrigin(rng, length=500)
        # x, y = self.path(0)
        # angle = self.path.get_angle(0)
        # self.speed = 4
        #
        # self.vessel = Vessel2D(angle, x, y)
        #
        # self.static_obstacles.append(
        #     StaticObstacle(position=self.path(100), radius=10, color=(0.6, 0, 0))
        # )
        #
        # self.dynamic_obstacles.append(
        #     DynamicObstacle(self.path, speed=4, init_s=50)
        # )
        pass
