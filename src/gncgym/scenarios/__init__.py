import os
import sys
import importlib
from gncgym.utils import auto_load_classes

this = sys.modules[__name__]

this.available_scenarios = None


def autoload():
    """
    Function to automatically load and import classes that are defined in the scenarios folder. References to the
    discovered scenarios are saved in scenarios.available_scenarios
    :return dict: Contains the discovered scenario classes in the scenarios folder, indexed by class name
    """
    from gncgym.base_env.base import BaseShipScenario

    if this.available_scenarios is None:
        this.available_scenarios = auto_load_classes(['gncgym', 'scenarios'], BaseShipScenario)
    return this.available_scenarios
