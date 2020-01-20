from gncgym.cli import play
from gncgym import BaseScenario
from gncgym.models.supplyship3DOF import SupplyShip3DOF
from gncgym.objectives. pathfollowing import PathFollowing


class MyScenario(BaseScenario, SupplyShip3DOF, PathFollowing):
    pass


play(('--scenario=ExampleScenario',))
